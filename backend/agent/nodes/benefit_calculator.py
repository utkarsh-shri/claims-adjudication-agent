from ..state import ClaimState

def benefit_calculator(state: ClaimState) -> ClaimState:
    if state.get('final_decision') == 'DENIED':
        return state

    member = state.get('member_data', {})
    drug = state.get('drug_data', {})

    tier = drug.get('tier', 1)
    copay_key = f"copay_tier{tier}"
    
    member_copay = float(member.get(copay_key, 0.0))
    total_cost = float(tier) * 50.0 * float(state.get('quantity', 1.0))
    plan_pays = max(0.0, total_cost - member_copay)

    state['benefit_result'] = {
        'member_copay': member_copay,
        'plan_pays': plan_pays,
        'total_cost': total_cost
    }

    state['reasoning_steps'].append(
        f"BENEFIT CALC ✅: Tier {tier} copay is ${member_copay:.2f}. Plan pays ${plan_pays:.2f}."
    )
    return state
