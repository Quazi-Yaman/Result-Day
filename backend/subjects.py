def get_current_subjects(table, prn):
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

    current_semester = student.get("current_semester")

    response = table.get_item(
        Key={
            "PK": f"SUBJECTS#{prn}#SEM{current_semester}"
        }
    )

    subjects = response.get("Item")

    if not subjects:
        return {
            "status": "success",
            "semester": current_semester,
            "subjects": []
        }, 200

    return {
        "status": "success",
        "semester": current_semester,
        "subjects": subjects.get("subjects", [])
    }, 200