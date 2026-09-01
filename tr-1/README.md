# Sistema de Notificações de Esportes

Este projeto consiste em um **Sistema Distribuído de Notificação de Esportes em Tempo Real** desenvolvido em **Python** para a disciplina de Sistemas Distribuídos da Universidade Federal do Ceará (UFC) – Campus Quixadá.

O sistema simula uma central esportiva onde administradores registram partidas e eventos (gols, cartões, fim de jogo) via **Sockets TCP**, e múltiplos clientes (torcedores) recebem atualizações instantâneas via **Sockets UDP Multicast**.

---

## Autores
1. Rubens Rabelo - SI - 555497
2. Samuel Augusto - ES - 601930

---

## Tecnologias e Conceitos Utilizados

* **Linguagem:** Python 3.x
* **Comunicação Unicast (TCP):** Utilizado para autenticação de clientes, conexões estáveis e envio de requisições estruturadas (Requests/Replies).
* **Comunicação Multicast (UDP):** Utilizado para a difusão eficiente de notificações em tempo real para múltiplos clientes simultâneos através do IP Classe D (230.0.0.1).
* **Multithreading:** Implementação de múltiplas threads no Servidor (para conexões concorrentes) e no Cliente (uma thread para interface do usuário e outra dedicada a escutar o canal UDP).
* **External Data Representation (Serialization):** Empacotamento manual e conversão dos objetos de dados em strings formatadas em JSON antes do envio pela rede.
* **Persistência de Dados (CSV):** Armazenamento estruturado de fluxos de eventos históricos em formato de texto delimitado para leitura e escrita baseada em streams.

---

## Estrutura de Classes (POJOs e Serviços)

### Classes de Dados (POJOs)
* **`Match`**: Representa uma partida de futebol, contendo `match_id`, `home_team`, `away_team`, `home_score` e `away_score`.
* **`MatchEvent`**: Representa um acontecimento no jogo, contendo `event_id`, `match_id`, `event_type` (GOL, CARD, END), `description` e `timestamp`.

### Sockets e Streams Customizados
Para atender aos requisitos de acesso e abstração de Streams, criamos componentes de codificação de baixo nível:
* **`MatchEventOutputStream`**: Abstração que recebe uma coleção de objetos `MatchEvent`, converte sua estrutura para um fluxo binário/JSON ou linhas CSV delimitadas e escreve o resultado no destino configurado (Terminal, Arquivo CSV ou Socket TCP).
* **`MatchEventInputStream`**: Abstração complementar responsável por ler fluxos de bytes e linhas vindos de uma origem (Teclado, Arquivo CSV ou Conexão TCP) e reconstruir os objetos `MatchEvent`.

---

## Estrutura de Diretórios

A organização das pastas do projeto separa as responsabilidades explicitamente entre o ambiente do servidor e as aplicações dos clientes:

```bash
live-sports-system/
│
├── src/
│   ├── __init__.py
│   │
│   ├── shared/                  # Componentes comuns compartilhados
│   │   ├── __init__.py
│   │   ├── models/              # Classes de Dados (POJOs)
│   │   │   ├── __init__.py
│   │   │   ├── match.py         # Classe Match
│   │   │   └── match_event.py   # Classe MatchEvent
│   │   │
│   │   └── streams/             # Abstrações de Input/Output Streams
│   │       ├── __init__.py
│   │       ├── event_input.py   # Classe MatchEventInputStream
│   │       └── event_output.py  # Classe MatchEventOutputStream
│   │
│   ├── server/                  # Módulos exclusivos do Servidor
│   │   ├── __init__.py
│   │   ├── services/            # Serviços lógicos e de rede do backend
│   │   │   ├── __init__.py
│   │   │   ├── match_service.py # Gerenciamento do placar e partidas
│   │   │   └── notify_service.py# Controle de disparo do Multicast UDP
│   │   └── main_server.py       # Servidor Central (TCP Multithread + UDP Multicast)
│   │
│   └── client/                  # Módulos exclusivos dos Clientes
│       ├── __init__.py
│       ├── admin_client.py      # Cliente Unicast TCP (Painel do Administrador)
│       └── viewer_client.py     # Cliente Multicast UDP (Terminal do Torcedor)
│
├── data/                        # Pasta para testes de persistência em arquivos estruturados
│   ├── input_test.csv           # Dados estruturados de origem para testes do InputStream
│   └── output_test.csv          # Destino de escrita estruturada para testes do OutputStream
│
└── README.md                    # Documentação do projeto
```

---

## Como Executar o Projeto

Certifique-se de ter o Python 3 instalado em sua máquina. Não são necessárias bibliotecas externas.

### 1. Iniciar o Servidor Central
O servidor gerencia o estado global das partidas, persiste os históricos em arquivos CSV, e lida com as requisições concorrentes TCP e transmissões UDP.
```bash
python src/server/main_server.py
```

### 2. Iniciar o Painel Administrativo (Client TCP)
Utilizado para registrar novas partidas e disparar eventos em tempo real.
```bash
python src/client/admin_client.py
```

### 3. Iniciar múltiplos Clientes Torcedores (Clients Multicast)
Você pode abrir múltiplos terminais para simular diferentes torcedores na rede recebendo notificações simultaneamente.
```bash
python src/client/viewer_client.py
```

---

## Formato das Mensagens de Notificação (JSON)

Sempre que um evento relevante acontece, o servidor empacota a informação e faz o envio Multicast no seguinte formato padronizado:

```json
{
  "type": "NOTIFICATION",
  "message": "GOAL! Flamengo 1 x 0 Vasco (42')",
  "timestamp": 1793542400
}
```

---

## Observações Acadêmicas

Os projetos contidos neste repositório possuem finalidade acadêmica e foram desenvolvidos para consolidar conhecimentos na disciplina de Sistemas Distribuídos.
