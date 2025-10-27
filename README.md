# 🧹 Tender Cleanup Lambda Function — Database Hygiene Specialist

[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![Amazon RDS](https://img.shields.io/badge/AWS-RDS-9d68c4.svg)](https://aws.amazon.com/rds/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2727.svg)](https://www.microsoft.com/sql-server/)
[![EventBridge](https://img.shields.io/badge/AWS-EventBridge-red.svg)](https://aws.amazon.com/eventbridge/)

**The digital janitor that keeps our tender database spotless!** 🧽 This AWS Lambda function serves as the automated maintenance crew for our tender database, systematically removing outdated records to ensure optimal performance and storage efficiency. Like a well-scheduled cleaning service, it works tirelessly behind the scenes to maintain database hygiene without any manual intervention.

## 📚 Table of Contents

- [📜 Overview](#-overview)
- [✨ Features](#-features)
- [⚙️ Architecture & Workflow](#️-architecture--workflow)
- [🔧 Setup & Deployment](#-setup--deployment)
- [⚙️ Configuration](#️-configuration-environment-variables)
- [🚀 Usage](#-usage)
- [📦 Dependencies](#-dependencies)
- [🧰 Troubleshooting](#-troubleshooting)
- [📊 Monitoring & Metrics](#-monitoring--metrics)

## 📜 Overview

Meet our database's best friend! 🤖 This `TenderCleanupHandler` is the unsung hero of data management, automatically sweeping away expired tender records to keep your system running at peak performance. Operating like a precision timekeeper, it identifies and removes tenders whose closing dates have passed the one-month threshold, ensuring your database stays lean, fast, and cost-effective.

**What makes it brilliantly efficient?** ⚡
- 🕐 **Time-Based Intelligence**: Automatically identifies outdated records using intelligent date calculations
- 🗂️ **Cascade Mastery**: Leverages database CASCADE constraints for bulletproof data integrity
- 🛡️ **Surgical Precision**: Targets only expired records while preserving valuable active data
- 🔄 **Set-and-Forget Automation**: Runs on autopilot with configurable scheduling

## ✨ Features

- **🤖 Automated Cleanup Intelligence**: Systematically removes tender records older than one month based on their `closingDate` with mathematical precision

- **🏗️ Database Integrity Guardian**: Leverages enterprise-grade `ON DELETE CASCADE` constraints for reliable removal of related data across multiple tables without orphaned records

- **⚡ Surgical Efficiency**: Executes a single, laser-targeted `DELETE` statement against the `dbo.BaseTender` table for maximum performance

- **🔒 Fort Knox Security**: Uses dedicated database credentials stored securely in Lambda environment variables with minimal required permissions

- **🚀 Performance Optimized**: Reuses database connections across invocations for superior performance and reduced overhead

- **📊 Comprehensive Logging**: Provides detailed CloudWatch insights regarding connection status, execution metrics, and the number of records processed

## ⚙️ Architecture & Workflow

Our cleanup process follows a methodical, fail-safe approach:

### 🔄 The Maintenance Pipeline:

```
⏰ EventBridge Scheduler (Daily/Weekly)
    ↓
🧹 Lambda: TenderCleanupHandler
    ├─ 🔗 Connect to RDS SQL Server
    ├─ 🎯 Identify Expired Tenders (> 1 month old)
    ├─ 🗑️ Execute Precision DELETE Statement
    ├─ 🏗️ Database CASCADE Auto-Cleanup
    └─ 📊 Log Results & Metrics
    ↓
📈 CloudWatch Logs & Monitoring
```

**🎯 The Precision Process:**

1. **⚡ Smart Triggering**: Activated by EventBridge Scheduler (configurable frequency) or manual execution
2. **🔐 Secure Connection**: Establishes authenticated connection to RDS SQL Server using `pymssql` and encrypted credentials
3. **🎯 Intelligent Targeting**: Executes surgical `DELETE` query: `WHERE closingDate < DATEADD(month, -1, GETDATE())`
4. **🏗️ Automated Cascade**: Database handles related record cleanup via `ON DELETE CASCADE` foreign key constraints
5. **📊 Performance Reporting**: Logs cleanup metrics and returns detailed success/error responses

## 🔧 Setup & Deployment

Ready to deploy your digital cleaning crew? Let's set up the ultimate database maintenance system! 🚀

### 📋 Prerequisites
- AWS Account with Lambda, RDS, and EventBridge permissions 🔑
- RDS SQL Server with properly configured CASCADE constraints 🗄️
- Dedicated cleanup database user with minimal permissions 👤
- Pre-built `pymssql` Lambda Layer for Python 3.9 📦

### 🏗️ Deployment Steps

#### 1. **🔐 Create Security Role**
```bash
# Create IAM role for Lambda execution
Role Name: TenderCleanupRole
Policies: 
  - AWSLambdaBasicExecutionRole (CloudWatch Logs)
  - Custom database access policy (if needed)
```

#### 2. **⚡ Deploy the Cleanup Function**
```yaml
Function Configuration:
  Name: TenderCleanupHandler
  Runtime: Python 3.9
  Architecture: x86_64
  Timeout: 60 seconds (adjust based on data volume)
  Memory: 128 MB (sufficient for most cleanup operations)
```

#### 3. **🗄️ Configure Database Access**
```sql
-- Create dedicated cleanup user with minimal permissions
CREATE LOGIN CleanupAppUser WITH PASSWORD = 'YourSecurePassword123!';
USE tendertool_db;
CREATE USER CleanupAppUser FOR LOGIN CleanupAppUser;
GRANT DELETE, SELECT ON dbo.BaseTender TO CleanupAppUser;
```

#### 4. **⚙️ Environment Setup**
Configure these critical environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `DB_ENDPOINT` | Database connection point | `tender-db.cluster-xxx.rds.amazonaws.com` |
| `DB_NAME` | Target database | `tendertool_db` |
| `DB_USER` | Cleanup service account | `CleanupAppUser` |
| `DB_PASSWORD` | Secure access credentials | `[YourSecurePassword123!]` |

#### 5. **📦 Attach Dependencies**
- Attach your pre-built `pymssql-layer` for database connectivity
- Ensure layer compatibility with Python 3.9 runtime

#### 6. **⏰ Schedule Automation**
```bash
# EventBridge Schedule Examples:
Daily at 3 AM UTC: cron(0 3 * * ? *)
Weekly on Sundays: cron(0 3 ? * SUN *)
Monthly cleanup: cron(0 3 1 * ? *)
```

## ⚙️ Configuration (Environment Variables)

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `DB_ENDPOINT` | ✅ Yes | RDS SQL Server hostname | `tender-cleanup.cluster-xxx.rds.amazonaws.com` |
| `DB_NAME` | ✅ Yes | Target database name | `tendertool_production` |
| `DB_USER` | ✅ Yes | Cleanup service account | `CleanupAppUser` |
| `DB_PASSWORD` | ✅ Yes | Service account password | `[SecurePassword123!]` |

> 🔐 **Security Best Practice**: Store `DB_PASSWORD` in AWS Secrets Manager for enhanced security!

## 🚀 Usage

### ⏰ **Automated Execution** (Recommended)
Your cleanup function runs automatically based on your EventBridge schedule - no manual intervention required!

### 🔧 **Manual Execution**
```bash
# Test via AWS CLI
aws lambda invoke \
  --function-name TenderCleanupHandler \
  --payload '{}' \
  response.json

# Expected Response
{
  "statusCode": 200,
  "body": {
    "message": "Cleanup completed successfully",
    "recordsDeleted": 1247,
    "executionTimeMs": 2340
  }
}
```

### 📊 **Monitoring Execution**
Check CloudWatch Logs for detailed execution reports:
```
[INFO] Database connection established successfully
[INFO] Executing cleanup query for records older than 2024-09-27
[INFO] Successfully deleted 1247 expired tender records
[INFO] Cleanup completed in 2.34 seconds
```

## 📦 Dependencies

- **🔗 `pymssql`**: High-performance SQL Server connector (via Lambda Layer)
- **☁️ `boto3`**: AWS SDK (included in Lambda runtime)
- **📊 `json`**: Response formatting (Python standard library)
- **⚙️ `os`**: Environment variable access (Python standard library)
- **📋 `logging`**: Comprehensive logging (Python standard library)

## 🧰 Troubleshooting

### 🚨 Common Maintenance Challenges

<details>
<summary><strong>🔌 Database Connection Failures</strong></summary>

**Issue**: Lambda cannot connect to RDS SQL Server database.

**🔧 Diagnostic Checklist:**
- ✅ Verify RDS instance is running and accessible
- ✅ Check database endpoint URL in environment variables
- ✅ Validate cleanup user credentials and permissions
- ✅ Ensure `pymssql` layer is properly attached
- ✅ Review VPC settings if Lambda requires network access

</details>

<details>
<summary><strong>⏰ Function Timeout Issues</strong></summary>

**Issue**: Lambda times out before completing cleanup operation.

**🔧 Performance Optimization:**
- ✅ Increase Lambda timeout (start with 5 minutes for large datasets)
- ✅ Monitor CloudWatch metrics for execution duration trends
- ✅ Consider batch processing for extremely large datasets
- ✅ Optimize database indexes on `closingDate` column

</details>

<details>
<summary><strong>🗑️ Incomplete Cascade Deletions</strong></summary>

**Issue**: Related records not being automatically deleted.

**🔧 Database Schema Review:**
- ✅ Verify `ON DELETE CASCADE` constraints are properly configured
- ✅ Check foreign key relationships in database schema
- ✅ Test cascade behavior in development environment
- ✅ Monitor for constraint violation errors in logs

</details>

<details>
<summary><strong>🔐 Permission Denied Errors</strong></summary>

**Issue**: Cleanup user lacks sufficient database permissions.

**🔧 Security Configuration:**
- ✅ Grant `DELETE` and `SELECT` permissions on `dbo.BaseTender`
- ✅ Verify user can access target database
- ✅ Check for additional schema-level permissions
- ✅ Test permissions with manual query execution

</details>

## 📊 Monitoring & Metrics

### 📈 **Key Performance Indicators**
- **Records Processed**: Number of expired tenders removed per execution
- **Execution Duration**: Time taken for cleanup operations
- **Success Rate**: Percentage of successful cleanup runs
- **Database Performance**: Impact on overall system performance

### 🔔 **Recommended Alerts**
```yaml
CloudWatch Alarms:
  - Function Errors > 0 (immediate notification)
  - Execution Duration > 5 minutes (performance alert)
  - No successful executions in 7 days (maintenance alert)
```

### 📊 **Sample Metrics Dashboard**
- Daily cleanup volume trends
- Database size reduction over time
- Function performance metrics
- Error rate and failure analysis

---

> Built with love, bread, and code by **Bread Corporation** 🦆❤️💻
