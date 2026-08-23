from fastapi import APIRouter, Depends
from ..dependencies import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/ai-guide", tags=["ai-guide"])

RESPONSES = {
    "Why is this my next step?": "Model Evaluation is your next step because you've completed Supervised Learning, Classification, and Regression. Evaluating your models is the prerequisite gate before Ensemble Methods — without it, you wouldn't be able to measure whether your models actually work.",
    "Can I skip this module?": "Skipping Model Evaluation is not recommended. It's a hard prerequisite for the next 3 stages. Without it, you'd have no way to validate models you build in Deep Learning or MLOps. I'd suggest spending 45 minutes on it now — it will unlock your next stage.",
    "What should I practice today?": "Today I'd recommend working through the Cross Validation notebook in your Machine Learning stage. You have 45 minutes available, and this directly addresses your highest-priority skill gap.",
    "Why do I need this skill?": "Model Evaluation is foundational to everything that follows. In Deep Learning, you'll evaluate neural networks. In MLOps, you'll monitor model performance in production. Without knowing how to evaluate a model, you can't know if your AI system is actually working.",
    "How long will my route take?": "Based on your 7 hours/week commitment and current progress (68%), you have approximately 4-5 weeks remaining for your Machine Learning stage, then 3 weeks for Deep Learning, and 2 weeks for MLOps. Total: around 10 weeks at your current pace.",
}


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


@router.post("/chat")
async def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    msg = req.message.strip()
    
    # Check for exact or partial match
    response = None
    for key, val in RESPONSES.items():
        if key.lower() in msg.lower() or msg.lower() in key.lower():
            response = val
            break
    
    if not response:
        name = current_user.get("name", "learner")
        target = current_user.get("target_career", "your goal")
        response = f"That's a great question, {name}. Based on your current route toward {target}, I'd suggest focusing on Model Evaluation first — it's directly blocking your progression to the Deep Learning stage. Once you clear that gap, your next 3 skills will unlock automatically. Would you like me to explain why Model Evaluation matters for your specific goal?"

    return {"response": response, "role": "assistant"}
