# Sistema de Notificações de Esportes

Este projeto consiste em um **Sistema Distribuído de Notificação de Esportes** desenvolvido em **Python** para a disciplina de Sistemas Distribuídos da Universidade Federal do Ceará (UFC) – Campus Quixadá.

O sistema simula uma central esportiva onde administradores registram partidas e eventos (gols, cartões, fim de jogo) via **Sockets TCP**, e múltiplos clientes (torcedores) recebem atualizações instantâneas via **Sockets UDP Multicast**.

---

## Autores
1. Rubens Rabelo - SI - 555497
2. Samuel Augusto - ES - 601930

### Separação das tarefas

| Módulo / Componente | Escopo Técnico | Rubens Rabelo | Samuel Augusto |
|---|---|---|---|
| Modelos Compartilhados (`src/shared/models/`) | Criação das classes polimórficas (`BaseMatchEvent`, `MatchEvent`, `GoalEvent` e `CardEvent`) com correções estritas para Pylint e Type Hints. | X | X |
| Streams de Saída (`src/shared/streams/`) | Desenvolvimento do gerador de fluxos de escrita estruturada em CSV e rede TCP (`event_output.py`). | X | |
| Streams de Entrada (`src/shared/streams/`) | Desenvolvimento do leitor de fluxos com buffer para reconstrução de dados via CSV e rede TCP (`event_input.py`). | | X |
| Servidor Principal (`src/server/`) | Arquitetura básica do socket TCP multithread concorrido do `main_server.py`. | X | |
| Lógica do Servidor (`src/server/services/`) | Gerenciamento do placar em memória, persistência via streams CSV e injeção do padrão **Factory** para subclasses no `match_service.py`. | | X |
| Emissão de Notificações (`src/server/services/`) | Configuração do socket de envio UDP Multicast e formatação de alertas em JSON no arquivo `notify_service.py`. | X | |
| Painel de Controle (`src/client/`) | Desenvolvimento do `admin_client.py` (Unicast TCP) para envio estruturado de comandos do administrador. | | X |
| Terminal do Torcedor (`src/client/`) | Desenvolvimento do `viewer_client.py` com interface local e thread em segundo plano ouvindo UDP Multicast. | X | |
| Massa de Testes (`data/`) | Criação de scripts locais para leitura e escrita em arquivos `.csv` e arquivos de teste para validar o InputStream. | | X |
| Integração Final | Testes de concorrência com múltiplos torcedores conectados de forma simultânea e polimento do repositório. | X | X |

---

## Tecnologias e Conceitos Utilizados

* **Linguagem:** Python 3.x (com uso estrito de *Type Hints* e propriedades abstratas).
* **Comunicação Unicast (TCP):** Utilizado para conexões estáveis, controle de fluxo e envio de requisições estruturadas (Requests/Replies) entre o Administrador e o Servidor.
* **Comunicação Multicast (UDP):** Utilizado para a difusão assíncrona e eficiente de notificações em tempo real para múltiplos clientes simultâneos através do IP Classe D (230.0.0.1).
* **Multithreading Coordenado:** Implementação de múltiplas threads no Servidor (para conexões TCP concorrentes controladas via `threading.RLock`) e no Cliente (uma thread para interface do usuário e outra dedicada a escutar o canal UDP).
* **External Data Representation (Serialization):** Empacotamento manual e conversão dos objetos de dados em payloads estruturados em JSON para a rede e strings delimitadas em formato CSV para persistência física.
* **Padrões de Projeto (Factory Method):** Centralização da lógica de instanciação dinâmica de subclasses (`GoalEvent`, `CardEvent`) com base no tipo do registro de entrada na camada de serviços.

---

## Estrutura de Classes

### Classes de Dados Polimórficas (`src/shared/models/`)
* **`BaseMatchEvent`**: Classe abstrata pura que define o contrato de interface de propriedades e o método comum de formatação textual `build_message()`.
* **`MatchEvent`**: Subclasse base que representa um acontecimento genérico no jogo (ex: END), gerenciando atributos como `event_id`, `match_id`, `event_type` e `description`.
* **`GoalEvent`**: Subclasse especializada para gols, gerenciando de forma encapsulada o atributo específico `team`.
* **`CardEvent`**: Subclasse especializada para advertências, gerenciando de forma encapsulada o atributo específico `player`.
* **`Match`**: Representa uma partida de futebol ativa, contendo metadados das equipes e o estado do placar em tempo real (`home_score` e `away_score`).

