from pyspark import SparkContext
from pyspark.streaming import StreamingContext

# Criar spark context
sc = SparkContext("spark://192.168.8.5:7077", "WordCount")

# Seta log level para o terminal não ter spam de log
sc.setLogLevel("WARN")

# Seta uma janela de 5 segundos para os batches
ssc = StreamingContext(sc, 5)

# cria uma socket stream para receber dados do socket
lines = ssc.socketTextStream("192.168.8.5", 9999)

# separa as linhas em palavras
words = lines.flatMap(lambda line: line.split(" "))

total = words.map(lambda word: ('total', 1)).reduceByKey(lambda x, y: x + y)

# Contador de palavras por palavra
word_count = words.map(lambda word: (word, 1)).reduceByKey(lambda x, y: x +y)

# contador de palavras que iniciam com determinadas letras
words_starting_with_SPR = words\
    .filter(lambda word: word.upper().startswith(('S', 'P', 'R')))\
    .map(lambda word: (word[0].upper(), 1))\
    .reduceByKey(lambda x, y: x + y)

# contador de palavras que têm certo tamanho
words_per_length = words\
    .filter(lambda word: len(word) in [6, 8, 11])\
    .map(lambda word: (str(len(word)), 1))\
    .reduceByKey(lambda x, y: x + y)

word_count.pprint()
total.pprint()
words_starting_with_SPR.pprint()
words_per_length.pprint()

ssc.start()
ssc.awaitTermination()