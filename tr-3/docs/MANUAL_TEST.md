# Guia de Execução Manual do Sistema (Trabalho 3)

Este guia descreve a execução do sistema distribuído baseado na arquitetura **Publicar/Assinar (Pub/Sub)** em Python com sockets TCP, aplicado ao monitoramento de partidas de futebol em tempo real, com persistência de eventos em arquivo CSV.

---

## Pré-requisitos

- Python 3.10 ou superior instalado.
- Três terminais abertos na pasta raiz `tr-3`.

---

## Passo 1: Iniciar o Servidor Broker

No primeiro terminal, acesse a pasta do projeto e inicie o servidor central (Broker):

```bash
cd ~/Documentos/github-projects/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.server.main_server
```

*(Opcional: é possível especificar `--host`, `--port` e `--storage`, por padrão `127.0.0.1:5000` e `src/data/event.csv`).*

O servidor ficará escutando conexões e exibirá:

```text
Servidor Broker Pub/Sub escutando em 127.0.0.1:5000...
```

---

## Passo 2: Iniciar o Cliente Espectador (Subscriber)

Em um segundo terminal, inicie o cliente assinante para acompanhar as notificações ao vivo no tópico `match.events`:

```bash
cd ~/Documentos/github-projects/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.client.viewer_client
```

*(Caso queira filtrar uma partida específica, utilize `--match-id 1` ou altere o tópico com `--topic`).*

A saída inicial esperada no terminal do espectador é:

```text
Conectado ao Broker (127.0.0.1:5000). Tópico: 'match.events'
[BROKER] Inscrição confirmada (SUBSCRIBED)
```

---

## Passo 3: Iniciar o Painel Administrativo (Publisher)

Em um terceiro terminal, abra o painel interativo de administração para cadastrar partidas, publicar lances e realizar consultas:

```bash
cd ~/Documentos/github-projects/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.client.admin_client
```

### Roteiro de Teste no Menu Interativo

1. **Cadastrar partida (Opção `1`):**
   - **ID da partida:** `1`
   - **Time mandante:** `Flamengo`
   - **Time visitante:** `Vasco`

2. **Registrar gol (Opção `2`):**
   - **ID da partida:** `1`
   - **Tipo:** `GOL`
   - **Time que marcou:** `Flamengo`
   - **Jogador que marcou:** `Pedro`
   - **Descrição:** `Pedro marcou aos 15'`

3. **Registrar cartão (Opção `2`):**
   - **ID da partida:** `1`
   - **Tipo:** `CARD`
   - **Time do jogador:** `Vasco`
   - **Jogador advertido:** `Vegetti`
   - **Descrição:** `Cartão amarelo para Vegetti`

4. **Realizar consultas síncronas:**
   - Utilize a **Opção `3`** para consultar o placar consolidado da partida `1`.
   - Utilize a **Opção `4`** para listar o histórico completo de eventos da partida `1`.
   - Utilize a **Opção `5`** para listar todas as partidas ativas.

5. **Encerrar partida (Opção `2`):**
   - **ID da partida:** `1`
   - **Tipo:** `END`
   - **Descrição:** `Fim de jogo`

---

## Verificação Esperada

### No terminal do Servidor Broker:
```text
Novo assinante no tópico 'match.events' (Total: 1)
Partida cadastrada: [1] Flamengo x Vasco
Evento salvo no CSV: [GOL] Pedro marcou aos 15'
Evento salvo no CSV: [CARD] Cartão amarelo para Vegetti
Evento salvo no CSV: [END] Fim de jogo
```

### No terminal do Cliente Espectador (`viewer_client`):
```text
Partida cadastrada: [1] Flamengo x Vasco
[GOL] [1] Flamengo 1 x 0 Vasco - Pedro marcou aos 15'
[CARD] [1] Flamengo 1 x 0 Vasco - Cartão amarelo para Vegetti
[END] [1] Flamengo 1 x 0 Vasco - Fim de jogo
```

### Persistência em Disco (`event.csv`):
Ao encerrar ou inspecionar o arquivo `src/data/event.csv`, os eventos registrados estarão persistidos linha a linha no formato CSV, permitindo que o Broker recarregue o histórico automaticamente caso seja reiniciado.

---

## Problemas Comuns

- **`ModuleNotFoundError`:** Certifique-se de executar os comandos a partir da pasta raiz `tr-3` (um nível acima de `src/`).
- **`ConnectionRefusedError`:** Verifique se o `main_server.py` já está rodando antes de iniciar o `viewer_client.py` ou `admin_client.py`.
- **`Address already in use`:** Caso a porta `5000` esteja ocupada por uma execução anterior, libere-a no Linux com `fuser -k 5000/tcp` ou inicie o servidor em outra porta usando `--port 5001`.
