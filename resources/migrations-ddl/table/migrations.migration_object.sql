CREATE OR REPLACE TABLE MIGRATIONS.MIGRATION_OBJECT(
    MIGRATION_OBJECT_NAME VARCHAR NOT NULL COMMENT 'Migration object name: DB_CHANGE_LOG, GET_MIGRATION_LOG etc',
    OBJECT_TYPE VARCHAR NOT NULL COMMENT 'One of "table" or "procedure"',
    MD5SUM VARCHAR(50) NOT NULL COMMENT 'The latest executed script''s md5sum',
    SCRIPT_NAME VARCHAR(255) NOT NULL COMMENT 'Migration object script''s base name',
    SCRIPT_PATH VARCHAR(255) NOT NULL COMMENT 'Migration object script folder',
    SIGNATURE VARCHAR NULL COMMENT 'Migrations schema stored procedure signature',
    SYSTEM_CREATE_DATETIME TIMESTAMP_NTZ(9) NOT NULL DEFAULT CURRENT_TIMESTAMP(9)::TIMESTAMP_NTZ(9)
        COMMENT 'Timestamp when an object entity was created',
    SYSTEM_UPDATE_DATETIME TIMESTAMP_NTZ(9) COMMENT 'Timestamp when script was updated last time',
    CONSTRAINT PK_MIGRATION_TABLE PRIMARY KEY (MIGRATION_OBJECT_NAME)
) COMMENT = 'DB Migration tables description'
