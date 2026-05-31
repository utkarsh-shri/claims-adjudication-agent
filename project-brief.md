# Project Brief: claims-adjudication-agent
## Stack: Vercel + Render + Supabase PostgreSQL + Groq

---

## One-Line Description
A LangGraph multi-step agentic workflow processing pharmacy claims end-to-end
(eligibility → formulary → prior auth → adjudication) with Human-In-The-Loop
routing. Fully hosted, free, live demo URL.

---

## Free Hybrid Stack

| Layer | Service | URL Pattern |
|-------|---------|-------------|
| Frontend (React) | Vercel | https://claims-agent.vercel.app |
| Backend (FastAPI) | Render | https://claims-agent-api.onrender.com |
| Database | Supabase PostgreSQL | your-project.supabase.co |
| LLM | Groq (Llama 3.1 70B) | api.groq.com |

No vector store needed for this project — it's all relational state management.

---

## Folder Structure

```
claims-adjudication-agent/
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── claims.py               # POST /api/claims/process
│   │   ├── review.py               # POST /api/review/approve|reject
│   │   └── dashboard.py            # GET /api/dashboard/pending
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                # LangGraph StateGraph
│   │   ├── state.py                # ClaimState TypedDict
│   │   ├── nodes/
│   │   │   ├── eligibility_check.py
│   │   │   ├── formulary_check.py
│   │   │   ├── prior_auth_check.py
│   │   │   ├── benefit_calculator.py
│   │   │   ├── adjudicate.py
│   │   │   └── hitl_router.py
│   │   └── prompts.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── client.py               # Supabase client singleton
│   │   ├── queries.py              # All DB queries in one place
│   │   └── seed.py                 # Seed Supabase with synthetic data
│   ├── models/
│   │   └── schemas.py
│   ├── requirements.txt
│   ├── .env.example
│   └── render.yaml
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── ClaimSubmit.jsx
│   │   │   ├── AgentTrace.jsx
│   │   │   └── ReviewerDashboard.jsx
│   │   ├── components/
│   │   │   ├── StepTimeline.jsx
│   │   │   ├── ClaimCard.jsx
│   │   │   └── DecisionBadge.jsx
│   │   └── api/
│   │       └── claims.js
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json
├── tests/
│   ├── test_graph.py
│   ├── test_nodes.py
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```

---

## Supabase Setup (Run Once in SQL Editor)

```sql
-- Members table
CREATE TABLE members (
  member_id TEXT PRIMARY KEY,
  plan_id TEXT NOT NULL,
  plan_type TEXT NOT NULL,           -- COMMERCIAL, MEDICAID, MEDICARE
  enrollment_start DATE NOT NULL,
  enrollment_end DATE NOT NULL,
  deductible_met BOOLEAN DEFAULT FALSE,
  copay_tier1 DECIMAL(10,2) DEFAULT 5.00,
  copay_tier2 DECIMAL(10,2) DEFAULT 15.00,
  copay_tier3 DECIMAL(10,2) DEFAULT 40.00,
  copay_tier4 DECIMAL(10,2) DEFAULT 80.00
);

-- Drugs table
CREATE TABLE drugs (
  ndc TEXT PRIMARY KEY,
  drug_name TEXT NOT NULL,
  drug_class TEXT NOT NULL,
  tier INTEGER NOT NULL CHECK (tier BETWEEN 1 AND 4),
  pa_required BOOLEAN DEFAULT FALSE,
  quantity_limit INTEGER,
  days_supply_limit INTEGER DEFAULT 90,
  step_therapy_required BOOLEAN DEFAULT FALSE
);

-- Claims table
CREATE TABLE claims (
  claim_id TEXT PRIMARY KEY,
  member_id TEXT REFERENCES members(member_id),
  drug_ndc TEXT REFERENCES drugs(ndc),
  drug_name TEXT,
  prescriber_npi TEXT,
  quantity DECIMAL(10,2),
  days_supply INTEGER,
  diagnosis_code TEXT,
  status TEXT DEFAULT 'PENDING',     -- PENDING, APPROVED, DENIED, PENDING_HUMAN_REVIEW
  final_decision TEXT,
  denial_reason TEXT,
  confidence_score DECIMAL(4,3),
  member_copay DECIMAL(10,2),
  plan_pays DECIMAL(10,2),
  reasoning_steps JSONB DEFAULT '[]',
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  decided_at TIMESTAMPTZ
);

-- Human review queue
CREATE TABLE review_queue (
  id BIGSERIAL PRIMARY KEY,
  claim_id TEXT REFERENCES claims(claim_id),
  reviewer_id TEXT,
  review_reason TEXT,
  human_decision TEXT,
  override_reason TEXT,
  queued_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ
);
```

