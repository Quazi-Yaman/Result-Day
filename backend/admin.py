from datetime import datetime, timezone


def get_admin_dashboard(table):
    response = table.scan()

    items = response.get("Items", [])

    students = []
    results = []
    notifications = []
    exams = []

    for item in items:
        pk = item.get("PK", "")

        if pk.startswith("STUDENT#"):
            students.append(item)

        elif pk.startswith("RESULT#"):
            results.append(item)

        elif pk.startswith("NOTIFICATION#"):
            notifications.append(item)

        elif pk.startswith("EXAM#"):
            exams.append(item)

    scheduled_results = 0
    published_results = 0

    for result in results:
        release_datetime = result.get("release_datetime")

        if release_datetime:
            release_time = datetime.fromisoformat(
                release_datetime
            )

            if datetime.now(timezone.utc) >= release_time:
                published_results += 1
            else:
                scheduled_results += 1

    return {
        "status": "success",
        "dashboard": {
            "total_students": len(students),
            "total_results": len(results),
            "published_results": published_results,
            "scheduled_results": scheduled_results,
            "total_exams": len(exams),
            "total_notifications": len(notifications)
        }
    }, 200


def get_result_release_schedule(table):
    response = table.scan()

    schedule = []

    for item in response.get("Items", []):
        if not item.get("PK", "").startswith("RESULT#"):
            continue

        release_datetime = item.get("release_datetime")

        if not release_datetime:
            continue

        release_time = datetime.fromisoformat(
            release_datetime
        )

        now = datetime.now(timezone.utc)

        if now >= release_time:
            release_status = "PUBLISHED"
        else:
            release_status = "SCHEDULED"

        schedule.append({
            "PRN": item.get("PRN"),
            "semester": item.get("semester"),
            "year": item.get("year"),
            "release_datetime": release_datetime,
            "release_status": release_status
        })

    schedule.sort(
        key=lambda x: x.get("release_datetime", "")
    )

    return {
        "status": "success",
        "schedule": schedule
    }, 200