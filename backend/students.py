from datetime import datetime, timezone


def get_student_dashboard(table, prn):
    # Get student
    response = table.get_item(
        Key={
            "PK": f"STUDENT#{prn}"
        }
    )

    student = response.get("Item")

    if not student:
        return {
            "status": "error",
            "message": "Student not found"
        }, 404

    # Get all results
    response = table.scan()

    published_results = []

    for item in response.get("Items", []):
        if item.get("PK", "").startswith(f"RESULT#{prn}#"):

            release_datetime = item.get("release_datetime")

            if release_datetime:
                release_time = datetime.fromisoformat(
                    release_datetime
                )

                if datetime.now(timezone.utc) < release_time:
                    continue

            published_results.append(item)

    # Find latest published semester
    latest_result = None

    if published_results:
        latest_result = max(
            published_results,
            key=lambda x: int(x.get("semester", 0))
        )

    return {
        "status": "success",

        "student": {
            "PRN": student.get("PRN"),
            "name": student.get("name"),
            "email": student.get("email"),
            "phone": student.get("phone"),
            "college": student.get("college"),
            "branch": student.get("branch"),
            "admission_year": student.get("admission_year"),
            "current_year": student.get("current_year"),
            "current_semester": student.get("current_semester")
        },

        "latest_result": (
            {
                "semester": latest_result.get("semester"),
                "SGPA": latest_result.get("SGPA"),
                "CGPA": latest_result.get("CGPA")
            }
            if latest_result else None
        )
    }, 200
