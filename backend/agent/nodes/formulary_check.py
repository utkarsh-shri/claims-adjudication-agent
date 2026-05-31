from ..state import ClaimState
from database.queries import get_drug

def formulary_check(state: ClaimState) -> ClaimState:
    # If already denied, skip
    if state.get('final_decision') == 'DENIED':
        return state

    drug = get_drug(state['drug_ndc'])

    if not drug:
        state['formulary_result'] = {'covered': False, 'reason': 'Drug not found in formulary'}
        state['final_decision'] = 'DENIED'
        state['denial_reason'] = f"Drug {state['drug_ndc']} is not on the formulary."
        state['reasoning_steps'].append(
            f"FORMULARY ❌: Drug NDC {state['drug_ndc']} not found in formulary."
        )
        return state

    state['drug_data'] = drug
    state['formulary_result'] = {
        'covered': True,
        'tier': drug['tier'],
        'pa_required': drug['pa_required'],
        'drug_class': drug['drug_class']
    }

    pa_msg = "PA Required" if drug['pa_required'] else "No PA Required"
    state['reasoning_steps'].append(
        f"FORMULARY ✅: {drug['drug_name']} (Tier {drug['tier']}, {drug['drug_class']}). {pa_msg}."
    )
    return state
