# Relatório Acadêmico – Trabalho 3

## Comunicação Indireta em Sistemas Distribuídos: Modelo Publicar e Assinar

## 1. Introdução

Este trabalho foi desenvolvido com foco na comunicação indireta em sistemas distribuídos, seguindo a abordagem de publicar e assinar (publish/subscribe). A estrutura adotada diferencia-se da comunicação direta por chamada remota, pois produtores e consumidores não se conectam diretamente entre si. Em vez disso, ambos interagem por meio de um broker intermediário que recebe as publicações e encaminha as notificações para os assinantes interessados.

O cenário escolhido foi o de eventos esportivos de futebol. A ideia foi representar uma partida em que ações como gols, cartões e consultas ao placar são publicadas em um canal específico e distribuídas para clientes que se inscreveram nesse tópico. Esse modelo representa corretamente o desacoplamento predominante na comunicação indireta.

## 2. Objetivo do Trabalho

O objetivo principal foi implementar um sistema distribuído em Python para eventos esportivos, seguindo o paradigma publicar e assinar. A solução deveria demonstrar como uma entidade produtora envia eventos para um canal compartilhado enquanto diversas entidades consumidoras absorvem mensagens conforme o tópico em que se inscreveram.

Os requisitos esperados da solução incluem:
- publicação de eventos esportivos em um tópico;
- inscrição de clientes em tópicos de interesse;
- entrega de notificações assinadas;
- manutenção do estado da partida;
- consulta do placar e do histórico de eventos;
- uso de sockets TCP para comunicação em rede.

## 3. Fundamentação Teórica

A comunicação indireta é uma abordagem em que os componentes não se comunicam diretamente, mas por meio de um mediador. Esse mediador pode ser um broker, canal, fila ou serviço de distribuição. A principal vantagem é o desacoplamento entre produtores e consumidores, o que permite:
- desacoplamento espacial;
- desacoplamento temporal;
- desacoplamento de sincronização;
- maior escalabilidade e flexibilidade no sistema.

Na arquitetura publicar e assinar, o produtor publica uma mensagem em um tópico. Os consumidores assumem a responsabilidade de se inscrever nesse tópico para receber as notificações relevantes. Esse padrão é muito utilizado em sistemas de alertas, feeds de eventos, canais de atualização e plataformas de mensageria.

## 4. Arquitetura da Solução

A arquitetura adotada no projeto é composta por um broker central, que atua como ponto de distribuição de eventos, e por clientes que publicam ou assinam tópicos.

### 4.1 Componentes principais

- `AdminClient`: publica eventos relacionados à partida;
- `ViewerClient`: assina tópicos e recebe as notificações;
- `MatchEventBroker`: gerencia tópicos e encaminha mensagens;
- `EventBroker`: implementa a lógica de inscrição e publicação;
- `MatchService`: atualiza a lógica do placar e do histórico;
- `EventProtocol`: define o formato JSON das mensagens;
- `Match` e `MatchEvent`: representam o modelo de domínio da partida e dos eventos esportivos.

A arquitetura segue o fluxo:

Produtor → Broker → Tópico → Assinantes

## 5. Modelo de Domínio

O cenário esportivo foi representado por modelos específicos para facilitar a lógica de negócio e as notificações.

### 5.1 Partida
A classe `Match` representa a partida em progresso e contém o estado do jogo, incluindo o placar e o histórico de eventos.

### 5.2 Evento da partida
A classe `MatchEvent` encapsula informações como:
- tipo do evento (gol ou cartão);
- time envolvido;
- jogador envolvido;
- minuto da partida;
- descrição do evento.

Esses objetos permitem manter coerência entre o estado da partida e a fase de disseminação dos eventos para os assinantes.

## 6. Protocolo e Comunicação

A comunicação foi modelada em JSON com ações explícitas. O broker recebe mensagens do tipo:

- `SUBSCRIBE`: um cliente se inscreve em um tópico;
- `PUBLISH`: um produtor publica um evento no tópico;
- `NOTIFY`: o broker envia a notificação para os assinantes;
- `QUERY`: consulta do placar ou do histórico;
- `ACK`: confirmação do broker.

Exemplo de mensagem de publicação:

```json
{
  "action": "PUBLISH",
  "topic": "match.events",
  "payload": {
    "event_type": "gol",
    "team": "Flamengo",
    "player": "Pedro",
    "minute": "13'",
    "description": "Pedro marcou para Flamengo aos 13'."
  }
}
```

