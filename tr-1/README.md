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
| Lógica do Servidor (`src/server/services/`) | Gerenciamento interno do placar das partidas em memória no arquivo `match_service.py`. | | X |
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
* **External Data Representation (Serialization):** Empacotamento manual e conversão dos objetos de dados em strings formatadas in JSON antes do envio pela rede.
* **Persistência de Dados (CSV):** Armazenamento estruturado de fluxos de eventos históricos em formato de texto delimitado para leitura e escrita baseada em streams.

---

## Estrutura de Classes

### Classes de Dados
* **`Match`**: Representa uma partida de futebol, contendo `match_id`, `home_team`, `away_team`, `home_score` e `away_score`.
* **`MatchEvent`**: Representa um acontecimento no jogo, contendo `event_id`, `match_id`, `event_type` (GOL, CARD, END), `description` e `timestamp`.

### Sockets e Streams Customizados
Para atender aos requisitos de acesso e abstração de Streams, criamos componentes de codificação de baixo nível:
* **`MatchEventOutputStream`**: Abstração que recebe uma coleção de objetos `MatchEvent`, converte sua estrutura para um fluxo binário/JSON ou linhas CSV delimitadas e escreve o resultado no destino configurado (Terminal, Arquivo CSV ou Socket TCP).
* **`MatchEventInputStream`**: Abstração complementar responsável por ler fluxos de bytes e linhas vindos de uma origem (Teclado, Arquivo CSV ou Conexão TCP) e reconstruir os objetos `MatchEvent`.

---

## Estrutura de Diretórios

A organização das pastas do projeto separa as responsabilidades explicitamente entre o ambiente do servidor, as aplicações dos clientes e a pirâmide de testes completa:

```bash
live-sports-system/
│
├── src/
│   ├── __init__.py
│   ├── shared/                     # Componentes comuns compartilhados
│   │   ├── models/                 # Classes de Dados (Match, MatchEvent)
│   │   └── streams/                # Abstrações de Input/Output Streams
│   ├── server/                     # Módulos exclusivos do Servidor (main_server e services)
│   └── client/                     # Módulos exclusivos dos Clientes (admin e viewer)
│
├── data/                           # Pasta para persistência em arquivos estruturados
│   └── event_test.csv              # Massa compartilhada de dados de eventos
│
└── tests/                          # Suíte de Testes Automatizados e Manuais
    ├── unit/                       # Testes Unitários Isolados e Scripts Manuais
    ├── integration/                # Testes de Integração de Componentes e Redes
    └── e2e/                        # Testes de Ponta a Ponta com Sockets Reais
```

---

## Como Executar o Projeto de Forma Manual

Para inicializar a topologia de rede local (Servidor Central, Painel Administrativo TCP e múltiplos Terminais de Torcedores UDP Multicast), siga o guia passo a passo detalhado no arquivo complementar de instruções:

**[Clique aqui para abrir o MANUAL.md](./docs/MANUAL_TEST.md)**

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

---

## Formatos das Mensagens de Notificação (JSON)

Sempre que um evento relevante acontece, o servidor empacota a informação e faz o envio Multicast no seguinte formato padronizado:

```json
{
  "tipo": "GOL",
  "mensagem": "[GOL] Ceara 1 x 0 Fortaleza - Gol do mandante",
  "timestamp": 1793542400
}
```

---

## Observações Acadêmicas

Este projeto possui finalidade estritamente acadêmica e foi desenvolvido com o objetivo de consolidar os conhecimentos práticos adquiridos na disciplina de Sistemas Distribuídos.
