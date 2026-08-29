# Granatum Financeiro

Conecta o Claude ao Granatum da sua empresa. Depois de instalado, dá para pedir
relatórios, consultar lançamentos e registrar movimentos conversando
normalmente — sem abrir o sistema.

## Instalação

1. Abra o arquivo `granatum-financeiro.plugin` que você recebeu.
2. Clique em **Instalar**.
3. Na primeira vez que usar, o Claude vai pedir para você conectar sua conta
   Granatum. Autorize com o mesmo login que você já usa no sistema. Se quiser
   poder registrar lançamentos pelo Claude, e não só consultar, autorize também
   a permissão de escrita nessa etapa.
4. Digite `/granatum-config` para confirmar que está tudo funcionando.

Não é preciso configurar chave de API, servidor ou variável de ambiente. A
autorização é feita pela sua própria conta Granatum, e o Claude só enxerga o
que o seu usuário já enxerga.

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
julho", "o que vence essa semana", "quanto gastei com energia esse ano".

## Antes de registrar qualquer coisa

O Claude **sempre** mostra um resumo e espera sua confirmação antes de criar um
lançamento. Nada é gravado sem você dizer que pode.

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

**Pede autenticação de novo:** reconecte o Granatum nas configurações de
conectores.

**Diz que não tem permissão para registrar lançamentos:** ao conectar o
Granatum, é possível autorizar só a consulta ou também o registro. Se você
autorizou apenas a consulta, os relatórios funcionam normalmente mas criar ou
editar lançamentos não. Reconecte o Granatum e autorize também a escrita.

**Relatório vem todo zerado:** normalmente não é falta de dados. Costuma ser
categoria fora da árvore da DRE ou período informado errado. Peça ao Claude para
verificar — ele sabe diagnosticar isso.

**Não acha uma categoria para lançar:** o Granatum só aceita lançamento em
categoria final, não nas que servem para agrupar. Peça as opções disponíveis e
escolha uma delas.

**Lançamento em série ou transferência:** esses precisam ser editados na
interface do Granatum. O plugin trabalha com lançamentos simples.

## Componentes

- **1 conector MCP** — Granatum (produção)
- **8 skills** — 7 comandos e uma base de comportamento (`granatum-fundamentos`)
  que carrega as regras de regime contábil e os guardrails de escrita em toda
  interação
