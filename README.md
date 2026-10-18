# OR SplitShield

Motor de detecção de fracionamento de transações (structuring/smurfing) em janelas móveis, com evidências reproduzíveis.

## MVP

- Agrupar operações por cliente, conta, canal e contraparte.
- Avaliar quantidade, soma, proximidade de limite e intervalo temporal.
- Detectar depósitos, saques e transferências fragmentadas.
- Explicar cada alerta com regra, janela e transações relacionadas.

## Próximo passo

O pacote já detecta fracionamento por conta em janela configurável e devolve as transações de evidência. Próximo: adicionar regras por canal/contraparte e uma API.

