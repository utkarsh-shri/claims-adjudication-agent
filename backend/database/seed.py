import os
from dotenv import load_dotenv
from client import get_supabase

load_dotenv()

def seed_database():
    supabase = get_supabase()
    
    print("Seeding members...")
    members = [
        {
            "member_id": f"MBR-{(i+1):07d}",
            "plan_id": "PLAN-A",
            "plan_type": "COMMERCIAL",
            "enrollment_start": "2024-01-01",
            "enrollment_end": "2026-12-31" if i != 19 else "2023-12-31", # one expired member
            "deductible_met": i % 2 == 0,
            "copay_tier1": 5.00,
            "copay_tier2": 15.00,
            "copay_tier3": 40.00,
            "copay_tier4": 80.00
        }
        for i in range(20)
    ]
    supabase.table("members").upsert(members).execute()

    print("Seeding drugs...")
    drugs = [
        {"ndc": "NDC-ATORVA-40", "drug_name": "Atorvastatin 40mg", "drug_class": "Statin", "tier": 1, "pa_required": False},
        {"ndc": "NDC-HUMIRA-40", "drug_name": "Humira 40mg", "drug_class": "Biologic", "tier": 4, "pa_required": True},
        {"ndc": "NDC-AMOXIC-500", "drug_name": "Amoxicillin 500mg", "drug_class": "Antibiotic", "tier": 1, "pa_required": False},
        {"ndc": "NDC-OZEMPIC-2", "drug_name": "Ozempic 2mg", "drug_class": "GLP-1", "tier": 3, "pa_required": True},
        {"ndc": "NDC-LISINO-20", "drug_name": "Lisinopril 20mg", "drug_class": "ACE Inhibitor", "tier": 1, "pa_required": False},
    ]
    # Add more synthetic drugs to reach 30
    for i in range(5, 30):
        drugs.append({
            "ndc": f"NDC-DRUG-{i:03d}",
            "drug_name": f"Synthetic Drug {i}",
            "drug_class": "Various",
            "tier": (i % 4) + 1,
            "pa_required": i % 5 == 0,
        })
    supabase.table("drugs").upsert(drugs).execute()

    print("Seeding review queue...")
    # Just to have some existing data
    pass

    print("Database seeding completed.")

if __name__ == "__main__":
    seed_database()
