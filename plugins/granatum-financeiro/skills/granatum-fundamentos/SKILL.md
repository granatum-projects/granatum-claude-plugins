---
name: granatum-fundamentos
description: >
  Esta skill deve ser usada sempre que a conversa envolver o Granatum ou dados
  financeiros da empresa do usuário: quando ele pedir "DRE", "fluxo de caixa",
  "resultado do mês", "quanto entrou", "quanto gastei", "lançamentos",
  "contas a pagar", "contas a receber", "criar um lançamento", "registrar uma
  despesa", "lançar uma receita", ou quando qualquer ferramenta do Granatum for
  chamada. Contém as regras de regime contábil, resolução de empresa e os
  guardrails obrigatórios de escrita.
metadata:
  version: "0.1.0"
---

# Fundamentos do Granatum

Regras que valem para toda interação com o Granatum. Aplicar mesmo quando o
usuário não invocar nenhum comando específico.

## Resolver a empresa antes de qualquer coisa

Toda ferramenta do Granatum exige `wgi_conta_id`. Nunca inventar esse valor.

1. Chamar `listar_empresas` na primeira operação da sessão.
2. Se houver uma única empresa, adotá-la e seguir sem perguntar.
3. Se houver mais de uma, perguntar em qual trabalhar e manter essa escolha pelo
   resto da conversa.
4. Ao trocar de empresa no meio da conversa, avisar explicitamente e descartar
   IDs de conta, categoria e centro de custo obtidos para a empresa anterior —
   eles não são válidos entre empresas.

## Regime contábil: nunca deixar implícito

O regime determina qual data conta. Errar aqui produz um relatório que parece
certo e está errado.

| Situação | Regime |
| --- | --- |
| DRE (`obter_dre`) | `competencia`, sempre |
| Fluxo de caixa (`obter_fluxo_caixa`) | `caixa`, sempre |
| Drill-down após um relatório | o **mesmo** regime do relatório de origem |
| Listagem livre de lançamentos | `caixa` por padrão; declarar qual foi usado |

Ao apresentar qualquer número, dizer qual regime foi usado e o período coberto.
Se o usuário pedir algo ambíguo ("quanto faturei em julho"), assumir o padrão da
tabela, entregar o resultado e mencionar em uma linha que existe a outra leitura.

## Relatório zerado é diagnóstico, não resposta

Um DRE ou fluxo de caixa que volta com tudo em zero quase nunca significa
"não houve movimento". Antes de reportar ausência de dados ao usuário, verificar:

1. **Regime trocado** — competência vs caixa invertidos.
2. **Categorias não mapeadas** — conferir os alertas de mapeamento na resposta
   do relatório; categorias fora da árvore da DRE não aparecem no resultado.
3. **Período de referência** — confirmar o formato (`mensal`=YYYY-MM,
   `trimestral`=YYYY-Tn, `semestral`=YYYY-Sn, `anual`=YYYY) e se o período já
   fechou.
4. **Filtros herdados** — `conta_ids`, `categoria_ids` ou
   `centro_custo_lucro_ids` restritivos vindos de uma pergunta anterior.

Cruzar com `obter_lancamentos` no mesmo período para checar se há movimento
bruto. Só afirmar "não houve movimentação" depois disso.

## Guardrails de escrita

Escritas atingem os livros reais do cliente. Não existe modo de simulação.

**Antes de `criar_lancamento`:**

- Reunir os dados, montar um resumo legível (tipo, valor, vencimento, categoria,
  conta, pessoa, descrição) e **esperar confirmação explícita do usuário**.
  Nunca criar direto a partir do primeiro pedido, mesmo que todos os campos
  tenham sido informados de uma vez.
- Validar a categoria: só usar item com `aceita_lancamento=true`. Categoria-pai é
  recusada pela API. Se o usuário nomear uma categoria-pai, mostrar as folhas
  disponíveis abaixo dela e pedir para escolher.
- Validar a conta: usar `listar_contas` com `apenas_para_lancamento=true`.

**Duplicatas:**

Se a resposta vier com status `confirmacao_necessaria`, apresentar os
`lancamentos_existentes` ao usuário e perguntar se deve criar mesmo assim. Só
reenviar com `confirmar_duplicata: true` após um "sim" humano explícito.
**Nunca definir `confirmar_duplicata: true` por conta própria**, em nenhuma
circunstância, nem para "resolver" um erro, nem em retry automático.

**Exclusão:**

Só chamar `excluir_lancamento` quando o usuário pedir exclusão de forma direta e
inequívoca, identificando o lançamento. Confirmar antes. Nunca excluir como
efeito colateral de uma correção — para corrigir, usar `atualizar_lancamento`.

**Escopo de escrita ausente:**

Se uma ferramenta de escrita retornar código `-32002` com `escopo_insuficiente`,
a conexão do usuário foi autorizada apenas para leitura. Não é erro nos dados e
não adianta ajustar os campos e tentar de novo.

Dizer ao usuário, em uma frase: a conexão atual não tem permissão de escrita, e
reconectar o Granatum resolve — a autorização nova já inclui o registro de
lançamentos.

**Não** dizer para "autorizar a escrita" na tela de consentimento: essa escolha
não existe. A autorização é tudo-ou-nada, e mandar o usuário procurar uma opção
que não está lá o deixa girando em falso. O caso típico é conexão antiga,
autorizada antes de o registro de lançamentos existir.

Depois de avisar, parar. **Não** repetir a chamada, não tentar outra ferramenta
de escrita, não sugerir contorno. Consultas continuam funcionando normalmente —
seguir ajudando com relatórios e leitura.

**Atualização preserva o que não é enviado:**

Em `atualizar_lancamento`, omitir um campo preserva o valor atual; passar `0` nos
campos de vínculo (`pessoa_id`, `centro_custo_lucro_id`, `forma_pagamento_id`)
é que remove. Isso é o **oposto** de `criar_lancamento`, onde omitir e passar
zero dão no mesmo. Para limpar um vínculo, enviar `0` explicitamente — omitir
retorna sucesso sem alterar nada. Enviar somente o delta confirmado com o
usuário, nunca o objeto inteiro.

## Regras de campo que causam erro silencioso

- `valor` é sempre positivo. O sinal vem de `tipo_lancamento`, nunca do número.
- `data_pagamento` é o único indicador de pago. Presente = pago, ausente =
  previsto. Não pode ser data futura.
- `data_competencia` omitida faz o Granatum resolver sozinho. Não inventar valor.
- `identificador_externo` é obrigatório e é o que protege contra duplicidade.
  Regras completas em `references/regras-de-campo.md`.
- `atualizar_lancamento` só opera em lançamento simples. Séries, lançamentos
  compostos e transferências precisam ser editados na interface do Granatum —
  informar isso ao usuário em vez de tentar.

## Como apresentar números

- Formatar em reais (R$ 1.234,56).
- Sempre indicar período e regime.
- Em variações, dar o valor absoluto e o percentual.
- Não arredondar valores de lançamentos individuais.
- Não afirmar causa para uma variação sem ter feito drill-down. Dizer o que
  mudou, e oferecer investigar o porquê.

## Quando abrir a referência

Ao montar uma escrita, interpretar um erro da API ou investigar um relatório com
resultado inesperado, ler `references/regras-de-campo.md`. Ele traz as regras de
`identificador_externo`, a diferença entre omitir e passar zero em criação e
atualização, os formatos de período e o procedimento de drill-down.
