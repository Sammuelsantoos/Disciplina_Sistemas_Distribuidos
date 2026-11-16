# Guia de Execução Manual do Sistema (Trabalho 3)

Este guia descreve os procedimentos de validação do sistema distribuído baseado na arquitetura **Publicar/Assinar (Pub/Sub)** em Python com sockets TCP, aplicado ao monitoramento de partidas de futebol em tempo real, com persistência de eventos em arquivo CSV e suporte a entrega retroativa.

---

## Pré-requisitos

- Python 3.10 ou superior instalado.
- Terminais abertos na pasta raiz `tr-3`.
- Para iniciar um teste limpo do zero (opcional):
  ```bash
  fuser -k 5000/tcp 2>/dev/null; rm -f src/data/event.csv
  ```

---

## Cenário 1: Fluxo Completo em Tempo Real e Desacoplamento Espacial

Este teste comprova que o produtor (`admin_client`) envia eventos sem conhecer o IP/porta dos consumidores (`viewer_client`), comunicando-se exclusivamente via tópico no Broker.

### 1. Iniciar o Servidor Broker (Terminal 1)

```bash
cd ~/Documentos/github-projects/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.server.main_server
```

Saída esperada:
```text
Servidor Broker Pub/Sub escutando em 127.0.0.1:5000...
```

### 2. Iniciar um ou mais Clientes Espectadores (Terminal 2)

```bash
cd ~/Documentos/github-projects/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.client.viewer_client
```

*(Dica: abra um segundo espectador em outra aba para validar múltiplos assinantes simultâneos).*

Saída esperada:
```text
Conectado ao Broker (127.0.0.1:5000). Tópico: 'match.events'
[BROKER] Inscrição confirmada (SUBSCRIBED)
```

### 3. Operar o Painel Administrativo (Terminal 3)

```bash
cd ~/Documentos/github-projects/Disciplina_Sistemas_Distribuidos/tr-3
python3 -m src.client.admin_client
```

Execute as ações abaixo no menu interativo:

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

4. **Validar consultas síncronas:**
   - **Opção `3` (ID `1`):** Exibe `Placar (Jogo 1): Flamengo 1 x 0 Vasco`.
   - **Opção `4` (ID `1`):** Lista os eventos `[GOL]` e `[CARD]` registrados.
   - **Opção `5`:** Lista todas as partidas cadastradas em memória.

5. **Encerrar partida (Opção `2`):**
   - **ID da partida:** `1`
   - **Tipo:** `END`
   - **Descrição:** `Fim de jogo`

### Verificação Esperada no Terminal do Espectador (`viewer_client`):

```text
Partida cadastrada: [1] Flamengo x Vasco
[GOL] [1] Flamengo 1 x 0 Vasco - Pedro marcou aos 15'
[CARD] [1] Flamengo 1 x 0 Vasco - Cartão amarelo para Vegetti
[END] [1] Flamengo 1 x 0 Vasco - Fim de jogo
```

---

## Cenário 2: Prova de Desacoplamento Temporal (Assinante Offline)

Este teste comprova que produtor e consumidor possuem tempos de vida independentes: eventos publicados enquanto o espectador está desligado são armazenados pelo Broker e entregues assim que ele se conecta.

1. Certifique-se de que **nenhum `viewer_client` esteja em execução** (encerre-os com `Ctrl + C`).
2. Com o `main_server` (Terminal 1) e o `admin_client` (Terminal 3) ativos, cadastre uma nova partida (ex: **ID `2`**, `Botafogo` x `Fluminense`) e registre um gol (`GOL`).
3. Após publicar o evento, abra o espectador no **Terminal 2**:
   ```bash
   python3 -m src.client.viewer_client
   ```
4. **Verificação esperada:** Logo após a mensagem `[BROKER] Inscrição confirmada (SUBSCRIBED)`, o espectador receberá automaticamente o histórico acumulado, exibindo a partida `2` e o gol ocorrido enquanto estava offline.

---

## Cenário 3: Persistência em Disco (`event.csv`) e Recuperação

1. No **Terminal 1**, encerre o servidor Broker com `Ctrl + C`.
2. Verifique no terminal se o arquivo CSV foi gerado e contém os lances:
   ```bash
   cat src/data/event.csv
   ```
3. Inicie o servidor novamente (`python3 -m src.server.main_server`) e conecte um novo `viewer_client` ou consulte a **Opção `4`** no `admin_client` para confirmar que o histórico persistido foi recarregado do disco.

---

## Problemas Comuns

- **`ModuleNotFoundError`:** Certifique-se de executar os comandos a partir da pasta raiz `tr-3` (um nível acima de `src/`).
- **`ConnectionRefusedError`:** Verifique se o `main_server.py` já está rodando antes de iniciar o `viewer_client.py` ou `admin_client.py`.
- **`Address already in use`:** Caso a porta `5000` esteja ocupada por uma execução anterior, libere-a no Ubuntu com `fuser -k 5000/tcp` ou inicie o servidor em outra porta usando `--port 5001`.