### Sockets e Streams Customizados (`src/shared/streams/`)
* **`MatchEventOutputStream`**: Abstração que recebe uma coleção de objetos derivados de `MatchEvent`, converte sua estrutura interna para linhas CSV delimitadas e escreve o resultado no destino configurado.
* **`MatchEventInputStream`**: Abstração complementar responsável por ler fluxos de bytes brutos vindo de uma origem e reconstruir as linhas do formato CSV em memória.

---

## Estrutura de Diretórios

A organização das pastas do projeto separa as responsabilidades explicitamente entre o ambiente do servidor, as aplicações dos clientes e a pirâmide de testes completa conforme a árvore real mapeada pelo sistema:

```bash
.
├── docs/
│   └── MANUAL_TEST.md
├── README.md
├── src/
│   ├── client/
│   │   ├── admin_client.py
│   │   ├── __init__.py
│   │   └── viewer_client.py
│   ├── data/
│   │   ├── event.csv
│   │   └── event_test.csv
│   ├── __init__.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── main_server.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── match_service.py
│   │       └── notify_service.py
│   └── shared/
│       ├── base_multicast_endpoint.py
│       ├── base_network_client.py
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── match_event.py
│       │   └── match.py
│       └── streams/
│           ├── event_input.py
│           ├── event_output.py
│           └── __init__.py
└── tests/
    ├── e2e/
    │   ├── __init__.py
    │   ├── main_e2e.py
    │   └── test_main_server.py
    ├── __init__.py
    ├── integration/
    │   ├── __init__.py
    │   ├── main_integration.py
    │   ├── test_admin_client.py
    │   ├── test_services.py
    │   ├── test_streams.py
    │   └── test_viewer_client.py
    └── unit/
        ├── event_input_test.py
        ├── event_output_test.py
        ├── __init__.py
        ├── main_unit.py
        ├── test_match_service.py
        └── test_notify_service.py
```

---

## Como Executar o Projeto de Forma Manual

Para inicializar a topologia de rede local (Servidor Central, Painel Administrativo TCP e múltiplos Terminais de Torcedores UDP Multicast), siga o guia passo a passo detalhado no arquivo complementar de instruções:

**[Clique aqui para abrir o manual de testes passo a passo](./docs/MANUAL_TEST.md)**

---

## Suíte de Testes Automatizados

O sistema foi blindado contra falhas de concorrência e regressões usando uma pirâmide completa de testes baseada no framework nativo `unittest` do Python. Certifique-se de executar todos os comandos **a partir do diretório raiz do projeto** (`tr-1`).

### 1. Testes de Unidade (`tests/unit/`)
Validações de lógica isolada sem dependência de rede, englobando serialização CSV, tipagem estrita de payloads e funcionamento polimórfico das subclasses de evento.
```bash
python3 -m tests.unit.main_unit
```

### 2. Testes de Integração (`tests/integration/`)
Valida o acoplamento de componentes, cobrindo o comportamento thread-safe do `MatchService`, fragmentação de fluxos TCP e decodificação do canal UDP Multicast.
```bash
python3 -m tests.integration.main_integration
```

### 3. Testes de Ponta a Ponta / End-to-End (`tests/e2e/`)
Abre sockets reais de sistema operacional utilizando portas efêmeras alocadas dinamicamente pelo kernel para orquestrar fluxos concorrentes completos entre múltiplos clientes simulados.
```bash
python3 -m tests.e2e.main_e2e
```

### 4. Execução de Todos os Testes Simultaneamente
Para disparar a descoberta automatizada de todos os cenários da suíte de uma única vez:
```bash
python3 -m unittest discover -s tests -p "*.py" -v
```

---

## Formato dos Registros de Eventos (CSV)

Sempre que um novo evento relevante é processado pelo servidor, as classes de stream realizam a serialização e persistem os dados no arquivo `src/data/event_test.csv` utilizando o seguinte formato padronizado:

```csv
1,10,GOL,Gol de cabeca após cruzamento,Ceara
2,10,CARD,Cartao amarelo por falta dura,Fortaleza
3,10,END,Fim do segundo tempo,
```

*(Estrutura posicional dos campos: ID do Evento, ID da Partida, Tipo do Evento, Descrição do Evento e Contexto Específico - Nome do Time ou do Jogador).*

---

## Observações Acadêmicas

Este projeto possui finalidade estritamente acadêmica e foi desenvolvido com o objetivo de consolidar de forma prática os conceitos de chamadas remotas, sincronização de threads, concorrência distribuída e representation externa de dados ministrados na disciplina de Sistemas Distribuídos.
