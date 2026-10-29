from datetime import date
from backend.risk_engine import score_student
def test_high_risk():
 r=score_student("STU-2026-000001",date(2026,1,1),65,42,True,False)
 assert r["risk_score"]==80 and r["risk_level"]=="HIGH" and len(r["reasons"])==3
def test_missing_not_failure():
 r=score_student("STU-2026-000001",date(2026,1,1),None,None,None,None)
 assert r["risk_score"]==0 and r["risk_level"]=="LOW"
