from fastapi import APIRouter, HTTPException, Depends, Request
from models.schemas import ClaimRequest, ClaimResponse
from agent.graph import claims_graph
from database.queries import save_claim
from api.auth import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/process", response_model=ClaimResponse)
@limiter.limit("5/minute")
def process_claim(request: Request, claim_req: ClaimRequest, username: str = Depends(get_current_user)):
    # Initialize state
    state = claim_req.model_dump()
    state['reasoning_steps'] = []
    
    # Run graph
    try:
        final_state = claims_graph.invoke(state)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Graph execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Graph error: {str(e)}")
        
    # Save claim to Supabase
    claim_data = {
        'claim_id': final_state['claim_id'],
        'member_id': final_state['member_id'],
        'drug_ndc': final_state['drug_ndc'],
        'drug_name': final_state['drug_name'],
        'prescriber_npi': final_state['prescriber_npi'],
        'quantity': final_state['quantity'],
        'days_supply': final_state['days_supply'],
        'diagnosis_code': final_state['diagnosis_code'],
        'status': final_state.get('final_decision', 'PENDING_HUMAN_REVIEW'),
        'final_decision': final_state.get('final_decision'),
        'denial_reason': final_state.get('denial_reason'),
        'confidence_score': final_state.get('confidence_score'),
        'member_copay': final_state.get('benefit_result', {}).get('member_copay'),
        'plan_pays': final_state.get('benefit_result', {}).get('plan_pays'),
        'reasoning_steps': final_state.get('reasoning_steps', [])
    }
    
    try:
        save_claim(claim_data)
        if claim_data['status'] == 'PENDING_HUMAN_REVIEW':
            from database.queries import add_to_review_queue
            add_to_review_queue(claim_data['claim_id'], "Flagged by AI Agent for manual review.")
    except Exception as e:
        print(f"Failed to save claim to DB: {e}")
        raise HTTPException(status_code=400, detail=f"Database error (check Member ID / NDC): {str(e)}")
    
    return ClaimResponse(
        claim_id=final_state['claim_id'],
        status=claim_data['status'],
        final_decision=final_state.get('final_decision'),
        denial_reason=final_state.get('denial_reason'),
        confidence_score=final_state.get('confidence_score'),
        reasoning_steps=final_state.get('reasoning_steps', [])
    )
