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

## 📦 Deployment

This section covers three deployment methods for the Tender Cleanup Lambda Function. Choose the method that best fits your workflow and infrastructure preferences.

### 🛠️ Prerequisites

Before deploying, ensure you have:
- AWS CLI configured with appropriate credentials 🔑
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Python 3.9 runtime support in your target region
- Access to AWS Lambda, RDS, and CloudWatch Logs services ☁️
- Analytics layer dependencies for database connectivity

### 🎯 Method 1: AWS Toolkit Deployment

Deploy directly through your IDE using the AWS Toolkit extension.

#### Setup Steps:
1. **Install AWS Toolkit** in your IDE (VS Code, IntelliJ, etc.)
2. **Configure AWS Profile** with your credentials
3. **Open Project** containing `lambda_function.py`

#### Deploy Process:
1. **Right-click** on `lambda_function.py` in your IDE
2. **Select** "Deploy Lambda Function" from AWS Toolkit menu
3. **Configure Deployment**:
   - Function Name: `TenderCleanupHandler`
   - Runtime: `python3.9`
   - Handler: `lambda_function.lambda_handler`
   - Memory: `128 MB`
   - Timeout: `60 seconds`
4. **Add Layers** manually after deployment:
   - analytics-layer (for database connectivity)
5. **Set Environment Variables**:
   ```
   DB_ENDPOINT=tender-tool-db.c2hq4seoidxc.us-east-1.rds.amazonaws.com
   DB_NAME=tendertool_db
   DB_PASSWORD=T3nder$Tool_DB_2025!
   DB_USER=CleanupAppUser
   ```
6. **Configure IAM Permissions** for CloudWatch Logs

#### Post-Deployment:
- Test the function using the AWS Toolkit test feature
- Monitor logs through CloudWatch integration
- Verify database connectivity and cleanup operations

### 🚀 Method 2: SAM Deployment

Use AWS SAM for infrastructure-as-code deployment with the provided template.

#### Initial Setup:
```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Verify installation
sam --version
```

#### Create Required Layer Directory:
Since the template references an analytics layer not included in the repository, create it:

```bash
# Create analytics layer directory
mkdir -p analytics-layer/python

# Install required database connectivity packages
pip install pymssql -t analytics-layer/python/
pip install sqlalchemy -t analytics-layer/python/
pip install pyodbc -t analytics-layer/python/
```

#### Build and Deploy:
```bash
# Build the SAM application
sam build

# Deploy with guided configuration (first time)
sam deploy --guided

# Follow the prompts:
# Stack Name: tender-cleanup-lambda-stack
# AWS Region: us-east-1 (or your preferred region)
# Confirm changes before deploy: Y
# Allow SAM to create IAM roles: Y
# Save parameters to samconfig.toml: Y
```

#### Environment Variables Setup:
The template already includes the required environment variables:

```yaml
# Already configured in template.yml
Environment:
  Variables:
    DB_ENDPOINT: tender-tool-db.c2hq4seoidxc.us-east-1.rds.amazonaws.com
    DB_NAME: tendertool_db
    DB_PASSWORD: T3nder$Tool_DB_2025!
    DB_USER: CleanupAppUser
```

#### Subsequent Deployments:
```bash
# Quick deployment after initial setup
sam build && sam deploy
```

#### Local Testing with SAM:
```bash
# Test function locally with environment variables
sam local invoke TenderCleanupHandler

# The function will use the environment variables from template.yml
```

#### SAM Deployment Advantages:
- ✅ Complete infrastructure management
- ✅ Automatic layer creation and management
- ✅ Environment variables defined in template
- ✅ IAM permissions configured
- ✅ Easy rollback capabilities
- ✅ CloudFormation integration

### 🔄 Method 3: Workflow Deployment (CI/CD)

Automated deployment using GitHub Actions workflow for production environments.

#### Setup Requirements:
1. **GitHub Repository Secrets**:
   ```
   AWS_ACCESS_KEY_ID: Your AWS access key
   AWS_SECRET_ACCESS_KEY: Your AWS secret key
   AWS_REGION: us-east-1 (or your target region)
   ```

2. **Pre-existing Lambda Function**: The workflow updates an existing function, so deploy initially using Method 1 or 2.

#### Deployment Process:
1. **Create Release Branch**:
   ```bash
   # Create and switch to release branch
   git checkout -b release
   
   # Make your changes to lambda_function.py
   # Commit changes
   git add .
   git commit -m "feat: update tender cleanup logic"
   
   # Push to trigger deployment
   git push origin release
   ```

2. **Automatic Deployment**: The workflow will:
   - Checkout the code
   - Configure AWS credentials
   - Create deployment zip with `lambda_function.py`
   - Update the existing Lambda function code
   - Maintain existing configuration (layers, environment variables, etc.)

#### Manual Trigger:
You can also trigger deployment manually:
1. Go to **Actions** tab in your GitHub repository
2. Select **"Deploy Python Lambda to AWS"** workflow
3. Click **"Run workflow"**
4. Choose the `release` branch
5. Click **"Run workflow"** button

#### Workflow Deployment Advantages:
- ✅ Automated CI/CD pipeline
- ✅ Consistent deployment process
- ✅ Audit trail of deployments
- ✅ Easy rollback to previous commits
- ✅ No local environment dependencies

### 🔧 Post-Deployment Configuration

Regardless of deployment method, verify the following:

#### Environment Variables Verification:
Ensure these environment variables are properly set:

