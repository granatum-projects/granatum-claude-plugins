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
7. Rode **`/granatum-config`** — ele confirma a conexão e mostra as empresas às
   quais você tem acesso. É a forma mais rápida de saber que deu tudo certo.

### No Claude Code (terminal)

```
/plugin marketplace add granatum-projects/granatum-claude-plugins
/plugin install granatum-financeiro@granatum
```

### Sobre a autorização

Na primeira vez, o Claude abre a tela do Granatum para você entrar e autorizar.
A autorização é única: você concede todas as permissões pedidas ou nenhuma — não
dá para liberar só a consulta e recusar o registro de lançamentos.

Quem controla isso é o próprio Claude, nas permissões de ferramentas. Lá você
pode bloquear as ferramentas de escrita (`criar_lancamento`,
`atualizar_lancamento`, `excluir_lancamento`) e manter as de leitura liberadas,
ou marcar as de escrita como **sempre perguntar** — assim cada gravação passa
pela sua confirmação.

Independentemente disso, o plugin sempre mostra um resumo e espera você
confirmar antes de criar um lançamento.

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
