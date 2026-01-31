CREATE OR REPLACE TABLE MIGRATIONS.DB_CHANGE_LOG (
	ID VARCHAR(255) NOT NULL comment 'Unique change set identifier',
	AUTHOR VARCHAR(255) NOT NULL comment 'Author''s name',
	FILE_NAME VARCHAR(255) NOT NULL comment 'Change ste file name within ./changelog folder',
	DATE_EXECUTED TIMESTAMP_NTZ(9) NOT NULL comment 'The time when a change set was applied last time',
	MD5SUM VARCHAR(35) comment 'Themd5sum calculated based on the file context.',
	CONTEXTS VARCHAR(255) comment 'Coma separated list of execution contexts. Used to contain an environment',
    JIRA_TICKET VARCHAR(50) comment 'JIRA ticket explaining change set requirements and progress',
    JIRA_DESCRIPTION VARCHAR comment 'Description from the JRA ticket',
    APPROVED_BY VARCHAR(255) comment 'the manager name approved this change set deployment',
    DEPENDS_ON VARCHAR(255) comment 'an id of change set to be applied prior to the change set',
    RUN_MANUALLY BOOLEAN DEFAULT FALSE comment 'Boolean. When it is set to true the change set would be ignored when running ci/cd, but will be required to be executed manually by dependent change-set(s)',
    TAG VARCHAR comment 'any free string you want to group change sets by. Could be list of coma separated strings',
    CHANGE_SET_DESCRIPTION VARCHAR comment 'change set description. Every change set has to have detailed description',
    RUN_ALWAYS BOOLEAN DEFAULT FALSE COMMENT 'Set it to true whenever you need your change set to be executed every run',
    SYSTEM_CREATE_DATETIME TIMESTAMP_NTZ(9) comment 'The timestamp when the record was created',
    SYSTEM_UPDATE_DATETIME TIMESTAMP_NTZ(9) comment 'The timestamp when the record was last time updated',
    CONSTRAINT PK_DB_CHANGE_LOG PRIMARY KEY(ID)
) comment = 'The DBMigrator migration log';