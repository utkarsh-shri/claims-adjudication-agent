from langgraph.graph import StateGraph, END
from .state import ClaimState
from .nodes.eligibility_check import eligibility_check
from .nodes.formulary_check import formulary_check
from .nodes.prior_auth_check import prior_auth_check
from .nodes.benefit_calculator import benefit_calculator
from .nodes.adjudicate import adjudicate

def should_continue(state: ClaimState) -> str:
    if state.get('final_decision') == 'DENIED':
        return 'end'
    return 'continue'

def build_graph() -> StateGraph:
    graph = StateGraph(ClaimState)

    graph.add_node('eligibility_check', eligibility_check)
    graph.add_node('formulary_check', formulary_check)
    graph.add_node('prior_auth_check', prior_auth_check)
    graph.add_node('benefit_calculator', benefit_calculator)
    graph.add_node('adjudicate', adjudicate)

    graph.set_entry_point('eligibility_check')

    graph.add_conditional_edges('eligibility_check',
        should_continue, {'continue': 'formulary_check', 'end': END})
    graph.add_conditional_edges('formulary_check',
        should_continue, {'continue': 'prior_auth_check', 'end': END})
    graph.add_conditional_edges('prior_auth_check',
        should_continue, {'continue': 'benefit_calculator', 'end': END})
    graph.add_edge('benefit_calculator', 'adjudicate')
    graph.add_edge('adjudicate', END)

    return graph.compile()

claims_graph = build_graph()
