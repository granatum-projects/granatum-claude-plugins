---
name: pendencias
description: >
  Esta skill deve ser usada quando o usuário rodar "/pendencias" ou perguntar
  "o que tenho a pagar", "contas a pagar", "contas a receber", "o que vence essa
  semana", "o que está atrasado", "quem me deve", "quanto tenho pra receber",
  "tem alguma conta vencendo" — qualquer pergunta sobre valores em aberto por
  vencimento.
metadata:
  version: "0.1.0"
---

# Pendências

Lançamentos em aberto organizados por vencimento. É a pergunta mais frequente do
dia a dia — otimizar para clareza e velocidade de leitura.

## O que conta como pendência

Lançamento **sem `data_pagamento`**. Esse é o único critério: ausência de data de
pagamento significa previsto, não realizado. Não usar `apenas_pagos` aqui, e sim
filtrar o resultado pela ausência do campo.

## Janela

Padrão: do início do mês corrente até 30 dias à frente. Isso captura tanto o que
já venceu e não foi pago quanto o que está chegando.

Se o usuário disser "essa semana", "esse mês", "próximos 15 dias", ajustar. Se
disser "atrasados", limitar a `periodo_fim` = ontem.

## Coleta

`obter_lancamentos` com a janela, `regime: caixa`, `ordenacao: data_asc` e
`limite: 100`. Se vier truncado, avisar o total e estreitar a janela em vez de
apresentar lista parcial como completa.

## Apresentação

Separar em **a pagar** (despesa) e **a receber** (receita), e dentro de cada um
agrupar por faixa de vencimento:

- Vencidos (com quantos dias de atraso)
- Vence hoje
- Próximos 7 dias
- Depois disso

Para cada item: vencimento, descrição, pessoa quando houver, valor. Subtotal por
faixa e total geral de cada lado.

Abrir a resposta com os números que importam: quanto está vencido, quanto vence
nos próximos 7 dias, de cada lado. O detalhamento vem depois.

## Regras

- Vencidos primeiro, sempre. É o que exige ação.
- Se não houver nada vencido, dizer isso explicitamente — é uma boa notícia e o
  usuário quer ouvi-la.
- Não sugerir que algo seja pago ou cobrado. Apresentar a situação; a decisão é
  do usuário.
- Se o usuário quiser marcar algo como pago, isso é `atualizar_lancamento`
  preenchendo `data_pagamento` — seguir os guardrails de escrita de
  `granatum-fundamentos` e confirmar antes.
