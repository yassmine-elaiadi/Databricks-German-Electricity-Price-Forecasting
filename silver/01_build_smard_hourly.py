from databricks.connect import DatabricksSession
from pyspark.sql import functions as F
from pyspark.sql import Window              # ← new import goes here, at the top


spark = DatabricksSession.builder.serverless().getOrCreate()

df = spark.table("energy_lakehouse.bronze.smard_raw")
df.printSchema()
#df.show(5)

df = df.withColumn("ts_utc", F.timestamp_millis(F.col("ts_ms")))      # ms → timestamp
df = df.withColumn("ts_berlin", F.from_utc_timestamp(F.col("ts_utc"), "Europe/Berlin"))   # ts_utc → German time

df = df.select("filter_id","value","ts_utc","ts_berlin")
#df.show(5)

df = df.groupBy("ts_utc","ts_berlin").pivot("filter_id").agg(F.first("value"))
df.orderBy("ts_utc").show(5)

df = df.withColumnsRenamed({"410": "load", "1225": "wind_offshore", "4067" :"wind_onshore", "4068": "solar" , "4169": "price"})
df = df.filter(F.col("ts_utc") >= "2018-09-30 22:00:00")
df = df.filter(F.col("price").isNotNull())
#df.orderBy(F.col("ts_utc").desc()).show(5)
# --- Step 4a: add the neighbours of each hour ---
w = Window.orderBy("ts_utc")

df = df.withColumn("load_prev", F.lag("load", 1).over(w))    # load of the hour before
df = df.withColumn("load_next", F.lead("load", 1).over(w))   # load of the hour after

#df.filter(F.col("ts_berlin").between("2018-10-08 00:00:00", "2018-10-08 05:00:00")).orderBy("ts_utc").show()
df.filter( (F.col("load").isNull()) & (F.col("ts_utc") < "2026-01-01") ).orderBy("ts_utc").show()