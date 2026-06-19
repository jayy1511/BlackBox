from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import DetectedEntity, LlmCall, PolicyDecision, Run
from app.schemas.run import (
    EntityResponse,
    LlmCallResponse,
    PolicyDecisionResponse,
    RunCreateRequest,
    RunCreateResponse,
    RunDetailResponse,
    RunListItemResponse,
    RunListResponse,
)
from app.services.run_service import RunService

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=RunCreateResponse)
async def create_run(
    payload: RunCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = RunService()

    return await service.create_run(
        db=db,
        input_text=payload.input,
        policy_mode=payload.policy_mode,
        model_name=payload.model,
    )


@router.get("", response_model=RunListResponse)
async def list_runs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(select(func.count()).select_from(Run))
    total = total_result.scalar_one()

    runs_result = await db.execute(
        select(Run)
        .order_by(Run.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    runs = runs_result.scalars().all()

    items: list[RunListItemResponse] = []

    for run in runs:
        entity_count_result = await db.execute(
            select(func.count())
            .select_from(DetectedEntity)
            .where(DetectedEntity.run_id == run.id)
        )
        entities_count = entity_count_result.scalar_one()

        llm_result = await db.execute(
            select(LlmCall)
            .where(LlmCall.run_id == run.id)
            .order_by(LlmCall.created_at.desc())
            .limit(1)
        )
        llm_call = llm_result.scalar_one_or_none()

        items.append(
            RunListItemResponse(
                run_id=str(run.id),
                status=run.status,
                policy_mode=run.policy_mode,
                risk_level=run.risk_level,
                model_provider=run.model_provider,
                model_name=run.model_name,
                created_at=run.created_at,
                entities_count=entities_count,
                llm_status=llm_call.status if llm_call else None,
            )
        )

    return RunListResponse(items=items, total=total)


@router.get("/{run_id}", response_model=RunDetailResponse)
async def get_run_detail(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    run_result = await db.execute(select(Run).where(Run.id == run_id))
    run = run_result.scalar_one_or_none()

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    entities_result = await db.execute(
        select(DetectedEntity)
        .where(DetectedEntity.run_id == run.id)
        .order_by(DetectedEntity.created_at.asc())
    )
    entities = entities_result.scalars().all()

    decisions_result = await db.execute(
        select(PolicyDecision)
        .where(PolicyDecision.run_id == run.id)
        .order_by(PolicyDecision.created_at.asc())
    )
    decisions = decisions_result.scalars().all()

    llm_result = await db.execute(
        select(LlmCall)
        .where(LlmCall.run_id == run.id)
        .order_by(LlmCall.created_at.desc())
        .limit(1)
    )
    llm_call = llm_result.scalar_one_or_none()

    entity_payload = [
        EntityResponse(
            type=entity.entity_type,
            source=entity.source,
            start_index=entity.start_index,
            end_index=entity.end_index,
            confidence=entity.confidence,
            risk_level=entity.risk_level,
            action=entity.action,
            replacement_value=entity.replacement_value,
        )
        for entity in entities
    ]

    decisions_payload = [
        PolicyDecisionResponse(
            rule_id=decision.rule_id,
            policy_mode=decision.policy_mode,
            action=decision.action,
            reason=decision.reason,
            created_at=decision.created_at,
        )
        for decision in decisions
    ]

    llm_payload = (
        LlmCallResponse(
            provider=llm_call.provider,
            model_name=llm_call.model_name,
            latency_ms=llm_call.latency_ms,
            status=llm_call.status,
            error_message=llm_call.error_message,
            created_at=llm_call.created_at,
        )
        if llm_call
        else None
    )

    report = {
        "input_entities_count": len([entity for entity in entities if entity.source == "input"]),
        "response_entities_count": len(
            [entity for entity in entities if entity.source == "model_response"]
        ),
        "critical_entities_count": len(
            [entity for entity in entities if entity.risk_level == "critical"]
        ),
        "high_entities_count": len(
            [entity for entity in entities if entity.risk_level == "high"]
        ),
        "tokenized_count": len([entity for entity in entities if entity.action == "tokenize"]),
        "warned_count": len([entity for entity in entities if entity.action == "warn"]),
        "flagged_response_count": len(
            [
                entity
                for entity in entities
                if entity.source == "model_response" and entity.action == "flag"
            ]
        ),
        "llm_status": llm_call.status if llm_call else None,
    }

    return RunDetailResponse(
        run_id=str(run.id),
        status=run.status,
        policy_mode=run.policy_mode,
        risk_level=run.risk_level,
        model_provider=run.model_provider,
        model_name=run.model_name,
        created_at=run.created_at,
        protected_prompt=run.protected_prompt,
        model_response=run.model_response,
        detected_entities=entity_payload,
        policy_decisions=decisions_payload,
        llm_call=llm_payload,
        report=report,
    )