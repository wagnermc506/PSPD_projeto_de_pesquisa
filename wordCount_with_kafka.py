import sys
from datetime import datetime
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import explode, split, col, length, substring, window, current_timestamp, to_timestamp, from_csv, desc, asc, upper

# Cria sessão spark
spark = SparkSession.builder.master("spark://192.168.8.5:7077").appName("WordCountKafka").getOrCreate()

# Seta nível de log para "WARN" para que o console não imprima o spam de log que aparece no nível INFO
spark.sparkContext.setLogLevel("WARN")

# Conta o número de ocorrências de palavras
def basic_word_count(lines: DataFrame):
    # words = lines.select(explode(split(lines.value, " ")).alias("word"), lines['timestamp'])
    # windowned_counts = words.groupBy(
    #     window("timestamp", "5 seconds", "5 seconds"),
    #     words.word
    # ).count().sort(desc('window'))
    # return windowned_counts.writeStream.outputMode("complete").format("console").option("truncate", "false").start()
    words = lines.select(explode(split(lines.value, " ")).alias("word"))
    word_counts = words.groupBy("word").count()
    return word_counts.writeStream.outputMode("complete").format("console").option("truncate", "false").start()

# Conta o número de ocorrências de palavras que começam com S, P e R em janelas de 5 segundos
def word_count_for_letters(lines: DataFrame):
    words = lines.select(explode(split(lines.value, " ")).alias("word"), lines["timestamp"])
    first_letters = words.select("timestamp", upper(col('word')).substr(1, 1).alias("letter"))\
        .filter("letter in ('S', 'P', 'R')")\
        .groupBy(
            window("timestamp", "5 seconds", "5 seconds"),
            "letter"
        ).count().sort(desc('window'))
    return first_letters.writeStream.outputMode("complete").format("console").option("truncate", "false").start()

# Conta o número de ocorrências de palavras que têm 6, 8 e 11 caracteres em janelas de 5 segundos
def word_count_by_length(lines: DataFrame):
    words = lines.select(explode(split(lines.value, " ")).alias("word"), lines["timestamp"])
    lengths = words.select(length("word").alias('len'), "timestamp")\
        .filter("len in (6, 8, 11)")\
        .groupBy(
            window("timestamp", "5 seconds", "5 seconds"),
            "len"
        ).count().sort(desc('window'))
    return lengths.writeStream.outputMode("complete").format("console").option("truncate", "false").start()


if __name__ == '__main__':

    if len(sys.argv) < 4:
        print(f"uso: {sys.argv[0]} <host> <port> [basic|letter|len]")
        exit(0)

    # Cria conexão com o kafka para leitura do tópico
    lines = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers", "192.168.8.5:9092")\
        .option("subscribe", "wordCount")\
        .option("includeTimestamp", 'true')\
        .load()

    if sys.argv[3] == 'basic':
        query = basic_word_count(lines)
        query.awaitTermination()

    elif sys.argv[3] == 'letter':
        query = word_count_for_letters(lines)
        query.awaitTermination()

    elif sys.argv[3] == 'len':
        query = word_count_by_length(lines)
        query.awaitTermination()

    elif sys.argv[3] == 'all':
        [q.awaitTermination() for q in [basic_word_count(lines), word_count_for_letters(lines), word_count_by_length(lines)]]
