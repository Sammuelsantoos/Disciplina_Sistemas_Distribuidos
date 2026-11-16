# Trabalho 3 – Comunicação Indireta em Python com Publicar e Assinar

Este projeto implementa uma arquitetura de comunicação indireta baseada no modelo **Publicar e Assinar (Pub/Sub)** em Python, aplicada ao monitoramento e transmissão de eventos esportivos em tempo real. A solução utiliza um **Broker central** via sockets TCP para receber publicações em tópicos, persistir o histórico em arquivo CSV e distribuir notificações de forma assíncrona para os clientes inscritos.

Ao contrário da comunicação direta via RPC, produtores e consumidores não precisam conhecer a identidade ou o endereço um do outro. O Broker atua como mediador, garantindo o desacoplamento espacial, temporal e de sincronização entre os componentes.

---

## Objetivo

Implementar um sistema distribuído em Python para gerenciamento e transmissão de partidas de futebol, contemplando:

- Um servidor Broker centralizado e *thread-safe* (`MatchEventBroker`);
- Comunicação baseada em tópicos de assinatura (como `match.events`);
- Painel administrativo interativo (Producer / `SportsAdminClient`) e cliente espectador em tempo real (Subscriber / `ViewerClient`);
- Protocolo de mensagens estruturado em JSON delimitado por linha (`EventProtocol`);
- Gerenciamento de múltiplas partidas simultâneas, placar e histórico de eventos (`MatchService`);
- Persistência automática de eventos em disco (`src/data/event.csv`) por meio de streams customizados (`MatchEventInputStream` e `MatchEventOutputStream`).

---

## Arquitetura da Solução

O sistema é dividido em três camadas principais:

- **`SportsAdminClient` (Producer):** Interface interativa via linha de comando (CLI) utilizada para cadastrar partidas, publicar eventos (`GOL`, `CARD`, `END`) e realizar consultas síncronas (`QUERY`).
- **`MatchEventBroker` & `EventBroker` (Broker):** Gerencia conexões TCP concorrentes, mantém a tabela de assinaturas por tópico, coordena a atualização de estado com o `MatchService` e dissemina notificações (`NOTIFY`) aos espectadores.
- **`ViewerClient` (Subscriber):** Conecta-se ao Broker, inscreve-se em um tópico de interesse e exibe os lances e placares atualizados em formato textual limpo no terminal.
- **`MatchService`:** Camada de negócio *thread-safe* (`threading.RLock`) responsável por validar times e eventos, atualizar placares e persistir/recarregar o histórico no arquivo CSV.
- **`EventProtocol`:** Responsável pela serialização (marshalling) e desserialização (unmarshalling) das mensagens JSON trocadas na rede.

Fluxo principal de dados:

```text
SportsAdminClient (Publisher) ──► MatchEventBroker ──► ViewerClient(s) (Subscribers)
                                         │
                                         ▼
                                   MatchService ──► src/data/event.csv
```

---

## Estrutura do Projeto

```text
tr-3/
├── README.md
├── RELATORIO_TRABALHO_3.md
├── docs/
│   └── MANUAL_TEST.md
└── src/
    ├── __init__.py
    ├── client/
    │   ├── __init__.py
    │   ├── admin_client.py
    │   └── viewer_client.py
    ├── data/
    │   └── event.csv          # Gerado automaticamente ao registrar eventos
    ├── server/
    │   ├── __init__.py
    │   ├── main_server.py
    │   └── services/
    │       ├── __init__.py
    │       ├── event_broker.py
    │       ├── match_service.py
    │       └── notify_service.py
    └── shared/
        ├── __init__.py
        ├── infra/
        │   ├── __init__.py
        │   └── protocol.py
        ├── models/
        │   ├── __init__.py
        │   ├── match.py
        │   └── match_event.py
        └── streams/
            ├── __init__.py
            ├── event_input.py
            └── event_output.py
```

---

## Componentes Principais

