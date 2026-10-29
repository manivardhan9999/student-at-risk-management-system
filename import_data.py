import csv
from datetime import date, datetime
from pathlib import Path
from backend.database import Base, engine, SessionLocal
from backend import models as m

DATA_DIR = Path('data/generated')

def read_rows(filename):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run generate_data.py first.")
    with path.open('r', newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def d(value):
    return date.fromisoformat(value) if value else None

def dt(value):
    return datetime.fromisoformat(value) if value else None

def number(value):
    return float(value) if value not in (None, '') else None

def flag(value):
    return str(value).strip().lower() in {'true', '1', 'yes'}

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    # This is a demo seeder: it replaces existing synthetic rows in this local database.
    for model in [m.InterventionHistory, m.SupportCaseHistory, m.Outcome, m.Intervention,
                  m.SupportCase, m.LMSActivity, m.AssessmentResult, m.AttendanceEvent,
                  m.Assessment, m.Enrollment, m.Course, m.Student]:
        db.query(model).delete(synchronize_session=False)
    db.commit()

    for r in read_rows('students.csv'):
        db.add(m.Student(student_id=r['student_id'], first_name=r['first_name'], last_name=r['last_name'],
                         program=r['program'], lifecycle_status=r['lifecycle_status']))
    db.flush()

    for r in read_rows('courses.csv'):
        db.add(m.Course(course_id=r['course_id'], course_name=r['course_name'], department=r['department'], credits=int(r['credits'])))
    db.flush()

    for r in read_rows('enrollments.csv'):
        db.add(m.Enrollment(enrollment_id=r['enrollment_id'], student_id=r['student_id'], course_id=r['course_id'],
                            start_date=d(r['start_date']), end_date=d(r['end_date']), status=r['status']))
    db.flush()

    for r in read_rows('assessments.csv'):
        db.add(m.Assessment(assessment_id=r['assessment_id'], course_id=r['course_id'], title=r['title'],
                            due_date=d(r['due_date']), max_score=float(r['max_score'])))
    db.flush()

    for r in read_rows('attendance_events.csv'):
        db.add(m.AttendanceEvent(attendance_id=r['attendance_id'], enrollment_id=r['enrollment_id'],
                                 event_date=d(r['event_date']), session_status=r['session_status'],
                                 absence_approved=flag(r['absence_approved'])))
    for r in read_rows('assessment_results.csv'):
        db.add(m.AssessmentResult(result_id=r['result_id'], assessment_id=r['assessment_id'], enrollment_id=r['enrollment_id'],
                                  score=number(r['score']), result_status=r['result_status']))
    for r in read_rows('lms_activity.csv'):
        db.add(m.LMSActivity(activity_id=r['activity_id'], enrollment_id=r['enrollment_id'],
                             occurred_at=dt(r['occurred_at']), activity_type=r['activity_type'],
                             duration_seconds=int(r['duration_seconds'])))
    db.flush()

    for r in read_rows('support_cases.csv'):
        db.add(m.SupportCase(case_id=r['case_id'], student_id=r['student_id'], opened_at=dt(r['opened_at']),
                             reason=r['reason'], status=r['status'], assigned_to=r['assigned_to'] or None))
    db.flush()

    for r in read_rows('interventions.csv'):
        db.add(m.Intervention(intervention_id=r['intervention_id'], case_id=r['case_id'],
                              intervention_type=r['intervention_type'], created_at=dt(r['created_at']),
                              due_date=d(r['due_date']), status=r['status'], result_note=r['result_note'] or None))
    for r in read_rows('outcomes.csv'):
        db.add(m.Outcome(outcome_id=r['outcome_id'], enrollment_id=r['enrollment_id'], outcome_date=d(r['outcome_date']),
                         outcome_label=r['outcome_label'], final_grade=number(r['final_grade']),
                         label_rule_version=r.get('label_rule_version') or 'grade-under-50-v1'))
    db.commit()
    print('Import successful!')
    for label, model in [('Students', m.Student), ('Courses', m.Course), ('Enrollments', m.Enrollment),
                         ('Attendance events', m.AttendanceEvent), ('Assessment results', m.AssessmentResult),
                         ('LMS activities', m.LMSActivity), ('Support cases', m.SupportCase),
                         ('Interventions', m.Intervention), ('Outcomes', m.Outcome)]:
        print(f'{label}: {db.query(model).count()}')
except Exception:
    db.rollback()
    raise
finally:
    db.close()
