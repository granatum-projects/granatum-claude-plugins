---
name: escrita-avancada
description: >
  Esta skill deve ser usada quando o usuário pedir para alterar ou excluir
  lançamentos que já existem, ou para criar algo além do lançamento simples:
  "muda o valor da parcela 3", "exclui essa série", "excluir os próximos",
  "troca a categoria desses lançamentos", "coloca a tag em todos", "divide esse
  lançamento", "transferir entre contas", "parcelar em 6 vezes", "lançamento
  recorrente", "dá baixa", "paguei só uma parte", "estorna o pagamento", "anexa
  a nota fiscal", "cadastra o fornecedor" — qualquer escrita que alcance mais de
  um lançamento, uma série, um lançamento dividido ou uma transferência.
metadata:
  version: "0.1.0"
---

# Escrita avançada

Complementa `granatum-fundamentos.md` e `novo-lancamento`. Tudo aqui grava nos
livros reais do cliente, sem simulação. O que cada ferramenta aceita e recusa
está na descrição dela; esta skill diz **quando perguntar, o que mostrar e o que
não decidir sozinho**.

## Três coisas que o usuário decide, nunca você

1. **O escopo da série** (`escopo_serie`): `so_este` ou `este_e_proximos`.
2. **A confirmação** (`confirmado: true`), depois de ver a prévia.
3. **A natureza da diferença num pagamento menor** (`desconto` ou
   `gerar_restante`).

Pergunte, espere a resposta e só então chame. Não deduza da frase do usuário
quando ela não diz.

## Série (parcelas e recorrência)

Em `atualizar_lancamento`, `excluir_lancamento`, `anexar_arquivo` e
`excluir_anexo`, um lançamento de série sem `escopo_serie` **não grava**: a
ferramenta devolve `status: "escopo_necessario"` com o tamanho da série
(`tamanho_da_serie`, que conta as parcelas **vivas**, ou `serie_sem_fim`) e a
posição. Quando vier também `total_gravado`, o total gravado é outro (excluir
parcela não o desce): diga os dois números ao usuário, sem tratar um como o
outro. Pergunte ao usuário:

- só esta ocorrência, as outras ficam como estão;
- esta e as seguintes.

**Regra do escopo.** Nunca preencha `escopo_serie` sem que o usuário tenha dito o escopo nesta conversa. Sem isso, chame a tool **sem** o parâmetro, deixe-a devolver `escopo_necessario` e pergunte. Exemplo:

> Usuário: "Exclui a ocorrência de 10/10 da assinatura de internet."
> Você: chama `excluir_lancamento` sem `escopo_serie`; a tool devolve `escopo_necessario`.
> Você: "É uma assinatura recorrente. Excluo só esta ocorrência ou esta e as próximas?"
> Usuário: "Só esta." Agora sim, chame com `escopo_serie: "so_este"`.

**Exceção: parcela de série de transferência.** Em `atualizar_lancamento` a tool **não** devolve `escopo_necessario` nessa parcela: sem `escopo_serie` ela grava só aquela parcela, como `so_este`, sem prévia. Pergunte o escopo **antes** da primeira chamada e envie `escopo_serie` explícito. `excluir_lancamento` pergunta como no lançamento.

Em lançamento que não é de série, não envie `escopo_serie`. `criar_lancamento` e
`registrar_pagamento` não têm esse campo: pagar ou estornar mexe só na
ocorrência pedida.

## Prévia e confirmação

Toda chamada que alcança mais de um lançamento (vários `lancamento_ids`,
`escopo_serie: "este_e_proximos"` ou `total_repeticoes`) **não grava na primeira
vez**. Devolve `status: "confirmacao_necessaria"` com a quantidade, quantos já
estão pagos (`ja_pagos`) e os pulados com o motivo.

**A quantidade conta por parcela.** Numa série de transferência cada parcela é
uma transferência, que são **dois lançamentos** (as duas pontas). A prévia traz
`quantidade_de_transferencias_a_alterar` (ou `_a_excluir`) e
`quantidade_de_lancamentos_a_alterar` (ou `_a_excluir`), e a dica diz, por
exemplo, "2 transferência(s) (4 lançamentos)". Repasse as duas contagens, para o
usuário não ler 4 lançamentos como 4 transferências.

