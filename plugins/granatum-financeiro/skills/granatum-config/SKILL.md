---
name: granatum-config
description: >
  Esta skill deve ser usada quando o usuário rodar "/granatum-config", disser
  "configurar Granatum", "começar", "conectar minha empresa", "quais empresas eu
  tenho", perguntar se a conexão está funcionando, ou quando for a primeira
  operação Granatum da conversa e ainda não houver empresa definida.
metadata:
  version: "0.1.0"
---

# Configuração inicial do Granatum

Estabelecer o contexto de trabalho e confirmar que a conexão funciona nas três
áreas. Rodar uma vez por cliente; depois disso a conversa já sabe onde está.

## Passos

1. Chamar `listar_empresas`. Se falhar por autenticação, orientar o usuário a
   reconectar o Granatum nas configurações de conectores e parar aqui.
2. Se houver mais de uma empresa, apresentar a lista e perguntar qual usar. Se
   houver uma só, adotá-la e informar qual foi.
3. Com a empresa definida, carregar em paralelo:
   - `listar_contas` com `apenas_para_lancamento=true`
   - `listar_categorias` com `apenas_ativas=true`
   - `listar_formas_pagamento`
   - `listar_centros_custo_lucro`
4. Fazer um teste de leitura leve: `obter_fluxo_caixa` com
   `periodicidade: mensal` e `quantidade_periodos: 1`.

## O que apresentar

Um resumo curto, em linguagem de dono de empresa, não de API:

- Empresa conectada.
- Quantas contas bancárias estão disponíveis para lançamento, nomeando-as.
- Quantas categorias existem e quantas aceitam lançamento.
- Formas de pagamento e centros de custo cadastrados, se houver.
- Se o teste de leitura trouxe movimento, uma linha com o resultado do último
  mês fechado.

Não despejar IDs numéricos na resposta. Guardá-los para uso interno.

## Sinalizar problemas de cadastro

Se algo vai atrapalhar o uso, avisar agora em vez de deixar o cliente descobrir
no meio de um lançamento:

- Nenhuma conta com `permite_lancamento` — não será possível criar lançamentos.
- Nenhuma categoria com `aceita_lancamento=true` — mesmo problema.
- O relatório de teste voltou zerado — seguir o diagnóstico da skill
  `granatum-fundamentos` antes de concluir que não há dados.
- Alertas de mapeamento na resposta do relatório — mencionar que algumas
  categorias podem não aparecer na DRE.

## Fechamento

Terminar sugerindo dois ou três comandos que fazem sentido para o que foi
encontrado. Se há movimento no mês passado, sugerir `/resumo-mes`. Se há
lançamentos em aberto, sugerir `/pendencias`.
