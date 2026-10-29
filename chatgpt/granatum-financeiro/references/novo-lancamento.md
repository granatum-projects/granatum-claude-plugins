---
name: novo-lancamento
description: >
  Esta skill deve ser usada quando o usuário rodar "/novo-lancamento" ou disser
  "criar um lançamento", "lançar uma despesa", "registrar uma receita", "anotar
  um pagamento", "adicionar uma conta", "recebi X de fulano", "paguei o boleto
  de Y" — qualquer pedido de registro de movimento financeiro no Granatum.
metadata:
  version: "0.1.0"
---

# Novo lançamento

Fluxo guiado de criação. Escrita real nos livros do cliente, sem modo de
simulação. A confirmação humana não é opcional.

Este fluxo cobre receita e despesa, avulsas ou com repetição. Transferência
entre contas, lançamento dividido em itens, cadastro de pessoa nova, edição,
exclusão, pagamento e anexo estão na referência `escrita-avancada.md`; leia-a quando o
pedido for um deles.

Antes de montar o lançamento, ler
`regras-de-campo.md`. Ele traz as regras
completas de `identificador_externo`, a diferença entre omitir e passar zero nos
campos de vínculo, e o critério de categoria-folha — as três coisas que fazem
uma escrita falhar ou gravar errado em silêncio.

## 1. Coletar

Obrigatórios: `tipo_lancamento` (receita ou despesa), `valor`,
`data_vencimento`, `categoria_id`, `conta_id`, `identificador_externo`.

Opcionais que valem perguntar: `descricao`, `pessoa_id`, `data_pagamento`,
`documento`, `forma_pagamento_id`, `centro_custo_lucro_id`, `tag_ids`.

**Repetição.** Se o lançamento se repete (parcelas, mensalidade, recorrente),
preencher `repeticao`: `periodicidade` e `total_repeticoes` (quantidade de
ocorrências, contando a primeira) **ou** `infinito: true`, nunca os dois. Cada
ocorrência é um lançamento real, então a **quantidade entra no resumo** que o
usuário confirma. Com `data_pagamento`, só a primeira ocorrência nasce paga. A
resposta traz o `grupo_id` da série e a `quantidade_criada`.

**Dividido.** Se o usuário quer um lançamento com vários itens (várias
categorias, um desconto), usar `itens` em vez de `valor` e `categoria_id`; os
detalhes estão em `escrita-avancada.md`.

**Descrição.** Só a pontuação do português: seta (→), emojis e símbolos
decorativos são recusados. Antes de montar o resumo, troque por texto ("de A
para B", "-") ou avise o usuário, para a descrição gravada ser a mostrada.

Aproveitar o que o usuário já disse. "Paguei 450 de energia hoje" já entrega
tipo, valor, data de pagamento e uma pista de categoria — perguntar apenas o que
falta, não repetir o que foi dado.

## 2. Resolver referências

- **Categoria**: `listar_categorias`. Escolher apenas item com
  `aceita_lancamento=true`. Se o termo do usuário casar com uma categoria-pai,
  listar as folhas abaixo dela e pedir para escolher. Se casar com várias folhas,
  mostrar o caminho completo de cada uma para desambiguar.
- **Conta**: `listar_contas` com `apenas_para_lancamento=true`. Se houver só
  uma, adotá-la e mencionar qual.
- **Pessoa**: `buscar_pessoas` quando o usuário nomear cliente ou fornecedor.
  Se não achar, oferecer cadastrar com `criar_pessoa` (ver `escrita-avancada.md`)
  ou seguir sem pessoa; não travar o fluxo.
- **Forma de pagamento** e **centro de custo**: só resolver se o usuário
  mencionar.

## 3. Montar o identificador_externo

Se existe chave natural — número da nota, ID do extrato, ID do sistema de
origem — usar crua, sem prefixo, nome do fornecedor ou tipo: a nota 7788 é
`7788`, nunca `CLARO-NF-7788`. É ela que detecta a duplicata; um identificador
diferente na segunda conversa não casa e grava a duplicata.

Se não existe, gerar `mcp:<uuid v4>`. **Gerar o UUID uma vez** e reutilizar em
qualquer retry desta mesma tentativa. UUID novo a cada retry desliga a proteção
contra duplicidade.

## 4. Confirmar

Apresentar um resumo legível e **parar**:

```
Tipo:         Despesa
Valor:        R$ 450,00
Vencimento:   15/08/2026
Pagamento:    15/08/2026 (pago)
Categoria:    Despesas > Operacionais > Energia elétrica
Conta:        Banco do Brasil - Conta corrente
Fornecedor:   CEMIG
Descrição:    Conta de luz agosto
```

Perguntar se está correto. Só chamar `criar_lancamento` depois de um "sim"
explícito. Nunca criar direto, mesmo quando o usuário forneceu todos os campos
de uma vez e o pedido parece completo.

## 5. Tratar duplicata

Se a resposta vier com `confirmacao_necessaria`, apresentar os
`lancamentos_existentes` ao usuário e perguntar se deve criar mesmo assim.

Só reenviar com `confirmar_duplicata: true` após resposta humana explícita.
**Nunca autoconfirmar** — nem para destravar o fluxo, nem em retry, nem quando
parecer óbvio que não é duplicata de verdade.

## 6. Confirmar o resultado

Informar que foi criado e o ID gerado (com repetição, o `grupo_id` e quantas
ocorrências foram criadas). Se o usuário quiser corrigir, usar
`atualizar_lancamento` com o mesmo id em `lancamento_ids`, nunca criar outro.

## Erros comuns

| Erro | Causa | O que fazer |
| --- | --- | --- |
| `-32002` `escopo_insuficiente` | conexão sem permissão de escrita, em geral autorizada antes de o registro existir | pedir para reconectar o Granatum — a autorização nova já inclui escrita — e parar; não repetir a chamada, e não mandar procurar opção de escrita no consentimento, que é tudo-ou-nada |
| Categoria recusada | `aceita_lancamento=false` — é categoria-pai | listar as folhas abaixo e pedir escolha |
| Conta recusada | `permite_lancamento=false` | listar contas com `apenas_para_lancamento=true` |
| Data de pagamento rejeitada | data futura não é permitida | omitir para deixar previsto, ou usar data passada |
| Data recusada por ano | data de entrada com ano fora de 1600 a 9999 | corrigir a data com o usuário |
| Valor rejeitado | valor deve ser positivo | corrigir o sinal via `tipo_lancamento` |

O erro de escopo é o único da tabela que não se resolve ajustando os dados. Nos
demais, corrigir e reapresentar o resumo ao usuário antes de tentar de novo.
