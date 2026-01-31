CREATE OR REPLACE TABLE MIGRATIONS.SCHEMA_DISCREPANCY (
    SCHEMA_DISCREPANCY_ID VARCHAR NOT NULL DEFAULT UUID_STRING(),
    ENVIRONMENT VARCHAR NOT NULL DEFAULT 'DEV' COMMENT 'Environment identifier (e.g., DEV, STAGING, PROD)',
    DATABASE_NAME VARCHAR NOT NULL DEFAULT 'MY_DATABASE' comment 'The database name being compared',
    SCHEMA_NAME VARCHAR NOT NULL COMMENT 'One of schemas in the database',
    DB_OBJECT_TYPE VARCHAR NOT NULL COMMENT 'TABLE, COLUMN, PRIMARY KEY, UNIQUE KEY, FOREIGN KEY',
    DB_OBJECT_NAME VARCHAR NOT NULL COMMENT 'The db object name',
    DB_OBJECT_PARENT_TYPE VARCHAR COMMENT 'TABLE',
    DB_OBJECT_PARENT_NAME VARCHAR,
    DDL VARCHAR comment 'The object create or alter script',
    ACTION VARCHAR COMMENT 'One of the following: DROP, ADD, KEEP. When it is empty, action needs to be approved or a default will be chosen. KEEP is a default value for action',
    ACTION_APPROVED_BY VARCHAR COMMENT 'The action was approved by a team member',
    ACTION_APPROVED_AT TIMESTAMP_NTZ COMMENT 'When action was approved',
    KEEP_UNTIL TIMESTAMP_NTZ COMMENT 'When chosen Action is KEEP, the time the table will be kept until. The default value is 7 days.',
    OBJECT_DEPENDENCIES VARCHAR COMMENT 'A dictionary of dependant objects, which may be affected when a table is dropped',
    SYSTEM_CREATE_DATETIME TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    SYSTEM_UPDATE_DATETIME TIMESTAMP_NTZ
)COMMENT = 'The table to keep project and environments clean using the action and keep_until attributes';
