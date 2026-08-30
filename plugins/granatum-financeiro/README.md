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
de ferramentas do próprio Claude: bloqueie `criar_lancamento`,
`atualizar_lancamento` e `excluir_lancamento`, ou marque-as como **sempre
perguntar**.

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

**Lançamento em série ou transferência:** esses precisam ser editados na
interface do Granatum. O plugin trabalha com lançamentos simples.

## Componentes

- **1 conector MCP** — Granatum (produção)
- **8 skills** — 7 comandos e uma base de comportamento (`granatum-fundamentos`)
  que carrega as regras de regime contábil e os guardrails de escrita em toda
  interação
