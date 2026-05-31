import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_supabase():
    with patch('backend.database.queries.get_supabase') as mock:
        yield mock

@pytest.fixture
def mock_groq():
    with patch('backend.agent.nodes.adjudicate.client') as mock:
        yield mock

def test_full_happy_path(mock_supabase, mock_groq):
    from backend.agent.graph import claims_graph
    
    # Mock member query
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        'plan_id': 'PLAN-A', 'plan_type': 'COMMERCIAL', 
        'enrollment_start': '2020-01-01', 'enrollment_end': '2099-12-31',
        'copay_tier1': 5.0
    }]
    
    # Mock drug query
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        'tier': 1, 'pa_required': False, 'drug_class': 'Statin', 'drug_name': 'Atorvastatin'
    }]
    
    # Mock Groq response
    mock_choice = MagicMock()
    mock_choice.message.content = '{"decision": "APPROVED", "confidence": 0.95, "reasoning": "Standard approval"}'
    mock_groq.chat.completions.create.return_value.choices = [mock_choice]
    
    state = {
        'claim_id': '123', 'member_id': 'MBR-1', 'drug_ndc': 'NDC-1', 'quantity': 30, 'reasoning_steps': []
    }
    
    final_state = claims_graph.invoke(state)
    assert final_state['final_decision'] == 'APPROVED'
    assert final_state['confidence_score'] == 0.95

def test_denial_inactive_member(mock_supabase):
    from backend.agent.graph import claims_graph
    
    # Mock member query (expired)
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        'plan_id': 'PLAN-A', 'plan_type': 'COMMERCIAL', 
        'enrollment_start': '2020-01-01', 'enrollment_end': '2023-12-31'
    }]
    
    state = {
        'claim_id': '123', 'member_id': 'MBR-1', 'drug_ndc': 'NDC-1', 'reasoning_steps': []
    }
    
    final_state = claims_graph.invoke(state)
    assert final_state['final_decision'] == 'DENIED'
    assert 'expired' in final_state['denial_reason'].lower()

def test_hitl_low_confidence(mock_supabase, mock_groq):
    from backend.agent.graph import claims_graph
    
    # Mock valid member and drug
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        'plan_id': 'PLAN-A', 'plan_type': 'COMMERCIAL', 
        'enrollment_start': '2020-01-01', 'enrollment_end': '2099-12-31', 'copay_tier1': 5.0,
        'tier': 1, 'pa_required': False, 'drug_class': 'Class', 'drug_name': 'Drug'
    }]
    
    # Mock Groq low confidence response
    mock_choice = MagicMock()
    mock_choice.message.content = '{"decision": "PENDING_HUMAN_REVIEW", "confidence": 0.60, "reasoning": "Ambiguous diagnosis"}'
    mock_groq.chat.completions.create.return_value.choices = [mock_choice]
    
    state = {
        'claim_id': '123', 'member_id': 'MBR-1', 'drug_ndc': 'NDC-1', 'quantity': 30, 'reasoning_steps': []
    }
    
    final_state = claims_graph.invoke(state)
    assert final_state['final_decision'] == 'PENDING_HUMAN_REVIEW'
