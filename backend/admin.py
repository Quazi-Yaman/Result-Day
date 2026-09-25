from datetime import datetime, timezone


# =========================================================
# HELPERS
# =========================================================

def parse_datetime(value):
    if not value:
        return None

    try:
        dt = datetime.fromisoformat(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt

    except (ValueError, TypeError):
        return None


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def get_admin_dashboard(table):

    response = table.scan()
    items = response.get("Items", [])

    students = []
    results = []
    notifications = []
    exams = []
    releases = []

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

        elif pk.startswith("RELEASE#"):
            releases.append(item)

    now = datetime.now(timezone.utc)

    # -----------------------------------------------------
    # Result statistics
    # -----------------------------------------------------

    published_result_keys = set()
    scheduled_result_keys = set()

    # Existing individual results
    for result in results:

        prn = result.get("PRN")

        if not prn:
            pk = result.get("PK", "")

            if pk.startswith("RESULT#"):
                parts = pk.split("#")

                if len(parts) >= 3:
                    prn = parts[1]

        semester = str(
            result.get("semester", "")
        )

        if not prn or not semester:
            continue

        result_key = f"{prn}#SEM{semester}"

        release_datetime = result.get(
            "release_datetime"
        )

        release_time = parse_datetime(
            release_datetime
        )

        if release_time is None or now >= release_time:
            published_result_keys.add(result_key)

        else:
            scheduled_result_keys.add(result_key)

    # -----------------------------------------------------
    # New batch release records
    # -----------------------------------------------------

    for release in releases:

        release_datetime = release.get(
            "release_datetime"
        )

        release_time = parse_datetime(
            release_datetime
        )

        if release_time is None:
            continue

        batch = str(
            release.get("batch", "")
        )

        branch = release.get(
            "branch",
            ""
        )

        semester = str(
            release.get("semester", "")
        )

        release_key = (
            f"{batch}#{branch}#SEM{semester}"
        )

        stored_status = release.get(
            "status",
            "SCHEDULED"
        )

        if (
            stored_status == "PUBLISHED"
            or now >= release_time
        ):

            # A batch release is published.
            published_result_keys.add(
                release_key
            )

            scheduled_result_keys.discard(
                release_key
            )

        else:

            scheduled_result_keys.add(
                release_key
            )

    published_results = len(
        published_result_keys
    )

    scheduled_results = len(
        scheduled_result_keys
    )

    total_release_records = (
        published_results +
        scheduled_results
    )

    release_percent = 0

    if total_release_records:
        release_percent = round(
            (
                published_results /
                total_release_records
            ) * 100
        )

    return {
        "status": "success",

        "total_students": len(
            students
        ),

        "total_results": len(
            results
        ),

        "published_results":
            published_results,

        "scheduled_results":
            scheduled_results,

        "pending_results":
            scheduled_results,

        "release_percent":
            release_percent,

        "total_exams": len(
            exams
        ),

        "total_notifications": len(
            notifications
        )
    }, 200


# =========================================================
# RESULT RELEASE SCHEDULE
# =========================================================

def get_result_release_schedule(table):

    response = table.scan()

    schedule = []

    now = datetime.now(timezone.utc)

    for item in response.get(
        "Items",
        []
    ):

        pk = item.get("PK", "")

        # Only new release configuration records
        if not pk.startswith(
            "RELEASE#"
        ):
            continue

        release_datetime = item.get(
            "release_datetime"
        )

        release_time = parse_datetime(
            release_datetime
        )

        if release_time is None:
            continue

        stored_status = item.get(
            "status",
            "SCHEDULED"
        )

        if (
            stored_status == "PUBLISHED"
            or now >= release_time
        ):
            release_status = "PUBLISHED"
        else:
            release_status = "SCHEDULED"

        schedule.append({

            "batch": item.get(
                "batch"
            ),

            "branch": item.get(
                "branch"
            ),

            "semester": item.get(
                "semester"
            ),

            "release_datetime":
                release_datetime,

            "release_status":
                release_status
        })

    schedule.sort(
        key=lambda x:
        x.get(
            "release_datetime",
            ""
        )
    )

    return {
        "status": "success",
        "results": schedule
    }, 200