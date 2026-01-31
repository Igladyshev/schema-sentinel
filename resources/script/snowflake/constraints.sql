select
    'PRIMARY KEY' as "constraint_type",
    "database_name",
    "schema_name",
    "table_name",
    "constraint_name",
    listagg("column_name", ', ') within group(order by "key_sequence") as "columns",
    NULL AS "referenced_key"
from primary_keys
group by "database_name",
    "schema_name",
    "table_name",
    "constraint_name"

union all

select
    'UNIQUE KEY' as "constraint_type",
    "database_name",
    "schema_name",
    "table_name",
    "constraint_name",
    listagg("column_name", ', ') within group(order by "key_sequence") as "columns",
    NULL AS "referenced_key"
from unique_keys
group by "database_name",
    "schema_name",
    "table_name",
    "constraint_name"

union all

select
    'FOREIGN KEY' as "constraint_type",
    "fk_database_name",
    "fk_schema_name",
    "fk_table_name",
    "fk_name",
    listagg("fk_column_name", ', ') within group(order by "key_sequence") as "columns",
    concat("pk_database_name", '.', "pk_schema_name", '.', "pk_name") as "reference_key"
from imported_keys ik
group by "fk_database_name",
    "fk_schema_name",
    "fk_table_name",
    "fk_name",
    "pk_database_name",
    "pk_schema_name",
    "pk_name";