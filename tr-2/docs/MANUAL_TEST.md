# Guia de Execução Manual do Sistema (Trabalho 2)

Este guia orienta o passo a passo para inicializar e validar a comunicação de rede ponta a ponta do **Sistema de Notificações de Esportes** utilizando chamadas síncronas via **RPC**.

Para evitar erros de caminhos de módulos, todas as execuções utilizam a flag `-m` do Python a partir da raiz do projeto.

---

## Pré-requisitos
* Abra os terminais sempre **no diretório raiz do projeto** (`tr-2`).
* Não é necessária a instalação de nenhuma biblioteca externa.

---

## Fluxo de Execução (Passo a Passo)

Para ver a comunicação baseada em consultas síncronas funcionando, abra **3 abas ou janelas de terminal** diferentes.

### Passo 1: Iniciar o Servidor Central (Terminal 1)
O servidor abrirá uma porta RPC (`5000`) para comandos e requisições síncronas através do barramento JSON.

* **No Linux / macOS:**
  ```bash
  python3 -m src.server.main_server
  ```
* **No Windows:**
  ```cmd
  python -m src.server.main_server
  ```
* **O que esperar:** O terminal exibirá uma mensagem informando que o servidor central RPC está escutando requisições na porta 5000.

---

### Passo 2: Iniciar o Cliente Torcedor / Viewer (Terminal 2)
Este cliente permite realizar consultas explícitas (*pull*) ao servidor para buscar placares e históricos de lances. Você deve passar a flag `--host localhost` para realizar os testes locais.

* **No Linux / macOS:**
  ```bash
  python3 -m src.client.viewer_client --host localhost
  ```
* **No Windows:**
  ```cmd
  python -m src.client.viewer_client --host localhost
  ```
* **O que esperar:** Uma mensagem de boas-vindas será exibida informando a conexão bem-sucedida ao canal de consulta RPC e o menu de opções.

---

### Passo 3: Iniciar o Painel de Controle / Admin (Terminal 3)
Este terminal permite enviar comandos de criação de partidas e eventos de jogo diretamente para a memória do processo do servidor através de chamadas RPC síncronas. Você deve passar a flag `--host localhost` para conectar localmente.

* **No Linux / macOS:**
  ```bash
  python3 -m src.client.admin_client --host localhost
  ```
* **No Windows:**
  ```cmd
  python -m src.client.admin_client --host localhost
  ```
* **O que esperar:** O terminal exibirá a confirmação de prontidão e o menu de cadastro.

---

## Parâmetros Principais de Configuração

Ao executar ou testar os módulos do sistema, você pode customizar o comportamento da rede utilizando os parâmetros de linha de comando aceitos:

* **`--host`**: Define o endereço IP ou hostname do servidor central RPC. É utilizado pelo servidor para indicar em qual interface escutar e pelos clientes para localizá-lo na rede.
  * *Exemplo de teste (Mudar host no Admin):*
    ```bash
    python3 -m src.client.admin_client --host localhost
    ```
* **`--port`**: Define a porta lógica de comunicação da chamada remota RPC. Permite alterar a porta padrão do barramento caso a porta `5000` já esteja ocupada.
  * *Exemplo de teste (Iniciar o Servidor em outra porta RPC):*
    ```bash
    python3 -m src.server.main_server --port 7000
    ```
  * *Exemplo de teste (Conectar o Admin nessa nova porta):*
    ```bash
    python3 -m src.client.admin_client --host localhost --port 7000
    ```

---

## Cenário de Teste Prático

Com os 3 terminais rodando de forma simultânea, faça as seguintes ações sequenciais para validar a arquitetura de Requisição-Resposta:

1. **Cadastrar Partida (Admin):**
   * No **Terminal 3**, escolha a opção `1`.
   * ID da partida: `1`
   * Time mandante: `C`
   * Time visitante: `F`
   * *Verificação:* O Admin receberá na hora a mensagem `SUCCESS: Partida cadastrada com sucesso`. No **Terminal 1 (Servidor)**, aparecerá o log confirmando o registro em memória: `Partida registrada em memória: C x F`.

2. **Listar Partidas Registradas (Torcedor):**
   * No **Terminal 2**, escolha a opção `1` (Listar todas as partidas).
   * *Verificação:* O torcedor fará uma requisição síncrona via RPC e listará o jogo criado: `Partida: C 0 x 0 F`.

3. **Registrar um Gol (Admin):**
   * No **Terminal 3**, escolha a opção `2`.
   * Tipo: `GOL`.
   * Time envolvido: `C`.
   * ID do evento: `1`.
   * ID da partida: `1`.
   * Descrição: `Gooooooooooooooooooooool de cabeça de Roberto Silva`.
   * *Verificação:* O Admin receberá o retorno imediato de sucesso no processamento do evento. No servidor, aparecerá o log do novo evento salvo.

4. **Consultar Histórico de Lances (Torcedor):**
   * No **Terminal 2**, escolha a opção `3` (Ver lances de uma partida).
   * Informe o ID da partida: `1`.
   * *Verificação:* O torcedor puxará do servidor e exibirá na tela o histórico completo do lance com sua descrição:
     ```text
     --- Histórico de Lances do Jogo ---
     [GOL] C - Gooooooooooooooooooooool de cabeça de Roberto Silva
     ```

---

## Resolução de Problemas Comuns

* **Address already in use:** Se você reiniciar o servidor rapidamente, o sistema operacional pode reter a porta por alguns instantes. Aguarde um momento ou inicie utilizando outra porta com a flag `--port`.
* **Fault 1 / AttributeError:** Se uma chamada de consulta estourar falha de atributo no console do cliente, certifique-se de que o servidor (`main_server.py`) foi atualizado corretamente para ler as propriedades nativas das entidades do seu modelo.
* **Torcedor não atualiza sozinho:** O sistema não utiliza mais Multicast ou transmissão empurrada de forma assíncrona. O comportamento atual exige que o torcedor execute manualmente as opções do menu para buscar os dados atualizados via Requisição-Resposta.
