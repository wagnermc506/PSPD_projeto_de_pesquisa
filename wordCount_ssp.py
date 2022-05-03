from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, col, length

spark = SparkSession.builder.master("spark://192.168.8.5:7077").appName("WordCountKafka").getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# lines = spark.readStream.format("kafka")\
#             .option("kafka.bootstrap.servers", "192.168.8.5:9092")\
#             .option("subscribe", "words")\
#             .load()
lines = spark.readStream.format("socket").option("host", "192.168.8.5").option("port", 9999).load()

words = lines.select(explode(split(lines.value, " ")).alias("word"))
wordCounts = words.groupBy("word").count()

words_with_SPR = words.filter(length(words['word']) > 3).groupBy("word").count()

query = wordCounts.writeStream.outputMode("complete").format("console").start()

query2 = words_with_SPR.writeStream.outputMode("complete").format("console").start()

# query = wordCounts.writeStream.format("kafka").option("checkpointLocation", "/tmp/checkpoint").option("kafka.bootstrap.servers", "192.168.8.5:9092").option("topic", "text_topic").start()

query.awaitTermination()
query2.awaitTermination()