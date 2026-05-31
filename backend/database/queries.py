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

def add_to_review_queue(claim_id: str, reason: str) -> None:
    get_supabase().table('review_queue').insert({
        'claim_id': claim_id,
        'review_reason': reason
    }).execute()

def update_claim_status(claim_id: str, status: str, decision: dict, reviewer_id: str = None) -> None:
    get_supabase().table('claims').update({
        'status': status,
        **decision
    }).eq('claim_id', claim_id).execute()
    
    if reviewer_id is not None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        get_supabase().table('review_queue').update({
            'reviewed_at': now,
            'human_decision': status,
            'reviewer_id': reviewer_id,
            'override_reason': decision.get('denial_reason')
        }).eq('claim_id', claim_id).is_('reviewed_at', 'null').execute()
