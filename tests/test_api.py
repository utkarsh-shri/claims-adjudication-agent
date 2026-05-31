import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from main import app

client = TestClient(app)

@patch('api.claims.claims_graph.invoke')
@patch('api.claims.save_claim')
def test_process_claim_endpoint(mock_save, mock_invoke):
    mock_invoke.return_value = {
        'claim_id': 'TEST-123',
        'member_id': 'MBR-1',
        'drug_ndc': 'NDC-1',
        'drug_name': 'Drug',
        'prescriber_npi': 'NPI',
        'quantity': 30,
        'days_supply': 30,
        'diagnosis_code': 'D-1',
        'final_decision': 'APPROVED',
        'confidence_score': 0.9,
        'reasoning_steps': ["Step 1", "Step 2"]
    }
    
    response = client.post("/api/claims/process", json={
        'claim_id': 'TEST-123',
        'member_id': 'MBR-1',
        'drug_ndc': 'NDC-1',
        'drug_name': 'Drug',
        'prescriber_npi': 'NPI',
        'quantity': 30.0,
        'days_supply': 30,
        'diagnosis_code': 'D-1'
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['claim_id'] == 'TEST-123'
    assert data['status'] == 'APPROVED'
    assert data['final_decision'] == 'APPROVED'
    assert mock_save.called
