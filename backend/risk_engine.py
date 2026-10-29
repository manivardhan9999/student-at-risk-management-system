
def score_student(
    student_id,
    prediction_date,
    attendance_percentage=None,
    assessment_average=None,
    engagement_declining=None,
    unresolved_support_case=None,
):
    score = 0
    reasons = []

    if attendance_percentage is not None and attendance_percentage < 75:
        score += 30
        reasons.append("Attendance below 75%")

    if assessment_average is not None and assessment_average < 50:
        score += 30
        reasons.append("Assessment average below 50%")

    if engagement_declining is True:
        score += 20
        reasons.append("LMS engagement declined")

    if unresolved_support_case is True:
        score += 20
        reasons.append("Unresolved support case")

    score = min(score, 100)

    risk_level = (
        "HIGH" if score >= 60
        else "MEDIUM" if score >= 30
        else "LOW"
    )

    return {
        "student_id": student_id,
        "prediction_date": prediction_date.isoformat(),
        "risk_score": score,
        "risk_level": risk_level,
        "attendance_percentage": attendance_percentage,
        "assessment_average": assessment_average,
        "engagement_declining": engagement_declining,
        "unresolved_support_case": unresolved_support_case,
        "reasons": reasons,
        "rule_version": "rules-v1",
    }
