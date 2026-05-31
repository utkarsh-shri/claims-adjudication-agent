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
            model="llama-3.1-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""You are a pharmacy claims adjudication engine.
Based on these check results, give a final decision.

{summary}

Benefit calculation: {json.dumps(state.get('benefit_result', {}))}

Respond in JSON only:
{{
  "decision": "APPROVED" or "PENDING_HUMAN_REVIEW",
  "confidence": 0.0-1.0,
  "reasoning": "one sentence"
}}

Use PENDING_HUMAN_REVIEW if confidence < 0.85 or any result is ambiguous."""
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
