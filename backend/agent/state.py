from typing import TypedDict, Optional

class ClaimState(TypedDict):
    # Input
    claim_id: str
    member_id: str
    drug_ndc: str
    drug_name: str
    prescriber_npi: str
    quantity: float
    days_supply: int
    diagnosis_code: str

    # DB lookups (populated by nodes)
    member_data: Optional[dict]
    drug_data: Optional[dict]

    # Node results
    eligibility_result: Optional[dict]
    formulary_result: Optional[dict]
    prior_auth_result: Optional[dict]
    benefit_result: Optional[dict]

    # Final
    final_decision: Optional[str]     # APPROVED | DENIED | PENDING_HUMAN_REVIEW
    denial_reason: Optional[str]
    confidence_score: Optional[float]

    # Audit trail — each node appends one string
    reasoning_steps: list[str]
