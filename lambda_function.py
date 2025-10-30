import os
import pymssql
import logging
import json

# --- Logger Setup ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- Global Scope ---
# Fetch configuration directly from environment variables
db_endpoint = os.environ.get('DB_ENDPOINT')
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_port = 1433

# This global variable holds our database connection for reuse
db_connection = None

def get_db_connection():
    """
    Establishes or reuses a database connection using credentials from environment variables.
    """
    global db_connection
    if db_connection:
        try:
            db_connection.autocommit(True)
            cursor = db_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            logger.info("Reusing existing database connection.")
            return db_connection
        except Exception as e:
            logger.warning(f"Stale connection detected, reconnecting. Reason: {e}")
            db_connection = None

    logger.info("Connecting directly to RDS instance with credentials from environment variables.")
    try:
        db_connection = pymssql.connect(
            server=db_endpoint,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            autocommit=True # Autocommit is important for DELETE statements
        )
        logger.info("Database connection established successfully.")
        return db_connection
    except Exception as e:
        logger.error(f"Failed to establish new database connection: {e}")
        raise # Re-raise the exception to be caught by the handler

def lambda_handler(event, context):
    """
    Connects to the database and deletes tenders from BaseTender
    where the closingDate is older than one month. Relies on
    ON DELETE CASCADE constraints in the database.
    """
    conn = None
    cursor = None
    deleted_count = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- Step 1: Update Stale 'Open' Tenders ---
        logger.info("Executing status update: Setting expired 'Open' tenders to 'Closed'...")
        
        # This query finds tenders marked 'Open' whose closing date has passed
        # and updates their status to 'Closed'.
        update_sql = """
        UPDATE dbo.BaseTender
        SET Status = 'Closed'
        OUTPUT inserted.TenderID
        WHERE Status = 'Open' AND closingDate < GETDATE();
        """
        cursor.execute(update_sql)
        updated_rows = cursor.fetchall()
        updated_count = len(updated_rows)
        
        if updated_count > 0:
            logger.info(f"Successfully updated {updated_count} tenders from 'Open' to 'Closed'.")
        else:
            logger.info("No stale 'Open' tenders found to update.")

        # --- Step 2: Delete Old Tenders ---
        logger.info("Executing cleanup query: Deleting tenders older than 1 month...")

        # SQL query to delete old tenders from the base table
        cleanup_sql = """
        DELETE FROM dbo.BaseTender
        OUTPUT deleted.TenderID -- Output the IDs of deleted rows (optional but good for logging)
        WHERE closingDate < DATEADD(month, -1, GETDATE());
        """
        cursor.execute(cleanup_sql)

        # Fetch the results (if any) to get the count
        deleted_rows = cursor.fetchall()
        deleted_count = len(deleted_rows)

        # pymssql might require explicit commit even with autocommit=True for some operations
        # or if OUTPUT clause is used, though typically not needed for single DELETE.
        # conn.commit() # Usually not needed with autocommit=True

        if deleted_count > 0:
            logger.info(f"Successfully deleted {deleted_count} old tenders from dbo.BaseTender.")
            # Optional: Log the first few deleted IDs for verification
            # deleted_ids = [str(row[0]) for row in deleted_rows[:10]]
            # logger.info(f"Sample deleted TenderIDs: {', '.join(deleted_ids)}")
        else:
            logger.info("No old tenders found matching the criteria. No records deleted.")

        # --- Final Success Response ---
        success_message = f"Cleanup successful. Updated {updated_count} tender statuses. Deleted {deleted_count} old tenders."
        logger.info(success_message)
        return {
            'statusCode': 200,
            'body': json.dumps(success_message)
        }

    except pymssql.Error as db_err:
        logger.error(f"Database error during cleanup: {db_err}")
        # Consider rolling back if not using autocommit
        # if conn:
        #     conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps('Database error occurred during cleanup.')
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        # Consider rolling back if not using autocommit
        # if conn:
        #     conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps('An unexpected error occurred during cleanup.')
        }
    finally:
        # Ensure the cursor is always closed if it was opened
        if cursor:
            try:
                cursor.close()
                logger.info("Database cursor closed.")
            except Exception as e:
                logger.error(f"Error closing cursor: {e}")