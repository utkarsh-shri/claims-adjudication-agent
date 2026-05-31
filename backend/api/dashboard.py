from fastapi import APIRouter, Depends
from models.schemas import DashboardResponse, PendingClaim
from database.queries import get_pending_review
from api.auth import get_current_user

router = APIRouter()

@router.get("/pending", response_model=DashboardResponse)
def get_pending(username: str = Depends(get_current_user)):
    data = get_pending_review()
    pending_claims = []
    for row in data:
        pending_claims.append(PendingClaim(
            id=str(row.get('review_id', 'unknown')),
            claim_id=row['claim_id'],
            reviewer_id=row.get('reviewer_id'),
            review_reason=row.get('review_reason'),
            queued_at=row['queued_at'],
            claims=row.get('claims', {})
        ))
    return DashboardResponse(pending_reviews=pending_claims)
