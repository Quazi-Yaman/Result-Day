from flask import Flask, request
from flask_cors import CORS
import boto3
from datetime import datetime, timezone, timedelta
from werkzeug.security import check_password_hash
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
    schedule_batch_result,
    get_batch_release_status,
    publish_batch_result
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

autoscaling = boto3.client(
    "autoscaling",
    region_name=AWS_REGION
)

ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION
)

elbv2 = boto3.client(
    "elbv2",
    region_name=AWS_REGION
)

cloudwatch = boto3.client(
    "cloudwatch",
    region_name=AWS_REGION
)


# =========================================================
# AWS RESOURCE CONFIGURATION
# =========================================================

ASG_NAME = "result-day-asg"

TARGET_GROUP_ARN = (
    "arn:aws:elasticloadbalancing:ap-south-1:"
    "220664822853:targetgroup/"
    "result-day-tg/8b80f854ee5a349a"
)

ALB_NAME = "result-day-alb"

ALB_METRIC_DIMENSION = (
    "app/result-day-alb/ef63173b9a7ca03e"
)


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


@app.route("/notifications/<prn>", methods=["POST"])
def create_student_notification(prn):
    data = request.get_json() or {}

    title = data.get("title")
    message = data.get("message")
    notification_type = data.get("type", "INFO")

    if not message:
        return {
            "status": "error",
            "message": "Message is required"
        }, 400

    if not title:
        title_map = {
            "GENERAL": "General Notification",
            "RESULT": "Result Notification",
            "EXAM": "Examination Notification",
            "IMPORTANT": "Important Notification",
            "INFO": "Notification"
        }

        title = title_map.get(
            notification_type,
            "Notification"
        )

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
def schedule_batch_result_route():

    data = request.get_json() or {}

    batch = data.get("batch")
    branch = data.get("branch")
    semester = data.get("semester")
    release_datetime = data.get("release_datetime")

    if (
        not batch
        or not branch
        or semester is None
        or not release_datetime
    ):
        return {
            "status": "error",
            "message": (
                "Batch, branch, semester and "
                "release_datetime are required"
            )
        }, 400

    result, status_code = schedule_batch_result(
        table,
        str(batch),
        branch,
        int(semester),
        release_datetime
    )

    return result, status_code


@app.route(
    "/release-status/<batch>/<branch>/<int:semester>",
    methods=["GET"]
)
def release_status(batch, branch, semester):

    result, status_code = get_batch_release_status(
        table,
        batch,
        branch,
        semester
    )

    return result, status_code


@app.route(
    "/admin/results/publish",
    methods=["POST"]
)
def publish_batch_result_route():

    data = request.get_json() or {}

    batch = data.get("batch")
    branch = data.get("branch")
    semester = data.get("semester")

    if (
        not batch
        or not branch
        or semester is None
    ):
        return {
            "status": "error",
            "message": (
                "Batch, branch and semester "
                "are required"
            )
        }, 400

    result, status_code = publish_batch_result(
        table,
        str(batch),
        branch,
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


# =========================================================
# RESULT RELEASE SCHEDULE
# =========================================================

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
# ADMIN STUDENTS
# =========================================================

@app.route(
    "/admin/students",
    methods=["GET"]
)
def admin_students():

    response = table.scan()

    students = []

    for item in response.get("Items", []):

        if not item.get("PK", "").startswith(
            "STUDENT#"
        ):
            continue

        students.append({
            "PRN": item.get("PRN"),
            "name": item.get("name"),
            "email": item.get("email"),
            "phone": item.get("phone"),
            "college": item.get("college"),
            "branch": item.get("branch"),
            "admission_year": item.get(
                "admission_year"
            ),
            "current_year": item.get(
                "current_year"
            ),
            "current_semester": item.get(
                "current_semester"
            ),
            "account_active": item.get(
                "account_active",
                False
            )
        })

    students.sort(
        key=lambda x: str(
            x.get("PRN") or ""
        )
    )

    return {
        "status": "success",
        "students": students,
        "total_students": len(students)
    }, 200


# =========================================================
# AWS COMPUTE STATUS
# =========================================================

@app.route(
    "/admin/aws/compute",
    methods=["GET"]
)
def aws_compute():

    response = autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[ASG_NAME]
    )

    groups = response.get(
        "AutoScalingGroups",
        []
    )

    if not groups:
        return {
            "status": "error",
            "message": "Auto Scaling group not found"
        }, 404

    group = groups[0]

    instances = []

    instance_ids = [
        item.get("InstanceId")
        for item in group.get("Instances", [])
        if item.get("InstanceId")
    ]

    if instance_ids:

        ec2_response = ec2.describe_instances(
            InstanceIds=instance_ids
        )

        for reservation in ec2_response.get(
            "Reservations",
            []
        ):
            for instance in reservation.get(
                "Instances",
                []
            ):

                instances.append({
                    "instance_id": instance.get(
                        "InstanceId"
                    ),
                    "state": instance.get(
                        "State", {}
                    ).get("Name"),
                    "private_ip": instance.get(
                        "PrivateIpAddress"
                    ),
                    "availability_zone": instance.get(
                        "Placement", {}
                    ).get("AvailabilityZone"),
                    "instance_type": instance.get(
                        "InstanceType"
                    )
                })

    return {
        "status": "success",
        "asg_name": ASG_NAME,
        "min_size": group.get("MinSize", 0),
        "desired_capacity": group.get(
            "DesiredCapacity",
            0
        ),
        "max_size": group.get(
            "MaxSize",
            0
        ),
        "instances": instances,
        "instance_count": len(instances)
    }, 200


