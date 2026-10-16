# Pagamento e anexos

Consultar ao dar baixa, trocar a data de um pagamento, estornar, pagar parte do
valor ou mexer em anexos de lançamento. As regras de confirmação, série e
prévia estão em `../SKILL.md`.

## Pagamento: `registrar_pagamento`

O parâmetro `pago` decide a operação:

| Pedido | Argumentos |
|---|---|
| Dar baixa | `pago: true` e `data_pagamento` (`YYYY-MM-DD`; confirme a data com o usuário, nunca presuma "hoje") |
| Trocar a data de um pago | `pago: true` e a `data_pagamento` nova; valor e conta não mudam |
| Estornar | `pago: false`, sem `data_pagamento` |

**Valor diferente do lançamento** (`valor_pago`, só com um id e em lançamento em aberto):

- Igual: quita.
- Maior: a diferença é juros e multa.
- Menor: o usuário escolhe, e você pergunta. Nunca escolha sozinho.
  - `desconto: true`: o lançamento fica pago pelo valor informado e a diferença vira desconto.
  - `gerar_restante: true` (baixa parcial): o lançamento fica pago pelo valor informado e a diferença nasce como um novo lançamento em aberto, "Diferença ref.: …", com o mesmo vencimento, categoria, pessoa e demais dados do original, na conta original.
- `desconto` e `gerar_restante` se excluem. Pagar menos sem nenhum dos dois é recusado.
- `conta_id` informa a conta em que o dinheiro entrou ou saiu, quando difere da do lançamento. O restante fica sempre na conta original.

A resposta traz `valor_original` (o valor antes desta baixa), `valor_pago` e `diferenca` (`juros`, `desconto` ou `parcial`). Na baixa parcial traz também `valor_restante` e `lancamentos_restantes` (os ids criados). Em dividido nasce um restante por item que ficou com diferença; com dois ou mais, eles nascem agrupados num dividido novo, e a resposta traz `lancamento_composto_dos_restantes_id`. O restante é um lançamento comum e independente do original, sem vínculo. Para mudar o vencimento dele, use `atualizar_lancamento`.

**Estorno.** Limpa só a data de pagamento. O valor do lançamento não volta ao que era antes da baixa (juros, desconto e baixa parcial reescrevem o valor). Todo estorno responde com o mesmo aviso fixo, sem número. Repasse o aviso ao usuário e não prometa nem afirme um valor anterior: o estorno não sabe se a baixa teve juros, desconto ou restante. Um restante gerado pela baixa continua em aberto e não é apagado.

Outras regras:

- Série: paga ou estorna só a ocorrência pedida, nunca as próximas; não há `escopo_serie`.
- Dividido: o id de qualquer item paga o lançamento inteiro, só os itens em aberto (um item já pago fica como está, data e valor), e estorna o lançamento inteiro.
- Transferência não tem baixa aqui: é recusada. A baixa dela é `atualizar_lancamento` com `data_pagamento` (hoje ou passada), e `data_vencimento` não baixa nem reabre.
- Em lançamento, `atualizar_lancamento` não aceita `data_pagamento`: o pagamento é desta tool.
- Recusas comuns: data futura ou anterior ao bloqueio de caixa, lançamento conciliado, cobrança ativa, NFS-e agendada para o recebimento.

## Anexos

**Listar.** `obter_lancamentos` com `campos_adicionais: ["anexos"]` traz, por lançamento, `id`, `nome`, `tipo` e `tamanho_bytes` de cada anexo. Num dividido o anexo aparece em todos os itens; numa transferência, nas duas pontas. A lista nunca traz o link.

**Baixar.** `obter_anexo` com o `anexo_id` devolve um link temporário (30 minutos), com nome, tipo e tamanho. Você recebe só o link, não o arquivo. Entregue o link apenas ao usuário que pediu, não o repita nem o guarde; vencido, peça outro.

**Anexar.** `anexar_arquivo` é em duas chamadas, e o arquivo nunca vai como argumento nem volta em resposta.

1. Pedir o envio: `lancamento_id`, `nome_arquivo` (com a extensão) e `tamanho_bytes` (de 1 byte a 5 MB, 5242880). Nada foi anexado. A tool devolve `status: "envio_pendente"`, o `envio_id`, o endereço, os campos, a validade (10 minutos) e um `exemplo_de_comando`, um `curl` pronto.
2. Enviar: só se você consegue executar o comando com acesso à rede (shell, como no Claude Code). Execute o `exemplo_de_comando`, trocando `<caminho do arquivo>` pelo caminho real. O esperado é HTTP 204.
3. Confirmar: chame de novo com `lancamento_id` e `envio_id`, sem `nome_arquivo` nem `tamanho_bytes`. A tool devolve `status: "anexado"` com o anexo criado.

Se você não consegue executar o comando com acesso à rede (é o caso comum em apps de conversa):

- Não insista, não tente outro caminho e não afirme que anexou.
- Explique ao usuário e oriente-o a anexar pela tela do lançamento no Granatum.

Só diga que anexou depois que a confirmação devolver `anexado`. Antes disso nada foi anexado. Se a confirmação voltar com `arquivo_nao_enviado` (o arquivo não chegou, o link venceu ou o envio já foi confirmado), peça um envio novo, uma vez, e envie de novo; se falhar outra vez, oriente o usuário a anexar pela interface. Não repita o pedido de envio para o mesmo arquivo além disso.

O link de envio, os campos e o `envio_id` são credenciais temporárias: não os mostre ao usuário nem os repita.

Em lançamento de série, a confirmação exige `escopo_serie`. Sem ele a tool devolve `escopo_necessario` e não anexa; o arquivo já enviado e o `envio_id` continuam valendo. Pergunte ao usuário e, com a resposta, confirme com o **mesmo** `envio_id`: não peça outro envio nem envie o arquivo de novo (um envio por arquivo). `so_este` anexa só a esse lançamento; `este_e_proximos` põe o mesmo arquivo nesse e nos seguintes (a resposta diz em quantos, em `lancamentos_alcancados`), de uma vez e sem prévia: não escolha por conta própria.

**Excluir.** `excluir_anexo` com o `anexo_id` (da lista de anexos). Confirme com o usuário qual anexo será excluído. Anexo posto em vários lançamentos de uma série exige `escopo_serie`; sem ele a tool devolve `escopo_necessario`. `so_este` exclui só desse lançamento, e os outros continuam com o arquivo. `este_e_proximos` entra no protocolo de confirmação: a prévia traz a quantidade, os lançamentos afetados (`lancamentos_afetados`) e se o arquivo sairia do armazenamento (`arquivo_sera_apagado`). Em anexo que não é de série, não envie `escopo_serie`.

Perfis: "Somente relatórios" lista e baixa anexos, mas não anexa nem exclui. "Lançamentos por usuário" só mexe em anexo de lançamento que ele criou.