1. Mostre a prévia ao usuário em linguagem direta: quantos serão alterados ou
   excluídos, quantos já estão pagos, o que fica de fora e por quê.
2. Pergunte se deve prosseguir.
3. Só depois de um "sim" explícito, chame de novo com **os mesmos argumentos**
   mais `confirmado: true`.

A segunda chamada grava e devolve o resultado real, que pode diferir da prévia
se algo mudou no intervalo: apresente o resultado, não a prévia. Nunca envie
`confirmado: true` por conta própria, nem para destravar o fluxo. Teto de 100
ids por chamada.

**Regra da confirmação.** `confirmado: true` só depois de mostrar ao usuário a prévia **daquele pedido exato** e de ele dizer sim. Se o conjunto de ids, o escopo ou os campos mudaram (por exemplo, ao tirar o id impedido), chame de novo **sem** `confirmado`, mostre a prévia nova e pergunte de novo. O "sim" à prévia antiga não vale para o pedido novo. Exemplo:

> Prévia: 3 ids, 1 em `impedidos` (conciliado). Usuário: "Então faz sem ele."
> Você: chama de novo com 2 ids, sem `confirmado`; a tool devolve a prévia nova.
> Você: "Sem o conciliado, serão excluídos 2 lançamentos (R$ ...). Confirma?"
> Usuário: "Sim." Só agora chame com `confirmado: true`.

Com um id e sem série não há prévia, exceto na exclusão de lançamento dividido
(abaixo).

### Quando algum id é impedido

Com vários ids, todo id pedido é alvo. Se algum está impedido pelo estado
(conciliado, pago até a data de bloqueio de caixa, com competência até a de
competência, saldo inicial, cobrança ou NFS-e
agendada, fatura de cartão; na exclusão e no pagamento, também transferência
com ponta impedida), **nada** é
alterado ou excluído: a prévia traz `impedidos` (cada id com `codigo` e
`descricao`; nos de período fechado, também `mensagem`, a frase da trava) e diz que nada será feito enquanto eles estiverem no pedido.
Confirmar com eles no pedido devolve erro e não grava.

**Transferência em `atualizar_lancamento` com vários ids** é sempre impedida,
por ser transferência (não por uma ponta), com a mensagem de que ela se altera
sozinha: refaça sem ela e altere a transferência num pedido à parte, com um id.

Mostre a lista ao usuário. Se ele quiser seguir com o restante, refaça a chamada
**sem** esses ids, e a prévia nova passa pela confirmação de novo. Id
inexistente ou de outra empresa recusa o pedido todo.

## Edição de lançamentos

`atualizar_lancamento` recebe `lancamento_ids` (de 1 a 100). Com vários ids, a
**mesma** alteração vale para cada um, e só os campos comuns são aceitos
(descrição, valor, categoria, centro, pessoa, forma, conta, vencimento,
competência, observação, documento e tags). `identificador_externo`, `itens_*` e
`escopo_serie` não valem com vários ids.

- Omitir um campo preserva o gravado; `0` nos vínculos (`pessoa_id`,
  `centro_custo_lucro_id`, `forma_pagamento_id`) remove. Envie só o delta que o
  usuário confirmou.
- **Tags**: `tags_adicionar` e `tags_remover` não substituem o conjunto, as
  outras ficam. Para "coloca a tag X em todos", use `tags_adicionar`.
- **Pagamento** não se edita aqui: em lançamento, `data_pagamento` é recusado.
  Dar baixa, trocar a data ou estornar é `registrar_pagamento`.
- **Cobrança ou NFS-e agendada**: só aceitam observação, documento, tipo de
  documento, categoria, centro, identificador externo e tags. Qualquer outra
  mudança é recusada (`cobranca_ou_nfse_agendada`); diga que isso se altera
  pelo sistema atual do Granatum.
