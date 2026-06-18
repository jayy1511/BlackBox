from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.run import RunCreateRequest, RunCreateResponse
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