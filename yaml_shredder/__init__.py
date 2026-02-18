"""YAML Shredder - Automatic schema generation and tabular structure extraction from YAML/JSON files."""

from yaml_shredder.data_comparer import DataComparer, PrimaryKeyDetector, TableMatcher
from yaml_shredder.data_loader import SQLiteLoader
from yaml_shredder.ddl_generator import DDLGenerator
from yaml_shredder.doc_generator import MarkdownDocGenerator, generate_doc_from_yaml
from yaml_shredder.schema_generator import SchemaGenerator
from yaml_shredder.structure_analyzer import StructureAnalyzer
from yaml_shredder.table_generator import TableGenerator
from yaml_shredder.yaml_comparator import YAMLComparator

__version__ = "0.1.0"

__all__ = [
    "DataComparer",
    "PrimaryKeyDetector",
    "SQLiteLoader",
    "DDLGenerator",
    "MarkdownDocGenerator",
    "SchemaGenerator",
    "StructureAnalyzer",
    "TableGenerator",
    "TableMatcher",
    "YAMLComparator",
    "generate_doc_from_yaml",
]
