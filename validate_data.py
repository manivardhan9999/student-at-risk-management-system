import argparse,json,hashlib
from pathlib import Path
import pandas as pd
PK={"students.csv":"student_id","courses.csv":"course_id","enrollments.csv":"enrollment_id","attendance_events.csv":"attendance_id","assessments.csv":"assessment_id","assessment_results.csv":"result_id","lms_activity.csv":"activity_id","support_cases.csv":"case_id","interventions.csv":"intervention_id","outcomes.csv":"outcome_id"}
FK={"enrollments.csv":[("student_id","students.csv","student_id"),("course_id","courses.csv","course_id")],"attendance_events.csv":[("enrollment_id","enrollments.csv","enrollment_id")],"assessments.csv":[("course_id","courses.csv","course_id")],"assessment_results.csv":[("assessment_id","assessments.csv","assessment_id"),("enrollment_id","enrollments.csv","enrollment_id")],"lms_activity.csv":[("enrollment_id","enrollments.csv","enrollment_id")],"support_cases.csv":[("student_id","students.csv","student_id")],"interventions.csv":[("case_id","support_cases.csv","case_id")],"outcomes.csv":[("enrollment_id","enrollments.csv","enrollment_id")]}
def validate(folder):
 folder=Path(folder);t={p.name:pd.read_csv(p,keep_default_na=False) for p in folder.glob("*.csv") if p.name!="ground_truth.csv"};err=[]
 for f,k in PK.items():
  if f not in t:err.append("Missing "+f);continue
  if t[f][k].duplicated().any():err.append(f"{f}: duplicate PK {k}")
  if (t[f][k].astype(str).str.len()==0).any():err.append(f"{f}: blank PK {k}")
 for f,links in FK.items():
  if f not in t:continue
  for col,parent,pcol in links:
   if parent not in t:err.append("Missing parent "+parent);continue
   invalid=set(t[f][col].astype(str))-set(t[parent][pcol].astype(str));invalid.discard("")
   if invalid:err.append(f"{f}.{col}: {len(invalid)} invalid FKs")
 if "attendance_events.csv" in t:
  bad=set(t["attendance_events.csv"]["session_status"])-{"PRESENT","ABSENT","APPROVED_ABSENCE"}
  if bad:err.append("Invalid attendance status: "+str(bad))
 if "enrollments.csv" in t:
  for _,r in t["enrollments.csv"].iterrows():
   if r["end_date"] and r["end_date"]<r["start_date"]:err.append("Enrollment end date precedes start date");break
 if "interventions.csv" in t and "support_cases.csv" in t:
  opened=t["support_cases.csv"].set_index("case_id")["opened_at"].to_dict()
  for _,r in t["interventions.csv"].iterrows():
   if r["case_id"] in opened and r["created_at"]<opened[r["case_id"]]:err.append("Intervention precedes trigger: "+r["intervention_id"])
 return {"status":"PASS" if not err else "FAIL","errors":err,"row_counts":{k:len(v) for k,v in t.items()}}
def hashes(folder):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(folder).glob("*.csv")}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--input",default="data/generated");p.add_argument("--compare");a=p.parse_args()
 r=validate(a.input)
 if a.compare:
  x,y=hashes(a.input),hashes(a.compare);r["reproducibility"]={"match":x==y,"different":[k for k in set(x)&set(y) if x[k]!=y[k]]}
  if x!=y:r["status"]="FAIL"
 print(json.dumps(r,indent=2));Path(a.input,"validation_report.json").write_text(json.dumps(r,indent=2))
 raise SystemExit(0 if r["status"]=="PASS" else 1)
