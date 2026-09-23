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
| Modelos Compartilhados (`src/shared/models/`) | Criação das classes POJO (`match.py` e `match_event.py`) com conversão para formato string. | X | |
| Streams de Saída (`src/shared/streams/`) | Desenvolvimento do gerador de fluxos de escrita estruturada em CSV e rede TCP (`event_output.py`). | X | |
| Streams de Entrada (`src/shared/streams/`) | Desenvolvimento do leitor de fluxos com buffer para reconstrução de dados via CSV e rede TCP (`event_input.py`). | | X |
| Servidor Principal (`src/server/`) | Arquitetura básica do socket TCP multithread concorrido do `main_server.py`. | X | |
| Lógica do Servidor (`src/server/services/`) | Gerenciamento do placar em memória e persistência/leitura do histórico através de streams CSV no arquivo `match_service.py`. | | X |
| Emissão de Notificações (`src/server/services/`) | Configuração do socket de envio UDP Multicast e formatação de alertas em JSON no arquivo `notify_service.py`. | X | |
| Painel de Controle (`src/client/`) | Desenvolvimento do `admin_client.py` (Unicast TCP) para envio estruturado de comandos do administrador. | | X |
| Terminal do Torcedor (`src/client/`) | Desenvolvimento do `viewer_client.py` com interface local e thread em segundo plano ouvindo UDP Multicast. | X | |
| Massa de Testes (`data/`) | Criação de scripts locais para leitura e escrita em arquivos `.csv` e arquivos de teste para validar o InputStream. | | X |
| Integração Final | Testes de concorrência com múltiplos torcedores conectados de forma simultânea e polimento do repositório. | X | X |

---

## Tecnologias e Conceitos Utilizados

* **Linguagem:** Python 3.x
* **Comunicação Unicast (TCP):** Utilizado para autenticação de clientes, conexões estáveis e envio de requisições estruturadas (Requests/Replies).
* **Comunicação Multicast (UDP):** Utilizado para a difusão eficiente de notificações em tempo real para múltiplos clientes simultâneos através do IP Classe D (230.0.0.1).
* **Multithreading:** Implementação de múltiplas threads no Servidor (para conexões concorrentes) e no Cliente (uma thread para interface do usuário e outra dedicada a escutar o canal UDP).
* **External Data Representation (Serialization):** Empacotamento manual e conversão dos objetos de dados em strings formatadas em JSON e strings delimitadas em formato CSV antes do envio ou escrita.
* **Persistência de Dados (CSV):** Armazenamento estruturado de fluxos de eventos históricos em formato de texto delimitado para leitura e escrita baseada em streams.

---

## Estrutura de Classes

### Classes de Dados
* **`Match`**: Representa uma partida de futebol, contendo `match_id`, `home_team`, `away_team`, `home_score` e `away_score`.
* **`MatchEvent`**: Representa um acontecimento no jogo, contendo `event_id`, `match_id`, `event_type` (GOL, CARD, END) e `description`.

### Sockets e Streams Customizados
Para atender aos requisitos de acesso e abração de Streams, criamos componentes de codificação de baixo nível:
* **`MatchEventOutputStream`**: Abstração que recebe uma coleção de objetos `MatchEvent`, converte sua estrutura para linhas CSV delimitadas e escreve o resultado no destino configurado (Terminal ou Arquivo CSV).
* **`MatchEventInputStream`**: Abstração complementar responsável por ler fluxos de bytes e linhas vindos de uma origem (Arquivo CSV) e reconstruir os objetos `MatchEvent`.

---

## Estrutura de Diretórios

A organização das pastas do projeto separa as responsabilidades explicitamente entre o ambiente do servidor, as aplicações dos clientes e a pirâmide de testes completa:

```bash
tr-1/
│
├── src/
│   ├── __init__.py
│   ├── shared/                     # Componentes comuns compartilhados
│   │   ├── models/                 # Classes de Dados (match, match_event)
│   │   └── streams/                # Abstrações de Input/Output Streams (event_input, event_output)
│   ├── server/                     # Módulos do Servidor (main_server)
│   │   └── services/               # Lógica interna (match_service, notify_service)
│   └── client/                     # Módulos dos Clientes (admin_client, viewer_client)
│
├── src/data/                       # Pasta para persistência em arquivos estruturados
│   └── event_test.csv              # Massa compartilhada de dados de eventos
│
└── tests/                          # Suíte de Testes Automatizados e Manuais
    ├── unit/                       # Testes Unitários Isolados
    ├── integration/                # Testes de Integração de Componentes e Redes
    └── e2e/                        # Testes de Ponta a Ponta com Sockets Reais
```

---

## Como Executar o Projeto de Forma Manual

Para inicializar a topologia de rede local (Servidor Central, Painel Administrativo TCP e múltiplos Terminais de Torcedores UDP Multicast), siga o guia passo a passo detalhado no arquivo complementar de instruções:

**[Clique aqui para abrir o README.md](./README.md)**

---

## Suíte de Testes Automatizados

O sistema foi blindado contra bugs e regressões usando uma pirâmide completa de testes baseada no framework nativo `unittest` do Python. Certifique-se de executar todos os comandos **a partir do diretório raiz do projeto** (`tr-1`).

### 1. Testes de Unidade (`tests/unit/`)
Validações de lógica isolada sem dependência de rede, englobando serialização CSV de modelos de dados e formatação estrita de payloads JSON.
```bash
python3 -m tests.unit.main_unit
```

### 2. Testes de Integração (`tests/integration/`)
Valida o acoplamento entre os componentes e buffers de rede, cobrindo concorrência thread-safe de dados, fragmentação de fluxos TCP e decodificação assíncrona UDP Multicast.
```bash
python3 -m tests.integration.main_integration
```

### 3. Testes de Ponta a Ponta / End-to-End (`tests/e2e/`)
Abre sockets reais de sistema operacional utilizando portas efêmeras dinâmicas alocadas pelo SO para orquestrar fluxos de requisição e resposta completos simulando múltiplos clientes.
```bash
python3 -m tests.e2e.main_e2e
```

### 4. Execução de Todos os Testes Simultaneamente
Para rodar a descoberta automatizada de todos os cenários da suíte de uma vez só:
```bash
python3 -m unittest discover -s tests -p "*.py" -v
```

---

## Formato dos Registros de Eventos (CSV)

Sempre que um novo evento relevante é processado pelo servidor, as classes de stream realizam a serialização e persistem os dados no arquivo `src/data/event_test.csv` utilizando o seguinte formato padronizado (delimitado por quebras de linha):

```csv
1,10,GOL,Gol de cabeca após cruzamento,Ceara
2,10,CARD,Cartao amarelo por falta dura,Fortaleza
3,10,END,Fim do segundo tempo,
```

*(Campos na ordem: ID do Evento, ID da Partida, Tipo do Evento, Descrição e Time envolvido).*

---

## Observações Acadêmicas

Este projeto possui finalidade estritamente acadêmica e foi desenvolvido com o objetivo de consolidar os conhecimentos práticos adquiridos na disciplina de Sistemas Distribuídos.