- **`MatchEventBroker` (`src/server/main_server.py`):** Servidor TCP multithread que interpreta as ações `SUBSCRIBE`, `PUBLISH` e `QUERY`, integra-se ao `MatchService` e enriquece os payloads antes da notificação.
- **`EventBroker` (`src/server/services/event_broker.py`):** Implementa o núcleo do padrão Pub/Sub (inscrição, cancelamento, histórico em memória e envio via socket com tratamento de desconexão).
- **`MatchService` (`src/server/services/match_service.py`):** Controla o ciclo de vida das partidas, aplica o padrão Factory para instanciar eventos específicos (`GoalEvent`, `CardEvent`, `MatchEvent`) e gerencia a leitura/escrita no CSV.
- **`EventProtocol` (`src/shared/infra/protocol.py`):** Define os métodos estáticos `build_publish`, `build_subscribe`, `build_query`, `build_notify`, `build_ack` e `parse_message`.
- **`SportsAdminClient` (`src/client/admin_client.py`):** Menu interativo no terminal para operação completa do sistema pelo administrador.
- **`ViewerClient` (`src/client/viewer_client.py`):** Cliente espectador contínuo que formata as notificações recebidas em tempo real.
- **`Match`, `MatchEvent`, `GoalEvent`, `CardEvent` (`src/shared/models/`):** Modelos de domínio com suporte a serialização CSV.
- **`MatchEventInputStream` e `MatchEventOutputStream` (`src/shared/streams/`):** Fluxos de entrada e saída para leitura e gravação persistente dos eventos em disco.

---

## Protocolo e Comunicação

A comunicação ocorre sobre TCP utilizando objetos JSON delimitados por quebra de linha (`\n`), com as seguintes ações:

- **`SUBSCRIBE`:** Inscreve o cliente em um tópico (`match.events`).
- **`PUBLISH`:** Envia a criação de uma partida (`CREATE_MATCH`) ou um lance (`GOL`, `CARD`, `END`).
- **`NOTIFY`:** Mensagem *push* enviada pelo Broker a todos os assinantes do tópico com o placar atualizado.
- **`QUERY`:** Consulta síncrona de placar (`score`), histórico de lances (`events`) ou partidas ativas (`matches`).
- **`ACK`:** Resposta de confirmação ou erro enviada pelo Broker ao cliente solicitante.

### Exemplo de Publicação (`PUBLISH`)

```json
{
  "action": "PUBLISH",
  "topic": "match.events",
  "payload": {
    "event_type": "GOL",
    "match_id": 1,
    "team": "Flamengo",
    "player": "Pedro",
    "description": "Pedro marcou aos 15'"
  }
}
```

### Exemplo de Notificação aos Assinantes (`NOTIFY`)

```json
{
  "action": "NOTIFY",
  "topic": "match.events",
  "payload": {
    "event_type": "GOL",
    "match_id": 1,
    "team": "Flamengo",
    "player": "Pedro",
    "description": "Pedro marcou aos 15'",
    "home_team": "Flamengo",
    "away_team": "Vasco",
    "home_score": 1,
    "away_score": 0
  }
}
```

---

## Como Executar

Abra **três terminais** na pasta raiz do projeto (`tr-3`):

### 1. Iniciar o Servidor Broker (Terminal 1)

```bash
python3 -m src.server.main_server --host 127.0.0.1 --port 5000
```

### 2. Iniciar o Cliente Espectador / Subscriber (Terminal 2)

```bash
python3 -m src.client.viewer_client --host 127.0.0.1 --port 5000 --topic match.events
```

### 3. Abrir o Painel Administrativo / Publisher (Terminal 3)

```bash
python3 -m src.client.admin_client --host 127.0.0.1 --port 5000
```

No menu interativo exibido no Terminal 3, basta escolher a opção desejada:
- **`1`** para cadastrar uma nova partida;
- **`2`** para registrar eventos (`GOL`, `CARD` ou `END`);
- **`3`** para consultar o placar de uma partida;
- **`4`** para listar o histórico de eventos de uma partida;
- **`5`** para listar todas as partidas ativas.

---

## Observação Arquitetural

Este projeto reflete fielmente o modelo de **comunicação indireta (Publicar/Assinar)**: os produtores publicam eventos sem acoplamento com os consumidores, enquanto o Broker atua como intermediário responsável pelo roteamento por tópicos, manutenção de estado em memória e persistência em arquivo CSV.
