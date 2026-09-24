import boto3
from config import AWS_REGION, DYNAMODB_TABLE

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

table.put_item(
    Item={
        "PK": "RESULT#2022AI001#SEM8",
        "PRN": "2022AI001",
        "semester": "8",
        "year": "4",
        "status": "SCHEDULED",
        "release_datetime": "2026-09-22T08:00:00+00:00",
        "SGPA": "8.42",
        "CGPA": "8.15",
        "subjects": [
            {
                "code": "AI401",
                "name": "Machine Learning",
                "credits": "4",
                "marks": "82",
                "grade": "A+",
                "status": "PASS"
            },
            {
                "code": "AI402",
                "name": "Cloud Computing",
                "credits": "3",
                "marks": "76",
                "grade": "A",
                "status": "PASS"
            },
            {
                "code": "AI403",
                "name": "Big Data Analytics",
                "credits": "4",
                "marks": "68",
                "grade": "B+",
                "status": "PASS"
            },
            {
                "code": "AI404",
                "name": "Data Mining",
                "credits": "3",
                "marks": "74",
                "grade": "A",
                "status": "PASS"
            },
            {
                "code": "AI405",
                "name": "Project",
                "credits": "6",
                "marks": "88",
                "grade": "A+",
                "status": "PASS"
            }
        ]
    }
)

print("Result seeded successfully.")