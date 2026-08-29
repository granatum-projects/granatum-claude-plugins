# Regras de campo e diagnóstico

Consultar quando montar uma escrita, interpretar um erro da API, ou investigar
um relatório com resultado inesperado.

## identificador_externo

Campo obrigatório em `criar_lancamento`. É a chave que o Granatum usa para
detectar duplicata.

**Quando existe chave natural** (número da nota fiscal, ID do extrato bancário,
ID do sistema de origem): usar a chave natural crua, **sem prefixo**. Isso
permite detectar colisão com lançamentos vindos de outras origens — importação
de OFX, conciliação bancária, integração de ERP. Prefixar destrói essa proteção.

**Quando não existe chave natural**: usar `mcp:<uuid v4>`.

Gerar o UUID **uma única vez** por tentativa de lançamento e reutilizá-lo em
qualquer retry da mesma tentativa. Gerar um UUID novo a cada retry anula
completamente a proteção contra duplicidade — a segunda tentativa passa como se
fosse um lançamento diferente e o cliente fica com dois registros iguais.

## Campos de data

| Campo | Significado |
| --- | --- |
| `data_vencimento` | Obrigatório. Quando o valor vence. |
| `data_pagamento` | Presente = pago. Ausente = previsto. Não pode ser futura. |
| `data_competencia` | Se omitida, o Granatum resolve. Nunca preencher com palpite. |

Todas em `YYYY-MM-DD`.

Consequência prática: um lançamento sem `data_pagamento` aparece no DRE (regime
competência) mas **não** no fluxo de caixa (regime caixa). Essa é a explicação
mais comum para "o número não bate entre os dois relatórios".

## Campos com sentinela zero

`centro_custo_lucro_id`, `forma_pagamento_id` e `pessoa_id` aceitam `0` para
"nenhum". O zero não aparece nas listagens correspondentes — é um valor especial,
não um item cadastrado.

**Omitir e passar zero significam coisas opostas em criar e atualizar. Não
generalizar de um para o outro.**

| Operação | Omitir o campo | Passar `0` |
| --- | --- | --- |
| `criar_lancamento` | fica sem vínculo | fica sem vínculo |
| `atualizar_lancamento` | **preserva** o vínculo atual | **remove** o vínculo |

Na criação os dois caminhos chegam no mesmo lugar, então a distinção não importa.
Na atualização ela é tudo: para tirar o fornecedor de um lançamento, passar
`pessoa_id: 0`. Omitir o campo mantém o fornecedor que já estava lá, e a
operação retorna sucesso — o usuário acredita que limpou e não limpou.

A mesma lógica vale para os demais campos de `atualizar_lancamento`: **omitir
preserva o valor atual**. Só enviar os campos que devem mudar. `data_competencia`
omitida, por exemplo, preserva a competência atual, ao contrário da criação, onde
omitir deixa o Granatum resolver.

Consequência prática: nunca montar um `atualizar_lancamento` reenviando o objeto
inteiro "por segurança". Enviar só o delta confirmado com o usuário.

## Categorias

`listar_categorias` devolve a hierarquia com o caminho completo. Cada item traz
`aceita_lancamento`.

- `aceita_lancamento=true` — categoria-folha, aceita lançamento.
- `aceita_lancamento=false` — categoria-pai, existe para agrupar. A API recusa.

Ao ajudar o usuário a escolher, mostrar o caminho completo (ex.:
`Despesas > Operacionais > Energia elétrica`), não só o nome da folha. Nomes de
folha se repetem entre ramos diferentes.

## Períodos nos relatórios

`periodo_referencia` é o **último** período da janela, não o primeiro. A janela
se estende para trás por `quantidade_periodos`.

| Periodicidade | Formato | Exemplo |
| --- | --- | --- |
| mensal | `YYYY-MM` | `2026-03` |
| trimestral | `YYYY-Tn` | `2026-T1` |
| semestral | `YYYY-Sn` | `2026-S1` |
| anual | `YYYY` | `2026` |

Omitir `periodo_referencia` usa o último período completo automaticamente. Para
um relatório do mês corrente ainda em andamento, informar o período
explicitamente e avisar o usuário que o mês não fechou.

## Drill-down

Depois de `obter_dre` ou `obter_fluxo_caixa`, o caminho para investigar uma linha
é `obter_lancamentos` passando os `categoria_ids` que vieram em
`principais_categorias` daquela linha.

Manter o mesmo `regime` do relatório de origem. Um drill-down de DRE com
`regime: caixa` devolve um conjunto diferente de lançamentos e a soma não vai
fechar com a linha que originou a pergunta — o usuário vai interpretar a
diferença como erro do sistema.

Para "maiores movimentos primeiro", usar `ordenacao: valor_desc`, que ordena por
magnitude absoluta.

## Truncamento

`obter_lancamentos` tem `limite` máximo de 100. Quando trunca, a resposta traz
`total_disponivel`. Nunca apresentar uma lista truncada como se fosse completa:
informar quantos existem no total e sugerir um filtro que reduza o conjunto
(período menor, categoria específica, valor mínimo).
