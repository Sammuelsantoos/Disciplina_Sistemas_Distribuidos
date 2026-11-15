# Guia de Execução Manual do Sistema (Trabalho 3)

Este guia descreve a execução do exemplo de RPC em Python com sockets, adaptado para um cenário de futebol, com eventos do jogo sendo enviados e processados em tempo real.

---

## Pré-requisitos

- Python 3 instalado.
- Terminal aberto na pasta `tr-3`.

---

## Passo 1: Iniciar o servidor

```bash
cd /home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.server.main_server
```

O servidor ficará aguardando conexão na porta `5000`.

---

## Passo 2: Executar o cliente

Em outro terminal:

```bash
cd /home/smmy/sd/atividades_sd/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.client.client --team Flamengo --event-type gol --minute "13'"
```

O cliente envia a requisição:

```text
publishEvent:Flamengo|gol|13'
```

---

## Verificação esperada

No terminal do servidor, a mensagem esperada é:

```text
Requisição recebida: publishEvent:Flamengo|gol|13'
```

No terminal do cliente, a resposta esperada é:

```text
Requisição enviada: publishEvent:Flamengo|gol|13'
Resposta do servidor: Evento de futebol: Flamengo marcou gol aos 13'.
```

---

## Problemas comuns

- `ModuleNotFoundError`: verificar se o comando foi executado na pasta `tr-3`.
- `Connection refused`: confirmar que o servidor está em execução antes de abrir o cliente.
- `Address already in use`: aguardar ou trocar a porta de execução, se necessário.
