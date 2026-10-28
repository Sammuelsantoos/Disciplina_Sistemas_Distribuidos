# Sistema de Notificações de Esportes (Trabalho 2)

Este projeto consiste em um **Sistema Distribuído de Notificação de Esportes** desenvolvido em **Python** para a disciplina de Sistemas Distribuídos da Universidade Federal do Ceará (UFC) – Campus Quixadá.

O sistema simula uma central esportiva onde administradores registram partidas e eventos (gols, cartões, fim de jogo), e clientes (torcedores) realizam consultas síncronas de placares e históricos utilizando um protocolo manual de **Requisição-Resposta** baseado em **RPC** através de payloads estruturados em **JSON**.

---

## Autores
1. Rubens Rabelo - SI - 555497
2. Samuel Augusto - ES - 601930

---

## Tecnologias e Conceitos Utilizados

* **Linguagem:** Python 3.x (com uso estrito de *Type Hints* e propriedades abstratas).
* **Protocolo Requisição-Resposta:** Estrutura baseada na Seção 5.2 do livro-texto (Coulouris), encapsulando metadados obrigatórios (`messageType`, `requestId`, `objectReference`, `methodId`, `arguments`) e ocultando os canais de rede da camada de aplicação.
* **Comunicação Baseada em RPC Síncrono:** Os clientes realizam operações remotas bloqueantes (`wait` e `continuation`) para alterar ou extrair informações de estado do servidor em modo de consulta (*pull*).
* **Multithreading Coordenado:** Uso de travas thread-safe (`threading.Lock`) no servidor para garantir a integridade dos dados e do histórico ao receber múltiplas requisições RPC concorrentes.
* **External Data Representation (Serialization):** Empacotamento estruturado de parâmetros passados por valor utilizando representação externa baseada em strings **JSON** para a rede e strings delimitadas em formato CSV para persistência física.
* **Padrões de Projeto (Factory Method):** Centralização da lógica de instanciação dinâmica de subclasses (`GoalEvent`, `CardEvent`) com base no tipo do registro de entrada na camada de serviços.

---

## Estrutura de Classes

### Classes de Dados Polimórficas (`src/shared/models/`)
* **`BaseMatchEvent`**: Classe abstrata pura que define o contrato de interface de propriedades e o método comum de formatação textual `build_message()`.
* **`MatchEvent`**: Subclasse base que representa um acontecimento genérico no jogo (ex: END), gerenciando atributos como `event_id`, `match_id`, `event_type` e `description`.
* **`GoalEvent`**: Subclasse especializada para gols, gerenciando de forma encapsulada o atributo específico `team`.
* **`CardEvent`**: Subclasse especializada para advertências, gerenciando de forma encapsulada o atributo específico `player`.
* **`Match`**: Representa uma partida de futebol activa, contendo metadados das equipes e o estado do placar em tempo real (`home_score` e `away_score`).

### Infraestrutura do Protocolo (`src/shared/infra/`)
* **`Message`**: Classe encarregada do marshaling e unmarshaling de pacotes contendo os campos de controle exigidos pelo modelo arquitetural do livro-texto.
* **`RequestReplyProtocol`**: Abstração de barramento de alto nível que provê os métodos de execução `do_operation` e `send_reply` consumidos pela aplicação.

---

## Estrutura de Diretórios

A organização das pastas separa as responsabilidades explicitamente entre o ambiente do servidor, os pacotes de infraestrutura, os painéis dos clientes e as suítes de testes:

```bash
.
├── docs/
│   └── MANUAL_TEST.md
├── README.md
└── src/
    ├── client/
    │   ├── admin_client.py
    │   ├── __init__.py
    │   └── viewer_client.py
    ├── data/
    │   ├── event.csv
    │   └── event_test.csv
    ├── __init__.py
    ├── server/
    │   ├── __init__.py
    │   ├── main_server.py
    │   └── services/
    │       ├── __init__.py
    │       ├── match_service.py
    │       └── notify_service.py
    └── shared/
        ├── __init__.py
        ├── infra/
        │   ├── __init__.py
        │   └── protocol.py
        ├── models/
        │   ├── __init__.py
        │   ├── match_event.py
        │   └── match.py
        └── streams/
            ├── event_input.py
            ├── event_output.py
            └── __init__.py
```

---

## Como Executar o Projeto de Forma Manual

Para inicializar o barramento distribuído local (Servidor Central RPC, Painel do Administrador e Terminal do Torcedor), execute os módulos a partir do diretório raiz utilizando os sinalizadores locais de host:

### 1. Inicializar o Servidor Central
```bash
python3 -m src.server.main_server
```

### 2. Inicializar o Console do Administrador
```bash
python3 -m src.client.admin_client --host localhost
```

### 3. Inicializar o Terminal de Consulta do Torcedor
```bash
python3 -m src.client.viewer_client --host localhost
```

---

## Formato dos Registros de Eventos (CSV)

Sempre que um novo evento relevante é processado pelo servidor, os gerenciadores realizam a serialização e persistem os dados no arquivo `src/data/event.csv` utilizando o seguinte formato padronizado:

```csv
1,10,GOL,Gol de cabeca após cruzamento,Ceara
2,10,CARD,Cartao amarelo por falta dura,Fortaleza
3,10,END,Fim do segundo tempo,
```

*(Estrutura posicional dos campos: ID do Evento, ID da Partida, Tipo do Evento, Descrição do Evento e Contexto Específico - Nome do Time ou do Jogador).*

---

## Observações Acadêmicas

Este projeto possui finalidade estritamente acadêmica e foi desenvolvido com o objetivo de consolidar de forma prática os conceitos de chamadas remotas, sincronização de threads, concorrência distribuída e representação externa de dados ministrados na disciplina de Sistemas Distribuídos.
