from datetime import datetime, timezone


def get_student_result(table, prn, semester):
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

    release_datetime = result.get("release_datetime")

    if release_datetime:
        release_time = datetime.fromisoformat(release_datetime)

        if datetime.now(timezone.utc) < release_time:
            return {
                "status": "error",
                "message": "Result has not been published yet"
            }, 403

    return {
        "status": "success",
        "result": result
    }, 200


def get_all_student_results(table, prn):
    response = table.scan()

    results = []

    for item in response.get("Items", []):
        if item.get("PK", "").startswith(f"RESULT#{prn}#"):

            release_datetime = item.get("release_datetime")

            if release_datetime:
                release_time = datetime.fromisoformat(
                    release_datetime
                )

                if datetime.now(timezone.utc) < release_time:
                    continue

            results.append(item)

    results.sort(
        key=lambda x: int(x.get("semester", 0))
    )

    return {
        "status": "success",
        "results": results
    }, 200