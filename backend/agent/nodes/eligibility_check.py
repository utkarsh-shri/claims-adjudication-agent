from ..state import ClaimState
from database.queries import get_member
from datetime import date

def eligibility_check(state: ClaimState) -> ClaimState:
    member = get_member(state['member_id'])

    if not member:
        state['eligibility_result'] = {'eligible': False, 'reason': 'Member not found'}
        state['final_decision'] = 'DENIED'
        state['denial_reason'] = 'Member ID not found in system'
        state['reasoning_steps'].append(
            f"ELIGIBILITY ❌: Member {state['member_id']} not found in system."
        )
        return state

    today = date.today()
    enrolled = (date.fromisoformat(str(member['enrollment_start'])) <= today
                <= date.fromisoformat(str(member['enrollment_end'])))

    state['member_data'] = member
    state['eligibility_result'] = {
        'eligible': enrolled,
        'plan_id': member['plan_id'],
        'plan_type': member['plan_type'],
        'reason': 'Active enrollment verified' if enrolled else 'Enrollment expired'
    }

    if not enrolled:
        state['final_decision'] = 'DENIED'
        state['denial_reason'] = 'Member enrollment has expired'

    state['reasoning_steps'].append(
        f"ELIGIBILITY {'✅' if enrolled else '❌'}: Member {state['member_id']} "
        f"— Plan {member['plan_id']} ({member['plan_type']}). "
        f"{'Active through ' + str(member['enrollment_end']) if enrolled else 'Enrollment expired ' + str(member['enrollment_end'])}."
    )
    return state
