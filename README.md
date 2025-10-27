# Tender Cleanup Lambda Function

## 📜 Overview

This AWS Lambda function (`TenderCleanupHandler`) is responsible for maintaining database hygiene by periodically removing outdated tender records. It connects to the RDS SQL Server database and deletes tenders whose `closingDate` is older than one month. The function relies on `ON DELETE CASCADE` constraints configured at the database level to ensure that related records in child and linking tables are automatically removed when a record in `dbo.BaseTender` is deleted.

## ✨ Features

* **Automated Cleanup:** Deletes tender records older than one month based on their `closingDate`.
* **Database Integrity:** Leverages database-level `ON DELETE CASCADE` constraints for reliable removal of related data across multiple tables.
* **Simple Logic:** Executes a single, targeted `DELETE` statement against the `dbo.BaseTender` table.
* **Secure Connection:** Uses dedicated database credentials stored securely in Lambda environment variables.
* **Efficient:** Reuses database connections across invocations for better performance.
* **Logging:** Provides informative logs to CloudWatch regarding connection status and the number of records deleted.

## ⚙️ Architecture & Workflow

1. **Trigger:** Designed to be triggered on a schedule (e.g., daily or weekly via AWS EventBridge Scheduler) or manually.
2. **Connection:** Establishes a connection to the RDS SQL Server database using `pymssql` (provided via a Lambda Layer) and credentials stored in environment variables (`DB_ENDPOINT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).
3. **Identify Old Tenders:** Executes a `DELETE` query targeting `dbo.BaseTender` with a `WHERE` clause selecting records where `closingDate < DATEADD(month, -1, GETDATE())`.
4. **Database Cascade:** The database automatically handles the deletion of corresponding records in related tables (e.g., `dbo.EskomTender`, `dbo.User_Tender`) due to the `ON DELETE CASCADE` foreign key constraints.
5. **Logging & Response:** Logs the number of records deleted from `dbo.BaseTender` and returns a success (`statusCode: 200`) or error (`statusCode: 500`) response.

## 🔧 Setup & Deployment

### Prerequisites

* AWS Account with permissions for Lambda, Layers, IAM, RDS, and CloudWatch Logs.
* RDS SQL Server database instance (`tendertool_db`) with `ON DELETE CASCADE` constraints configured on all foreign keys referencing `dbo.BaseTender.TenderID`.
* A dedicated SQL Server login and database user (e.g., `CleanupAppUser`) granted `DELETE` and `SELECT` permissions *only* on the `dbo.BaseTender` table within the `tendertool_db` database.
* A pre-built AWS Lambda Layer containing the `pymssql` library compatible with the chosen Python runtime (e.g., Python 3.9).

### Steps

1. **Create IAM Role:**
    * Create an IAM role (e.g., `TenderCleanupRole`) for the Lambda function.
    * Attach the `AWSLambdaBasicExecutionRole` managed policy for CloudWatch Logs access.
    * *(If Lambda needs VPC access, which this version does not):* Attach `AWSLambdaVPCAccessExecutionRole`.
2. **Create Lambda Function:**
    * In the AWS Lambda console, create a new function.
    * **Name:** `TenderCleanupHandler`
    * **Runtime:** Select **Python 3.9** (or the version matching your layer).
    * **Architecture:** `x86_64`.
    * **Execution Role:** Choose the `TenderCleanupRole` created above.
3. **Configure Environment Variables:**
    * Navigate to Configuration > Environment variables.
    * Add the following variables:
        * `DB_ENDPOINT`: Hostname of your RDS SQL Server instance.
        * `DB_NAME`: Your database name (`tendertool_db`).
        * `DB_USER`: The dedicated cleanup username (`CleanupAppUser`).
        * `DB_PASSWORD`: The password for the `CleanupAppUser`.
4. **Attach Layer:**
    * Attach the pre-built `pymssql-layer`.
5. **Deploy Code:**
    * Copy the contents of `lambda_function.py` into the Lambda console's inline code editor.
    * Click **Deploy**.
6. **Configure Timeout:**
    * Navigate to Configuration > General configuration > Edit.
    * Set the **Timeout** to an appropriate value (e.g., **1 minute** to start, increase if deletions take longer).
7. **Set Up Trigger (Optional - If managing via AWS):**
    * Navigate to Configuration > Triggers > Add trigger.
    * Select **EventBridge (CloudWatch Events)**.
    * Choose "Create a new rule".
    * Define a **Schedule expression** (e.g., `cron(0 3 ? * SUN *)` for every Sunday at 3 AM UTC).

## ⚙️ Configuration (Environment Variables)

| Variable      | Description                                | Example Value                                          |
| :------------ | :----------------------------------------- | :----------------------------------------------------- |
| `DB_ENDPOINT` | Hostname of the RDS SQL Server instance.   | `your-db.xxxx.us-east-1.rds.amazonaws.com`             |
| `DB_NAME`     | Name of the specific database.             | `tendertool_db`                                        |
| `DB_USER`     | Dedicated database username for cleanup.   | `CleanupAppUser`                                       |
| `DB_PASSWORD` | Password for the `DB_USER`.                | `YourSecurePassword`                                   |

## 🚀 Usage

This function is intended to be run automatically on a schedule. It can also be invoked manually via the AWS Lambda console using any valid test event JSON (the event content is not used by the function).

## 📦 Dependencies

* **`pymssql`:** Used for connecting to the SQL Server database. Provided via the attached Lambda Layer.
* **`boto3`:** AWS SDK for Python. Included in the Lambda runtime environment by default (though not actively used in the final version).
* **`json`:** Standard Python library for handling JSON.
* **`os`:** Standard Python library for accessing environment variables.
* **`logging`:** Standard Python library for logging.

## ⚠️ Error Handling

* The function includes `try...except` blocks to catch potential database connection errors and SQL execution errors.
* Errors are logged to CloudWatch for debugging.
* Fatal errors result in a `statusCode: 500` response.
