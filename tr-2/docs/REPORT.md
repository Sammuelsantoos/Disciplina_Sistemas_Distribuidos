# Relatório Técnico – Trabalho 2

## 1. Introdução

Este trabalho teve como objetivo desenvolver uma solução distribuída de monitoramento esportivo utilizando o paradigma de Remote Procedure Call (RPC), com um servidor central responsável por manter o estado das partidas, processar eventos e responder consultas dos clientes de forma síncrona e segura.

A proposta foi aplicada em um sistema que simula uma central esportiva, onde administradores registram partidas e eventos, enquanto torcedores consultam o placar e o histórico de lances. A arquitetura foi organizada para separar claramente as camadas de comunicação, regras de negócio e modelos de domínio, promovendo um código mais legível, reutilizável e mais próximo do que se espera em sistemas distribuídos reais.

---

## 2. Objetivo do Sistema

O sistema implementado permite que um administrador cadastre novas partidas, registre eventos relevantes do jogo e consulte o estado do campeonato em memória. Já o cliente torcedor pode consultar o placar atual e o histórico de eventos do confronto. A aplicação foi desenhada para tratar esse fluxo por meio de chamadas remotas estruturadas, sem expor detalhes de rede diretamente para as regras de negócio.

---

## 3. Arquitetura Geral

A solução foi organizada em camadas bem definidas:

- Camada de infraestrutura: responsável pelo protocolo de requisição-resposta e pela referência lógica ao objeto remoto.
- Camada de servidor: centraliza a execução das operações recebidas e coordena o acesso ao serviço de partidas.
- Camada de domínio: modela as entidades principais do sistema, como partidas e eventos esportivos.
- Camada de cliente: representa os usuários do sistema, tanto administrativos quanto de visualização.

Essa organização permite que o cliente interaja com um objeto remoto sem conhecer detalhes internos do servidor, mantendo a lógica de negócios isolada do transporte de mensagens.

---

## 4. Protocolo de Comunicação e RPC

A comunicação entre cliente e servidor foi implementada com base em uma estrutura de mensagens contendo campos como identificador da requisição, referência do objeto remoto, nome do método e argumentos serializados em JSON.

Esse modelo atende ao conceito de Requisição-Resposta manual e ao estilo de RPC síncrono, em que a chamada do cliente fica bloqueada até que o servidor responda com o resultado do processamento. Além disso, a serialização em JSON torna o tráfego de dados portável e compreensível entre diferentes componentes da aplicação.

A infraestrutura do protocolo está centralizada em [tr-2/src/shared/infra/protocol.py](src/shared/infra/protocol.py), enquanto a lógica do servidor que despacha as operações está em [tr-2/src/server/main_server.py](src/server/main_server.py).

---

## 5. Modelagem de Domínio

### 5.1 Classe Match

A classe Match representa uma partida de futebol e armazena informações relevantes sobre o confronto, como os nomes dos times e o placar atual. Esse objeto é o núcleo do estado do jogo e serve como unidade principal de organização de uma partida.

### 5.2 Classe BaseMatchEvent

A classe BaseMatchEvent funciona como contrato base para todos os eventos esportivos. Ela define a estrutura comum esperada para operações como geração de mensagem textual e representação padronizada do evento.

### 5.3 Classes GoalEvent e CardEvent

As subclasses GoalEvent e CardEvent estendem a classe base e acrescentam atributos específicos para o contexto do evento. Isso demonstra a aplicação de herança e especialização dentro do domínio do problema, respeitando a ideia de que eventos diferentes possuem informações particulares, mas compartilham uma estrutura comum.

Essas entidades estão definidas em [tr-2/src/shared/models/match_event.py](src/shared/models/match_event.py) e [tr-2/src/shared/models/match.py](src/shared/models/match.py).

---

## 6. Agregações e Relações entre Objetos

### 6.1 Agregação de eventos na partida

A ideia da composição “tem-um” é representada pelo fato de que uma partida pode conter vários eventos ao longo do jogo. A implementação da solução centraliza esse histórico no serviço de partidas, que mantém uma estrutura de eventos associada a cada jogo.

Essa abordagem está em linha com a proposta da atividade, embora a estrutura de dados específica não esteja diretamente dentro da classe Match, mas sim na camada de serviço que gerencia todas as partidas e os eventos vinculados a elas. Essa diferença é pequena em termos funcionais, mas vale ser observada como um ponto de arquitetura.

### 6.2 Agregação de partidas no serviço

A classe MatchService é responsável por manter um dicionário interno com todas as partidas em memória. Isso permite que o servidor organize de forma eficiente o estado do campeonato, acessando e atualizando partidas por identificador. Esse relacionamento é importante para garantir que cada partida tenha um controle individual e que o sistema possa atender múltiplas consultas simultâneas.

A implementação dessa camada pode ser observada em [tr-2/src/server/services/match_service.py](src/server/services/match_service.py).

---

## 7. Operações RPC Implementadas

O sistema expõe operações que representam ações de negócio legítimas do domínio esportivo. As principais operações implementadas são:

1. create_match: cria uma nova partida com dois times e registra o confronto em memória.
2. register_event: registra um evento esportivo, como gol ou cartão, e atualiza o placar quando necessário.
3. get_score: retorna o placar atual de uma partida em formato legível.
4. get_events: devolve o histórico dos lances de uma determinada partida.

Essas operações estão integradas ao despachante do servidor em [tr-2/src/server/main_server.py](src/server/main_server.py), e os clientes que as invocam estão em [tr-2/src/client/admin_client.py](src/client/admin_client.py) e [tr-2/src/client/viewer_client.py](src/client/viewer_client.py).

---

## 8. Sincronização e Concorrência

Como o sistema pode atender múltiplos clientes ao mesmo tempo, houve necessidade de controlar o acesso concorrente ao estado interno do servidor. Para isso, foi utilizado um lock de thread, garantindo que as operações de escrita em memória sejam executadas de forma atômica.

Essa medida é relevante porque evita inconsistências e condições de corrida na atualização do placar e no registro de eventos simultâneos. O uso de sincronização reforça a robustez do servidor e mostra uma preocupação real com a consistência de dados em ambientes compartilhados.

---

## 9. Avaliação do Atendimento ao Requisito da Atividade

### Resultado geral

O trabalho atende, de forma clara, à maioria dos requisitos esperados para a atividade:

- protocolo de requisição-resposta implementado;
- uso de JSON como representação externa de dados;
- arquitetura RPC com referência remota;
- operações de negócio representando chamadas remotas legítimas;
- uso de threading para sincronização;
- modelagem orientada a objetos com herança e especialização;
- separação entre clientes, protocolo e servidor.


## 10. Conclusão

O Trabalho 2 cumpriu de forma satisfatória os objetivos propostos pelo docente: demonstrou a aplicação prática de um protocolo de comunicação distribuída baseado em RPC, a organização de um sistema orientado a objetos em camadas, o uso de serialização e a sincronização de acesso concorrente.

O sistema conseguiu abstrair as responsabilidades de rede e concentrar as regras de negócio em componentes bem definidos, mantendo o código coerente e funcional. Mesmo com um ponto de ajuste de modelagem relacionado à agregação explícita de eventos dentro da classe Match, a aplicação atende ao espírito da atividade e entrega um resultado sólido, funcional e alinhado com os conceitos ensinados na disciplina.

---

