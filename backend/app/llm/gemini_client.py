import asyncio
import time

from google import genai

from app.core.config import settings


class GeminiClient:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate(self, prompt: str, model_name: str | None = None) -> tuple[str, int]:
        model = model_name or settings.gemini_model
        started_at = time.perf_counter()

        last_error: Exception | None = None
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                text = await asyncio.to_thread(
                    self._call_gemini,
                    model,
                    prompt,
                )

                latency_ms = int((time.perf_counter() - started_at) * 1000)
                return text, latency_ms

            except Exception as exc:
                last_error = exc

                if not self._is_retryable_error(exc) or attempt == max_attempts - 1:
                    raise

                # Backoff: 1s, then 2s.
                await asyncio.sleep(2**attempt)

        raise RuntimeError(f"Gemini call failed: {last_error}")

    def _call_gemini(self, model: str, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text or ""

    def _is_retryable_error(self, exc: Exception) -> bool:
        message = str(exc).upper()

        retryable_markers = [
            "503",
            "UNAVAILABLE",
            "429",
            "RESOURCE_EXHAUSTED",
            "500",
            "INTERNAL",
            "DEADLINE_EXCEEDED",
        ]

        return any(marker in message for marker in retryable_markers)