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

        def _call_gemini() -> str:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text or ""

        text = await asyncio.to_thread(_call_gemini)
        latency_ms = int((time.perf_counter() - started_at) * 1000)

        return text, latency_ms