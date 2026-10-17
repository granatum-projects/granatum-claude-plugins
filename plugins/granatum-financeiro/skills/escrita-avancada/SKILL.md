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

Complementa `granatum-fundamentos` e `novo-lancamento`. Tudo aqui grava nos
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
(`tamanho_da_serie`, ou `serie_sem_fim`) e a posição. Pergunte ao usuário:

- só esta ocorrência, as outras ficam como estão;
- esta e as seguintes.

**Regra do escopo.** Nunca preencha `escopo_serie` sem que o usuário tenha dito o escopo nesta conversa. Sem isso, chame a tool **sem** o parâmetro, deixe-a devolver `escopo_necessario` e pergunte. Exemplo:

> Usuário: "Exclui a ocorrência de 10/10 da assinatura de internet."
> Você: chama `excluir_lancamento` sem `escopo_serie`; a tool devolve `escopo_necessario`.
> Você: "É uma assinatura recorrente. Excluo só esta ocorrência ou esta e as próximas?"
> Usuário: "Só esta." Agora sim, chame com `escopo_serie: "so_este"`.

Em lançamento que não é de série, não envie `escopo_serie`. `criar_lancamento`
e `registrar_pagamento` não têm esse campo: pagar ou estornar mexe só na
ocorrência pedida.

## Prévia e confirmação

Toda chamada que alcança mais de um lançamento (vários `lancamento_ids`, ou
`escopo_serie: "este_e_proximos"`) **não grava na primeira vez**. Devolve
`status: "confirmacao_necessaria"` com a quantidade, quantos já estão pagos
(`ja_pagos`) e os pulados com o motivo.

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
agendada, fatura de cartão, transferência com ponta impedida), **nada** é
alterado ou excluído: a prévia traz `impedidos` (cada id com `codigo` e
`descricao`; nos de período fechado, também `mensagem`, a frase da trava) e diz que nada será feito enquanto eles estiverem no pedido.
Confirmar com eles no pedido devolve erro e não grava.

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
  duas.
- Se a resposta vier `nao_excluido` (conciliado, pago no caixa fechado, competência fechada, saldo
  inicial), nada foi excluído; repasse o motivo.

## Transferência entre contas

`criar_lancamento` com `tipo_lancamento: "transferencia"`. Campos e regras:

- `conta_id` é a conta de **origem**, `conta_destino_id` a de destino; valor,
  vencimento e descrição obrigatórios. Categoria, pessoa, forma, repetição,
  itens e `identificador_externo` são recusados (a transferência tem um
  identificador por ponta: `identificador_externo_origem` e
  `identificador_externo_destino`, opcionais).
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
  baixa, `data_pagamento`, e `""` reabre. Ponta conciliada não muda valor,
  conta nem data de pagamento. Com a competência até a data de bloqueio de
  competência ela também não muda (valor, contas, descrição, competência), mas
  o vencimento passa; paga até a data de bloqueio de caixa, não muda nada.
- Pagar ou estornar uma transferência não é por `registrar_pagamento` (recusa).

## Repetição e dividido na criação

- `repeticao` (`periodicidade` e `total_repeticoes` **ou** `infinito: true`,
  nunca os dois): **confirme a quantidade antes**, porque cada ocorrência é um
  lançamento real. A resposta traz `repeticao.grupo_id` e `quantidade_criada`.
- `itens`: o total é a soma dos itens; `valor`, `categoria_id` e os demais
  campos do nível de cima **não** se informam. Cada item leva a sua categoria
  e o seu `tipo`.

## Pessoa

`criar_pessoa` só depois de `buscar_pessoas` por nome ou documento: o mesmo
nome repetido é aceito e duplicaria o cadastro. Só `nome` e `papel` são
obrigatórios; nunca invente documento. Use só os campos que a ferramenta oferece:
se ela não tiver campo de documento, não peça o documento ao usuário e oriente-o a
preenchê-lo pela tela do Granatum. Editar e excluir pessoa não existem aqui.

## Pagamento e anexos

Dar baixa, trocar a data, pagar valor diferente, estornar, e tudo de anexos:
`references/pagamento-e-anexos.md`. Pontos que não se negociam:

- Nunca presuma "pagou hoje": confirme a data.
- Pagar menos que o valor: pergunte se a diferença é desconto ou saldo a pagar
  depois.
- Estorno: não afirme que o valor voltou ao que era antes da baixa.
- Competência fechada: juros, multa e desconto viram lançamento próprio; nunca
  ofereça o restante (`gerar_restante` é recusado). Veja a referência.
- Trava de período fechado: repasse a frase da recusa e não contorne.
- Anexo: só diga que anexou depois que a confirmação devolver `anexado`.

## Erros que não se resolvem ajustando dados

- `-32002` `escopo_insuficiente`: conexão sem permissão de escrita; ver
  `granatum-fundamentos`. Pare e oriente a reconectar.
- Argumento que não existe no schema é recusado, com todos os erros de uma vez.
  Não invente parâmetro.
