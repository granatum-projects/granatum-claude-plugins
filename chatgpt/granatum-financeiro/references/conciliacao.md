---
name: conciliacao
description: Esta skill deve ser usada quando o usuário pedir para conciliar o extrato bancário ou perguntar pelas conciliações pendentes: "o que tenho pendente de conciliação", "concilia o extrato", "quais movimentos do banco faltam conciliar", "concilia as confiáveis", "desfaz essa conciliação", "desconcilia", "ignora esse movimento", "restaura o movimento", "esse movimento é a soma de dois lançamentos" — qualquer pedido de ligar movimentos do extrato a lançamentos do Granatum, de ignorar ou restaurar um movimento ou de desfazer essa ligação.
---

# Conciliação bancária

Conciliar é ligar um movimento do extrato bancário a um lançamento do Granatum. Se o lançamento estava em aberto, a conciliação dá a baixa com a data do movimento e a conta do extrato. Este fluxo usa quatro tools: `obter_conciliacoes_pendentes` (lê), `conciliar`, `desconciliar` e `ignorar_movimentos` (escrevem, com prévia e confirmação); `obter_lancamentos` acha os lançamentos. Siga também as regras de escrita da referência `granatum-fundamentos.md` e a empresa já resolvida (`wgi_conta_id`, o ID da empresa; `conta_id` é a conta bancária).

## O que não se negocia

1. **Um "sim" só, e ele é a resposta à prévia.** `conciliar`, `desconciliar` e `ignorar_movimentos` sem `confirmado: true` não gravam e devolvem `confirmacao_necessaria`. O pedido do usuário para conciliar ("pode conciliar") autoriza **só a prévia**. Mostre a contagem e o que cada ação faz e **termine a resposta ali**, perguntando "concilio estes 12?". Só repita **os mesmos pares** com `confirmado: true` na resposta seguinte a uma mensagem do usuário que veio **depois** da prévia e a aceita. "Pode", "sim" ou "confirma" ditos **antes** da prévia (inclusive à contagem das confiáveis) nunca valem como confirmação. **Nunca chame `conciliar` (ou `desconciliar`, ou `ignorar_movimentos`) duas vezes na mesma resposta**: a prévia e o `confirmado: true` ficam em respostas diferentes. Nunca autoconfirme. Se o pedido mudar (um par a menos, outro lançamento), é prévia nova, e ela também se mostra, com o fim da resposta, antes de confirmar.
2. **Passe `wgi_conta_id` (a empresa) em toda chamada** de `obter_conciliacoes_pendentes`, `conciliar`, `desconciliar` e `ignorar_movimentos`, prévia e confirmação. Sem ele a tool recusa.
3. **Nunca promova "Revisar" a confiável.** Quem diz o que é confiável é o servidor (`grau: "confiavel"`). Você não reclassifica: movimento em `revisar` ou `sem_sugestao` só é conciliado depois de o usuário escolher o lançamento.
4. **Nunca contorne o bloqueio.** Movimento com `bloqueio` não se concilia à força: não troque datas, não apague e recrie o lançamento, não mude a conta para fugir da trava. Mostre o motivo e as opções que a resposta traz, **com as palavras do servidor** (`motivo`/`bloqueio`): não suponha nem acrescente causa que ele não disse.

## Quem pode

Só os perfis Administrador e Lançamentos conciliam. Para os outros, as tools de escrita e a leitura das pendências recusam com "Seu perfil nesta empresa não dá acesso à conciliação". **Não insista** nem tente outra tool de conciliação: diga ao usuário que o perfil dele nesta empresa não dá acesso e que o administrador da empresa pode orientar. Lançamentos continuam disponíveis em `obter_lancamentos`.

## Fluxo

### 1. "Quais conciliações estão pendentes?"