# =========================================================
# AWS START
# =========================================================

@app.route(
    "/admin/aws/ec2/start",
    methods=["POST"]
)
def start_ec2():

    autoscaling.update_auto_scaling_group(
        AutoScalingGroupName=ASG_NAME,
        MinSize=2,
        DesiredCapacity=2
    )

    return {
        "status": "success",
        "message": (
            "Result Day Auto Scaling started "
            "with 2 instances"
        )
    }, 200


# =========================================================
# AWS STOP
# =========================================================

@app.route(
    "/admin/aws/ec2/stop",
    methods=["POST"]
)
def stop_ec2():

    autoscaling.update_auto_scaling_group(
        AutoScalingGroupName=ASG_NAME,
        MinSize=0,
        DesiredCapacity=0
    )

    return {
        "status": "success",
        "message": (
            "Result Day Auto Scaling stopped. "
            "ASG-managed instances will terminate."
        )
    }, 200


# =========================================================
# AWS TRAFFIC
# =========================================================

@app.route(
    "/admin/aws/traffic",
    methods=["GET"]
)
def aws_traffic():

    target_response = elbv2.describe_target_health(
        TargetGroupArn=TARGET_GROUP_ARN
    )

    target_descriptions = target_response.get(
        "TargetHealthDescriptions",
        []
    )

    healthy_targets = 0

    for target in target_descriptions:

        state = target.get(
            "TargetHealth",
            {}
        ).get("State")

        if state == "healthy":
            healthy_targets += 1

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=2)

    metric_response = cloudwatch.get_metric_statistics(
        Namespace="AWS/ApplicationELB",
        MetricName="RequestCount",
        Dimensions=[
            {
                "Name": "LoadBalancer",
                "Value": ALB_METRIC_DIMENSION
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=["Sum"]
    )

    datapoints = metric_response.get(
        "Datapoints",
        []
    )

    latest_requests = 0

    if datapoints:

        latest = max(
            datapoints,
            key=lambda x: x.get(
                "Timestamp"
            )
        )

        latest_requests = int(
            latest.get("Sum", 0)
        )

    return {
        "status": "success",
        "alb_name": ALB_NAME,
        "healthy_targets": healthy_targets,
        "total_targets": len(
            target_descriptions
        ),
        "requests_per_minute": latest_requests,
        "alb_status": (
            "Healthy"
            if healthy_targets > 0
            else "No healthy targets"
        )
    }, 200


# =========================================================
# AWS MONITORING
# =========================================================

@app.route(
    "/admin/aws/monitoring",
    methods=["GET"]
)
def aws_monitoring():

    backend_status = "Healthy"

    try:
        table.get_item(
            Key={
                "PK": "STUDENT#2022AI001"
            }
        )
        database_status = "Healthy"
    except Exception:
        database_status = "Unhealthy"

    try:
        target_response = (
            elbv2.describe_target_health(
                TargetGroupArn=TARGET_GROUP_ARN
            )
        )

        target_descriptions = (
            target_response.get(
                "TargetHealthDescriptions",
                []
            )
        )

        healthy_targets = sum(
            1
            for target in target_descriptions
            if target.get(
                "TargetHealth",
                {}
            ).get("State") == "healthy"
        )

        alb_status = (
            "Healthy"
            if healthy_targets > 0
            else "No healthy targets"
        )

    except Exception:
        alb_status = "Unavailable"
        healthy_targets = 0

    try:
        asg_response = (
            autoscaling.describe_auto_scaling_groups(
                AutoScalingGroupNames=[ASG_NAME]
            )
        )

        groups = asg_response.get(
            "AutoScalingGroups",
            []
        )

        if groups:

            group = groups[0]

            scaling_status = "Active"

            desired_capacity = group.get(
                "DesiredCapacity",
                0
            )

            running_instances = len(
                group.get(
                    "Instances",
                    []
                )
            )

        else:

            scaling_status = "Unavailable"
            desired_capacity = 0
            running_instances = 0

    except Exception:

        scaling_status = "Unavailable"
        desired_capacity = 0
        running_instances = 0

    return {
        "status": "success",
        "backend": backend_status,
        "database": database_status,
        "alb": alb_status,
        "scaling": scaling_status,
        "healthy_targets": healthy_targets,
        "desired_capacity": desired_capacity,
        "running_instances": running_instances
    }, 200


@app.route("/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    ADMIN_USERNAME = "admin"

    ADMIN_PASSWORD_HASH = "scrypt:32768:8:1$5JEfYxrkRETbiccb$101e1a5a8f5f55e5801afdba3fc20d04bfe68d29195225b8e53940da91074bbbdd7cdd46ebaf30b50e4acc7b4492e43af67f793c4f6716b6b4ad17281fc7c4b0"

    if username != ADMIN_USERNAME:
        return {
            "status": "error",
            "message": "Invalid administrator credentials"
        }, 401

    if not check_password_hash(
        ADMIN_PASSWORD_HASH,
        password
    ):
        return {
            "status": "error",
            "message": "Invalid administrator credentials"
        }, 401

    return {
        "status": "success",
        "message": "Admin login successful"
    }, 200


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )