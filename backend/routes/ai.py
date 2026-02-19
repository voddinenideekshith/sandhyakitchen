from fastapi import APIRouter, HTTPException

from services.ai import generate_response, AIRequest, AIResponse, health_check

router = APIRouter()


@router.post("/test", response_model=AIResponse)
async def ai_test(request: AIRequest):
    try:
        resp = await generate_response(request)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ai_health():
    return await health_check()
