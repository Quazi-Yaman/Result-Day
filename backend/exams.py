def get_exam_schedule(table, prn):
    response = table.scan()

    exams = []

    for item in response.get("Items", []):
        if item.get("PK", "").startswith(f"EXAM#{prn}#"):
            exams.append(item)

    exams.sort(
        key=lambda x: x.get("exam_date", "")
    )

    return {
        "status": "success",
        "exams": exams
    }, 200