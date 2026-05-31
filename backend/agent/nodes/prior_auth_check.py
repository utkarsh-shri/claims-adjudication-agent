from ..state import ClaimState
from database.client import get_supabase

def prior_auth_check(state: ClaimState) -> ClaimState:
    if state.get('final_decision') == 'DENIED':
        return state

    drug = state.get('drug_data', {})
    
    if drug.get('pa_required'):
        # Check if PA is on file.
        supabase = get_supabase()
        # Query review queue for past approved PA overrides or just mock for now
        # Actually, let's query the review queue for an approved human decision for this claim_id
        # if this claim was previously pended and approved by a human.
        result = supabase.table('review_queue')\
            .select('*')\
            .eq('claim_id', state['claim_id'])\
            .eq('human_decision', 'APPROVED')\
            .execute()
            
        has_pa = len(result.data) > 0
        
        if not has_pa:
            state['prior_auth_result'] = {'pa_approved': False}
            state['final_decision'] = 'DENIED'
            state['denial_reason'] = 'Prior Authorization required but not on file.'
            state['reasoning_steps'].append(
                f"PRIOR AUTH ❌: PA required for {drug['drug_name']} but none on file."
            )
            return state
        else:
            state['prior_auth_result'] = {'pa_approved': True}
            state['reasoning_steps'].append(
                f"PRIOR AUTH ✅: Valid PA found for {drug['drug_name']}."
            )
    else:
        state['prior_auth_result'] = {'pa_required': False}
        state['reasoning_steps'].append(
            "PRIOR AUTH ✅: No PA required."
        )

    return state
