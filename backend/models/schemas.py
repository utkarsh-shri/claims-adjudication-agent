from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ClaimRequest(BaseModel):
    claim_id: str
    member_id: str
    drug_ndc: str
    drug_name: str
    prescriber_npi: str
    quantity: float = Field(..., gt=0, le=1000, description="Must be between 1 and 1000")
    days_supply: int = Field(..., gt=0, le=365, description="Must be between 1 and 365")
    diagnosis_code: str

class ClaimResponse(BaseModel):
    claim_id: str
    status: str
    final_decision: Optional[str] = None
    denial_reason: Optional[str] = None
    confidence_score: Optional[float] = None
    reasoning_steps: List[str] = []

class ReviewDecisionRequest(BaseModel):
    claim_id: str
    reviewer_id: str
    decision: str  # APPROVED or DENIED
    override_reason: Optional[str] = None

class PendingClaim(BaseModel):
    id: str
    claim_id: str
    reviewer_id: Optional[str] = None
    review_reason: Optional[str] = None
    queued_at: datetime
    claims: Dict[str, Any]  # the joined claim data

class DashboardResponse(BaseModel):
    pending_reviews: List[PendingClaim]
