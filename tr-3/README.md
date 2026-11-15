# Trabalho 3 – RPC em Python com Eventos de Futebol

Este projeto foi adaptado para o mesmo contexto dos trabalhos anteriores, mas com a ideia do PDF convertida para um cenário de futebol, com eventos do jogo sendo enviados por RPC em socket TCP.

A implementação mantém a lógica central do material: o cliente envia uma chamada remota em texto para o servidor, o servidor interpreta a mensagem, executa a operação e responde com o evento correspondente.

---

## Objetivo

Implementar um exemplo de Remote Procedure Call em Python para eventos esportivos, utilizando:

- serviço com contrato e implementação;
- servidor TCP escutando na porta `5000`;
- cliente TCP enviando o payload `publishEvent:Flamengo|gol|13'`;
- comunicação por strings simples em socket;
- estrutura organizada em módulos para manter o padrão do repositório.

---

## Estrutura do projeto

```bash
.
├── README.md
├── docs/
│   ├── MANUAL_TEST.md
│   └── REPORT.md
├── src/
│   ├── __init__.py
│   ├── client/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── main_server.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── football_service.py
│   │       └── hello_service.py
│   └── shared/
│       ├── __init__.py
│       └── infra/
│           ├── __init__.py
│           └── protocol.py
└── tests/
    └── unit/
        ├── __init__.py
        └── test_hello_service.py
```

---

## Componentes principais

- `FootballEventService`: contrato do serviço RPC.
- `FootballEventServiceImpl`: implementação concreta do método `publish_event`.
- `main_server.py`: recebe conexões e processa a solicitação remota.
- `client.py`: envia a requisição ao servidor e exibe a resposta.
- `protocol.py`: encapsula o formato simples da chamada e sua manipulação.

---

## Como executar

1. Abra um terminal na pasta `tr-3`.
2. Inicie o servidor:

```bash
python3 -m src.server.main_server
```

3. Em outro terminal, execute o cliente:

```bash
python3 -m src.client.client --team Flamengo --event-type gol --minute "13'"
```

A resposta esperada é:

```text
Requisição enviada: publishEvent:Flamengo|gol|13'
Resposta do servidor: Evento de futebol: Flamengo marcou gol aos 13'.
```

---

## Observações

O projeto continua mantendo o conceito do PDF, mas com um cenário mais próximo dos trabalhos anteriores da disciplina: mensagens de futebol e eventos de partida, representando o fluxo de um RPC simples em Python.
