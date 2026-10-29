# Data dictionary summary
All data is synthetic; IDs are deterministic strings; dates are ISO-8601.

| Entity | Primary key | Foreign keys | Validation |
|---|---|---|---|
| Student | student_id | — | STU-2026-######; lifecycle ACTIVE/WITHDRAWN/TRANSFERRED |
| Course | course_id | — | CRS-######; credits 2–5 |
| Enrollment | enrollment_id | student_id, course_id | end date optional and >= start |
| AttendanceEvent | attendance_id | enrollment_id | PRESENT/ABSENT/APPROVED_ABSENCE |
| Assessment | assessment_id | course_id | max_score > 0 |
| AssessmentResult | result_id | assessment_id, enrollment_id | nullable score 0..max |
| LMSActivity | activity_id | enrollment_id | duration >= 0 |
| SupportCase | case_id | student_id | OPEN/IN_PROGRESS/RESOLVED/CLOSED |
| Intervention | intervention_id | case_id | created_at >= case opened_at |
| Outcome | outcome_id | enrollment_id | AT_RISK when synthetic final_grade < 50; evaluation only |

Student/Course is many-to-many through Enrollment. SupportCaseHistory and InterventionHistory are append-only state-transition records.
