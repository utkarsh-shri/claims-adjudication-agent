from groq import Groq
import os, json
from ..state import ClaimState

client = Groq(api_key=os.environ.get('GROQ_API_KEY', 'dummy_key_if_not_set'))

def adjudicate(state: ClaimState) -> ClaimState:
    # If already denied by upstream node, skip
    if state.get('final_decision') == 'DENIED':
        return state

    summary = "\n".join(state['reasoning_steps'])

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": f"""You are an advanced AI pharmacy claims adjudication engine.
Your job is to verify both the SYSTEM CHECKS and the CLINICAL APPROPRIATENESS of the claim.

CLAIM DETAILS:
- Drug: {state.get('drug_name', 'Unknown')}
- Quantity: {state.get('quantity')}
- Days Supply: {state.get('days_supply')}
- Diagnosis Code: {state.get('diagnosis_code')}

SYSTEM CHECKS:
{summary}

Benefit calculation: {json.dumps(state.get('benefit_result', {}))}

CRITICAL RULES:
1. If the Quantity is absurdly high for the Days Supply (e.g., > 100 pills for 30 days), you MUST output PENDING_HUMAN_REVIEW with low confidence (< 0.5).
2. If the Diagnosis Code does not logically match the Drug (e.g., a cholesterol drug for a broken arm), you MUST output PENDING_HUMAN_REVIEW with low confidence (< 0.5).
3. If all system checks passed AND the clinical details make sense, output APPROVED with high confidence (> 0.9).

Respond in JSON only:
{{
  "decision": "APPROVED" or "PENDING_HUMAN_REVIEW",
  "confidence": 0.0-1.0,
  "reasoning": "one sentence explaining your clinical reasoning"
}}"""
            }],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)
        state['final_decision'] = result['decision']
        state['confidence_score'] = result['confidence']
        state['reasoning_steps'].append(
            f"DECISION {'✅' if result['decision'] == 'APPROVED' else '⏳'}: "
            f"{result['decision']} (confidence: {result['confidence']:.2f}). "
            f"{result['reasoning']}"
        )
    except Exception as e:
        state['final_decision'] = 'PENDING_HUMAN_REVIEW'
        state['confidence_score'] = 0.0
        state['reasoning_steps'].append(
            f"DECISION ⏳: PENDING_HUMAN_REVIEW (confidence: 0.00). LLM Error: {str(e)}"
        )
        
    return state
