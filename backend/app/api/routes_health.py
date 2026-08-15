from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "healthy"}

@router.get("/metrics")
async def metrics():
    # Placeholder for metrics
    return {"latency_p50": 0, "latency_p70": 0, "latency_p100": 0}