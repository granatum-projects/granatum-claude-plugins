# Granatum Financeiro

Conecta o Claude ao Granatum da sua empresa. Depois de instalado, dá para pedir
relatórios, consultar lançamentos e registrar movimentos conversando
normalmente — sem abrir o sistema.

## Instalação

### No Claude (site ou aplicativo)

1. **Configurações → Plugins → Adicionar Marketplace → Adicionar de um repositório**
2. Informe `https://github.com/granatum-projects/granatum-claude-plugins`
3. Clique no **+** para adicionar o Granatum Financeiro
4. **Vincule sua conta Granatum** — sem esta etapa o plugin não funciona
5. **Comece uma conversa nova** para o Claude reconhecer o plugin
6. Rode **`/granatum-config`** para confirmar a conexão e ver suas empresas

### No Claude Code

```
/plugin marketplace add granatum-projects/granatum-claude-plugins
/plugin install granatum-financeiro@granatum
```

### Autorização

Ao conectar, você entra com o mesmo login que já usa no Granatum. A autorização
é única: são todas as permissões pedidas ou nenhuma — não há como liberar só a
consulta e recusar o registro de lançamentos.

Se você quer usar o plugin apenas para consultar, o controle está nas permissões
de ferramentas do próprio Claude: bloqueie as ferramentas de escrita
(`criar_lancamento`, `atualizar_lancamento`, `excluir_lancamento`,
`registrar_pagamento`, `criar_pessoa`, `anexar_arquivo` e `excluir_anexo`), ou
marque-as como **sempre perguntar**.

Não tem conta ainda, ou esqueceu a senha? A própria tela de login tem os links
para cadastrar-se e recuperar a senha.

Depois, digite `/granatum-config` para confirmar que está tudo funcionando.

Não é preciso configurar chave de API, servidor ou variável de ambiente. O
Claude só enxerga o que o seu usuário já enxerga.

## Comandos

| Comando | O que faz |
| --- | --- |
| `/granatum-config` | Conecta a empresa e confere se está tudo certo |
| `/resumo-mes` | Visão geral do mês: caixa, resultado e destaques |
| `/pendencias` | O que está vencido e o que vence a seguir |
| `/fluxo-caixa` | Entradas, saídas e saldo por período |
| `/dre` | Resultado, margens e EBITDA por período |
| `/extrato` | Lista e busca lançamentos individuais |
| `/novo-lancamento` | Registra uma receita ou despesa |

Os comandos são atalhos. Perguntar em linguagem normal funciona igual: "como foi
julho", "o que vence essa semana", "quanto gastei com energia esse ano", "quais
despesas de agosto estão sem tag", "quanto o setor Comercial gastou no
trimestre", "quantas parcelas do notebook ainda faltam".

## O que o Claude faz por você

Além das consultas, ele registra e altera movimentos conversando:

- **Criar** receita, despesa, parcelamento, recorrência, lançamento dividido em
  itens e transferência entre contas; cadastrar cliente ou fornecedor novo.
- **Alterar** um lançamento, vários de uma vez, uma parcela ou o restante de uma
  série, os itens de um lançamento dividido, tags e transferências.
- **Excluir** um lançamento, vários, uma parcela ou o restante de uma série, um
  lançamento dividido inteiro ou uma transferência.
- **Pagar**: dar baixa, trocar a data do pagamento, pagar com juros, desconto ou
  só uma parte (a diferença vira um novo lançamento em aberto) e estornar.
- **Anexos**: listar, baixar o link de um anexo, anexar e excluir (em duas
  chamadas; anexar depende de o ambiente conseguir enviar o arquivo, e o
  Claude avisa quando não consegue).
- **Saldo** das contas num dia que já passou, ou dia a dia numa conta
  (inclusive previsto, que é estimativa).

## Antes de registrar qualquer coisa

O Claude **sempre** mostra um resumo e espera sua confirmação antes de criar um
lançamento. Nada é gravado sem você dizer que pode.

Quando um pedido alcança mais de um lançamento (vários de uma vez, ou "este e os
próximos" de uma série), ele **não grava na primeira vez**: mostra a prévia, com
quantos serão alterados, quantos já estão pagos e o que fica de fora, e só
grava depois da sua confirmação. Numa série, ele pergunta se é só aquela
ocorrência ou ela e as seguintes. Excluir um item de um lançamento dividido
exclui o lançamento inteiro, e o Claude mostra os itens antes. Se algum
lançamento do pedido estiver travado (conciliado, em período bloqueado), nada é
alterado e ele diz quais.

Se o Granatum apontar que já existe um lançamento parecido, o Claude mostra o
que encontrou e pergunta se é para criar mesmo assim. Ele nunca decide isso
sozinho.

## Uma diferença que vale entender

Os dois relatórios contam coisas diferentes, e é normal que não batam:

- **Fluxo de caixa** conta o que entrou e saiu de fato, pela data de pagamento.
  Boleto emitido e não pago não aparece.
- **DRE** conta pelo fato gerador, tenha sido pago ou não. Uma nota faturada em
  julho entra em julho, mesmo que o cliente pague em setembro.

O Claude sempre diz qual dos dois está usando. Se os números divergirem muito, é
justamente essa diferença — e vale perguntar a ele o porquê.

## Se algo não funcionar

**O plugin aparece instalado mas nada funciona:** provavelmente falta vincular a
conta Granatum — instalar e autorizar são duas etapas separadas. Verifique a
conexão nas configurações do plugin.

**O Claude não parece conhecer os comandos:** comece uma conversa nova. Conversas
abertas antes da instalação podem não reconhecer o plugin.

**Pede autenticação de novo:** reconecte o Granatum nas configurações de
conectores.

**Diz que não tem permissão para registrar lançamentos:** verifique se as
ferramentas de escrita não estão bloqueadas nas permissões de ferramentas do
Claude. Se não for isso, reconecte o Granatum — a autorização pode ter sido
concedida antes de o seu usuário ter permissão de lançamento no sistema.

**Relatório vem todo zerado:** normalmente não é falta de dados. Costuma ser
categoria fora da árvore da DRE ou período informado errado. Peça ao Claude para
verificar — ele sabe diagnosticar isso.

**Não acha uma categoria para lançar:** o Granatum só aceita lançamento em
categoria final, não nas que servem para agrupar. Peça as opções disponíveis e
escolha uma delas.

**Lançamento com cobrança ou NFS-e agendada:** só aceita alterar observação,
documento, categoria, centro de custo, identificador e tags. Valor, vencimento,
conta e o resto se alteram pelo sistema do Granatum; o Claude avisa quando é o
caso.

**Lançamento conciliado ou em período bloqueado:** não muda de valor, conta nem
data de pagamento, e o Claude diz o motivo em vez de tentar de novo.

**Anexar arquivo não funcionou:** depende de o Claude conseguir executar um
comando com acesso à rede (é o caso do Claude Code). Onde não consegue, ele
explica e orienta a anexar pela tela do lançamento no Granatum.

## Componentes

- **1 conector MCP** — Granatum (produção)
- **9 skills** — 7 comandos e duas bases de comportamento: `granatum-fundamentos`
  (regras de regime contábil e guardrails de escrita, em toda interação) e
  `escrita-avancada` (série, prévia e confirmação, dividido, transferência,
  pagamento e anexos)
- **18 ferramentas** do conector: 11 de consulta e 7 que gravam

## Privacidade

O plugin conversa com o servidor MCP do Granatum usando a sua conta. O
tratamento dos dados segue a [Política de Privacidade do
Granatum](https://contas.granatum.com.br/politica-de-privacidade).
