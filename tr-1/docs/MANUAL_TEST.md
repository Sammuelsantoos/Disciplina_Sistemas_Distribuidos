# Guia de Execução Manual do Sistema

Este guia orienta o passo a passo para inicializar e validar a comunicação de rede ponta a ponta do **Sistema de Notificações de Esportes** usando múltiplos terminais locais.

Para evitar erros de caminhos de módulos, todas as execuções utilizam a flag `-m` do Python a partir da raiz do projeto.

---

## Pré-requisitos
* Abra os terminais sempre **no diretório raiz do projeto** (`tr-1`).
* Não é necessária a instalação de nenhuma biblioteca externa.

---

## Fluxo de Execução (Passo a Passo)

Para ver o Multicast funcionando em tempo real, o ideal é abrir pelo menos **3 abas ou janelas de terminal** diferentes.

### Passo 1: Iniciar o Servidor Central (Terminal 1)
O servidor abrirá uma porta TCP (`5000`) para comandos e preparará o canal de transmissão UDP Multicast (`230.0.0.1:6000`).

* **No Linux / macOS:**
  ```bash
  python3 -m src.server.main_server
  ```
* **No Windows:**
  ```cmd
  python -m src.server.main_server
  ```
* **O que esperar:** O terminal exibirá mensagens informando que as conexões TCP e o módulo Multicast estão ativos e prontos.

---

### Passo 2: Iniciar o Cliente Torcedor / Viewer (Terminal 2)
Este cliente entra imediatamente no canal de transmissão de dados via rede para escutar os alertas. Você pode abrir mais de um terminal com este comando para simular vários torcedores ao mesmo tempo.

* **No Linux / macOS:**
  ```bash
  python3 -m src.client.viewer_client
  ```
* **No Windows:**
  ```cmd
  python -m src.client.viewer_client
  ```
* **O que esperar:** Uma mensagem de boas-vindas será exibida informando a conexão ao canal de transmissão.

---

### Passo 3: Iniciar o Painel de Controle / Admin (Terminal 3)
Este terminal permite que você interaja enviando comandos reais de criação de partidas e eventos para o servidor via TCP.

* **No Linux / macOS:**
  ```bash
  python3 -m src.client.admin_client
  ```
* **No Windows:**
  ```cmd
  python -m src.client.admin_client
  ```

---

## Cenário de Teste Prático

Com os 3 terminais rodando de forma simultânea, faça as seguintes ações no **Terminal do Administrador (Terminal 3)** para validar o sistema:

1. **Cadastrar Partida:**
   * Escolha a opção `1`.
   * Insira o ID da partida (ex: `10`).
   * Escolha o time mandante (ex: `Ceara`).
   * Escolha o time visitante (ex: `Fortaleza`).
   * *Verificação:* O **Terminal do Torcedor (Terminal 2)** deve exibir instantaneamente um alerta de `[TRANSMISSAO AO VIVO - NOTIFICACAO]` informando que uma nova partida foi iniciada.

2. **Registrar um Gol:**
   * Escolha a opção `2`.
   * Defina o tipo como `GOL`.
   * Digite o time envolvido (ex: `Ceara`).
   * Insira o ID do evento (ex: `1`).
   * Insira o ID da partida criada (ex: `10`).
   * Adicione uma descrição (ex: `Gol de cabeca após cruzamento`).
   * *Verificação:* O **Terminal do Torcedor (Terminal 2)** receberá um alerta imediato de `[TRANSMISSAO AO VIVO - ALERTA]` mostrando o placar atualizado em tempo real: `Ceara 1 x 0 Fortaleza`.

3. **Verificar o Histórico Persistido:**
   * No **Terminal do Servidor (Terminal 1)**, observe as mensagens de log confirmando que os dados foram registrados em memória e processados corretamente.

---

## Resolução de Problemas Comuns

* **Address already in use (Erro 98 / Erro 10048):** Se o servidor fechar inesperadamente e você tentar abri-lo logo em seguida, o sistema operacional pode demorar alguns segundos para liberar a porta `5000`. Aguarde um momento e tente novamente.
* **Torcedor não recebe mensagens:** Certifique-se de que os clientes torcedores foram iniciados *antes* de você disparar os eventos no painel administrativo, já que o protocolo UDP não garante a entrega de pacotes enviados no passado.
