from datetime import datetime, timezone


def schedule_result(table, prn, semester, release_datetime):
    result_key = f"RESULT#{prn}#SEM{semester}"

    response = table.get_item(
        Key={
            "PK": result_key
        }
    )

    result = response.get("Item")

    if not result:
        return {
            "status": "error",
            "message": "Result not found"
        }, 404

    table.update_item(
        Key={
            "PK": result_key
        },
        UpdateExpression="SET release_datetime = :release_datetime, #status = :status",
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":release_datetime": release_datetime,
            ":status": "SCHEDULED"
        }
    )

    return {
        "status": "success",
        "message": "Result scheduled successfully",
        "prn": prn,
        "semester": semester,
        "release_datetime": release_datetime
    }, 200


def get_release_status(table, prn, semester):
    result_key = f"RESULT#{prn}#SEM{semester}"

    response = table.get_item(
        Key={
            "PK": result_key
        }
    )

    result = response.get("Item")

    if not result:
        return {
            "status": "error",
            "message": "Result not found"
        }, 404

    release_datetime = result.get("release_datetime")

    if not release_datetime:
        return {
            "status": "success",
            "release_status": "NOT_SCHEDULED"
        }, 200

    release_time = datetime.fromisoformat(release_datetime)
    now = datetime.now(timezone.utc)

    if now >= release_time:
        release_status = "PUBLISHED"
    else:
        release_status = "SCHEDULED"

    return {
        "status": "success",
        "release_status": release_status,
        "release_datetime": release_datetime,
        "prn": prn,
        "semester": semester
    }, 200


def publish_result(table, prn, semester):
    result_key = f"RESULT#{prn}#SEM{semester}"

    response = table.get_item(
        Key={
            "PK": result_key
        }
    )

    result = response.get("Item")

    if not result:
        return {
            "status": "error",
            "message": "Result not found"
        }, 404

    table.update_item(
        Key={
            "PK": result_key
        },
        UpdateExpression="SET #status = :status",
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "PUBLISHED"
        }
    )

    return {
        "status": "success",
        "message": "Result published successfully",
        "prn": prn,
        "semester": semester
    }, 200