Chame `obter_conciliacoes_pendentes` **sem `conta_id`**. Vem o resumo por conta, nos últimos 90 dias (a resposta diz o período; passe `periodo_inicio` e `periodo_fim` para outro): quantos movimentos pendentes, quantos `confiavel`, `revisar`, `sem_sugestao` e quantos `bloqueados` (os bloqueados já contam em `revisar`). Conte isso ao usuário em poucas linhas, por conta, e pergunte por onde ele quer começar. Não concilie nada ainda.

### 2. Listar uma conta

Chame de novo com `conta_id`, `periodo_inicio` e `periodo_fim` (no máximo 92 dias). Cada movimento vem com:

- `grau`: `confiavel`, `revisar` ou `sem_sugestao`;
- `motivo`: a razão do grau, escrita;
- `bloqueio`, quando existir: o motivo e as `opcoes`;
- até 5 `candidatos`, cada um com `lancamento_id`, valor, datas, conta, pessoa e `acao`.

A lista é paginada: siga `proxima_pagina` mantendo filtros e `ordenacao` (veja `truncado` e `total_disponivel`). O filtro `grau` ajuda a separar os grupos. Valor positivo é entrada, negativo é saída.

### 3. As confiáveis: contar, mostrar a prévia e só então o "sim"

As confiáveis são os movimentos com `grau: "confiavel"` (filtro `grau: "confiavel"`; o bloqueado nunca entra aqui). Diga a quantidade: **"38 confiáveis."** A contagem só informa; ela não é uma pergunta de confirmação, e um "sim" a ela não grava nada. Pergunte, por exemplo, **"12 confiáveis, concilio?"**. Mostre uma amostra se o usuário quiser ver.

Quando o usuário pedir para conciliar ("pode conciliar as confiáveis"), isso autoriza **só a prévia**: chame `conciliar` **sem `confirmado`**, com os pares `{movimento_id, lancamento_id}`, usando o **primeiro candidato** de cada movimento confiável, no máximo 100 pares por chamada. Com mais de 100 confiáveis, é **um lote por rodada**: prévia do 1º lote, o "sim", a confirmação, e só então a prévia do lote seguinte (nunca dois `conciliar` na mesma resposta). Mostre ao usuário a contagem e o que as ações fazem, **termine a resposta ali** e pergunte **"concilio estes 38?"**:

| `acao` | O que acontece no lançamento |
|---|---|
| `vincular` | Só liga ao movimento; o lançamento já estava pago no mesmo dia e na mesma conta e não muda |
| `baixar` | Lançamento em aberto recebe a baixa com a data do movimento e a conta do extrato. Se o lançamento é de **outra conta** (`conta_antes_id` diferente de `conta_depois_id` na prévia), diga ao usuário que a baixa leva o lançamento para a conta do extrato |
| `mudar_data_do_pagamento` | Já pago em outra data: a data do pagamento passa a ser a do movimento |
| `mudar_conta` | Já pago em outra conta: passa para a conta do extrato |
| `mudar_data_do_pagamento_e_conta` | As duas coisas |

Quando a ação muda o lançamento (todas menos `vincular`), vale o **caixa fechado**: se a data de pagamento antiga ou a nova cai até a data de bloqueio de caixa da empresa, o par é recusado, e o pedido inteiro com ele (veja a seção do 409). Movimento importado por CSV também é recusado.

Só quando o usuário responder a essa prévia, numa mensagem nova, aceitando, repita o pedido com `confirmado: true` (na resposta seguinte, nunca na mesma da prévia) e informe quantos foram conciliados (`conciliados`) e o que mudou. Se ele pedir outra coisa em vez de aceitar (menos um par, outro lançamento), é prévia nova.

Errado: "Pode conciliar as confiáveis." → `conciliar` sem `confirmado` e, na mesma resposta, `conciliar` com `confirmado: true`. Certo: prévia e fim da resposta; "Sim." → `confirmado: true`.

### 4. As bloqueadas: mostrar as opções

Movimento com `bloqueio` é o que o servidor sabe que seria recusado. Repita o `motivo` que ele deu, sem supor outra causa (quando o motivo é o caixa fechado, vem a data `caixa_bloqueado_ate`). Mostre o `motivo` e as opções, em linguagem simples, sem mudar o motivo do servidor:

