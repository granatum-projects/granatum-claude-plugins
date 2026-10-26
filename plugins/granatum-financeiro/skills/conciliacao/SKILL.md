---
name: conciliacao
description: Esta skill deve ser usada quando o usuário pedir para conciliar o extrato bancário ou perguntar pelas conciliações pendentes: "o que tenho pendente de conciliação", "concilia o extrato", "quais movimentos do banco faltam conciliar", "concilia as que estão claras", "desfaz essa conciliação", "desconcilia" — qualquer pedido de ligar movimentos do extrato a lançamentos do Granatum ou de desfazer essa ligação.
---

# Conciliação bancária

Conciliar é ligar um movimento do extrato bancário a um lançamento do Granatum. Se o lançamento estava em aberto, a conciliação dá a baixa com a data do movimento e a conta do extrato. Este fluxo usa três tools: `obter_conciliacoes_pendentes` (lê), `conciliar` e `desconciliar` (escrevem, com prévia e confirmação). Siga também as regras de escrita da skill `granatum-fundamentos` e a empresa já resolvida (`wgi_conta_id`, o ID da empresa; `conta_id` é a conta bancária).

## O que não se negocia

1. **Nunca confirme sem mostrar a prévia.** `conciliar` e `desconciliar` sem `confirmado: true` não gravam e devolvem `confirmacao_necessaria`. Mostre a contagem e o que cada ação faz, espere o "sim" do usuário e só então repita **os mesmos pares** com `confirmado: true`. Nunca autoconfirme. Se o pedido mudar (um par a menos, outro lançamento), é prévia nova, e ela também se mostra antes de confirmar.
2. **Nunca promova "Revisar" a claro.** Quem diz o que é claro é o servidor (`grau: "confiavel"`). Você não reclassifica: movimento em `revisar` ou `sem_sugestao` só é conciliado depois de o usuário escolher o lançamento.
3. **Nunca contorne o bloqueio.** Movimento com `bloqueio` não se concilia à força: não troque datas, não apague e recrie o lançamento, não mude a conta para fugir da trava. Mostre o motivo e as opções que a resposta traz.

## Quem pode

Só os perfis Administrador e Lançamentos conciliam. Para os outros, as três tools recusam com "Seu perfil nesta empresa não dá acesso à conciliação". **Não insista** nem tente outra tool de conciliação: diga ao usuário que o perfil dele nesta empresa não dá acesso e que o administrador da empresa pode orientar. Lançamentos continuam disponíveis em `obter_lancamentos`.

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

### 3. As claras: contar e pedir o "sim"

As claras são os movimentos com `grau: "confiavel"` (filtro `grau: "confiavel"`; o bloqueado nunca entra aqui). Diga a quantidade e peça a decisão: **"38 claras, confirma?"** Mostre uma amostra se o usuário quiser ver. Só com o "sim" chame `conciliar` com os pares `{movimento_id, lancamento_id}`, usando o **primeiro candidato** de cada movimento claro, de até 100 em 100 (divida em chamadas se passar de 100).

A primeira chamada é a prévia. Mostre ao usuário a contagem e o que as ações fazem:

| `acao` | O que acontece no lançamento |
|---|---|
| `vincular` | Só liga ao movimento; o lançamento já estava pago no mesmo dia e na mesma conta e não muda |
| `baixar` | Lançamento em aberto recebe a baixa com a data do movimento e a conta do extrato |
| `mudar_data_do_pagamento` | Já pago em outra data: a data do pagamento passa a ser a do movimento |
| `mudar_conta` | Já pago em outra conta: passa para a conta do extrato |
| `mudar_data_do_pagamento_e_conta` | As duas coisas |

Depois do "sim", repita o pedido com `confirmado: true` e informe quantos foram conciliados (`conciliados`) e o que mudou.

### 4. As bloqueadas: mostrar as opções

Movimento com `bloqueio` é o que o servidor sabe que seria recusado, em geral porque o **caixa está fechado** (a data de bloqueio de caixa da empresa, `caixa_bloqueado_ate`): a baixa, ou a mudança de data ou de conta, cairia no período fechado. Mostre o `motivo` e as opções, com as palavras do usuário:

1. **Voltar a data de bloqueio** (`voltar_data_de_bloqueio`): quem tem permissão ajusta a data de bloqueio de caixa na tela do Granatum; depois pede-se a conciliação de novo. O MCP não muda essa data.
2. **Deixar pendente** (`deixar_pendente`).
3. **Conciliar com outro candidato** (`conciliar_com_outro_candidato`, só quando a opção traz `lancamento_ids`): outro lançamento fora do bloqueio. Ele vem como "Revisar": apresente-o e deixe o usuário confirmar a escolha antes.