Quando a publicação entra no broker, a mensagem é disseminada para todos os clientes inscritos no tópico `match.events` usando o comando `NOTIFY`.

## 7. Serviços Implementados

### 7.1 MatchService
O `MatchService` foi implementado para controlar o estado da partida. Ele realiza operações como:
- registrar gol;
- registrar cartão;
- atualizar o placar;
- retornar histórico de eventos;
- manter o estado consistente para consultas.

### 7.2 EventBroker
O `EventBroker` atua como intermediário do sistema. Ele guarda as assinaturas por tópico e entrega as mensagens publicadas para os clientes que assinaram o canal correspondente.

### 7.3 Protocolo
O `EventProtocol` padroniza a troca de mensagens em JSON e permite que os clientes e o broker interpretem corretamente as operações de inscrição, publicação e resposta.

### 7.4 Clientes
O projeto contempla:
- `AdminClient`: responsável por publicar eventos da partida;
- `ViewerClient`: responsável por receber as notificações do tópico assinado.

## 8. Fluxo de Operação

O fluxo de execução do sistema foi definido da seguinte forma:

1. O cliente produtor envia uma mensagem de publicação para o broker.
2. O broker identifica o tópico e valida a ação.
3. O serviço de domínio atualiza o estado da partida.
4. O broker encaminha a mensagem para todos os assinantes daquele tópico.
5. Os clientes assinantes recebem a notificação e exibem o evento.
6. O histórico e o placar ficam disponíveis para consultas posteriores.

Esse processo exemplifica o modelo publicar e assinar, em que o produtor não precisa conhecer os consumidores e vice-versa.

## 9. Casos de Uso

Os principais cenários implementados foram:
- publicação de gol;
- publicação de cartão;
- assinatura em canal de eventos;
- recepção de notificações em tempo real;
- consulta do placar atual;
- consulta do histórico de eventos;
- atualização do estado da partida.

Esses cenários refletem o uso típico de uma aplicação de eventos esportivos em tempo real e demonstram a utilidade do padrão publicar e assinar.

## 10. Vantagens do Modelo Publicar e Assinar

A arquitetura escolhida oferece vantagens importantes em relação a comunicação direta:
- menor acoplamento entre módulos;
- múltiplos consumidores para um mesmo evento;
- maior escalabilidade para sistemas distribuídos;
- melhor suporte a notificações em tempo real;
- desacoplamento entre produtores e assinantes.

Essas vantagens são centrais para o trabalho e justificam a adoção da comunicação indireta como padrão de projeto.

## 11. Validação e Testes

A solução foi validada por testes automatizados em Python para verificar:
- funcionamento do broker;
- entrega de eventos para assinantes;
- atualização do placar;
- serialização e parsing das mensagens;
- consistência do fluxo de publicação e notificação.

A execução do conjunto de testes passou com sucesso, confirmando que o mecanismo de publicar e assinar está funcionando de forma coerente dentro da aplicação.

## 12. Resultados Obtidos

A implementação foi bem-sucedida e demonstrou, de forma prática, o funcionamento de uma arquitetura de comunicação indireta. O projeto mostrou que eventos esportivos podem ser publicados em um canal e recebidos por consumidores interessados, sem o acoplamento direto entre eles.

Essa abordagem está em conformidade com os princípios de comunicação indireta e corresponde ao paradigma que o trabalho 4 exige: publicar e assinar.

## 13. Conclusão

Este trabalho demonstrou a importância da comunicação indireta em sistemas distribuídos utilizando o paradigma publicar e assinar. Em vez de um modelo de comunicação direta e fortemente acoplado, a solução adotada separou produtores, broker e consumidores em um fluxo modular e flexível.

A temática de futebol foi útil para contextualizar o problema e permitir uma implementação didática de eventos em tempo real. O projeto mostrou-se coerente com o conceito acadêmico do trabalho, mantendo um cenário esportivo mas com a arquitetura correta de comunicação indireta.

## 14. Considerações Finais

A implementação desenvolvida evidencia que a comunicação indireta é uma alternativa eficiente para cenários em que há múltiplos consumidores, alta modularização e necessidade de desacoplamento entre componentes. Nesse contexto, o modelo publicar e assinar é mais adequado do que a comunicação direta por chamadas remotas.

Assim, a arquitetura adotada está alinhada com o material de referência e com o requisito central do trabalho: implementar uma solução de comunicação indireta com padrão publicar e assinar, utilizando Python e sockets em um cenário de eventos esportivos.
