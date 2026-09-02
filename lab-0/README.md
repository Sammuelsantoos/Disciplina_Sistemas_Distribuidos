# Laboratório 0: Pinger UDP

Repositório destinado ao desenvolvimento do Laboratório de Pinger UDP para a disciplina de Redes e Sistemas Distribuídos da Universidade Federal do Ceará - Campus Quixadá.

## Autores
- Rubens Rabelo (Sistemas de Informação - 555497)
- Samuel Augusto (Engenharia de Software - 601930)

## Descrição do Projeto
O objetivo deste laboratório é compreender o funcionamento do protocolo UDP por meio da implementação de um cliente de Ping que se comunica com um servidor Java fornecido. O servidor simula artificialmente uma taxa de perda de pacotes e atraso na rede.

## Estrutura de Arquivos
```bash
.
├── client
│   ├── ping_client_1.py
│   ├── ping_client_2.py
│   └── ping_client_3.py
└── server
    ├── ping_receiver_3.py
    └── PingServer.java
```

## Como Executar

### Pré-requisitos
- Java Development Kit (JDK) instalado.
- Python 3 instalado.

### Executando o Servidor Java (Questões 1 e 2)
1. Navegue até o diretório do servidor:
```bash
cd server
```

2. Compile o código Java:
```bash
javac PingServer.java
```

3. Execute o servidor especificando uma porta:
```bash
java PingServer 12000
```

### Executando os Clientes Python
Abra outro terminal, navegue até a pasta do cliente e execute o script correspondente à questão desejada informando o host e a porta:
```bash
cd client
```

Substitua `{X}` pelo número do arquivo (1 ou 2):
```bash
python3 ping_client_{X}.py 127.0.0.1 12000
```

### Executando a Questão 3 (UDP Confiável)
Para testar a transferência confiável da terceira questão, execute o receptor Python na pasta correspondente em um terminal e o cliente correspondente em outro.

Terminal 1 (Receptor):
```bash
cd server
python3 ping_receiver_3.py 12000
```

Terminal 2 (Cliente):
```bash
cd client
python3 ping_client_3.py 127.0.0.1 12000 "ola mundo" # [loss_rate] # O Loss Rate é opcional, com valor padrão de 0.0
```
