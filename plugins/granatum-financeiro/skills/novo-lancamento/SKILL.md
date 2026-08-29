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

Antes de montar o lançamento, ler
`../granatum-fundamentos/references/regras-de-campo.md`. Ele traz as regras
completas de `identificador_externo`, a diferença entre omitir e passar zero nos
campos de vínculo, e o critério de categoria-folha — as três coisas que fazem
uma escrita falhar ou gravar errado em silêncio.

## 1. Coletar

Obrigatórios: `tipo_lancamento` (receita ou despesa), `valor`,
`data_vencimento`, `categoria_id`, `conta_id`, `identificador_externo`.

Opcionais que valem perguntar: `descricao`, `pessoa_id`, `data_pagamento`,
`documento`, `forma_pagamento_id`, `centro_custo_lucro_id`.

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
  Se não achar, seguir sem pessoa em vez de travar o fluxo.
- **Forma de pagamento** e **centro de custo**: só resolver se o usuário
  mencionar.

## 3. Montar o identificador_externo

Se existe chave natural — número da nota, ID do extrato, ID do sistema de
origem — usar crua, sem prefixo.

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

Informar que foi criado e o ID gerado. Se o usuário quiser corrigir, usar
`atualizar_lancamento` com o mesmo `lancamento_id`, nunca criar outro.

## Erros comuns

| Erro | Causa | O que fazer |
| --- | --- | --- |
| `-32002` `escopo_insuficiente` | conexão autorizada só para leitura | pedir para reconectar o Granatum concedendo escrita, e parar — não repetir a chamada |
| Categoria recusada | `aceita_lancamento=false` — é categoria-pai | listar as folhas abaixo e pedir escolha |
| Conta recusada | `permite_lancamento=false` | listar contas com `apenas_para_lancamento=true` |
| Data de pagamento rejeitada | data futura não é permitida | omitir para deixar previsto, ou usar data passada |
| Valor rejeitado | valor deve ser positivo | corrigir o sinal via `tipo_lancamento` |

O erro de escopo é o único da tabela que não se resolve ajustando os dados. Nos
demais, corrigir e reapresentar o resumo ao usuário antes de tentar de novo.
