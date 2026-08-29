---
name: fluxo-caixa
description: >
  Esta skill deve ser usada quando o usuário rodar "/fluxo-caixa" ou pedir
  "fluxo de caixa", "quanto entrou e saiu", "movimentação do caixa", "saldo do
  mês", "evolução do caixa", "entradas e saídas" — qualquer pedido de relatório
  de caixa por período.
metadata:
  version: "0.1.0"
---

# Fluxo de caixa

Relatório de caixa. Regime **sempre `caixa`**: conta o que efetivamente entrou e
saiu, pela data de pagamento.

## Parâmetros

`obter_fluxo_caixa` com:

- `periodicidade` — `mensal` por padrão. Usar `trimestral`, `semestral` ou
  `anual` quando o usuário pedir essa granularidade explicitamente.
- `quantidade_periodos` — 6 por padrão. A série histórica é o que dá sentido ao
  número do mês; não pedir um período só.
- `periodo_referencia` — último período da janela. Omitir usa o último período
  completo. Formato conforme a periodicidade (ver `granatum-fundamentos`).
- `limite_categorias` — 10 por padrão.

Aplicar `conta_ids`, `categoria_ids` ou `centro_custo_lucro_ids` apenas quando o
usuário restringir. Ao aplicar um filtro, declarar isso na resposta.

## Apresentação

1. **Período de referência**: recebido, pago, líquido. Saldo inicial e final.
2. **Tendência**: como o líquido e o saldo acumulado se comportaram nos períodos
   da série. Uma sequência de meses negativos importa mais que o valor de um mês.
3. **Principais categorias**: o que mais pesou nas entradas e nas saídas.
4. **Comparação** com o período anterior, em valor e percentual.

Considerar um gráfico de linha do saldo acumulado quando houver 4 ou mais
períodos — a trajetória comunica melhor que a tabela.

## Regras

- Declarar que o regime é caixa e o que isso significa: só o que foi pago ou
  recebido de fato. Boleto emitido e não pago não aparece aqui.
- Se o usuário perguntar por que o fluxo de caixa não bate com a DRE, a resposta
  está na diferença de regime — explicar e oferecer os dois lado a lado.
- Drill-down usa `obter_lancamentos` com `regime: caixa` e os `categoria_ids` da
  linha investigada.
- Resultado zerado: aplicar o diagnóstico de `granatum-fundamentos` antes de
  reportar ausência de dados.