1. **Voltar a data de bloqueio** (`voltar_data_de_bloqueio`): quem tem permissão ajusta a data de bloqueio de caixa na tela do Granatum; depois pede-se a conciliação de novo. O MCP não muda essa data.
2. **Deixar pendente** (`deixar_pendente`).
3. **Conciliar com outro candidato** (`conciliar_com_outro_candidato`, só quando a opção traz `lancamento_ids`): outro lançamento fora do bloqueio. Ele vem como "Revisar": apresente-o e deixe o usuário confirmar a escolha antes.

Movimento **importado por CSV** também vem com bloqueio (`conciliar_na_tela`, sem candidatos): o MCP não concilia movimento de CSV. Oriente o usuário a conciliá-lo na tela de conciliação do Granatum, ou a deixá-lo pendente.

### 5. As de "Revisar": o usuário escolhe

Para cada movimento em `revisar` (sem bloqueio), **antes de qualquer chamada de `conciliar`** (nem a prévia), mostre o movimento (data, descrição, valor), o `motivo` e os candidatos (descrição, pessoa, datas, conta, `acao`), e peça a escolha; só depois da escolha chame a prévia. Os motivos mais comuns: mais de um lançamento com o mesmo valor, lançamento de **outra conta** (conciliar o move para a conta do extrato) ou um lançamento de valor parecido que vence mais perto da data. Com o lançamento escolhido pelo usuário, concilie como em 3: prévia, fim da resposta e o "sim" do usuário à prévia. Nunca escolha por ele.

### 6. As sem sugestão, e o movimento que é a soma de vários lançamentos

`sem_sugestao` quer dizer que não há lançamento sem vínculo, do mesmo sinal e com o valor exato, dentro da janela (em aberto com vencimento a até 30 dias, ou já pago a até 3 dias). **Sempre tente `obter_lancamentos`** antes de dizer que o movimento fica para a tela, procurando pela data e pelo valor do movimento (e, se preciso, por pessoa ou período mais largo): `conciliar` aceita qualquer lançamento sem vínculo, em aberto ou já pago, com o mesmo sinal e o valor exato ao centavo, de qualquer conta, mesmo fora da janela e mesmo que não tenha sido sugerido. Se achar, mostre ao usuário e concilie com prévia.

**Vários lançamentos para um movimento.** Se o valor do movimento é a **soma** de mais de um lançamento (por exemplo, um boleto que paga duas notas), ou o usuário diz isso, procure os lançamentos com `obter_lancamentos` e concilie com `lancamento_ids` no par: `{movimento_id, lancamento_ids: [..]}` (no máximo 100 lançamentos por pedido). A soma é **com sinal** (receita positiva, despesa negativa: +100,00 e -2,00 valem um movimento de +98,00) e tem de bater **ao centavo**, sem tolerância; se não bater, o par é recusado com `valor_diferente` (a mensagem diz o valor do movimento e a soma) e você **não tenta outra combinação por conta própria nem força**: mostre ao usuário. Um par traz `lancamento_id` **ou** `lancamento_ids`, nunca os dois nem nenhum (`lancamento_id_e_lancamento_ids`, `lancamento_id_ou_lancamento_ids_obrigatorio`).

**O dividido** (um lançamento de vários itens) entra **inteiro**: nomeado qualquer item, todos os itens entram, e a soma é a dos itens. Para achá-lo pelo total do movimento, chame `obter_lancamentos` com `agrupar_divididos: true` e `valor_min` e `valor_max` iguais ao valor do movimento (em módulo): o dividido vem como **uma linha**, com `valor` igual ao total dos itens, `ids_dos_itens` e `quantidade_itens`; passe **qualquer** id de `ids_dos_itens` ao `conciliar`. Item já conciliado recusa o par. Cada linha traz `conciliado` (verdadeiro quando tem vínculo; na linha agrupada, quando algum item tem). Se a linha agrupada traz `parte_de_dividido`, o dividido tem itens em outras datas, e a soma que vale é a de **todos** os itens (`itens_do_dividido`), não só os da linha. No perfil Lançamentos por usuário a linha agrupada com um item só visível sai sem `ids_dos_itens` e com o valor desse item; esse perfil não concilia.

