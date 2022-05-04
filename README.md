# Programação de Streaming em clusters

## Integrantes

|Matrícula|Nome|
|---------|----|
|18/0027352|Rodrigo Carvalho dos Santos
|18/0029177|Wagner Martins da Cunha

## Setup do cluster com máquinas virtuais

### Dependências

- vagrant
- virtualbox

### Iniciando máquinas virtuais

Para instanciar as máquinas virtuais, primeiro baixe a box do Ubuntu 20.04 com o comando

```shell
$ vagrant box add ubuntu/focal64
```

Logo em seguida, no diretório root deste repositório, utilize o comando

```shell
$ vagrant up
```

e serão criadas três máquinas virtuais com a seguinte configuração de rede:

|hostname|ip|
|--------|--|
|master|192.168.8.5|
|worker1|192.168.8.6|
|worker2|192.168.8.7|

Para desligar as máquinas virtuais use o comando:

```shell
$ vagrant halt
```

e para logar em qualquer uma das máquinas:


```shell
$ vagrant ssh <master|worker1|worker2>
```

### Configurando Cluster Spark standalone

No ambiente das 3 máquinas virtuais, cole o seguinte conteúdo no arquivo /etc/hosts:

```
192.168.8.5     master
192.168.8.6     worker1
192.168.8.7     worker2
```

Caso tenha uma linha que configure a respectiva máquina para outro endereço, como por exemplo

```
127.0.2.1 master master
```

comente, ou delete a linha.

Em seguida, siga o tutorial para [configurar o spark](https://towardsdatascience.com/setting-up-apache-spark-in-standalone-mode-81efb78c2b52).

Com o ambiente configura, destacam-se os comandos:

```shell
$ start-all.sh
```
para iniciar o cluster spark e

```shell
$ stop-all.sh
```

para parar o cluster.

### Apache KAFKA

O [Apache KAFKA](https://kafka.apache.org/) foi instanciado somente no servidor `master`, de forma que sua configuração não é a de um cluster.

A instalação e instanciação do servidor do KAFKA pode ser encontrada no [getting started](https://kafka.apache.org/quickstart) do site oficial.

### Rodando scripts

#### Parte 1 - Contabilizando palavras de entrada via socket

O algoritmo da parte 1 se encontra no arquivo `wordCount.py`. É necessário que o cluster do Spark esteja ativo.

Abra dois terminais conectados à vm `master`. Em um terminal, utilize o comando:

```shell
$ nc -l 9999
```
para iniciar o servidor tcp com o netcat.

Em outro terminal, mude para a pasta `/vagrant/`:

```shell
$ cd /vagrant
```

e utilize o comando:

```shell
$ spark-submit wordCount.py
```

_Obs.: o diretório `/vagrant` é um diretório especial que funciona como um volume para o diretório da máquina host onde está o arquivo `Vagrantfile`._

Ao enviar qualquer texto no terminal do netcat, o spark irá contabilizar as palavras e printar no terminal a contagem por palavras, o número total de palavras recebidas, o número de palavras que contém 'P', 'R' e 'S' e o número de palavras que contém 6, 8 e 11 caracteres. 

#### Parte 2 - Contabilizando palavras via Apache Kafka

O algoritmo para a parte 2 se encontra no arquivo `wordCount_with_kafka.py`. Para este programa é necessário que o cluster Spark e o broker Kafka estejam ativos.

Além dos terminais rodando o zookeeper e o kafka (como mostrado no [getting started](https://kafka.apache.org/quickstart)), serão necessários mais 2 terminais.

No primeiro terminal, dentro do diretório raíz da instalação do kafka, crie um produtor com o comando:

```shell
$ bin/kafka-console-producer.sh --topic wordCount --bootstrap-server localhost:9092
```

E em outro terminal, vá para a pasta `/vagrant`

```shell
$ cd /vagrant
```

e inicialize o script no Apache Spark:

```shell
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 wordCount_with_kafka.py localhost 9999 all
```

Após inicializado, a aplicação Spark começará a contar as palvras enviadas pelo KAFKA de 5 em 5 segundos e irá imprimir na tela:

- A contagem por palavra
- A contagem por palavra que inicia com as letras 'P', 'R' e 'S'. A contagem não considera se a letra é maiúscula ou minúscula, palavras com 'P' e 'p' serão contadas para 'P'.
- A contagem por palavra que contém tamanho igual a 6, 8 e 11.

