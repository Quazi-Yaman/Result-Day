import secrets
from datetime import datetime, timedelta, timezone

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)


def login_student(table, prn, password):
    response = table.get_item(
        Key={
            "PK": f"STUDENT#{prn}"
        }
    )

    student = response.get("Item")

    if not student:
        return {
            "status": "error",
            "message": "Invalid PRN or password"
        }, 401

    if not student.get("account_active", False):
        return {
            "status": "error",
            "message": "Account is not activated"
        }, 403

    password_hash = student.get("password_hash")

    if not password_hash or not check_password_hash(
        password_hash,
        password
    ):
        return {
            "status": "error",
            "message": "Invalid PRN or password"
        }, 401

    return {
        "status": "success",
        "message": "Login successful",
        "student": {
            "PRN": student.get("PRN"),
            "name": student.get("name"),
            "email": student.get("email"),
            "branch": student.get("branch"),
            "current_year": student.get("current_year"),
            "current_semester": student.get("current_semester")
        }
    }, 200


def activate_account(table, prn):
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

    if student.get("account_active", False):
        return {
            "status": "error",
            "message": "Account is already active"
        }, 400

    token = secrets.token_urlsafe(32)

    expiry = (
        datetime.now(timezone.utc)
        + timedelta(hours=24)
    )

    table.update_item(
        Key={
            "PK": f"STUDENT#{prn}"
        },
        UpdateExpression="""
            SET activation_token = :token,
                activation_token_expires = :expires,
                email_verified = :verified
        """,
        ExpressionAttributeValues={
            ":token": token,
            ":expires": expiry.isoformat(),
            ":verified": False
        }
    )

    return {
        "status": "success",
        "message": "Activation link generated",
        "email": student.get("email"),
        "activation_link": (
            f"/activate?token={token}"
        )
    }, 200


def complete_activation(table, token, password):
    response = table.scan()

    student = None

    for item in response.get("Items", []):
        if item.get("activation_token") == token:
            student = item
            break

    if not student:
        return {
            "status": "error",
            "message": "Invalid activation token"
        }, 400

    expiry_string = student.get(
        "activation_token_expires"
    )

    if not expiry_string:
        return {
            "status": "error",
            "message": "Activation token is invalid"
        }, 400

    expiry = datetime.fromisoformat(
        expiry_string
    )

    if datetime.now(timezone.utc) > expiry:
        return {
            "status": "error",
            "message": "Activation token has expired"
        }, 400

    password_hash = generate_password_hash(
        password
    )

    table.update_item(
        Key={
            "PK": student["PK"]
        },
        UpdateExpression="""
            SET password_hash = :password_hash,
                account_active = :active,
                email_verified = :verified
            REMOVE activation_token,
                   activation_token_expires
        """,
        ExpressionAttributeValues={
            ":password_hash": password_hash,
            ":active": True,
            ":verified": True
        }
    )

    return {
        "status": "success",
        "message": "Account activated successfully",
        "PRN": student.get("PRN")
    }, 200