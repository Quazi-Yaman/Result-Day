from datetime import datetime, timezone


def get_batch_release(table, batch, branch, semester):
    """
    Get the release configuration for a batch,
    branch and semester.
    """

    release_key = (
        f"RELEASE#{batch}#{branch}#SEM{semester}"
    )

    response = table.get_item(
        Key={
            "PK": release_key
        }
    )

    return response.get("Item")


def is_result_published(
    table,
    student,
    semester,
    result
):
    """
    Decide whether a student's result is currently published.

    Batch release configuration takes priority.
    Individual result release_datetime is used as fallback.
    """

    batch = (
        student.get("batch")
        or student.get("admission_year")
    )

    branch = student.get("branch")

    if batch and branch:

        release = get_batch_release(
            table,
            str(batch),
            branch,
            semester
        )

        if release:

            # Manual publish from Admin Portal.
            if release.get("status") == "PUBLISHED":
                return True

            release_datetime = release.get(
                "release_datetime"
            )

            if release_datetime:

                release_time = datetime.fromisoformat(
                    release_datetime
                )

                if release_time.tzinfo is None:
                    release_time = release_time.replace(
                        tzinfo=timezone.utc
                    )

                return (
                    datetime.now(timezone.utc)
                    >= release_time
                )

    # Fallback to the result's own release time.
    release_datetime = result.get(
        "release_datetime"
    )

    if not release_datetime:
        return True

    release_time = datetime.fromisoformat(
        release_datetime
    )

    if release_time.tzinfo is None:
        release_time = release_time.replace(
            tzinfo=timezone.utc
        )

    return (
        datetime.now(timezone.utc)
        >= release_time
    )


def get_student_result(table, prn, semester):

    # Get student information first.
    student_response = table.get_item(
        Key={
            "PK": f"STUDENT#{prn}"
        }
    )

    student = student_response.get("Item")

    if not student:
        return {
            "status": "error",
            "message": "Student not found"
        }, 404

    # Get result.
    response = table.get_item(
        Key={
            "PK": f"RESULT#{prn}#SEM{semester}"
        }
    )

    result = response.get("Item")

    if not result:
        return {
            "status": "error",
            "message": "Result not found"
        }, 404

    # Check batch release.
    if not is_result_published(
        table,
        student,
        semester,
        result
    ):
        return {
            "status": "error",
            "message": "Result has not been published yet"
        }, 403

    return {
        "status": "success",
        "result": result
    }, 200


def get_all_student_results(table, prn):

    # Get student information.
    student_response = table.get_item(
        Key={
            "PK": f"STUDENT#{prn}"
        }
    )

    student = student_response.get("Item")

    if not student:
        return {
            "status": "error",
            "message": "Student not found"
        }, 404

    response = table.scan()

    results = []

    for item in response.get("Items", []):

        if not item.get("PK", "").startswith(
            f"RESULT#{prn}#"
        ):
            continue

        semester = item.get(
            "semester",
            "0"
        )

        if is_result_published(
            table,
            student,
            semester,
            item
        ):
            results.append(item)

    results.sort(
        key=lambda x: int(
            x.get("semester", 0)
        )
    )

    return {
        "status": "success",
        "results": results
    }, 200