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