- **Sem diferença**: o campo enviado com o valor que já está gravado conta como
  não enviado. Se nada difere, a ferramenta não grava e responde com o estado
  atual. Não diga ao usuário que alterou algo nesse caso.

### Lançamento dividido

Um dividido tem itens, e cada item é um lançamento com id próprio (os ids vêm de
`obter_lancamentos` com `lancamento_ids`: a linha traz `itens`).

- Valor, categoria, descrição, pessoa, centro, forma e tags são **de cada
  item**: use `itens_alterar`. Vencimento, competência, conta, documento e
  observação valem para o todo, no nível de cima.
- `itens_adicionar`, `itens_alterar` e `itens_remover` mexem nos itens. O item
  novo grava **só o que você enviar**: pessoa, centro, forma e tags não são
  copiados de outro item. Se o usuário quer os de outro item, leia-os antes e
  envie.
- Cada item diz o que é: `tipo` (`despesa` ou `receita`) é obrigatório no item
  novo e o valor é sempre positivo. O desconto ou a retenção é o item de tipo
  contrário ao dos outros.
- `tipo_lancamento` no nível de cima não vale num dividido; o tipo é do item
  (`itens_alterar[].tipo`), e a pessoa do item precisa ter o papel do tipo novo.
- Pedido de valor, descrição ou tipo sobre um dividido de 2 ou mais itens,
  junto de outros ids, volta como `pedido_nao_se_aplica_aos_alvos`, sem
  alterar nada. Tire o dividido do pedido ou use `itens_alterar`.
- Para tirar um item: `itens_remover`. Para apagar o lançamento inteiro:
  `excluir_lancamento`.

### Mudar o total de parcelas de uma série (`total_repeticoes`)

`atualizar_lancamento` com `total_repeticoes` aumenta ou diminui o número de
parcelas de uma série **limitada** (lançamento, dividido ou transferência).
"Passa de 6 para 12 parcelas", "tira as parcelas depois da 8ª".

- O usuário diz o **novo total** (contando todas as parcelas); não deduza o
  número da frase. Vale a série inteira: não pergunte `escopo_serie` quando o
  total é o único campo do pedido, e só com **um** id, sem `itens_*` no mesmo
  pedido.
- **Nunca grava na primeira vez.** A prévia (`confirmacao_necessaria`) traz
  `quantidade_de_parcelas_a_criar` e `quantidade_de_parcelas_a_excluir`. Mostre
  as duas, diga que as novas são cópias da última parcela em aberto (em aberto,
  sem identificador externo) e que diminuir **exclui** as parcelas em aberto
  acima do novo total, e só confirme depois do "sim" à prévia. Se o total pedido
  é o já gravado, nada muda: diga isso ao usuário.
- **Avulso que vira série:** `total_repeticoes` com `periodicidade` (`DS`, `D1`,
  `D7`, `D15`, `M1`, `M2`, `M3`, `M6` ou `M12`; `DS` é segunda a sexta). Pergunte
  a periodicidade se o usuário não disse, e confirme a quantidade, porque cada
  parcela nova é um lançamento real. `total_repeticoes` sem `periodicidade` num
  avulso é recusado (`periodicidade_obrigatoria`). **A periodicidade de uma série
  existente não muda**: se o usuário pede para trocar mensal por semanal, diga
  que não dá por aqui.
- **Recusas, repasse o motivo e não contorne:** parcela paga ou com cobrança
  depois da pedida trava a redução (`total_travado_por_parcela_posterior`); série
  sem fim não se edita (`repeticao_nao_editavel`); total menor que 2, menor que
  o número da parcela pedida ou acima de 35 anos (`total_fora_dos_limites`);
  série com parcelas de outros criadores, para quem só vê os próprios
  lançamentos (`serie_com_parcelas_de_outros_criadores`).
- Se todas as parcelas vivas estão pagas, o valor das novas vem de uma parcela
  já baixada e a resposta traz o aviso `valor_copiado_de_parcela_baixada`:
  repasse o aviso ao usuário na prévia, para ele saber de onde vem o valor das
  novas.

