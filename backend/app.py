from flask import Flask, request
from flask_cors import CORS
import boto3

from config import AWS_REGION, DYNAMODB_TABLE

from auth import (
    login_student,
    activate_account,
    complete_activation
)

from students import get_student_dashboard

from results import (
    get_student_result,
    get_all_student_results
)

from exams import get_exam_schedule

from subjects import get_current_subjects

from release import (
    schedule_result,
    get_release_status,
    publish_result
)

from notifications import (
    create_notification,
    get_student_notifications,
    mark_notification_read
)

from admin import (
    get_admin_dashboard,
    get_result_release_schedule
)


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

CORS(app)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

table = dynamodb.Table(DYNAMODB_TABLE)


# =========================================================
# BASIC ROUTES
# =========================================================

@app.route("/", methods=["GET"])
def home():
    return {
        "status": "success",
        "message": "Result Day backend is running"
    }, 200


@app.route("/health", methods=["GET"])
def health():
    return {
        "status": "healthy"
    }, 200


@app.route("/test-dynamodb", methods=["GET"])
def test_dynamodb():
    response = table.get_item(
        Key={
            "PK": "STUDENT#2022AI001"
        }
    )

    student = response.get("Item")

    if not student:
        return {
            "status": "error",
            "message": "Student not found"
        }, 404

    return {
        "status": "success",
        "message": "DynamoDB connection successful",
        "student": student
    }, 200


# =========================================================
# AUTHENTICATION
# =========================================================

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    prn = data.get("prn")
    password = data.get("password")

    if not prn or not password:
        return {
            "status": "error",
            "message": "PRN and password are required"
        }, 400

    result, status_code = login_student(
        table,
        prn,
        password
    )

    return result, status_code


@app.route("/activate-account", methods=["POST"])
def activate():
    data = request.get_json() or {}

    prn = data.get("prn")

    if not prn:
        return {
            "status": "error",
            "message": "PRN is required"
        }, 400

    result, status_code = activate_account(
        table,
        prn
    )

    return result, status_code


@app.route("/complete-activation", methods=["POST"])
def complete_activation_route():
    data = request.get_json() or {}

    token = data.get("token")
    password = data.get("password")

    if not token or not password:
        return {
            "status": "error",
            "message": "Token and password are required"
        }, 400

    result, status_code = complete_activation(
        table,
        token,
        password
    )

    return result, status_code


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard/<prn>", methods=["GET"])
def dashboard(prn):
    result, status_code = get_student_dashboard(
        table,
        prn
    )

    return result, status_code


# =========================================================
# RESULTS
# =========================================================

@app.route("/result/<prn>/<int:semester>", methods=["GET"])
def get_result(prn, semester):
    result, status_code = get_student_result(
        table,
        prn,
        semester
    )

    return result, status_code


@app.route("/results/<prn>", methods=["GET"])
def get_results(prn):
    results, status_code = get_all_student_results(
        table,
        prn
    )

    return results, status_code


# =========================================================
# SUBJECTS
# =========================================================

@app.route("/subjects/<prn>", methods=["GET"])
def subjects(prn):
    result, status_code = get_current_subjects(
        table,
        prn
    )

    return result, status_code


# =========================================================
# EXAMINATION
# =========================================================

@app.route("/exams/<prn>", methods=["GET"])
def exams(prn):
    result, status_code = get_exam_schedule(
        table,
        prn
    )

    return result, status_code


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.route("/notifications/<prn>", methods=["GET"])
def notifications(prn):
    result, status_code = get_student_notifications(
        table,
        prn
    )

    return result, status_code


@app.route(
    "/notifications/<prn>",
    methods=["POST"]
)
def create_student_notification(prn):
    data = request.get_json() or {}

    title = data.get("title")
    message = data.get("message")
    notification_type = data.get(
        "type",
        "INFO"
    )

    if not title or not message:
        return {
            "status": "error",
            "message": "Title and message are required"
        }, 400

    result, status_code = create_notification(
        table,
        prn,
        title,
        message,
        notification_type
    )

    return result, status_code


@app.route(
    "/notifications/<prn>/<notification_id>/read",
    methods=["PUT"]
)
def read_notification(prn, notification_id):
    result, status_code = mark_notification_read(
        table,
        prn,
        notification_id
    )

    return result, status_code


# =========================================================
# RESULT RELEASE
# =========================================================

@app.route(
    "/admin/results/schedule",
    methods=["POST"]
)
def schedule_result_route():
    data = request.get_json() or {}

    prn = data.get("prn")
    semester = data.get("semester")
    release_datetime = data.get(
        "release_datetime"
    )

    if not prn or semester is None or not release_datetime:
        return {
            "status": "error",
            "message": (
                "PRN, semester and "
                "release_datetime are required"
            )
        }, 400

    result, status_code = schedule_result(
        table,
        prn,
        int(semester),
        release_datetime
    )

    return result, status_code


@app.route(
    "/release-status/<prn>/<int:semester>",
    methods=["GET"]
)
def release_status(prn, semester):
    result, status_code = get_release_status(
        table,
        prn,
        semester
    )

    return result, status_code


@app.route(
    "/admin/results/publish",
    methods=["POST"]
)
def publish_result_route():
    data = request.get_json() or {}

    prn = data.get("prn")
    semester = data.get("semester")

    if not prn or semester is None:
        return {
            "status": "error",
            "message": "PRN and semester are required"
        }, 400

    result, status_code = publish_result(
        table,
        prn,
        int(semester)
    )

    return result, status_code


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route(
    "/admin/dashboard",
    methods=["GET"]
)
def admin_dashboard():
    result, status_code = get_admin_dashboard(
        table
    )

    return result, status_code


@app.route(
    "/admin/results/schedule",
    methods=["GET"]
)
def admin_release_schedule():
    result, status_code = get_result_release_schedule(
        table
    )

    return result, status_code


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )