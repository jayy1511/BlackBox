from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.hashing import sha256_text
from app.detectors.custom_detector import CustomSensitiveDataDetector
from app.detectors.types import Detection
from app.llm.gemini_client import GeminiClient
from app.models import DetectedEntity, LlmCall, PolicyDecision, Run
from app.services.protection_service import ProtectionService


class RunService:
    def __init__(self) -> None:
        self.detector = CustomSensitiveDataDetector()
        self.protection_service = ProtectionService()
        self.gemini_client = GeminiClient()

    async def create_run(
        self,
        db: AsyncSession,
        input_text: str,
        policy_mode: str,
        model_name: str | None,
    ) -> dict:
        selected_model = model_name or settings.gemini_model

        input_detections = self.detector.detect(input_text)

        protected_prompt, replacement_records = self.protection_service.protect(
            text=input_text,
            detections=input_detections,
            policy_mode=policy_mode,
        )

        risk_level = self._calculate_risk_level(input_detections)

        run = Run(
            status="processing",
            policy_mode=policy_mode,
            model_provider="gemini",
            model_name=selected_model,
            input_hash=sha256_text(input_text),
            raw_input_stored=settings.store_raw_input,
            raw_input=input_text if settings.store_raw_input else None,
            protected_prompt=protected_prompt,
            risk_level=risk_level,
        )

        db.add(run)
        await db.flush()

        response_payload_entities: list[dict] = []

        input_payload_entities = await self._persist_input_entities(
            db=db,
            run=run,
            replacement_records=replacement_records,
            policy_mode=policy_mode,
        )

        response_payload_entities.extend(input_payload_entities)

        llm_call_row: LlmCall | None = None
        model_response: str | None = None

        try:
            model_response, latency_ms = await self.gemini_client.generate(
                prompt=protected_prompt,
                model_name=selected_model,
            )

            llm_call_row = LlmCall(
                run_id=run.id,
                provider="gemini",
                model_name=selected_model,
                latency_ms=latency_ms,
                status="success",
                error_message=None,
            )

            run.status = "completed"
            run.model_response = model_response

            response_detections = self.detector.detect(model_response)

            response_payload_entities.extend(
                await self._persist_response_entities(
                    db=db,
                    run=run,
                    detections=response_detections,
                )
            )

            combined_detections = input_detections + response_detections
            run.risk_level = self._calculate_risk_level(combined_detections)

        except Exception as exc:
            llm_call_row = LlmCall(
                run_id=run.id,
                provider="gemini",
                model_name=selected_model,
                latency_ms=None,
                status="failed",
                error_message=str(exc),
            )

            run.status = "failed"
            run.model_response = None

        db.add(llm_call_row)
        await db.commit()
        await db.refresh(run)

        report = self._build_report(
            input_detections=input_detections,
            all_payload_entities=response_payload_entities,
            llm_status=llm_call_row.status if llm_call_row else "unknown",
        )

        return {
            "run_id": str(run.id),
            "status": run.status,
            "policy_mode": run.policy_mode,
            "risk_level": run.risk_level,
            "protected_prompt": run.protected_prompt or "",
            "model_response": run.model_response,
            "detected_entities": response_payload_entities,
            "llm_call": {
                "provider": llm_call_row.provider,
                "model_name": llm_call_row.model_name,
                "latency_ms": llm_call_row.latency_ms,
                "status": llm_call_row.status,
                "error_message": llm_call_row.error_message,
            }
            if llm_call_row
            else None,
            "report": report,
        }

    async def _persist_input_entities(
        self,
        db: AsyncSession,
        run: Run,
        replacement_records: list[dict],
        policy_mode: str,
    ) -> list[dict]:
        payload_entities: list[dict] = []

        for record in replacement_records:
            detection: Detection = record["detection"]

            entity = DetectedEntity(
                run_id=run.id,
                source="input",
                entity_type=detection.entity_type,
                start_index=detection.start_index,
                end_index=detection.end_index,
                confidence=detection.confidence,
                risk_level=detection.risk_level,
                action=record["action"],
                original_value_hash=sha256_text(detection.value),
                replacement_value=record["replacement_value"],
            )

            db.add(entity)
            await db.flush()

            decision = PolicyDecision(
                run_id=run.id,
                entity_id=entity.id,
                rule_id=f"{policy_mode}_{detection.entity_type.lower()}",
                policy_mode=policy_mode,
                action=record["action"],
                reason=record["reason"],
            )

            db.add(decision)

            payload_entities.append(
                {
                    "type": entity.entity_type,
                    "source": entity.source,
                    "start_index": entity.start_index,
                    "end_index": entity.end_index,
                    "confidence": entity.confidence,
                    "risk_level": entity.risk_level,
                    "action": entity.action,
                    "replacement_value": entity.replacement_value,
                }
            )

        return payload_entities

    async def _persist_response_entities(
        self,
        db: AsyncSession,
        run: Run,
        detections: list[Detection],
    ) -> list[dict]:
        payload_entities: list[dict] = []

        for detection in detections:
            entity = DetectedEntity(
                run_id=run.id,
                source="model_response",
                entity_type=detection.entity_type,
                start_index=detection.start_index,
                end_index=detection.end_index,
                confidence=detection.confidence,
                risk_level=detection.risk_level,
                action="flag",
                original_value_hash=sha256_text(detection.value),
                replacement_value=detection.value,
            )

            db.add(entity)
            await db.flush()

            decision = PolicyDecision(
                run_id=run.id,
                entity_id=entity.id,
                rule_id=f"response_scan_{detection.entity_type.lower()}",
                policy_mode=run.policy_mode,
                action="flag",
                reason="Model response contained sensitive data and was flagged by response scanning.",
            )

            db.add(decision)

            payload_entities.append(
                {
                    "type": entity.entity_type,
                    "source": entity.source,
                    "start_index": entity.start_index,
                    "end_index": entity.end_index,
                    "confidence": entity.confidence,
                    "risk_level": entity.risk_level,
                    "action": entity.action,
                    "replacement_value": entity.replacement_value,
                }
            )

        return payload_entities

    def _calculate_risk_level(self, detections: list[Detection]) -> str:
        risk_order = {
            "unknown": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        if not detections:
            return "low"

        highest = max(detections, key=lambda item: risk_order.get(item.risk_level, 0))
        return highest.risk_level

    def _build_report(
        self,
        input_detections: list[Detection],
        all_payload_entities: list[dict],
        llm_status: str,
    ) -> dict:
        input_entities = [
            item for item in all_payload_entities if item["source"] == "input"
        ]

        response_entities = [
            item for item in all_payload_entities if item["source"] == "model_response"
        ]

        return {
            "llm_status": llm_status,
            "input_entities_count": len(input_entities),
            "response_entities_count": len(response_entities),
            "critical_entities_count": len(
                [item for item in all_payload_entities if item["risk_level"] == "critical"]
            ),
            "high_entities_count": len(
                [item for item in all_payload_entities if item["risk_level"] == "high"]
            ),
            "tokenized_count": len(
                [item for item in all_payload_entities if item["action"] == "tokenize"]
            ),
            "warned_count": len(
                [item for item in all_payload_entities if item["action"] == "warn"]
            ),
            "flagged_response_count": len(
                [item for item in response_entities if item["action"] == "flag"]
            ),
            "original_input_detection_count": len(input_detections),
        }