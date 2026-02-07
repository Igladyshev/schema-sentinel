"""YAML Shredder - Automatic schema generation and tabular structure extraction from YAML/JSON files."""

from yaml_shredder.data_loader import SQLiteLoader
from yaml_shredder.ddl_generator import DDLGenerator
from yaml_shredder.schema_generator import SchemaGenerator
from yaml_shredder.structure_analyzer import StructureAnalyzer
from yaml_shredder.table_generator import TableGenerator

__version__ = "0.1.0"

__all__ = [
    "TableGenerator",
    "DDLGenerator",
    "SQLiteLoader",
    "SchemaGenerator",
    "StructureAnalyzer",
]
