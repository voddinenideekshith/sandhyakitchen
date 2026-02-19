from pydantic import BaseModel
from typing import Optional, Dict, Any


class AIRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class AIResponse(BaseModel):
    reply: str
    tokens_used: Optional[int] = None
