---
name: resumo-mes
description: >
  Esta skill deve ser usada quando o usuário rodar "/resumo-mes" ou perguntar
  "como foi o mês", "como foi o mês passado", "me dá um resumo do mês",
  "fechamento do mês", "como está a empresa", "resumo financeiro" — qualquer
  pedido de visão geral do desempenho de um período sem especificar um relatório.
metadata:
  version: "0.1.0"
---

# Resumo do mês

Visão consolidada do período: caixa, resultado e destaques, numa resposta só.

## Período

Sem período informado, usar o **último mês fechado**. Se o usuário nomear um mês
("julho", "junho de 2026"), converter para `YYYY-MM`. Se pedir o mês corrente,
atender e avisar em uma linha que o mês ainda não fechou.

## Coleta

Chamar em paralelo, ambos com `periodicidade: mensal`, `quantidade_periodos: 6`
e `periodo_referencia` no mês alvo:

- `obter_fluxo_caixa` — entradas, saídas, líquido, saldo acumulado
- `obter_dre` — receita, custos, margens, resultado

Seis períodos dão a série histórica necessária para a comparação. Apresentar o
mês alvo em detalhe e usar os anteriores só para contexto de tendência.

## Estrutura da resposta

**1. A linha de cima.** Uma frase: entrou X, saiu Y, sobrou Z no caixa; o
resultado pelo regime de competência foi W. Se caixa e resultado divergem muito,
dizer isso já aqui — é a informação mais útil da resposta.

**2. Caixa.** Recebido, pago, líquido do mês. Saldo inicial e final. Comparação
com o mês anterior em valor e percentual.

**3. Resultado.** Receita, custos, margem, resultado líquido. Variação contra o
mês anterior. Se a resposta trouxer EBITDA, incluir.

**4. Destaques.** Três a cinco pontos das `principais_categorias` de cada
relatório: maiores despesas, maiores receitas, e qualquer categoria com variação
fora do padrão dos últimos seis meses.

**5. Atenção.** Só quando houver: alertas de mapeamento, meses com dado faltando
na série, ou divergência grande entre caixa e competência.

## Regras

- Rotular sempre qual número é caixa e qual é competência. Misturar os dois sem
  rótulo é o erro mais caro desta skill.
- Não especular a causa de uma variação. Descrever o movimento e oferecer o
  drill-down: "posso listar os lançamentos dessa categoria".
- Se algum dos dois relatórios voltar zerado, aplicar o diagnóstico de
  `granatum-fundamentos` antes de reportar ausência de dados.
- Terminar oferecendo um próximo passo concreto, não uma pergunta genérica.
