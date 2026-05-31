from fastapi import APIRouter, Depends
from models.schemas import ReviewDecisionRequest
from database.queries import update_claim_status
from api.auth import get_current_user

router = APIRouter()

@router.post("/approve")
def approve_claim(request: ReviewDecisionRequest, username: str = Depends(get_current_user)):
    decision = {
        'final_decision': 'APPROVED',
        'denial_reason': None
    }
    # Update claim status in Supabase
    update_claim_status(request.claim_id, 'APPROVED', decision, request.reviewer_id)
    return {"message": f"Claim {request.claim_id} approved"}

@router.post("/reject")
def reject_claim(request: ReviewDecisionRequest, username: str = Depends(get_current_user)):
    decision = {
        'final_decision': 'DENIED',
        'denial_reason': request.override_reason or 'Rejected by human reviewer'
    }
    # Update claim status in Supabase
    update_claim_status(request.claim_id, 'DENIED', decision, request.reviewer_id)
    return {"message": f"Claim {request.claim_id} rejected"}
