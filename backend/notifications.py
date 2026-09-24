from datetime import datetime, timezone


def create_notification(
    table,
    prn,
    title,
    message,
    notification_type="INFO"
):
    notification_id = (
        datetime.now(timezone.utc)
        .strftime("%Y%m%d%H%M%S%f")
    )

    notification_key = (
        f"NOTIFICATION#{prn}#{notification_id}"
    )

    item = {
        "PK": notification_key,
        "PRN": prn,
        "title": title,
        "message": message,
        "type": notification_type,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "read": False
    }

    table.put_item(
        Item=item
    )

    return {
        "status": "success",
        "message": "Notification created",
        "notification": item
    }, 201


def get_student_notifications(table, prn):
    response = table.scan()

    notifications = []

    for item in response.get("Items", []):
        if item.get("PK", "").startswith(
            f"NOTIFICATION#{prn}#"
        ):
            notifications.append(item)

    notifications.sort(
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )

    return {
        "status": "success",
        "notifications": notifications
    }, 200


def mark_notification_read(
    table,
    prn,
    notification_id
):
    notification_key = (
        f"NOTIFICATION#{prn}#{notification_id}"
    )

    response = table.get_item(
        Key={
            "PK": notification_key
        }
    )

    notification = response.get("Item")

    if not notification:
        return {
            "status": "error",
            "message": "Notification not found"
        }, 404

    table.update_item(
        Key={
            "PK": notification_key
        },
        UpdateExpression="SET #read = :read",
        ExpressionAttributeNames={
            "#read": "read"
        },
        ExpressionAttributeValues={
            ":read": True
        }
    )

    return {
        "status": "success",
        "message": "Notification marked as read"
    }, 200