---
name: dre
description: >
  Esta skill deve ser usada quando o usuário rodar "/dre" ou pedir "DRE",
  "demonstrativo de resultado", "resultado do exercício", "qual foi meu lucro",
  "margem", "EBITDA", "quanto a empresa lucrou", "receita e custos do período" —
  qualquer pedido de resultado por regime de competência.
metadata:
  version: "0.1.0"
---

# DRE

Demonstrativo de resultado. Regime **sempre `competencia`**: conta pelo fato
gerador, independente de ter sido pago.

## Parâmetros

`obter_dre` com:

- `periodicidade` — `mensal` por padrão; `trimestral`, `semestral` ou `anual`
  quando pedido.
- `quantidade_periodos` — 6 por padrão. Margem só faz sentido em série.
- `periodo_referencia` — último período da janela. Omitir usa o último período
  completo. Formato conforme a periodicidade (ver `granatum-fundamentos`).
- `limite_categorias` — 10 por padrão.
- `incluir_observacoes` — ativar quando o usuário pedir explicação, não só
  números.

## Apresentação

Seguir a árvore de tópicos que a resposta devolve, do topo para baixo: receita,
deduções, receita líquida, custos, margem bruta, despesas operacionais, EBITDA,
resultado líquido. Não reordenar nem inventar linhas que não vieram.

Para o período de referência, mostrar valor e participação sobre a receita. Para
a comparação, mostrar a variação contra o período anterior em valor e percentual.

Destacar o que mudou de fato: linhas com variação relevante em relação ao padrão
da série, e o efeito disso na margem e no resultado. Explicar o encadeamento
quando ele existir — receita subiu mas margem caiu porque o custo subiu mais.

## Regras

- Declarar que o regime é competência: inclui o que foi faturado e ainda não
  recebido, e exclui pagamento de algo competente a outro período.
- **Alertas de mapeamento** vêm na resposta. Sempre repassá-los. Categoria fora
  da árvore da DRE não entra no resultado, e o cliente precisa saber que o número
  está incompleto antes de tomar decisão em cima dele.
- Não afirmar causa sem drill-down. Oferecer investigar com `obter_lancamentos`
  usando `regime: competencia` e os `categoria_ids` da linha.
- Resultado todo zerado quase sempre é regime trocado ou categoria não mapeada,
  não ausência de movimento. Diagnosticar antes de reportar.
- Para comparar períodos distantes, aumentar `quantidade_periodos` em vez de
  fazer duas chamadas separadas.
