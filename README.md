# Result-Day

## Scalable University Result Portal

Result-Day is a university result management and student portal designed to provide a reliable experience during high-traffic result releases.

The application provides separate **Student** and **Administrator** portals and is deployed on AWS using an **Application Load Balancer, Auto Scaling Group, Amazon EC2, Amazon DynamoDB and CloudWatch**.

## Live Application

**Live URL:**
http://result-day-alb-696181440.ap-south-1.elb.amazonaws.com/

## Features

### Student Portal

* Student login using PRN and password
* Student dashboard
* Academic information
* Semester results
* Performance information
* Examination schedule
* Subject information
* Student profile
* Notifications
* Help & FAQ
* Logout

### Administrator Portal

* Administrator login
* Dashboard
* Student management
* Result scheduling
* Result publishing
* AWS compute information
* EC2 start/stop controls
* Traffic information
* Monitoring information

## AWS Architecture

```text
                         Internet
                            |
                            v
                 +----------------------+
                 | Application Load     |
                 | Balancer (ALB)       |
                 +----------+-----------+
                            |
                 +----------+-----------+
                 |                      |
                 v                      v
          +-------------+        +-------------+
          | EC2         |        | EC2         |
          | Instance 1  |        | Instance 2  |
          +------+------+        +------+------+
                 |                      |
                 +----------+-----------+
                            |
                            v
                    Nginx Web Server
                            |
                            v
                    Gunicorn / Flask
                            |
                            v
                     Amazon DynamoDB

                 Auto Scaling Group
                 manages EC2 capacity

                 CloudWatch
                 monitors resources
```

## AWS Services Used

| Service                   | Purpose                                 |
| ------------------------- | --------------------------------------- |
| Amazon EC2                | Runs the Flask/Gunicorn application     |
| Application Load Balancer | Distributes incoming traffic            |
| Auto Scaling Group        | Maintains and scales EC2 instances      |
| Amazon DynamoDB           | Stores application data                 |
| Amazon CloudWatch         | Monitoring and operational visibility   |
| Nginx                     | Serves frontend and routes API requests |
| Gunicorn                  | Production WSGI server for Flask        |
| AWS IAM                   | Controls AWS resource permissions       |

## Application Flow

### Student Flow

```text
Student
   ↓
ALB
   ↓
Nginx
   ↓
Student Frontend
   ↓
Flask Backend
   ↓
DynamoDB
```

### Administrator Flow

```text
Administrator
      ↓
ALB
      ↓
/admin/
      ↓
Admin Frontend
      ↓
Flask Backend
      ↓
DynamoDB / AWS Services
```

## High-Traffic Handling

The application is designed for periods when many students access their results at the same time.

The **Application Load Balancer** distributes incoming requests across healthy EC2 instances.

The **Auto Scaling Group** manages the EC2 instances and can launch replacement instances when required.

The production instances use a common AMI so that replacement instances can be created with the required application and server configuration.

## Project Structure

```text
Result-Day/
│
├── admin-frontend/
│   ├── index.html
│   ├── admin.js
│   └── admin.css
│
├── result-day-frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── backend/
│   ├── app.py
│   ├── admin.py
│   ├── release.py
│   └── results.py
│
├── README.md
└── .gitignore
```

## Deployment

The application is deployed on Amazon EC2 behind an Application Load Balancer.

Nginx handles incoming HTTP requests and provides:

* Student frontend routing
* Administrator frontend routing
* Backend API reverse proxying

Gunicorn runs the Flask backend application on the EC2 instances.

The EC2 instances are managed by an Auto Scaling Group and registered with the Application Load Balancer target group.

## Security

* AWS IAM is used for AWS resource permissions.
* Backend services run behind the Nginx reverse proxy.
* The application is accessed through the Application Load Balancer.
* Sensitive configuration and credentials should not be committed to GitHub.

## Screenshots

Screenshots demonstrating the application and AWS infrastructure will be added here.

### Student Portal

*Add student login and student portal screenshots here.*

### Administrator Portal

*Add admin login and admin portal screenshots here.*

### AWS Infrastructure

*Add screenshots of EC2, Application Load Balancer, Target Group, Auto Scaling Group and CloudWatch here.*

## Project Objective

The objective of this project is to demonstrate how a university result portal can be deployed on AWS with load balancing, horizontal scaling, persistent data storage and monitoring capabilities.

## Future Improvements

* HTTPS using an SSL/TLS certificate
* Custom domain name
* Amazon CloudFront integration
* Automated CI/CD deployment
* Additional monitoring and alerting
* More advanced authentication and authorization

## Author

**Yamania Quazi**

B.Tech — Artificial Intelligence & Data Science

GitHub: https://github.com/Quazi-Yaman
