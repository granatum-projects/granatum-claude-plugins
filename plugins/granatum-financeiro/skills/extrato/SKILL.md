---
name: extrato
description: >
  Esta skill deve ser usada quando o usuário rodar "/extrato" ou pedir
  "lançamentos de", "extrato do mês", "me mostra as movimentações", "quanto
  gastei com X", "todos os pagamentos para fulano", "maiores despesas do
  período", "procura um lançamento" — qualquer listagem ou busca de lançamentos
  individuais.
metadata:
  version: "0.1.0"
---

# Extrato

Listagem e busca de lançamentos. Serve tanto para conferência quanto como passo
anterior a corrigir algo.

## Parâmetros

`obter_lancamentos` exige `periodo_inicio` e `periodo_fim` (`YYYY-MM-DD`). Sem
período informado, usar o mês corrente e dizer qual janela foi usada.

Filtros opcionais, aplicar conforme o pedido:

| Pedido do usuário | Filtro |
| --- | --- |
| "gastos com energia" | `categoria_ids` via `listar_categorias` |
| "pagamentos ao fornecedor X" | `pessoa_id` — buscar com `buscar_pessoas` |
| "movimentação da conta Y" | `conta_ids` via `listar_contas` |
| "só o que já foi pago" | `apenas_pagos: true` |
| "acima de R$ 1.000" | `valor_min` |
| "aquele lançamento do aluguel" | `descricao` (correspondência parcial) |
| "maiores primeiro" | `ordenacao: valor_desc` |

## Regime

Padrão `caixa`. **Em drill-down, usar o mesmo regime do relatório de origem** —
`competencia` se veio da DRE, `caixa` se veio do fluxo de caixa. Regime trocado
faz a soma não fechar com a linha que originou a pergunta, e o usuário lê isso
como erro do sistema.

Declarar o regime usado ao apresentar o resultado.

## Apresentação

Tabela com data, descrição, categoria, pessoa quando houver, valor e situação
(pago ou previsto). Total do conjunto ao final.

Acima de 20 itens, agrupar por categoria com subtotais em vez de listar tudo
corrido. O usuário quer entender a composição, não ler 80 linhas.

## Truncamento

`limite` máximo é 100. Quando a resposta traz `total_disponivel` maior que o
retornado, informar quantos existem e propor um filtro concreto que reduza o
conjunto — período mais curto, categoria específica, `valor_min`. Nunca
apresentar lista truncada como se fosse o conjunto completo.

## Correções

Se o usuário identificar um lançamento errado, usar `atualizar_lancamento` com
o `lancamento_id`, confirmando as alterações antes. Séries, lançamentos
compostos e transferências não são editáveis por aqui — informar que precisam
ser ajustados na interface do Granatum.

Exclusão só com pedido direto e inequívoco, nunca como efeito colateral de uma
correção.
