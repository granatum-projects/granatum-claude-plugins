---
name: extrato
description: >
  Esta skill deve ser usada quando o usuário rodar "/extrato" ou pedir
  "lançamentos de", "extrato do mês", "me mostra as movimentações", "quanto
  gastei com X", "todos os pagamentos para fulano", "maiores despesas do
  período", "procura um lançamento", "lançamentos com a tag X", "o que está
  sem tag", "quais parcelas faltam" — qualquer listagem ou busca de lançamentos
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
| "gastos do setor Comercial" | `centro_custo_lucro_ids` via `listar_centros_custo_lucro` |
| "lançamentos com a tag Marketing" | `tag_ids` via `listar_tags` |
| "com a tag A ou a tag B" | `tag_ids: [A, B]` (padrão `tags_modo: qualquer`) |
| "com as tags A e B ao mesmo tempo" | `tag_ids: [A, B]` e `tags_modo: todas` |
| "o que está sem tag" | `tag_ids: [0]` |
| "só o que já foi pago" | `apenas_pagos: true` |
| "acima de R$ 1.000" | `valor_min` |
| "aquele lançamento do aluguel" | `descricao` (correspondência parcial) |
| "maiores primeiro" | `ordenacao: valor_desc` |

O `0` em `tag_ids` significa "sem nenhuma tag" e só combina com outras tags no
modo `qualquer` (`[0, A]` = sem tag ou com a tag A). Com `tags_modo: todas` a
combinação é contraditória e a API recusa.

## Campos adicionais

A resposta padrão já traz, em cada lançamento, `centro_custo_lucro_id` e
`centro_custo_lucro_descricao` (id `0` e descrição `null` = sem centro de
custo). O resto é opcional: pedir em `campos_adicionais` **só o que a pergunta
exige**, porque cada grupo aumenta o tamanho da resposta.

| Pedido do usuário | `campos_adicionais` |
| --- | --- |
| mostrar ou usar as tags de cada lançamento | `tags` |
| "pagou como?", boleto, cartão, Pix | `forma_pagamento` |
| nota fiscal, recibo, tipo de documento | `tipo_documento` |
| parcelas, recorrência, "quantas faltam" | `parcelamento` |
| conferir o que veio de integração ou ERP | `identificador_externo` |

Filtrar por tag e **mostrar** as tags são coisas diferentes: `tag_ids` só
recorta o conjunto. Para exibir as tags de cada item, pedir também
`campos_adicionais: ["tags"]`.

Não inferir repetição, parcela ou forma de pagamento pela descrição ou por
padrão de datas. Se a pergunta depende disso, pedir o grupo correspondente e
responder com o dado registrado. Detalhes dos campos em
`granatum-fundamentos/references/regras-de-campo.md`.

## Regime

Padrão `caixa`. **Em drill-down, usar o mesmo regime do relatório de origem** —
`competencia` se veio da DRE, `caixa` se veio do fluxo de caixa. Regime trocado
faz a soma não fechar com a linha que originou a pergunta, e o usuário lê isso
como erro do sistema.

Declarar o regime usado ao apresentar o resultado.

## Apresentação

Tabela com data, descrição, categoria, pessoa quando houver, valor e situação
(pago ou previsto). Total do conjunto ao final. Incluir colunas extras só
quando fizerem parte da pergunta: centro de custo, tags, forma de pagamento ou
parcela (ex.: "3 de 12").

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
