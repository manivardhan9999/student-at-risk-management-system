import argparse,json,hashlib
from pathlib import Path
from datetime import date,datetime,timedelta
import numpy as np,pandas as pd
SEED=20261022; START=date(2025,8,1); END=date(2026,5,31)
PROGRAMS=["Information Technology","Computer Science","Business","Mathematics","Biology"]
DEPTS=["Computing","Engineering","Business","Science"]
ACT=["LOGIN","RESOURCE_VIEW","QUIZ_ATTEMPT","VIDEO_VIEW","DISCUSSION"]
def student_id(i):return f"STU-2026-{i:06d}"
def course_id(i):return f"CRS-{i:06d}"
def enrollment_id(s,c):return f"ENR-{s}-{c}"
def write(df,path):
 df.to_csv(path,index=False,lineterminator="\n")
 return {"file":path.name,"rows":len(df),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
def generate(a):
 rng=np.random.default_rng(a.seed);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 students=[{"student_id":student_id(i),"first_name":f"Student{i:05d}","last_name":f"Learner{i:05d}","program":str(rng.choice(PROGRAMS)),"lifecycle_status":str(rng.choice(["ACTIVE"]*94+["WITHDRAWN"]*4+["TRANSFERRED"]*2))} for i in range(1,a.students+1)]
 courses=[{"course_id":course_id(i),"course_name":f"Course {i:03d}","department":str(rng.choice(DEPTS)),"credits":int(rng.choice([2,3,4,5]))} for i in range(1,a.courses+1)]
 target=min(a.enrollments,a.students*a.courses); pairs=set()
 while len(pairs)<target:pairs.add((int(rng.integers(1,a.students+1)),int(rng.integers(1,a.courses+1))))
 enroll=[]; attendance=[]; assessments=[]; results=[]; lms=[]; cases=[]; interventions=[]; outcomes=[]
 for c in range(1,a.courses+1):
  for j,off in enumerate([90,180],1):assessments.append({"assessment_id":f"ASM-{c:06d}-{j:02d}","course_id":course_id(c),"title":f"Assessment {j}","due_date":(START+timedelta(days=off)).isoformat(),"max_score":100})
 adf=pd.DataFrame(assessments)
 case_no=int(0);int_no=0
 for n,(si,ci) in enumerate(sorted(pairs),1):
  s=student_id(si);c=course_id(ci);eid=enrollment_id(s,c);start=START+timedelta(days=int(rng.integers(0,35)))
  status=students[si-1]["lifecycle_status"];end=None
  if status!="ACTIVE":end=start+timedelta(days=int(rng.integers(30,180)))
  actual_end=min(end or END,END)
  enroll.append({"enrollment_id":eid,"student_id":s,"course_id":c,"start_date":start.isoformat(),"end_date":end.isoformat() if end else "","status":status if status!="ACTIVE" else "ACTIVE"})
  latent=float(rng.beta(2.2,2.0))
  d=start;week=0
  while d<=actual_end:
   week+=1;approved=bool(rng.random()<.035);present=bool(rng.random()<(.55+.4*latent))
   stat="APPROVED_ABSENCE" if approved else ("PRESENT" if present else "ABSENT")
   attendance.append({"attendance_id":f"ATT-{eid}-{d.isoformat()}","enrollment_id":eid,"event_date":d.isoformat(),"session_status":stat,"absence_approved":approved,"issue_type":""})
   for k in range(int(rng.poisson(.7+3.5*latent))):
    day=d+timedelta(days=int(rng.integers(0,7)))
    if day<=actual_end:lms.append({"activity_id":f"LMS-{n:06d}-{d:%Y%m%d}-{k+1:02d}","enrollment_id":eid,"occurred_at":datetime.combine(day,datetime.min.time()).isoformat(),"activity_type":str(rng.choice(ACT)),"duration_seconds":int(rng.integers(10,1800))})
   d+=timedelta(days=7)
  for j in (1,2):
   aid=f"ASM-{ci:06d}-{j:02d}";due=date.fromisoformat(adf.loc[adf.assessment_id==aid,"due_date"].iloc[0])
   if start<=due<=actual_end:
    missing=bool(rng.random()<.04);grade=round(float(np.clip(rng.normal(38+52*latent,14),0,100)),2)
    results.append({"result_id":f"RES-{eid}-{j:02d}","assessment_id":aid,"enrollment_id":eid,"score":"" if missing else grade,"result_status":"MISSING" if missing else "GRADED"})
  final=round(float(np.clip(rng.normal(35+55*latent,12),0,100)),2);label="AT_RISK" if final<50 else "ON_TRACK"
  outcomes.append({"outcome_id":f"OUT-{n:08d}","enrollment_id":eid,"outcome_date":END.isoformat(),"outcome_label":label,"final_grade":final,"label_rule_version":"synthetic-grade-under-50-v1"})
  if label=="AT_RISK" and rng.random()<.42:
   case_no+=1;opened=max(start,END-timedelta(days=int(rng.integers(20,100))));caseid=f"CASE-{case_no:08d}"
   cases.append({"case_id":caseid,"student_id":s,"opened_at":datetime.combine(opened,datetime.min.time()).isoformat(),"reason":str(rng.choice(["Attendance concern","Assessment concern","Engagement concern"])),"status":str(rng.choice(["OPEN","IN_PROGRESS","RESOLVED"])),"assigned_to":str(rng.choice(["Advisor-01","Support-02","Instructor-03"]))})
   if rng.random()<.78:
    int_no+=1;created=opened+timedelta(days=int(rng.integers(0,5)))
    interventions.append({"intervention_id":f"INT-2026-{int_no:06d}","case_id":caseid,"intervention_type":str(rng.choice(["Advisor meeting","Tutoring referral","Study plan","Wellbeing check-in"])),"created_at":datetime.combine(created,datetime.min.time()).isoformat(),"due_date":(created+timedelta(days=14)).isoformat(),"status":str(rng.choice(["PLANNED","IN_PROGRESS","COMPLETED","CANCELLED"])),"result_note":"Synthetic intervention"})
 tables={"students.csv":pd.DataFrame(students),"courses.csv":pd.DataFrame(courses),"enrollments.csv":pd.DataFrame(enroll),"attendance_events.csv":pd.DataFrame(attendance,columns=["attendance_id","enrollment_id","event_date","session_status","absence_approved","issue_type"]),"assessments.csv":pd.DataFrame(assessments),"assessment_results.csv":pd.DataFrame(results,columns=["result_id","assessment_id","enrollment_id","score","result_status"]),"lms_activity.csv":pd.DataFrame(lms,columns=["activity_id","enrollment_id","occurred_at","activity_type","duration_seconds"]),"support_cases.csv":pd.DataFrame(cases,columns=["case_id","student_id","opened_at","reason","status","assigned_to"]),"interventions.csv":pd.DataFrame(interventions,columns=["intervention_id","case_id","intervention_type","created_at","due_date","status","result_note"]),"outcomes.csv":pd.DataFrame(outcomes)}
 manifest=[]
 for name,df in tables.items():
  manifest.append(write(df,out/name));df.to_json(out/name.replace(".csv",".json"),orient="records",indent=2)
 gt=pd.DataFrame([
 {"issue_id":"ANOM-001","issue_type":"FUTURE_GRADE_LEAKAGE","expected_result":"Fail validation if a future grade is used for an earlier prediction"},
 {"issue_id":"ANOM-002","issue_type":"WRONG_ATTENDANCE_DENOMINATOR","expected_result":"Flag incorrect denominator; approved absences excluded by policy"},
 {"issue_id":"ANOM-003","issue_type":"WITHDRAWN_STUDENT_ACTIVE","expected_result":"Flag student/enrollment lifecycle inconsistency"},
 {"issue_id":"ANOM-004","issue_type":"INTERVENTION_PRECEDES_TRIGGER","expected_result":"Flag intervention timestamp earlier than support case"},
 {"issue_id":"ANOM-005","issue_type":"MISSING_DATA_AS_FAILURE","expected_result":"Unknown feature adds no risk points"}])
 manifest.append(write(gt,out/"ground_truth.csv"))
 dictionary={"Student":"PK student_id; program and lifecycle enums; deterministic STU-2026-######","Course":"PK course_id; credits integer 2..5","Enrollment":"PK enrollment_id; FK student_id/course_id; end_date optional and >= start_date","AttendanceEvent":"PK attendance_id; FK enrollment_id; PRESENT/ABSENT/APPROVED_ABSENCE; approved absence excluded from denominator","Assessment":"PK assessment_id; FK course_id; max_score > 0","AssessmentResult":"PK result_id; FKs assessment_id/enrollment_id; score nullable in 0..max_score","LMSActivity":"PK activity_id; FK enrollment_id; timestamp and duration >= 0","SupportCase":"PK case_id; FK student_id; status OPEN/IN_PROGRESS/RESOLVED","Intervention":"PK intervention_id; FK case_id; created_at must be >= case opened_at","Outcome":"PK outcome_id; FK enrollment_id; AT_RISK if final_grade < 50; evaluation-only"}
 (out/"data_dictionary.json").write_text(json.dumps(dictionary,indent=2))
 (out/"manifest.json").write_text(json.dumps({"seed":a.seed,"parameters":{"students":a.students,"courses":a.courses,"enrollments":target},"files":manifest},indent=2))
 print(json.dumps({"output":str(out),"seed":a.seed,"counts":{k:len(v) for k,v in tables.items()}},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--students",type=int,default=100);p.add_argument("--courses",type=int,default=10);p.add_argument("--enrollments",type=int,default=200);p.add_argument("--seed",type=int,default=SEED);p.add_argument("--output",default="data/generated");generate(p.parse_args())
