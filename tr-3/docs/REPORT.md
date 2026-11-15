# Relatório Técnico – Trabalho 3

## 1. Introdução

O Trabalho 3 foi implementado em Python com base no conceito do PDF de RPC sem RMI, mas adaptado para um cenário de eventos de futebol. A ideia central continua a mesma: cliente e servidor se comunicam por sockets TCP, e o servidor executa uma operação remota a partir de uma mensagem textual recebida.

---

## 2. Objetivo

Reproduzir em Python o exemplo de RPC por sockets em um contexto esportivo, mantendo a estrutura dos trabalhos anteriores e o mesmo fluxo de comunicação do material didático.

---

## 3. Arquitetura da solução

A aplicação foi organizada em módulos para manter clareza e alinhamento com a padronização do repositório:

- `src/server/services/football_service.py`: contém a interface e a implementação do serviço de futebol.
- `src/server/main_server.py`: recebe conexões e processa requisições.
- `src/client/client.py`: inicia a conexão e envia a mensagem do RPC.
- `src/shared/infra/protocol.py`: organiza a representação textual da chamada.

---

## 4. Fluxo de comunicação

1. O cliente abre uma conexão TCP com o servidor na porta `5000`.
2. O cliente envia a string `publishEvent:Flamengo|gol|13'`.
3. O servidor interpreta a mensagem e separa o time, o tipo do evento e o minuto.
4. O servidor chama a implementação do serviço.
5. A resposta é enviada de volta ao cliente.

Esse fluxo mantém o modelo do PDF, porém em Python e com um contexto de eventos de futebol.

---

## 5. Resultado obtido

Quando o cliente envia a requisição, o servidor retorna:

```text
Evento de futebol: Flamengo marcou gol aos 13'.
```

Essa resposta confirma a funcionalidade do RPC simples e prova que a comunicação entre cliente e servidor está correta.

---

## 6. Conclusão

A implementação do Trabalho 3 atende ao objetivo do PDF, mas foi convertida para Python com um contexto de futebol, preservando a lógica do exemplo e a organização dos projetos anteriores da disciplina.

