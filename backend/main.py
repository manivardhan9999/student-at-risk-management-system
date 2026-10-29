from datetime import date,datetime,timedelta
from uuid import uuid4
from fastapi import FastAPI,Depends,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import Base,engine,get_db
from . import models as m
from .risk_engine import score_student
Base.metadata.create_all(bind=engine)
app=FastAPI(title="Student At-Risk Management System",version="1.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173"],allow_methods=["*"],allow_headers=["*"])
class CaseIn(BaseModel):
 student_id:str
 reason:str=Field(min_length=3,max_length=500)
 assigned_to:str|None=None
class StatusIn(BaseModel):
 status:str
 note:str|None=None
class InterventionIn(BaseModel):
 case_id:str
 intervention_type:str
 due_date:date
 created_at:datetime|None=None
def features(db,sid,asof):
 ids=[x[0] for x in db.query(m.Enrollment.enrollment_id).filter(m.Enrollment.student_id==sid,m.Enrollment.start_date<=asof).all()]
 att=db.query(m.AttendanceEvent).filter(m.AttendanceEvent.enrollment_id.in_(ids),m.AttendanceEvent.event_date<=asof).all() if ids else []
 eligible=[a for a in att if not a.absence_approved]
 ap=100*sum(a.session_status=="PRESENT" for a in eligible)/len(eligible) if eligible else None
 rs=db.query(m.AssessmentResult,m.Assessment).join(m.Assessment,m.AssessmentResult.assessment_id==m.Assessment.assessment_id).filter(m.AssessmentResult.enrollment_id.in_(ids),m.Assessment.due_date<=asof,m.AssessmentResult.result_status=="GRADED").all() if ids else []
 vals=[r.score/a.max_score*100 for r,a in rs if r.score is not None and a.max_score>0]
 avg=sum(vals)/len(vals) if vals else None
 activity=db.query(m.LMSActivity.occurred_at).filter(m.LMSActivity.enrollment_id.in_(ids),m.LMSActivity.occurred_at<=datetime.combine(asof,datetime.max.time())).all() if ids else []
 recent=sum(1 for (dt,) in activity if dt.date()>asof-timedelta(days=14))
 prior=sum(1 for (dt,) in activity if asof-timedelta(days=28)<dt.date()<=asof-timedelta(days=14))
 decline=(recent<prior*.5) if prior>0 else None
 unresolved=db.query(m.SupportCase).filter(m.SupportCase.student_id==sid,m.SupportCase.opened_at<=datetime.combine(asof,datetime.max.time()),m.SupportCase.status.in_(["OPEN","IN_PROGRESS"])).first() is not None
 return ap,avg,decline,unresolved
@app.get("/")
def root(): return {"project":"Student At-Risk Management System","docs":"/docs"}
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/dashboard/summary")
def summary(db:Session=Depends(get_db)):
 total=db.query(m.Student).count(); cases=db.query(m.SupportCase).filter(m.SupportCase.status.in_(["OPEN","IN_PROGRESS"])).count()
 ints=db.query(m.Intervention).count(); done=db.query(m.Intervention).filter(m.Intervention.status=="COMPLETED").count()
 counts={"HIGH":0,"MEDIUM":0,"LOW":0}
 for (sid,) in db.query(m.Student.student_id).filter(m.Student.lifecycle_status=="ACTIVE").all():
  counts[score_student(sid,date.today(),*features(db,sid,date.today()))["risk_level"]]+=1
 return {"total_students":total,"high_risk":counts["HIGH"],"medium_risk":counts["MEDIUM"],"low_risk":counts["LOW"],"open_cases":cases,"interventions":ints,"completed_interventions":done}
@app.get("/students")
def students(search:str|None=None,risk:str|None=None,limit:int=Query(100,ge=1,le=1000),db:Session=Depends(get_db)):
 q=db.query(m.Student)
 if search: q=q.filter((m.Student.student_id.contains(search))|(m.Student.first_name.contains(search))|(m.Student.last_name.contains(search)))
 out=[]
 for s in q.order_by(m.Student.student_id).limit(limit).all():
  r=score_student(s.student_id,date.today(),*features(db,s.student_id,date.today()))
  if risk and r["risk_level"]!=risk.upper(): continue
  out.append({"student_id":s.student_id,"first_name":s.first_name,"last_name":s.last_name,"program":s.program,"lifecycle_status":s.lifecycle_status,**r})
 return out
@app.get("/students/{student_id}")
def student_detail(student_id:str,db:Session=Depends(get_db)):
 s=db.get(m.Student,student_id)
 if not s: raise HTTPException(404,"Student not found")
 r=score_student(student_id,date.today(),*features(db,student_id,date.today()))
 cases=db.query(m.SupportCase).filter_by(student_id=student_id).order_by(m.SupportCase.opened_at.desc()).all()
 return {"student":{"student_id":s.student_id,"first_name":s.first_name,"last_name":s.last_name,"program":s.program,"lifecycle_status":s.lifecycle_status},"risk":r,
 "support_cases":[{"case_id":c.case_id,"reason":c.reason,"status":c.status,"opened_at":c.opened_at.isoformat(),"assigned_to":c.assigned_to} for c in cases]}
@app.get("/students/{student_id}/risk")
def risk(student_id:str,as_of:date|None=None,db:Session=Depends(get_db)):
 if not db.get(m.Student,student_id): raise HTTPException(404,"Student not found")
 d=as_of or date.today()
 return score_student(student_id,d,*features(db,student_id,d))
@app.get("/support-cases")
def cases(status:str|None=None,db:Session=Depends(get_db)):
 q=db.query(m.SupportCase)
 if status:q=q.filter(m.SupportCase.status==status.upper())
 return [{"case_id":c.case_id,"student_id":c.student_id,"reason":c.reason,"status":c.status,"opened_at":c.opened_at.isoformat(),"assigned_to":c.assigned_to} for c in q.order_by(m.SupportCase.opened_at.desc()).limit(500).all()]
@app.post("/support-cases",status_code=201)
def create_case(p:CaseIn,db:Session=Depends(get_db)):
 if not db.get(m.Student,p.student_id): raise HTTPException(404,"Student not found")
 cid="CASE-"+uuid4().hex[:12].upper(); now=datetime.utcnow()
 db.add(m.SupportCase(case_id=cid,student_id=p.student_id,opened_at=now,reason=p.reason,status="OPEN",assigned_to=p.assigned_to));db.flush()
 db.add(m.SupportCaseHistory(case_id=cid,old_status=None,new_status="OPEN",note="Case created"));db.commit()
 return {"case_id":cid,"status":"OPEN"}
@app.patch("/support-cases/{case_id}/status")
def update_case(case_id:str,p:StatusIn,db:Session=Depends(get_db)):
 new=p.status.upper()
 if new not in {"OPEN","IN_PROGRESS","RESOLVED","CLOSED"}:raise HTTPException(422,"Invalid case status")
 c=db.get(m.SupportCase,case_id)
 if not c:raise HTTPException(404,"Case not found")
 old=c.status;c.status=new;db.add(m.SupportCaseHistory(case_id=case_id,old_status=old,new_status=new,note=p.note));db.commit()
 return {"case_id":case_id,"old_status":old,"new_status":new}
@app.get("/interventions")
def interventions(db:Session=Depends(get_db)):
 return [{"intervention_id":i.intervention_id,"case_id":i.case_id,"type":i.intervention_type,"created_at":i.created_at.isoformat(),"due_date":i.due_date.isoformat(),"status":i.status,"result_note":i.result_note} for i in db.query(m.Intervention).order_by(m.Intervention.created_at.desc()).limit(500).all()]
@app.post("/interventions",status_code=201)
def create_intervention(p:InterventionIn,db:Session=Depends(get_db)):
 c=db.get(m.SupportCase,p.case_id)
 if not c:raise HTTPException(404,"Case not found")
 created=p.created_at or datetime.utcnow()
 if created<c.opened_at:raise HTTPException(422,"Intervention cannot precede trigger")
 iid=f"INT-2026-{db.query(m.Intervention).count()+1:06d}"
 i=m.Intervention(intervention_id=iid,case_id=p.case_id,intervention_type=p.intervention_type,created_at=created,due_date=p.due_date,status="PLANNED")
 db.add(i);db.flush();db.add(m.InterventionHistory(intervention_id=iid,old_status=None,new_status="PLANNED",note="Created"));db.commit()
 return {"intervention_id":iid,"status":"PLANNED"}
@app.patch("/interventions/{iid}/status")
def update_intervention(iid:str,p:StatusIn,db:Session=Depends(get_db)):
 new=p.status.upper()
 if new not in {"PLANNED","IN_PROGRESS","COMPLETED","CANCELLED"}:raise HTTPException(422,"Invalid intervention status")
 i=db.get(m.Intervention,iid)
 if not i:raise HTTPException(404,"Intervention not found")
 old=i.status;i.status=new
 if p.note:i.result_note=p.note
 db.add(m.InterventionHistory(intervention_id=iid,old_status=old,new_status=new,note=p.note));db.commit()
 return {"intervention_id":iid,"old_status":old,"new_status":new}
@app.get("/evaluation/metrics")
def metrics(db:Session=Depends(get_db)):
 outcomes=db.query(m.Outcome).all()
 if not outcomes:return {"evaluated":0,"message":"No outcomes imported into API database yet."}
 yt=[];yp=[]
 for o in outcomes:
  e=db.get(m.Enrollment,o.enrollment_id)
  if not e:continue
  d=o.outcome_date-timedelta(days=30)
  pred=score_student(e.student_id,d,*features(db,e.student_id,d))
  yt.append(o.outcome_label=="AT_RISK");yp.append(pred["risk_level"]=="HIGH")
 tp=sum(a and b for a,b in zip(yt,yp));fp=sum((not a) and b for a,b in zip(yt,yp));fn=sum(a and not b for a,b in zip(yt,yp))
 pr=tp/(tp+fp) if tp+fp else 0;re=tp/(tp+fn) if tp+fn else 0
 return {"evaluated":len(yt),"true_positive":tp,"false_positive":fp,"false_negative":fn,"precision":round(pr,4),"recall":round(re,4),"f1":round(2*pr*re/(pr+re),4) if pr+re else 0}
