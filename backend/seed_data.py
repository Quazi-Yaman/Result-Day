import boto3

from config import AWS_REGION, DYNAMODB_TABLE


dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

table = dynamodb.Table(DYNAMODB_TABLE)


PRN = "2022AI001"


def seed_results():
    results = [
        {
            "PK": f"RESULT#{PRN}#SEM1",
            "PRN": PRN,
            "semester": 1,
            "year": 1,
            "status": "PUBLISHED",
            "release_datetime": "2023-01-15T08:00:00+00:00",
            "SGPA": "7.82",
            "CGPA": "7.82"
        },
        {
            "PK": f"RESULT#{PRN}#SEM2",
            "PRN": PRN,
            "semester": 2,
            "year": 1,
            "status": "PUBLISHED",
            "release_datetime": "2023-07-15T08:00:00+00:00",
            "SGPA": "8.05",
            "CGPA": "7.94"
        },
        {
            "PK": f"RESULT#{PRN}#SEM3",
            "PRN": PRN,
            "semester": 3,
            "year": 2,
            "status": "PUBLISHED",
            "release_datetime": "2024-01-15T08:00:00+00:00",
            "SGPA": "7.91",
            "CGPA": "7.93"
        },
        {
            "PK": f"RESULT#{PRN}#SEM4",
            "PRN": PRN,
            "semester": 4,
            "year": 2,
            "status": "PUBLISHED",
            "release_datetime": "2024-07-15T08:00:00+00:00",
            "SGPA": "8.20",
            "CGPA": "8.06"
        },
        {
            "PK": f"RESULT#{PRN}#SEM5",
            "PRN": PRN,
            "semester": 5,
            "year": 3,
            "status": "PUBLISHED",
            "release_datetime": "2025-01-15T08:00:00+00:00",
            "SGPA": "8.11",
            "CGPA": "8.07"
        },
        {
            "PK": f"RESULT#{PRN}#SEM6",
            "PRN": PRN,
            "semester": 6,
            "year": 3,
            "status": "PUBLISHED",
            "release_datetime": "2025-07-15T08:00:00+00:00",
            "SGPA": "8.34",
            "CGPA": "8.16"
        },
        {
            "PK": f"RESULT#{PRN}#SEM7",
            "PRN": PRN,
            "semester": 7,
            "year": 4,
            "status": "PUBLISHED",
            "release_datetime": "2026-01-15T08:00:00+00:00",
            "SGPA": "8.27",
            "CGPA": "8.17"
        }
    ]

    for result in results:
        table.put_item(Item=result)

    print("Semester 1-7 results seeded successfully.")


def seed_subjects():
    subjects = [
        {
            "PK": f"SUBJECTS#{PRN}#SEM8",
            "PRN": PRN,
            "semester": 8,
            "subjects": [
                {
                    "code": "AI401",
                    "name": "Machine Learning",
                    "credits": "4"
                },
                {
                    "code": "AI402",
                    "name": "Cloud Computing",
                    "credits": "3"
                },
                {
                    "code": "AI403",
                    "name": "Big Data Analytics",
                    "credits": "4"
                },
                {
                    "code": "AI404",
                    "name": "Data Mining",
                    "credits": "3"
                },
                {
                    "code": "AI405",
                    "name": "Project",
                    "credits": "6"
                }
            ]
        }
    ]

    for subject in subjects:
        table.put_item(Item=subject)

    print("Current semester subjects seeded successfully.")


def seed_exams():
    exams = [
        {
            "PK": f"EXAM#{PRN}#AI401",
            "PRN": PRN,
            "subject_code": "AI401",
            "subject": "Machine Learning",
            "exam_date": "2026-10-05",
            "exam_time": "10:00 AM",
            "venue": "Block A - Room 101"
        },
        {
            "PK": f"EXAM#{PRN}#AI402",
            "PRN": PRN,
            "subject_code": "AI402",
            "subject": "Cloud Computing",
            "exam_date": "2026-10-08",
            "exam_time": "10:00 AM",
            "venue": "Block A - Room 102"
        },
        {
            "PK": f"EXAM#{PRN}#AI403",
            "PRN": PRN,
            "subject_code": "AI403",
            "subject": "Big Data Analytics",
            "exam_date": "2026-10-12",
            "exam_time": "10:00 AM",
            "venue": "Block B - Room 201"
        },
        {
            "PK": f"EXAM#{PRN}#AI404",
            "PRN": PRN,
            "subject_code": "AI404",
            "subject": "Data Mining",
            "exam_date": "2026-10-15",
            "exam_time": "10:00 AM",
            "venue": "Block B - Room 202"
        },
        {
            "PK": f"EXAM#{PRN}#AI405",
            "PRN": PRN,
            "subject_code": "AI405",
            "subject": "Project",
            "exam_date": "2026-10-20",
            "exam_time": "02:00 PM",
            "venue": "Project Lab"
        }
    ]

    for exam in exams:
        table.put_item(Item=exam)

    print("Exam schedule seeded successfully.")


def seed_notifications():
    notifications = [
        {
            "PK": f"NOTIFICATION#{PRN}#001",
            "PRN": PRN,
            "title": "Result Release Announcement",
            "message": "Your Semester 8 result will be released soon.",
            "type": "RESULT",
            "created_at": "2026-09-20T08:00:00+00:00",
            "read": False
        },
        {
            "PK": f"NOTIFICATION#{PRN}#002",
            "PRN": PRN,
            "title": "Examination Schedule",
            "message": "Your Semester 8 examination schedule is now available.",
            "type": "EXAM",
            "created_at": "2026-09-18T08:00:00+00:00",
            "read": False
        }
    ]

    for notification in notifications:
        table.put_item(Item=notification)

    print("Notifications seeded successfully.")


def seed_all():
    seed_results()
    seed_subjects()
    seed_exams()
    seed_notifications()

    print("All demo data seeded successfully.")


if __name__ == "__main__":
    seed_all()