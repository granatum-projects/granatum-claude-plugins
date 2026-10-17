---
name: granatum-fundamentos
description: >
  Esta skill deve ser usada sempre que a conversa envolver o Granatum ou dados
  financeiros da empresa do usuário: quando ele pedir "DRE", "fluxo de caixa",
  "resultado do mês", "quanto entrou", "quanto gastei", "lançamentos",
  "contas a pagar", "contas a receber", "criar um lançamento", "registrar uma
  despesa", "lançar uma receita", ou quando qualquer ferramenta do Granatum for
  chamada. Contém as regras de regime contábil, resolução de empresa e os
  guardrails obrigatórios de escrita (criar, alterar, excluir, pagar e anexar).
metadata:
  version: "0.1.0"
---

# Fundamentos do Granatum

Regras que valem para toda interação com o Granatum. Aplicar mesmo quando o
usuário não invocar nenhum comando específico.

## Resolver a empresa antes de qualquer coisa

Toda ferramenta do Granatum exige `wgi_conta_id`. Nunca inventar esse valor.
`wgi_conta_id` é a empresa (de `listar_empresas`), não a conta bancária (`conta_id`):
"conta 89595" dito pelo usuário não é o id da empresa.

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
4. **Filtros herdados** — `conta_ids`, `categoria_ids`,
   `centro_custo_lucro_ids` ou `tag_ids` restritivos vindos de uma pergunta
   anterior.

Cruzar com `obter_lancamentos` no mesmo período para checar se há movimento
bruto. Só afirmar "não houve movimentação" depois disso.

## Guardrails de escrita

Escritas atingem os livros reais do cliente. Não existe modo de simulação.

Valem para toda ferramenta que grava: `criar_lancamento`,
`atualizar_lancamento`, `excluir_lancamento`, `registrar_pagamento`,
`criar_pessoa`, `anexar_arquivo` e `excluir_anexo`. Série, prévia, dividido,
transferência, pagamento e anexos têm o detalhe na skill `escrita-avancada`.

**Antes de `criar_lancamento`:**

- Reunir os dados, montar um resumo legível (tipo, valor, vencimento, categoria,
  conta, pessoa, descrição) e **esperar confirmação explícita do usuário**.
  Nunca criar direto a partir do primeiro pedido, mesmo que todos os campos
  tenham sido informados de uma vez.
- Validar a categoria: só usar item com `aceita_lancamento=true`. Categoria-pai é
  recusada pela API. Se o usuário nomear uma categoria-pai, mostrar as folhas
  disponíveis abaixo dela e pedir para escolher.
- Categoria **não** valida o `tipo_lancamento`. Existe categoria mista (aceita
  os dois tipos), e mesmo categoria exclusiva de receita ou despesa não
  bloqueia um lançamento do tipo oposto — a API não faz essa checagem. Nunca
  inferir receita/despesa a partir da categoria escolhida: confirmar o tipo
  diretamente com o usuário. Isso é usado de propósito para registrar
  **estorno/devolução na mesma categoria** do lançamento original (ex.: cliente
  devolveu um recebimento, empréstimo concedido que voltou) — não é só um risco
  a evitar. Detalhes em `references/regras-de-campo.md`.
- Validar a conta: usar `listar_contas` com `apenas_para_lancamento=true`.

**Duplicatas:**

Se a resposta vier com status `confirmacao_necessaria`, apresentar os
`lancamentos_existentes` ao usuário e perguntar se deve criar mesmo assim. Só
reenviar com `confirmar_duplicata: true` após um "sim" humano explícito.
**Nunca definir `confirmar_duplicata: true` por conta própria**, em nenhuma
circunstância, nem para "resolver" um erro, nem em retry automático. Vale
também para a transferência, que tem um identificador por ponta.

**Prévia e escopo:**

`atualizar_lancamento`, `excluir_lancamento`, `registrar_pagamento` e
`excluir_anexo` não gravam na primeira vez quando a chamada alcança mais de um
lançamento: devolvem `confirmacao_necessaria` com a prévia. Em lançamento de
série, sem `escopo_serie` devolvem `escopo_necessario`. Mostrar a prévia ou
perguntar o escopo, esperar a resposta humana e só então repetir os mesmos
argumentos com `confirmado: true` ou com o `escopo_serie` escolhido. **Nunca**
definir `confirmado` nem escolher o escopo por conta própria.

**Regra do escopo.** Nunca preencha `escopo_serie` sem que o usuário tenha dito o escopo nesta conversa. Sem isso, chame a tool **sem** o parâmetro, deixe-a devolver `escopo_necessario` e pergunte. Exemplo:

> Usuário: "Exclui a ocorrência de 10/10 da assinatura de internet."
> Você: chama `excluir_lancamento` sem `escopo_serie`; a tool devolve `escopo_necessario`.
> Você: "É uma assinatura recorrente. Excluo só esta ocorrência ou esta e as próximas?"
> Usuário: "Só esta." Agora sim, chame com `escopo_serie: "so_este"`.

**Regra da confirmação.** `confirmado: true` só depois de mostrar ao usuário a prévia **daquele pedido exato** e de ele dizer sim. Se o conjunto de ids, o escopo ou os campos mudaram (por exemplo, ao tirar o id impedido), chame de novo **sem** `confirmado`, mostre a prévia nova e pergunte de novo. O "sim" à prévia antiga não vale para o pedido novo. Escolher uma opção (por exemplo, "refazer sem o conciliado") não confirma a prévia nova: ela tem de ser mostrada antes. Exemplo:

