"""
Setup: create the catalog, schemas and Volume for the project.

Safe to run many times: IF NOT EXISTS skips anything that already exists.
Run with the normal Run button (Databricks Connect).
"""


from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.serverless().getOrCreate()

spark.sql("CREATE CATALOG IF NOT EXISTS energy_lakehouse")
spark.sql("CREATE SCHEMA IF NOT EXISTS energy_lakehouse.bronze")
spark.sql("CREATE SCHEMA IF NOT EXISTS energy_lakehouse.silver")
spark.sql("CREATE SCHEMA IF NOT EXISTS energy_lakehouse.gold")

#volume

spark.sql("CREATE VOLUME IF NOT EXISTS energy_lakehouse.bronze.raw_files")

spark.sql("SHOW SCHEMAS IN energy_lakehouse").show()
spark.sql("SHOW VOLUMES IN energy_lakehouse.bronze").show()

