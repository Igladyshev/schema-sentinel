create or replace TRANSIENT TABLE OBJECT_DEPENDENCIES (
    REFERENCED_DATABASE TEXT COMMENT 'The parent database of the referenced object.',
    REFERENCED_SCHEMA TEXT COMMENT 'The parent schema of the referenced object.',
    REFERENCED_OBJECT_NAME TEXT COMMENT 'The name of the referenced object.',
    REFERENCED_OBJECT_ID NUMBER COMMENT 'The object ID of the referenced object.',
    REFERENCED_OBJECT_DOMAIN TEXT COMMENT 'The domain (e.g. TABLE, VIEW) of the referenced object.',
    REFERENCING_DATABASE TEXT COMMENT 'The parent database of the referencing object.',
    REFERENCING_SCHEMA TEXT COMMENT 'The parent schema of the referencing object.',
    REFERENCING_OBJECT_NAME TEXT COMMENT 'The name of the referencing object.',
    REFERENCING_OBJECT_ID NUMBER COMMENT 'The object ID of the referencing object.',
    REFERENCING_OBJECT_DOMAIN TEXT COMMENT 'The domain (e.g. TABLE, VIEW) of the referencing object.',
    DEPENDENCY_TYPE TEXT COMMENT 'The type of dependency (BY_ID, BY_NAME, or BY_NAME_AND_ID).'
);