## Exclusão

`excluir_lancamento` (`lancamento_ids`, de 1 a 100). Só com pedido direto e
inequívoco, identificando o que sai. Série pergunta o escopo; vários ids e
`este_e_proximos` passam pela prévia.

- **Dividido**: o id de qualquer item exclui o lançamento **inteiro**, nunca só
  o item, e isso sempre passa pela prévia, que traz a quantidade de itens, o
  valor total e a lista (`lancamentos_divididos`). Diga ao usuário que o
  lançamento sai inteiro, com os N itens listados. Para tirar só um item, não
  use a exclusão: `itens_remover` em `atualizar_lancamento`.
- **Série com `este_e_proximos`**: os próximos já pagos ficam e aparecem em
  `pulados`; só saem com `excluir_pagos: true`, que o usuário precisa pedir.
- **Transferência**: o id de qualquer ponta serve, e excluir uma exclui as
  duas. Numa parcela de série de transferência, `escopo_serie` aceita `so_este`
  (só o par da parcela pedida) e `este_e_proximos` (a pedida e as seguintes, com
  prévia e confirmado), e `excluir_pagos` vale como no lançamento: cada parcela
  sai sempre com as duas pontas, e a parcela que o estado impede em qualquer das
  pontas fica como está e aparece em `pulados`. Em série **sem fim**, as parcelas
  que sobram deixam de repetir nas duas pontas.
- Se a resposta vier `nao_excluido` (conciliado, pago no caixa fechado, competência fechada, saldo
  inicial), nada foi excluído; repasse o motivo.

## Transferência entre contas

`criar_lancamento` com `tipo_lancamento: "transferencia"`. Campos e regras:

- `conta_id` é a conta de **origem**, `conta_destino_id` a de destino; valor,
  vencimento e descrição obrigatórios. Categoria, pessoa, forma, itens e
  `identificador_externo` são recusados (a transferência tem um identificador
  por ponta: `identificador_externo_origem` e `identificador_externo_destino`,
  opcionais).
