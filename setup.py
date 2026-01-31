from setuptools import setup

setup(name='schema-sentinel',
      version='2.0.5',
      description='SQL Comparison tool',
      packages=['schema_sentinel'],
      install_requires=[
          'click==8.1.3',
          'pandas==2.0.1',
          'snowflake-connector-python==3.0.3',
          'cryptography==39.0.2',
          'snowflake-sqlalchemy==1.4.7',
          'jinja2==3.1.2',
          'tinyhtml==1.2.0',
          'markdownmaker==0.4.0',
          'tabulate==0.9.0',
          'simple-ddl-parser==0.30.0',
          'snakemd==2.1.0',
          'sql-formatter==0.6.2',
          'pre-commit==3.3.3',
          'sqlparse==0.4.4',
          'pdfkit==1.0.0',
          'alembic[tz]==1.11.3',
          'SQLAlchemy==1.4.49'
      ],
      zip_safe=False)