---

## Key Implementation Files

### backend/database/client.py
```python
from supabase import create_client, Client
import os

_client: Client | None = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_ROLE_KEY']
        )
    return _client
```

### backend/database/queries.py
```python
from .client import get_supabase

def get_member(member_id: str) -> dict | None:
    result = get_supabase().table('members')\
        .select('*').eq('member_id', member_id).execute()
    return result.data[0] if result.data else None

def get_drug(ndc: str) -> dict | None:
    result = get_supabase().table('drugs')\
        .select('*').eq('ndc', ndc).execute()
    return result.data[0] if result.data else None

def save_claim(claim: dict) -> dict:
    result = get_supabase().table('claims').upsert(claim).execute()
    return result.data[0]

def get_pending_review() -> list:
    result = get_supabase().table('review_queue')\
        .select('*, claims(*)').is_('reviewed_at', 'null').execute()
    return result.data

def update_claim_status(claim_id: str, status: str, decision: dict) -> None:
    get_supabase().table('claims').update({
        'status': status,
        **decision
    }).eq('claim_id', claim_id).execute()
```

### backend/agent/state.py
```python
from typing import TypedDict, Optional

class ClaimState(TypedDict):
    # Input
    claim_id: str
    member_id: str
    drug_ndc: str
    drug_name: str
    prescriber_npi: str
    quantity: float
    days_supply: int
    diagnosis_code: str

    # DB lookups (populated by nodes)
    member_data: Optional[dict]
    drug_data: Optional[dict]

    # Node results
    eligibility_result: Optional[dict]
    formulary_result: Optional[dict]
    prior_auth_result: Optional[dict]
    benefit_result: Optional[dict]

    # Final
    final_decision: Optional[str]     # APPROVED | DENIED | PENDING_HUMAN_REVIEW
    denial_reason: Optional[str]
    confidence_score: Optional[float]

    # Audit trail — each node appends one string
    reasoning_steps: list[str]
```

### backend/agent/nodes/eligibility_check.py
```python
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
```

### backend/agent/nodes/adjudicate.py
```python
from groq import Groq
import os, json
from ..state import ClaimState

client = Groq(api_key=os.environ['GROQ_API_KEY'])

def adjudicate(state: ClaimState) -> ClaimState:
    # If already denied by upstream node, skip
    if state.get('final_decision') == 'DENIED':
        return state

    summary = "\n".join(state['reasoning_steps'])

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
    return state
```

### backend/agent/graph.py
```python
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
```

---

## requirements.txt
```
fastapi==0.110.0
uvicorn==0.27.0
groq==0.4.0
langgraph==0.1.0
langchain-core==0.1.0
supabase==2.3.0
python-dotenv==1.0.0
pydantic==2.6.0
pytest==7.4.0
httpx==0.26.0
```

---

## render.yaml
```yaml
services:
  - type: web
    name: claims-agent-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
```

---

## Session-by-Session Claude Code Prompts