- **Repetição:** a transferência aceita `repeticao`, como o lançamento
  (`periodicidade` com `total_repeticoes` **ou** `infinito: true`). Cada
  ocorrência é um **par de pontas**, todas no mesmo `grupo_id`, com as mesmas
  tags e centro. **Só a 1ª nasce paga** (se houver `data_pagamento`) e os
  identificadores externos ficam só na 1ª. **Confirme a quantidade com o
  usuário dizendo que cada ocorrência são dois lançamentos reais** ("12
  transferências, 24 lançamentos"). A resposta traz as pontas da 1ª ocorrência.
- **Sem `data_pagamento`, ela nasce em aberto**, qualquer que seja o vencimento.
  Para uma transferência que já aconteceu, informe `data_pagamento` (hoje ou
  passada); o vencimento fica como veio. Pergunte a data se o usuário disse só
  "transferi".
- Em aberto, ela **não se efetiva sozinha**. `pagamento_automatico: true` só
  quando o usuário pediu explicitamente.
- Duplicata de identificador: mesma regra do lançamento (`confirmacao_necessaria`
  e `confirmar_duplicata` só depois do "sim"). Se a resposta se perder, confira
  com `obter_lancamentos` antes de repetir.
- Editar: `atualizar_lancamento` com o id de qualquer ponta; vale para as duas.
  `data_vencimento` muda só o vencimento e **não** baixa nem reabre; para dar
  baixa, `data_pagamento` (e `""` reabre), **mas prefira `registrar_pagamento`**
  para a baixa (veja o último item desta lista); `data_pagamento` aqui só quando
  a baixa vai junto de outra edição da mesma transferência. Ponta conciliada não muda valor,
  conta nem data de pagamento. Com a competência até a data de bloqueio de
  competência ela também não muda (valor, contas, descrição, competência), mas
  o vencimento passa; paga até a data de bloqueio de caixa, não muda nada.
- **Parcela de série de transferência:** `escopo_serie` vale (o padrão é
  `so_este`, que muda só aquela parcela, e ela segue na série), e
  `este_e_proximos` leva o que mudou também às parcelas seguintes, os dois
  lançamentos de cada uma, **com prévia e `confirmado`**. Atenção: aqui a tool
  não devolve `escopo_necessario`; sem `escopo_serie` ela grava só a parcela
  pedida. Pergunte o escopo **antes** da primeira chamada e envie `escopo_serie`
  explícito. Só o que difere da pedida propaga; o vencimento anda
  a partir do pedido, um período por parcela; a conta de origem e a de destino
  vão cada uma para a sua ponta; a **baixa** (`data_pagamento`) e os
  identificadores externos ficam só na parcela pedida; a parcela seguinte já paga
  também muda, salvo a protegida por bloqueio, que fica como está e aparece em
  `pulados`.
- Efetivar, trocar a data ou estornar (`pago: false`) uma transferência é `registrar_pagamento` (a preferência: aceita vários ids e pedido misto) com o id de
  qualquer ponta: vale para as duas, cada uma na sua conta, com um id ou com vários. Só a data:
  `valor_pago`, `desconto`, `gerar_restante` e `conta_id` são recusados (`transferencia_so_com_data`);
  para mudar conta ou valor, `atualizar_lancamento`.

## Repetição e dividido na criação

- `repeticao` (`periodicidade` e `total_repeticoes` **ou** `infinito: true`,
  nunca os dois): **confirme a quantidade antes**, porque cada ocorrência é um
  lançamento real (na transferência, um par de pontas). A resposta traz
  `repeticao.grupo_id` e `quantidade_criada`. Para mudar depois o número de
  parcelas, `total_repeticoes` em `atualizar_lancamento` (acima).
- `itens`: o total é a soma dos itens; `valor`, `categoria_id` e os demais
  campos do nível de cima **não** se informam. Cada item leva a sua categoria
  e o seu `tipo`.

## Pessoa

`criar_pessoa` só depois de `buscar_pessoas` por nome ou nome fantasia: o mesmo
nome repetido é aceito e duplicaria o cadastro. Só `nome` e `papel` são
obrigatórios. Use só os campos que a ferramenta oferece: dados de cadastro que ela
não recebe, não peça ao usuário; oriente-o a completá-los pela tela do Granatum.
Editar e excluir pessoa não existem aqui.

## Pagamento e anexos

Dar baixa, trocar a data, pagar valor diferente, estornar, e tudo de anexos:
`pagamento-e-anexos.md`. Pontos que não se negociam:

- Nunca presuma "pagou hoje": confirme a data.
- Descrição (`descricao`, e a de cada item): só a pontuação do português. A seta
  (→), emojis e símbolos decorativos são recusados (`erro_validacao`). **Antes de
  montar a prévia**, troque esses caracteres por texto ("de A para B", "-") ou
  avise o usuário do que vai mudar, para a descrição gravada ser a mostrada na
  prévia. Vale na criação (inclusive de transferência) e na edição.
- Baixa, troca de data e transferência pedidas juntas vão numa chamada só de
  `registrar_pagamento`, com uma prévia só; com vários ids, um impedido segura o
  pedido inteiro e a lista vai ao usuário.
- Pagar menos que o valor: pergunte se a diferença é desconto ou saldo a pagar
  depois.
- Estorno: não afirme que o valor voltou ao que era antes da baixa.
- Competência fechada: juros, multa e desconto viram lançamento próprio; nunca
  ofereça o restante (`gerar_restante` é recusado). Veja a referência.
- Trava de período fechado: repasse a frase da recusa e não contorne.
- Anexo: só diga que anexou depois que a confirmação devolver `anexado`.

## Erros que não se resolvem ajustando dados

- `-32002` `escopo_insuficiente`: conexão sem permissão de escrita; ver
  `granatum-fundamentos.md`. Pare e oriente a reconectar.
- Argumento que não existe no schema é recusado, com todos os erros de uma vez.
  Não invente parâmetro.
