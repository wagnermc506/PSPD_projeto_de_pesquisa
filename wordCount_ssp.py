import sys
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import explode, split, col, length, substring

spark = SparkSession.builder.master("spark://192.168.8.5:7077").appName("WordCountKafka").getOrCreate()

spark.sparkContext.setLogLevel("WARN")

def basic_word_count(lines: DataFrame):
    words = lines.select(explode(split(lines.value, " ")).alias("word"))
    word_counts = words.groupBy("word").count()
    query = word_counts.writeStream.outputMode("complete").format("console").start()
    query.awaitTermination()

def word_count_for_letters(lines: DataFrame):
    words = lines.select(explode(split(lines.value, " ")).alias("word"))
    first_letters = words.select(col('word').substr(1, 1).alias("letter")).filter("letter in ('S', 'P', 'R')").groupBy("letter").count()
    query = first_letters.writeStream.outputMode("complete").format("console").start()
    query.awaitTermination()

def word_count_by_length(lines: DataFrame):
    words = lines.select(explode(split(lines.value, " ")).alias("word"))
    lengths = words.select(length("word").alias('len')).groupBy('len').count()
    query = lengths.writeStream.outputMode("complete").format("console").start()
    query.awaitTermination()


if __name__ == '__main__':

    if len(sys.argv) < 4:
        print(f"uso: {sys.argv[0]} <host> <port> [basic|letter|len]")
        exit(0)

    lines = spark.readStream.format("socket").option("host", "192.168.8.5").option("port", 9999).load()

    if sys.argv[3] == 'basic':
        basic_word_count(lines)
    elif sys.argv[3] == 'letter':
        word_count_for_letters(lines)
    elif sys.argv[3] == 'len':
        word_count_by_length(lines)
