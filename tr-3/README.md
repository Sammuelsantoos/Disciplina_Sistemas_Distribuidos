# Trabalho 3 – Comunicação Indireta em Python com Publicar e Assinar

Este projeto implementa a arquitetura de comunicação indireta baseada no modelo publicar e assinar, aplicada ao cenário de eventos de futebol. A solução utiliza um broker central para receber mensagens publicadas em tópicos e distribuí-las para clientes que se inscreveram no mesmo canal.

Ao contrário de uma comunicação direta por chamada remota, os produtores e consumidores não se conhecem diretamente. O canal intermediário desempenha o papel de mediador entre eles, respeitando a ideia de desacoplamento espacial, temporal e de sincronização, conforme a fundamentação do material de referência.

---

## Objetivo

Implementar um sistema distribuído didático em Python para eventos esportivos, usando:

- um broker intermediário;
- tópicos de assinatura (`match.events`, `match.status`);
- clientes produtores e consumidores;
- sockets TCP para comunicação em rede;
- protocolo JSON para encapsular as mensagens;
- manutenção de histórico e estado da partida.

---

## Arquitetura da solução

O sistema é composto por:

- Producer / AdminClient: publica eventos da partida, como gol ou cartão;
- Broker: recebe as publicações e encaminha para os assinantes;
- ViewerClient: assina um tópico e recebe notificações em tempo real;
- MatchService: atualiza o placar e o histórico de eventos;
- EventBroker: gerencia tópicos, assinaturas e disseminação;
- EventProtocol: estrutura o formato das mensagens em JSON.

Fluxo principal:

```text
AdminClient -> broker -> subscribers
       \-> MatchService (atualiza placar/histórico)
```

---

## Estrutura do projeto

```bash
tr-3/
├── README.md
├── RELATORIO_TRABALHO_3.md
├── RELATORIO_TRABALHO_3.pdf
├── docs/
│   ├── MANUAL_TEST.md
│   └── REPORT.md
├── src/
│   ├── __init__.py
│   ├── client/
│   │   ├── __init__.py
│   │   ├── admin_client.py
│   │   └── viewer_client.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── main_server.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── event_broker.py
│   │       └── match_service.py
│   └── shared/
│       ├── __init__.py
│       ├── infra/
│       │   ├── __init__.py
│       │   └── protocol.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── match.py
│       │   └── match_event.py
│       └── streams/
├── tests/
│   └── unit/
│       ├── __init__.py
│       ├── test_event_broker.py
│       ├── test_match_service.py
│       ├── test_protocol.py
│       └── test_hello_service.py
└── pom.xml
```

---

## Componentes principais

- `MatchEventBroker`: mantém a lógica do broker, aceita inscrições e publica eventos em tópicos;
- `EventBroker`: implementa a estrutura de tópicos e envio de notificações;
- `MatchService`: controla o placar, o histórico e a lógica de gol/cartão;
- `EventProtocol`: serializa e desserializa mensagens em JSON;
- `AdminClient`: publica eventos da partida;
- `ViewerClient`: se inscreve em tópicos e recebe notificações;
- `Match` e `MatchEvent`: modelam o domínio de futebol.

---

## Protocolo e comunicação

A comunicação é baseada em JSON, com as seguintes ações principais:

- `SUBSCRIBE`: o cliente se inscreve em um tópico;
- `PUBLISH`: o produtor envia um evento para um tópico;
- `NOTIFY`: o broker encaminha a mensagem aos assinantes;
- `QUERY`: consulta estado da partida ou histórico;
- `ACK`: resposta do broker confirmando a operação.

Exemplo de publicação:

```json
{
  "action": "PUBLISH",
  "topic": "match.events",
  "payload": {
    "event_type": "gol",
    "team": "Flamengo",
    "player": "Pedro",
    "minute": "13'",
    "description": "Pedro marcou para Flamengo aos 13'."
  }
}
```

Exemplo de notificação enviada ao assinante:

```json
{
  "action": "NOTIFY",
  "topic": "match.events",
  "payload": {
    "event_type": "gol",
    "team": "Flamengo",
    "player": "Pedro",
    "minute": "13'",
    "description": "Pedro marcou para Flamengo aos 13'."
  }
}
```

---

## Como executar

### 1. Iniciar o broker

```bash
cd /home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3
PYTHONPATH=/home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3 python3 -m src.server.main_server
```

### 2. Assinar um tópico

```bash
cd /home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3
PYTHONPATH=/home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3 python3 -m src.client.viewer_client --topic match.events
```

### 3. Publicar um evento

```bash
cd /home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3
PYTHONPATH=/home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3 python3 -m src.client.admin_client --action goal --team Flamengo --player Pedro --minute "13'" --topic match.events
```

### 4. Consultar o placar

```bash
cd /home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3
PYTHONPATH=/home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3 python3 -m src.client.admin_client --action query-score
```

---

## Validação

Os testes automatizados do projeto validam:

- publicação de eventos no broker;
- entrega de notificações para assinantes;
- atualização do placar e do histórico;
- serialização/parse do protocolo JSON;
- funcionamento do cenário de eventos esportivos em arquitetura indireta.

Comando de verificação:

```bash
cd /home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m unittest discover -s tests -p "*.py" -v
```

---

## Observação final

Este projeto está totalmente alinhado ao modelo de comunicação indireta do trabalho 4: ele não implementa uma chamada remota direta, mas sim um broker que recebe eventos públicos e distribui notificações para consumidores interessados. Esse é o comportamento esperado de uma arquitetura publicar e assinar em sistemas distribuídos.
