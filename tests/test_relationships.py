
import pandas as pd
from pathlib import Path

DATA = Path("data/full")


def load(name):
    file_path = DATA / f"{name}.csv"
    assert file_path.exists(), f"Dataset file not found: {file_path}"
    return pd.read_csv(file_path)


def assert_unique(df, column):
    """Verify primary keys are non-null and unique."""
    assert df[column].notna().all(), f"{column} contains null IDs"
    assert df[column].is_unique, f"{column} contains duplicates"


def assert_foreign_key(child, child_col, parent, parent_col):
    """Verify foreign keys reference existing parent records."""
    missing = set(child[child_col].dropna()) - set(parent[parent_col].dropna())
    assert not missing, (
        f"Invalid {child_col}: {list(missing)[:5]}"
    )


def test_student_and_course_primary_keys():
    students = load("students")
    courses = load("courses")

    assert_unique(students, "student_id")
    assert_unique(courses, "course_id")


def test_enrollments_reference_existing_parents():
    students = load("students")
    courses = load("courses")
    enrollments = load("enrollments")

    assert_unique(enrollments, "enrollment_id")

    assert_foreign_key(
        enrollments, "student_id", students, "student_id"
    )
    assert_foreign_key(
        enrollments, "course_id", courses, "course_id"
    )


def test_attendance_references_enrollment():
    enrollments = load("enrollments")
    attendance = load("attendance_events")

    assert_unique(attendance, "attendance_id")

    assert_foreign_key(
        attendance, "enrollment_id",
        enrollments, "enrollment_id"
    )


def test_assessment_results_reference_parents():
    enrollments = load("enrollments")
    assessments = load("assessments")
    results = load("assessment_results")

    assert_unique(results, "result_id")
    assert_unique(assessments, "assessment_id")

    assert_foreign_key(
        results, "enrollment_id",
        enrollments, "enrollment_id"
    )
    assert_foreign_key(
        results, "assessment_id",
        assessments, "assessment_id"
    )


def test_lms_and_support_reference_parents():
    enrollments = load("enrollments")
    students = load("students")
    lms = load("lms_activity")
    cases = load("support_cases")

    assert_unique(lms, "activity_id")
    assert_unique(cases, "case_id")

    assert_foreign_key(
        lms, "enrollment_id",
        enrollments, "enrollment_id"
    )
    assert_foreign_key(
        cases, "student_id",
        students, "student_id"
    )


def test_interventions_reference_support_cases():
    cases = load("support_cases")
    interventions = load("interventions")

    assert_unique(interventions, "intervention_id")

    # Correct relationship: intervention -> support case
    assert_foreign_key(
        interventions, "case_id",
        cases, "case_id"
    )


def test_outcomes_reference_enrollments():
    enrollments = load("enrollments")
    outcomes = load("outcomes")

    assert_foreign_key(
        outcomes, "enrollment_id",
        enrollments, "enrollment_id"
    )
