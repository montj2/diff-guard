"""Webhook endpoint stubs.

Real implementation will validate payload and enqueue a worker job.
"""

from __future__ import annotations

from fastapi import APIRouter, status

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/artifactory", status_code=status.HTTP_202_ACCEPTED)
async def artifactory_webhook() -> dict[str, bool]:  # pragma: no cover - simple stub
    """Stub handler for Artifactory webhook.

    Returns:
        dict[str,bool]: Indication that a job would be enqueued.
    """
    return {"enqueued": True}
