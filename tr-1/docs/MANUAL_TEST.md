# Guia de Execução Manual do Sistema

Este guia orienta o passo a passo para inicializar e validar a comunicação de rede ponta a ponta do **Sistema de Notificações de Esportes** usando múltiplos terminais locais.

Para evitar erros de caminhos de módulos, todas as execuções utilizam a flag `-m` do Python a partir da raiz do projeto.

---

## Pré-requisitos
* Abra os terminais sempre **no diretório raiz do projeto** (`tr-1`).
* Não é necessária a instalação de nenhuma biblioteca externa.

---

## Fluxo de Execução (Passo a Passo)

Para ver o Multicast funcionando em tempo real, abra pelo menos **3 abas ou janelas de terminal** diferentes.

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

> **Importante:** Como o IP padrão do código está configurado para uma rede externa, você **deve passar o argumento `--host 127.0.0.1`** para forçar a conexão com o servidor local.

* **No Linux / macOS:**
  ```bash
  python3 -m src.client.admin_client --host 127.0.0.1
  ```
* **No Windows:**
  ```cmd
  python -m src.client.admin_client --host 127.0.0.1
  ```

---

## Parâmetros Principais de Configuração

Ao executar ou testar os módulos do sistema, você pode customizar o comportamento da rede utilizando os **3 parâmetros principais** aceitos via linha de comando:

* **`--host`**: Define o endereço IP do servidor central. É utilizado pelo servidor para indicar em qual interface escutar e pelos clientes TCP (Admin) para localizar o servidor na rede local.
  * *Exemplo de teste (Mudar host no Admin):*
    ```bash
    python3 -m src.client.admin_client --host 192.168.1.50
    ```
* **`--port`**: Define a porta lógica de comunicação de rede. Permite alterar as portas padrões tanto dos canais TCP quanto UDP caso a porta `5000` ou `6000` já estejam ocupadas.
  * *Exemplo de teste (Iniciar o Servidor em outra porta TCP):*
    ```bash
    python3 -m src.server.main_server --port 7000
    ```
  * *Exemplo de teste (Conectar o Admin nessa nova porta):*
    ```bash
    python3 -m src.client.admin_client --host 127.0.0.1 --port 7000
    ```
* **`--group`** (ou **`--multicast-group`**): Configura o endereço IP Classe D reservado para as transmissões de Multicast. Utilizado para isolar ou criar salas de transmissões diferentes na rede.
  * *Exemplo de teste (Iniciar o Servidor com outro grupo multicast):*
    ```bash
    python3 -m src.server.main_server --multicast-group 226.0.0.2
    ```
  * *Exemplo de teste (Fazer o Viewer escutar esse novo grupo):*
    ```bash
    python3 -m src.client.viewer_client --group 226.0.0.2
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

## Cenário de Teste Avançado (Portas e Grupos Customizados)

Para validar o funcionamento completo isolando os canais e modificando todas as configurações padrões de rede simultaneamente (Porta TCP para `7000`, Porta UDP Multicast para `8000` e Grupo para `226.0.0.2`), utilize os seguintes comandos em seus respectivos terminais:

### 1. Iniciar o Servidor Customizado (Terminal 1)
```bash
python3 -m src.server.main_server --port 7000 --multicast-group 226.0.0.2 --multicast-port 8000
```

### 2. Iniciar o Viewer Alinhado ao Novo Multicast (Terminal 2)
O Viewer não escuta o canal TCP, portanto precisa apenas sintonizar no novo endereço de grupo e porta UDP configurados no servidor:
```bash
python3 -m src.client.viewer_client --group 226.0.0.2 --port 8000
```

### 3. Iniciar o Admin Alinhado ao Novo Canal TCP (Terminal 3)
O Admin ignora o fluxo Multicast e conecta diretamente na nova porta TCP aberta pelo servidor:
```bash
python3 -m src.client.admin_client --host 127.0.0.1 --port 7000
```

---

## Resolução de Problemas Comuns

* **Address already in use (Erro 98 / Erro 10048):** Se o servidor fechar inesperadamente e você tentar abri-lo logo em seguida, o sistema operacional pode demorar alguns segundos para liberar a porta `5000`. Aguarde um momento e tente novamente.
* **Connection Refused (Conexão Recusada no Admin):** Certifique-se de que o servidor (Terminal 1) está rodando ativamente e que você incluiu explicitamente o argumento `--host 127.0.0.1` na inicialização do Admin.
* **Torcedor não recebe mensagens:** Certifique-se de que os clientes torcedores foram iniciados *antes* de você disparar os eventos no painel administrativo, já que o protocolo UDP não garante a entrega de pacotes enviados no passado.