Na resposta do `conciliar`, `conciliados` e `quantidade_a_conciliar` contam **lançamentos** (o dividido conta cada item), e `movimentos_conciliados` e `quantidade_de_movimentos` contam movimentos: diga os dois ao usuário ("2 lançamentos, 1 movimento").

Se não achar nada, diga que o movimento fica para a tela do Granatum (criar o lançamento a partir do movimento é de lá).

### 7. Quando o pedido é recusado (409)

Se algum par estiver impedido, o pedido **inteiro** é recusado e **nada é gravado**. A resposta vem com `status: "erro"`, `codigo: "alvos_impedidos"` e `impedidos`, cada um com o `movimento_id`, o `lancamento_id` (ausente quando o motivo é do par, como a soma que não bate) e o motivo (caixa fechado, movimento ou lançamento já conciliado, par que deixou de valer, soma diferente, o mesmo dividido em dois pares, movimento de CSV, id inexistente). Isso costuma ser algo que mudou entre a leitura e a confirmação. Conte ao usuário, com os motivos que o servidor deu: **"2 mudaram desde a consulta: (motivos). Concilio as outras 36?"** Essa pergunta autoriza só a prévia: com a resposta dele, repita **sem os impedidos e sem `confirmado`**, mostre a prévia nova, **termine a resposta ali** e confirme só na resposta seguinte a um "sim" dado **depois** dessa prévia. Não retente o mesmo pedido nem tente contornar o impedimento.

### 8. Desconciliar

Para desfazer, use `desconciliar` com `movimento_ids` ou, **quando o usuário falar do lançamento** ("desfaz a conciliação daquele pagamento de 678,78"), com `lancamento_ids` (até 100; um ou outro, nunca os dois; cada lançamento resolve para o movimento do seu vínculo ativo, e o lançamento que não está conciliado volta como impedido, "o lançamento não está conciliado"). Ache os ids com `obter_lancamentos`. Vale a mesma regra: prévia (sem `confirmado`), fim da resposta e `confirmado: true` só depois do "sim" do usuário a ela. Explique o que a prévia diz de cada um:

- **Com o estado de antes da conciliação (snapshot):** o lançamento volta pelo que era antes: a data de pagamento (se era em aberto, volta a em aberto), o vencimento e o valor. O já pago e conciliado no mesmo dia volta igual.
- **Sem snapshot (conciliação antiga):** só o vínculo sai. **O lançamento continua pago**, e reabrir é o estorno (`registrar_pagamento` com `pago: false`), que é outro pedido. Só informe isso ao usuário; **não ofereça** preparar o estorno nem pergunte se ele quer. Se ele pedir o estorno, aí é um pedido novo, com o próprio "sim".
- **A conta não volta.** A resposta diz em que conta o lançamento ficou; avise o usuário.
- O caixa fechado também vale: se a restauração mudar uma data até a data de bloqueio de caixa, o movimento é recusado, o pedido inteiro não grava, e a resposta lista o motivo de cada um; refaça sem eles, como no 409 acima.
- **O desfazer alcança o grupo inteiro.** O movimento de vários lançamentos desfaz todos; o lançamento ligado a outros movimentos leva todos eles; o dividido volta item a item. A prévia lista cada vínculo, e `pelo_grupo: true` marca o que entrou pelo grupo e não foi nomeado: diga ao usuário quais são antes do "sim".
- **Lançamento conciliado não se edita, não se paga de novo nem se exclui.** `atualizar_lancamento` (valor, conta), `registrar_pagamento` (troca da data, estorno) e `excluir_lancamento` recusam o conciliado, e a recusa aponta o `desconciliar` (perfis Administrador e Lançamentos; os outros, a interface do Granatum). Diante disso, **proponha desconciliar antes** (com prévia e o "sim"), e só depois refaça o pedido original; não contorne.

