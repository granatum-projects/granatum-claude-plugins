# Granatum para o Claude

Conecte o Claude ao Granatum da sua empresa e peça relatórios, consulte
lançamentos e registre movimentos conversando normalmente — sem abrir o sistema.

## Instalação

### No Claude (site ou aplicativo)

1. Abra **Configurações → Plugins**.
2. Clique em **Adicionar Marketplace** e escolha **Adicionar de um repositório**.
3. Informe a URL deste repositório:

   ```
   https://github.com/granatum-projects/granatum-claude-plugins
   ```

4. Clique no **+** para adicionar o **Granatum Financeiro**.
5. **Vincule sua conta Granatum.** Esta etapa não é opcional: sem ela o plugin
   aparece instalado, mas nenhuma consulta funciona. Autorize com o mesmo login
   que você já usa no Granatum.
6. **Comece uma conversa nova.** Conversas já abertas podem não reconhecer o
   plugin recém-instalado.

### No Claude Code (terminal)

```
/plugin marketplace add granatum-projects/granatum-claude-plugins
/plugin install granatum-financeiro@granatum
```

### Sobre a autorização

Na primeira vez, o Claude abre a tela do Granatum para você entrar e autorizar.
Se quiser registrar lançamentos pelo Claude, e não só consultar, autorize também
a permissão de escrita nessa etapa — sem ela os relatórios funcionam, mas criar
ou editar lançamentos não.

Depois de conectar, `/granatum-config` confirma que está tudo funcionando.

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

[Fale com a gente](https://www.granatum.com.br/financeiro/contato)

---

Quem for contribuir com o repositório: veja [DEVELOPMENT.md](./DEVELOPMENT.md).
