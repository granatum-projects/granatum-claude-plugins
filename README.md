# Granatum para o Claude

Conecte o Claude ao Granatum da sua empresa e peça relatórios, consulte
lançamentos e registre movimentos conversando normalmente — sem abrir o sistema.

## Instalação

No Claude Code, rode:

```
/plugin marketplace add granatum-projects/granatum-claude-plugins
/plugin install granatum-financeiro@granatum
```

Na primeira vez que usar, o Claude pede para você conectar sua conta Granatum.
Autorize com o mesmo login que já usa no sistema. Depois, `/granatum-config`
confirma que está tudo funcionando.

Não é preciso configurar chave de API, servidor ou variável de ambiente.

## Plugins disponíveis

| Plugin | O que faz |
| --- | --- |
| [`granatum-financeiro`](./plugins/granatum-financeiro) | Fluxo de caixa, DRE, consulta de lançamentos e registro de receitas e despesas |

Cada plugin tem seu próprio README com os comandos, o que esperar e o que fazer
quando algo não funciona. Para o `granatum-financeiro`, veja
[plugins/granatum-financeiro/README.md](./plugins/granatum-financeiro/README.md).

## Fixar uma versão

Por padrão você acompanha a versão mais recente. Para travar numa específica:

```
/plugin marketplace add granatum-projects/granatum-claude-plugins@v1.0.0
```

## Suporte

***REMOVED***

---

Quem for contribuir com o repositório: veja [DEVELOPMENT.md](./DEVELOPMENT.md).