Movimento **importado por CSV** também vem com bloqueio (`conciliar_na_tela`, sem candidatos): o MCP não concilia movimento de CSV. Oriente o usuário a conciliá-lo na tela de conciliação do Granatum, ou a deixá-lo pendente.

### 5. As de "Revisar": o usuário escolhe

Para cada movimento em `revisar` (sem bloqueio), mostre o movimento (data, descrição, valor), o `motivo` e os candidatos (descrição, pessoa, datas, conta, `acao`), e peça a escolha. Os motivos mais comuns: mais de um lançamento com o mesmo valor, lançamento de **outra conta** (conciliar o move para a conta do extrato) ou um lançamento de valor parecido que vence mais perto da data. Com o lançamento escolhido, concilie como em 3, com prévia e "sim". Nunca escolha por ele.

### 6. As sem sugestão

`sem_sugestao` quer dizer que não há lançamento sem vínculo, do mesmo sinal e com o valor exato, dentro da janela (em aberto com vencimento a até 30 dias, ou já pago a até 3 dias). Antes de desistir, **procure outro lançamento** com `obter_lancamentos` (por exemplo por pessoa, valor ou período mais largo): `conciliar` aceita qualquer lançamento sem vínculo, em aberto ou já pago, com o mesmo sinal e o **valor exato ao centavo**, de qualquer conta, mesmo fora da janela e mesmo que não tenha sido sugerido. Se achar, mostre ao usuário e concilie com prévia. Se não achar, diga que o movimento fica para a tela do Granatum (criar o lançamento a partir do movimento é de lá).

### 7. Quando o pedido é recusado (409)

Se algum par estiver impedido, o pedido **inteiro** é recusado e **nada é gravado**. A resposta vem com `status: "erro"`, `codigo: "alvos_impedidos"` e `impedidos`, cada um com o `movimento_id`, o `lancamento_id` e o motivo (caixa fechado, movimento ou lançamento já conciliado, par que deixou de valer, movimento de CSV, id inexistente). Isso costuma ser algo que mudou entre a leitura e o "sim". Conte ao usuário: **"2 mudaram desde a consulta: (motivos). Concilio as outras 36?"** Com o "sim", repita **sem os impedidos**, mostre a prévia nova e confirme só depois do "sim" dela. Não retente o mesmo pedido nem tente contornar o impedimento.

### 8. Desconciliar

Para desfazer, use `desconciliar` com os `movimento_ids` (até 100), com a mesma prévia e o mesmo "sim". Explique o que a prévia diz de cada um:

- **Com o estado de antes da conciliação (snapshot):** o lançamento volta pelo que era antes: a data de pagamento (se era em aberto, volta a em aberto), o vencimento e o valor. O já pago e conciliado no mesmo dia volta igual.
- **Sem snapshot (conciliação antiga):** só o vínculo sai. **O lançamento continua pago**, e reabrir é o estorno (`registrar_pagamento` com `pago: false`), que é outro pedido, com o próprio "sim".
- **A conta não volta.** A resposta diz em que conta o lançamento ficou; avise o usuário.
- O caixa fechado também vale: se a restauração mudar uma data até a data de bloqueio de caixa, o movimento é recusado, o pedido inteiro não grava, e a resposta lista o motivo de cada um; refaça sem eles, como no 409 acima.
- Se o lançamento tem outro movimento conciliado, só aquele vínculo sai.

## O que fica na tela do Granatum

O MCP não faz, e você encaminha o usuário à tela de conciliação do Granatum:

- conciliar com **valor diferente** (ajustar, registrar a diferença, baixa parcial);
- ligar **vários lançamentos a um movimento**, ou juntar movimentos;
- **criar** lançamento ou transferência a partir do movimento;
- **ignorar** e restaurar movimentos, ver duplicadas;
- importar OFX, conectar banco, cancelar cobrança ao conciliar;
- **voltar a data de bloqueio** (a pessoa com permissão faz na tela);
- movimentos importados por **CSV**.

## Antipadrões

- Não confirme por conta própria, nem na primeira chamada de `conciliar` ou `desconciliar`.
- Não conte como "claras" mais do que o servidor marcou `confiavel`, e não some as bloqueadas nelas.
- Não escolha o lançamento de um movimento em `revisar` ou `sem_sugestao`.
- Não suponha, ao reler, que as páginas acabaram: siga `proxima_pagina`.
- Não afirme que conciliou antes da resposta dizer `status: "conciliado"` (ou `"desconciliado"`).
- Não prometa que o desconciliar reabre um lançamento sem snapshot nem que a conta volta.