```bash
# Verify environment variables via AWS CLI
aws lambda get-function-configuration \
    --function-name TenderCleanupHandler \
    --query 'Environment.Variables'
```

Expected output:
```json
{
    "DB_ENDPOINT": "tender-tool-db.c2hq4seoidxc.us-east-1.rds.amazonaws.com",
    "DB_NAME": "tendertool_db",
    "DB_PASSWORD": "T3nder$Tool_DB_2025!",
    "DB_USER": "CleanupAppUser"
}
```

#### Database User Setup:
Ensure the cleanup database user exists and has proper permissions:

```sql
-- Connect to your SQL Server RDS instance
-- Create the cleanup user if not exists
CREATE LOGIN CleanupAppUser WITH PASSWORD = 'T3nder$Tool_DB_2025!';
USE tendertool_db;
CREATE USER CleanupAppUser FOR LOGIN CleanupAppUser;

-- Grant minimal required permissions
GRANT DELETE ON dbo.BaseTender TO CleanupAppUser;
GRANT SELECT ON dbo.BaseTender TO CleanupAppUser;
```

#### EventBridge Scheduler Setup (Optional):
Configure automated cleanup schedules:

```bash
# Create EventBridge rule for daily cleanup at 3 AM UTC
aws events put-rule \
    --name "TenderCleanupSchedule" \
    --schedule-expression "cron(0 3 * * ? *)" \
    --description "Daily tender database cleanup"

# Add Lambda as target
aws events put-targets \
    --rule "TenderCleanupSchedule" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:211635102441:function:TenderCleanupHandler"

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
    --function-name TenderCleanupHandler \
    --statement-id "AllowEventBridgeInvoke" \
    --action "lambda:InvokeFunction" \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:us-east-1:211635102441:rule/TenderCleanupSchedule"
```

### 🧪 Testing Your Deployment

After deployment, test the function:

```bash
# Test via AWS CLI
aws lambda invoke \
    --function-name TenderCleanupHandler \
    --payload '{}' \
    response.json

# Check the response
cat response.json
```

#### Expected Success Response:
```json
{
    "statusCode": 200,
    "body": {
        "message": "Cleanup completed successfully",
        "recordsDeleted": 42,
        "executionTime": "1.23 seconds"
    }
}
```

#### Expected Success Indicators:
- ✅ Function executes without errors
- ✅ CloudWatch logs show successful database connection
- ✅ Records are deleted from the database
- ✅ No timeout or memory errors
- ✅ Proper cleanup metrics in logs

### 🔍 Monitoring and Maintenance

#### CloudWatch Metrics to Monitor:
- **Duration**: Function execution time
- **Error Rate**: Failed cleanup operations
- **Memory Utilization**: RAM usage during database operations
- **Database Connections**: Monitor RDS connection metrics

#### Log Analysis:
```bash
# View recent logs
aws logs tail /aws/lambda/TenderCleanupHandler --follow

# Search for successful cleanups
aws logs filter-log-events \
    --log-group-name /aws/lambda/TenderCleanupHandler \
    --filter-pattern "Cleanup completed successfully"

# Search for database connection issues
aws logs filter-log-events \
    --log-group-name /aws/lambda/TenderCleanupHandler \
    --filter-pattern "Database connection"
```

### 🚨 Troubleshooting Deployments

<details>
<summary><strong>Analytics Layer Dependencies Missing</strong></summary>

**Issue**: Database connectivity packages not available

**Solution**: Ensure analytics layer is properly created and attached:
```bash
# For SAM: Verify layer directory exists and contains packages
ls -la analytics-layer/python/
ls -la analytics-layer/python/pymssql/

# For manual deployment: Create and upload layer separately
```
</details>

<details>
<summary><strong>Database Connection Failures</strong></summary>

**Issue**: Cannot connect to RDS SQL Server

**Solution**: Verify database configuration and credentials:
- Check DB_ENDPOINT points to correct RDS instance
- Verify CleanupAppUser exists and has correct password
- Ensure RDS security groups allow Lambda access
- Check VPC configuration if Lambda is in VPC
</details>

<details>
<summary><strong>Environment Variables Not Set</strong></summary>

**Issue**: Missing database configuration

**Solution**: Set environment variables using AWS CLI:
```bash
aws lambda update-function-configuration \
    --function-name TenderCleanupHandler \
    --environment Variables='{
        "DB_ENDPOINT":"tender-tool-db.c2hq4seoidxc.us-east-1.rds.amazonaws.com",
        "DB_NAME":"tendertool_db",
        "DB_USER":"CleanupAppUser",
        "DB_PASSWORD":"T3nder$Tool_DB_2025!"
    }'
```
</details>

<details>
<summary><strong>Workflow Deployment Fails</strong></summary>

**Issue**: GitHub Actions workflow errors

**Solution**: 
- Check repository secrets are correctly configured
- Verify the target Lambda function exists in AWS
- Ensure workflow has correct function ARN
</details>

<details>
<summary><strong>Permission Denied Errors</strong></summary>

**Issue**: CleanupAppUser lacks database permissions

**Solution**: Grant required permissions:
```sql
USE tendertool_db;
GRANT DELETE ON dbo.BaseTender TO CleanupAppUser;
GRANT SELECT ON dbo.BaseTender TO CleanupAppUser;
```
</details>

Choose the deployment method that best fits your development workflow and infrastructure requirements. SAM deployment is recommended for development environments, while workflow deployment excels for production maintenance schedules.

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