### 9. Ignorar e restaurar um movimento

Movimento que o usuário não quer conciliar (tarifa duplicada, lançamento que não é da empresa) se **ignora** com `ignorar_movimentos` (`movimento_ids`, de 1 a 100); ele sai das pendências. Com `desfazer: true` o movimento ignorado é **restaurado** e volta às pendências. Só os perfis Administrador e Lançamentos. Vale a mesma regra de escrita: sem `confirmado: true` é a prévia (`quantidade_a_ignorar` ou `quantidade_a_restaurar`, com data, descrição e valor de cada movimento); mostre, **termine a resposta ali**, e só confirme depois do "sim" do usuário à prévia. Só muda o movimento no extrato (e o status da importação de que ele veio): nenhum lançamento, vínculo ou saldo muda.

Recusas, por movimento, que recusam o pedido inteiro (`alvos_impedidos`, nada gravado): de outra empresa ou inexistente (`movimento_nao_encontrado`), já ignorado (`movimento_ja_ignorado`), não ignorado ao restaurar (`movimento_nao_ignorado`), **conciliado** (`movimento_conciliado`: desconcilie antes, com `desconciliar`) e de origem que o MCP não trata (`movimento_de_importacao_csv`: fica na tela do Granatum). Na recusa, conte ao usuário os motivos e, se ele quiser o restante, refaça sem os impedidos com prévia nova ("ignoro os outros 36?"). O ignorar não tem caixa fechado.

## O que fica na tela do Granatum

O MCP não faz, e você encaminha o usuário à tela de conciliação do Granatum:

- conciliar com **valor diferente** (ajustar, registrar a diferença, baixa parcial);
- juntar **vários movimentos num lançamento**;
- **criar** lançamento ou transferência a partir do movimento;
- ver duplicadas;
- importar OFX, conectar banco, cancelar cobrança ao conciliar;
- **voltar a data de bloqueio** (a pessoa com permissão faz na tela);
- movimentos importados por **CSV**.

## Antipadrões

- Não confirme por conta própria, nem na primeira chamada de `conciliar` ou `desconciliar`.
- Não trate o "pode" do pedido, nem o "sim" à contagem, como confirmação: o "sim" que vale é o da prévia, dado depois dela.
- Não chame `conciliar`, `desconciliar` nem `ignorar_movimentos` duas vezes na mesma resposta (prévia e confirmação).
- Não omita `wgi_conta_id` em nenhuma das tools.
- Não suponha o motivo de um bloqueio ("deve ser caixa fechado"): repita o `motivo` que o servidor deu.
- Não conte como "confiáveis" mais do que o servidor marcou `confiavel`, e não some as bloqueadas nelas.
- Não mande parâmetro opcional vazio ou zero (`conta_id: 0`, `grau: ""`, `periodo_inicio: ""`): omita-o.
- Não vá direto à prévia de um movimento em `revisar`: mostre o candidato e peça a escolha antes.
- Não escolha o lançamento de um movimento em `revisar` ou `sem_sugestao`.
- Não suponha, ao reler, que as páginas acabaram: siga `proxima_pagina`.
- Não afirme que conciliou antes da resposta dizer `status: "conciliado"` (ou `"desconciliado"`, `"ignorado"`, `"restaurado"`).
- Não prometa que o desconciliar reabre um lançamento sem snapshot nem que a conta volta.
- Não tente outra combinação de lançamentos quando a soma não bate, nem force: mostre o valor do movimento e a soma que o servidor disse.
- Não ignore movimento conciliado (desconcilie antes) nem edite, pague de novo ou exclua lançamento conciliado sem desconciliar.
- Não escreva "conciliados" como se contasse movimentos: conta lançamentos.
