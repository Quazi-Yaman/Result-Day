from datetime import datetime, timezone


def schedule_batch_result(table, batch, branch, semester, release_datetime):
    """
    Schedule a result release for an entire batch and branch.
    """

    release_key = f"RELEASE#{batch}#{branch}#SEM{semester}"

    table.put_item(
        Item={
            "PK": release_key,
            "type": "RESULT_RELEASE",
            "batch": batch,
            "branch": branch,
            "semester": str(semester),
            "release_datetime": release_datetime,
            "status": "SCHEDULED"
        }
    )

    return {
        "status": "success",
        "message": "Batch result scheduled successfully",
        "batch": batch,
        "branch": branch,
        "semester": semester,
        "release_datetime": release_datetime
    }, 200


def get_batch_release_status(table, batch, branch, semester):
    """
    Check release status for an entire batch.
    """

    release_key = f"RELEASE#{batch}#{branch}#SEM{semester}"

    response = table.get_item(
        Key={
            "PK": release_key
        }
    )

    release = response.get("Item")

    if not release:
        return {
            "status": "success",
            "release_status": "NOT_SCHEDULED"
        }, 200

    release_datetime = release.get("release_datetime")

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
        "batch": batch,
        "branch": branch,
        "semester": semester
    }, 200


def publish_batch_result(table, batch, branch, semester):
    """
    Manually publish a batch result.
    """

    release_key = f"RELEASE#{batch}#{branch}#SEM{semester}"

    response = table.get_item(
        Key={
            "PK": release_key
        }
    )

    release = response.get("Item")

    if not release:
        return {
            "status": "error",
            "message": "Batch result release configuration not found"
        }, 404

    table.update_item(
        Key={
            "PK": release_key
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
        "message": "Batch result published successfully",
        "batch": batch,
        "branch": branch,
        "semester": semester
    }, 200