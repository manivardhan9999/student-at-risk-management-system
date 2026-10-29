from datetime import datetime
from sqlalchemy import String,Integer,Float,Boolean,Date,DateTime,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from .database import Base
class Student(Base):
 __tablename__="students"
 student_id:Mapped[str]=mapped_column(String,primary_key=True)
 first_name:Mapped[str]=mapped_column(String,nullable=False)
 last_name:Mapped[str]=mapped_column(String,nullable=False)
 program:Mapped[str]=mapped_column(String,nullable=False)
 lifecycle_status:Mapped[str]=mapped_column(String,default="ACTIVE",nullable=False)
class Course(Base):
 __tablename__="courses"
 course_id:Mapped[str]=mapped_column(String,primary_key=True)
 course_name:Mapped[str]=mapped_column(String,nullable=False)
 department:Mapped[str]=mapped_column(String,nullable=False)
 credits:Mapped[int]=mapped_column(Integer,nullable=False)
class Enrollment(Base):
 __tablename__="enrollments"
 enrollment_id:Mapped[str]=mapped_column(String,primary_key=True)
 student_id:Mapped[str]=mapped_column(ForeignKey("students.student_id"),nullable=False)
 course_id:Mapped[str]=mapped_column(ForeignKey("courses.course_id"),nullable=False)
 start_date:Mapped[datetime]=mapped_column(Date,nullable=False)
 end_date:Mapped[datetime|None]=mapped_column(Date,nullable=True)
 status:Mapped[str]=mapped_column(String,default="ACTIVE",nullable=False)
class AttendanceEvent(Base):
 __tablename__="attendance_events"
 attendance_id:Mapped[str]=mapped_column(String,primary_key=True)
 enrollment_id:Mapped[str]=mapped_column(ForeignKey("enrollments.enrollment_id"),nullable=False)
 event_date:Mapped[datetime]=mapped_column(Date,nullable=False)
 session_status:Mapped[str]=mapped_column(String,nullable=False)
 absence_approved:Mapped[bool]=mapped_column(Boolean,default=False,nullable=False)
class Assessment(Base):
 __tablename__="assessments"
 assessment_id:Mapped[str]=mapped_column(String,primary_key=True)
 course_id:Mapped[str]=mapped_column(ForeignKey("courses.course_id"),nullable=False)
 title:Mapped[str]=mapped_column(String,nullable=False)
 due_date:Mapped[datetime]=mapped_column(Date,nullable=False)
 max_score:Mapped[float]=mapped_column(Float,nullable=False)
class AssessmentResult(Base):
 __tablename__="assessment_results"
 result_id:Mapped[str]=mapped_column(String,primary_key=True)
 assessment_id:Mapped[str]=mapped_column(ForeignKey("assessments.assessment_id"),nullable=False)
 enrollment_id:Mapped[str]=mapped_column(ForeignKey("enrollments.enrollment_id"),nullable=False)
 score:Mapped[float|None]=mapped_column(Float,nullable=True)
 result_status:Mapped[str]=mapped_column(String,nullable=False)
class LMSActivity(Base):
 __tablename__="lms_activities"
 activity_id:Mapped[str]=mapped_column(String,primary_key=True)
 enrollment_id:Mapped[str]=mapped_column(ForeignKey("enrollments.enrollment_id"),nullable=False)
 occurred_at:Mapped[datetime]=mapped_column(DateTime,nullable=False)
 activity_type:Mapped[str]=mapped_column(String,nullable=False)
 duration_seconds:Mapped[int]=mapped_column(Integer,nullable=False)
class SupportCase(Base):
 __tablename__="support_cases"
 case_id:Mapped[str]=mapped_column(String,primary_key=True)
 student_id:Mapped[str]=mapped_column(ForeignKey("students.student_id"),nullable=False)
 opened_at:Mapped[datetime]=mapped_column(DateTime,nullable=False)
 reason:Mapped[str]=mapped_column(String,nullable=False)
 status:Mapped[str]=mapped_column(String,default="OPEN",nullable=False)
 assigned_to:Mapped[str|None]=mapped_column(String,nullable=True)
class SupportCaseHistory(Base):
 __tablename__="support_case_history"
 history_id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
 case_id:Mapped[str]=mapped_column(ForeignKey("support_cases.case_id"),nullable=False)
 old_status:Mapped[str|None]=mapped_column(String,nullable=True)
 new_status:Mapped[str]=mapped_column(String,nullable=False)
 changed_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,nullable=False)
 note:Mapped[str|None]=mapped_column(Text,nullable=True)
class Intervention(Base):
 __tablename__="interventions"
 intervention_id:Mapped[str]=mapped_column(String,primary_key=True)
 case_id:Mapped[str]=mapped_column(ForeignKey("support_cases.case_id"),nullable=False)
 intervention_type:Mapped[str]=mapped_column(String,nullable=False)
 created_at:Mapped[datetime]=mapped_column(DateTime,nullable=False)
 due_date:Mapped[datetime]=mapped_column(Date,nullable=False)
 status:Mapped[str]=mapped_column(String,default="PLANNED",nullable=False)
 result_note:Mapped[str|None]=mapped_column(Text,nullable=True)
class InterventionHistory(Base):
 __tablename__="intervention_history"
 history_id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
 intervention_id:Mapped[str]=mapped_column(ForeignKey("interventions.intervention_id"),nullable=False)
 old_status:Mapped[str|None]=mapped_column(String,nullable=True)
 new_status:Mapped[str]=mapped_column(String,nullable=False)
 changed_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,nullable=False)
 note:Mapped[str|None]=mapped_column(Text,nullable=True)
class Outcome(Base):
 __tablename__="outcomes"
 outcome_id:Mapped[str]=mapped_column(String,primary_key=True)
 enrollment_id:Mapped[str]=mapped_column(ForeignKey("enrollments.enrollment_id"),nullable=False)
 outcome_date:Mapped[datetime]=mapped_column(Date,nullable=False)
 outcome_label:Mapped[str]=mapped_column(String,nullable=False)
 final_grade:Mapped[float|None]=mapped_column(Float,nullable=True)
 label_rule_version:Mapped[str]=mapped_column(String,default="grade-under-50-v1",nullable=False)