### Session A — Agent Graph + Database
```
Build the backend for claims-adjudication-agent.
Stack: Python FastAPI on Render, Supabase PostgreSQL (NOT SQLite), Groq API
(llama-3.1-70b-versatile), LangGraph for agent orchestration.
Do NOT use SQLAlchemy, SQLite, or OpenAI.

Create this exact folder structure: [paste folder structure]

Implement:
- agent/state.py: [paste ClaimState exactly]
- agent/graph.py: [paste graph.py exactly]
- agent/nodes/eligibility_check.py: [paste eligibility_check exactly]
- agent/nodes/adjudicate.py: [paste adjudicate exactly]
- agent/nodes/formulary_check.py: query drugs table from Supabase, check tier
  and PA requirement, update state.formulary_result, append to reasoning_steps
- agent/nodes/prior_auth_check.py: if PA required but no PA on file (check
  review_queue table), deny claim with reason, otherwise pass
- agent/nodes/benefit_calculator.py: use member copay tier from member_data,
  calculate member_copay and plan_pays based on drug tier
- database/client.py: [paste client.py exactly]
- database/queries.py: [paste queries.py exactly]
- database/seed.py: seed Supabase with 20 members, 30 drugs, 10 pending claims
  using the Supabase client (not SQL files)
- api/claims.py: POST /api/claims/process (runs graph, saves to Supabase, returns state)
- api/review.py: POST /api/review/approve, /api/review/reject
- api/dashboard.py: GET /api/dashboard/pending (calls get_pending_review)
- models/schemas.py: Pydantic schemas for all request/response types
- requirements.txt, .env.example, render.yaml
```

### Session B — Frontend
```
Here is my claims-adjudication-agent backend:
[paste graph.py, state.py, schemas.py]

Build the React Vite Tailwind frontend for Vercel.
API_URL from import.meta.env.VITE_API_URL.

- ClaimSubmit.jsx: form with all ClaimState input fields, submit calls
  POST $API_URL/api/claims/process, on response navigate to AgentTrace
- AgentTrace.jsx: receives the full response with reasoning_steps array.
  Show each step as a timeline card that appears one by one with 300ms delay
  (CSS animation, not polling — the full response comes at once from Render).
  Each card: icon (✅/❌/⏳) + step text. Bottom: final decision badge.
- ReviewerDashboard.jsx: fetches GET /api/dashboard/pending, shows table of
  pending claims. Clicking a row expands to show reasoning_steps and
  Approve/Reject buttons that call the review endpoints.
- StepTimeline.jsx: reusable component for animated step display
- DecisionBadge.jsx: APPROVED (green), DENIED (red), PENDING REVIEW (yellow)
Add cold-start warning banner. vercel.json included.
```

### Session C — Seed + Tests + README
```
Add to claims-adjudication-agent:
1. Run database/seed.py instructions in README (not auto-run on startup — run once)
2. tests/test_graph.py: mock Supabase queries, test full graph runs without error,
   test denial path (inactive member), test HITL path (low confidence)
3. tests/test_api.py: mock graph, test API response shapes
4. .github/workflows/ci.yml
5. README.md: architecture with LangGraph state machine ASCII diagram,
   Supabase SQL setup section, deployment steps, demo scenarios table,
   HITL pattern explanation, sample curl commands
```

---

## Demo Scenarios Table (put in README)

| Scenario | member_id | drug_ndc | Expected |
|----------|-----------|----------|----------|
| Happy path | MBR-0000001 | NDC-ATORVA-40 | APPROVED |
| Expired member | MBR-9999999 | NDC-ATORVA-40 | DENIED: Not Eligible |
| PA required drug | MBR-0000001 | NDC-HUMIRA-40 | DENIED: PA Required |
| Low confidence | MBR-0000002 | NDC-UNKNOWN-01 | PENDING_HUMAN_REVIEW |

---

## Resume Bullet
```
Built claims-adjudication-agent: LangGraph multi-node agent for pharmacy claims
adjudication (eligibility → formulary → prior auth → benefit calc → decision).
HITL routing for low-confidence cases. Supabase PostgreSQL for state persistence.
Groq Llama 3.1 for adjudication reasoning. React reviewer dashboard. Live: [URL]
```
