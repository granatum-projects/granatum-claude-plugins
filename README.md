# Granatum — plugins para o Claude Code

Marketplace oficial dos plugins do [Granatum](https://www.granatum.com.br).

## Instalação

```
/plugin marketplace add webgoal/granatum-claude-plugins
/plugin install granatum-financeiro@granatum
```

Para fixar uma versão:

```
/plugin marketplace add webgoal/granatum-claude-plugins@v1.0.0
```

## Plugins

| Plugin | O que faz |
| --- | --- |
| [`granatum-financeiro`](./plugins/granatum-financeiro) | Relatórios (DRE e fluxo de caixa), consulta de lançamentos e criação de lançamentos com confirmação obrigatória, via conector MCP do Granatum |

## Desenvolvimento

Testar um plugin localmente, sem instalar:

```
claude --plugin-dir ./plugins/granatum-financeiro
```

Validar antes de publicar ou submeter:

```
claude plugin validate ./plugins/granatum-financeiro
claude plugin validate .          # valida o marketplace.json
```

Depois de editar um plugin numa sessão aberta, `/reload-plugins`.

## Estrutura

```
.claude-plugin/marketplace.json     catálogo do marketplace
plugins/<nome>/
  .claude-plugin/plugin.json        manifesto do plugin
  .mcp.json                         conectores MCP
  skills/<nome>/SKILL.md            skills e comandos
```

Nada além de `plugin.json` vai dentro de `.claude-plugin/` — `skills/`, `.mcp.json`
e afins ficam na raiz do plugin.