> Prévia: 3 ids, 1 em `impedidos` (conciliado). Usuário: "Então faz sem ele."
> Você: chama de novo com 2 ids, sem `confirmado`; a tool devolve a prévia nova.
> Você: "Sem o conciliado, serão excluídos 2 lançamentos (R$ ...). Confirma?"
> Usuário: "Sim." Só agora chame com `confirmado: true`.

**Exclusão:**

Só chamar `excluir_lancamento` quando o usuário pedir exclusão de forma direta e
inequívoca, identificando o lançamento. Confirmar antes. Nunca excluir como
efeito colateral de uma correção — para corrigir, usar `atualizar_lancamento`.
O id de um item de lançamento dividido exclui o lançamento **inteiro**, sempre
depois da prévia; para tirar só um item, `itens_remover` em
`atualizar_lancamento`.

**Período fechado (datas de bloqueio):**

A empresa tem duas datas de bloqueio, a de **caixa** (pela data de pagamento) e a
de **competência**. Até a data, o período está fechado: nada entra, nada sai e
nada que entra no cálculo muda. Quem define a data é o administrador, na
interface do Granatum; nenhuma ferramenta a altera.

- **Competência fechada:** valor, competência, tipo, categoria, centro, pessoa,
  tags, descrição, observação, itens do dividido e exclusão não mudam, no
  lançamento inteiro. O **vencimento é livre**, e o anexo também.
- **Caixa fechado:** lançamento pago com data de pagamento até a data não muda
  nada (nem o vencimento), não se estorna, não troca a data e não se exclui.
- **Juros, multa e desconto** na baixa de lançamento de competência fechada: o
  valor dele não muda; a diferença vira **lançamento próprio**, pago na data do
  pagamento, e a resposta traz `lancamentos_da_diferenca`. Mostre os dois
  lançamentos ao usuário. Pagar menos exige `desconto: true`, e `gerar_restante`
  é recusado: ofereça só o valor cheio ou o desconto. Detalhe em
  `escrita-avancada`.
- **Quando a trava recusa**, a resposta traz a frase pronta (em `erro`, no começo
  de `hint_for_llm` e, por campo, em `erros`), por exemplo "Competência fechada até
  30/09: valor, competência e classificação deste lançamento não mudam." Repasse
  a frase ao usuário e pare. **Não** contorne mudando a data, apagando e
  recriando ou trocando de ferramenta; o que se oferece é o que a trava deixa
  livre (o vencimento, o anexo, o desconto no lugar do restante).

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

Em `atualizar_lancamento` (que recebe `lancamento_ids`, de 1 a 100), omitir um
campo preserva o valor atual; passar `0` nos
campos de vínculo (`pessoa_id`, `centro_custo_lucro_id`, `forma_pagamento_id`)
é que remove. Isso é o **oposto** de `criar_lancamento`, onde omitir e passar
zero dão no mesmo. Para limpar um vínculo, enviar `0` explicitamente — omitir
retorna sucesso sem alterar nada. Enviar somente o delta confirmado com o
usuário, nunca o objeto inteiro. Campo enviado com o valor que já está
gravado conta como não enviado: se nada difere, a ferramenta não grava e
responde com o estado atual.

## Regras de campo que causam erro silencioso

- `valor` é sempre positivo. O sinal vem de `tipo_lancamento`, nunca do número.
- `data_pagamento` é o único indicador de pago. Presente = pago, ausente =
  previsto. Não pode ser data futura.
- `data_competencia` omitida faz o Granatum resolver sozinho. Não inventar valor.
- `identificador_externo` é obrigatório em despesa e receita e é o que protege
  contra duplicidade. Use o número do documento como está no papel (a nota 7788
  → `7788`), sem prefixo, nome do fornecedor ou tipo. Na transferência não se informa: há um por ponta,
  opcionais. Regras completas em `references/regras-de-campo.md`.
- `data_pagamento` não se altera por `atualizar_lancamento` em lançamento: dar
  baixa, trocar a data de um pagamento e estornar é `registrar_pagamento`. Na
  transferência, a baixa é `data_pagamento` em `atualizar_lancamento`.
- Data de entrada com ano fora de 1600 a 9999 é recusada.

## Como apresentar números

- Formatar em reais (R$ 1.234,56).
- Sempre indicar período e regime.
- Em variações, dar o valor absoluto e o percentual.
- Não arredondar valores de lançamentos individuais.
- Não afirmar causa para uma variação sem ter feito drill-down. Dizer o que
  mudou, e oferecer investigar o porquê.

## Quando abrir a referência

Ao montar uma escrita, interpretar um erro da API, investigar um relatório com
resultado inesperado ou pedir campos extras de lançamentos, ler
`references/regras-de-campo.md`. Ele traz as regras de `identificador_externo`,
a diferença entre omitir e passar zero em criação e atualização, os campos de
leitura de `obter_lancamentos` (centro de custo, `campos_adicionais`, filtro por
tags, paginação), os formatos de período e o procedimento de drill-down. Para
alterar em lote, mexer em série, dividido ou transferência, pagar ou anexar, ler
a skill `escrita-avancada`.
