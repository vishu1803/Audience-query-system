"""
Scheduled job to check and escalate queries.
Run this every 15 minutes with cron or similar.

Cron example: */15 * * * * cd /path/to/backend && python -m app.scripts.run_escalations
"""

import sys
from app.database import SessionLocal
from app.services.escalation_service import EscalationService


def main():
    """Run escalation checks"""
    print("\n" + "="*60)
    print("🚨 ESCALATION CHECK - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    db = SessionLocal()
    
    try:
        result = EscalationService.check_and_escalate_all(db)
        
        total = sum(len(v) for v in result.values())
        
        if total == 0:
            print("✅ No queries needed escalation")
        else:
            print(f"⚠️  Escalated {total} queries:")
            print(f"   - Urgent unassigned: {len(result['urgent_unassigned'])}")
            print(f"   - SLA breaches: {len(result['sla_breach'])}")
            print(f"   - Stuck queries: {len(result['stuck'])}")
        
        # Show at-risk queries
        at_risk = EscalationService.get_at_risk_queries(db)
        approaching = len(at_risk['approaching_sla'])
        stale = len(at_risk['getting_stale'])
        
        if approaching > 0 or stale > 0:
            print(f"\n ⚠️  At-risk queries:")
            print(f"   - Approaching SLA: {approaching}")
            print(f"   - Getting stale: {stale}")
        
    except Exception as e:
        print(f"❌ Error during escalation check: {e}")
        sys.exit(1)
    finally:
        db.close()
    
    print("="*60 + "\n")

if __name__ == "__main__":
    from datetime import datetime
    main()
