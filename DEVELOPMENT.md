# Desenvolvimento

Guia de quem mexe neste repositório. Para instalar e usar, veja o
[README](./README.md).

## O que este repositório é

Um **marketplace** de plugins do Claude Code — um catálogo, não um plugin. O
catálogo é o `.claude-plugin/marketplace.json` da raiz; cada plugin vive numa
pasta sob `plugins/`.

```
.claude-plugin/marketplace.json     catálogo: nome do marketplace e lista de plugins
plugins/<nome>/
  .claude-plugin/plugin.json        manifesto do plugin
  .mcp.json                         conectores MCP
  skills/<nome>/SKILL.md            skills e comandos
  README.md                         documentação de quem usa o plugin
```

Só o `plugin.json` mora dentro de `.claude-plugin/`. `skills/`, `.mcp.json` e o
resto ficam na raiz do plugin — trocar isso é o erro mais comum, e o sintoma é
um plugin que carrega sem nenhuma skill.

## Rodar sem instalar

```bash
claude --plugin-dir ./plugins/granatum-financeiro
```

Tem precedência sobre uma versão já instalada com o mesmo nome, então dá para
testar uma alteração sem desinstalar nada. Depois de editar durante uma sessão
aberta, `/reload-plugins`.

## Validar

```bash
claude plugin validate ./plugins/granatum-financeiro --strict
claude plugin validate .          # valida o marketplace.json
```

O pipeline de review da Anthropic roda a mesma checagem em toda submissão.
`--strict` trata warnings como erro.

## Autenticação do conector

O `.mcp.json` declara `oauth.clientId` em vez de deixar o Claude Code descobrir
sozinho. É necessário: a API do Granatum **não** tem Dynamic Client
Registration (`/oauth/register` responde 404 por decisão), e sem o client_id
estático o Claude Code aborta na descoberta, com "does not support dynamic
client registration".

O client é `claude-code`, público — um CLI distribuído não tem onde guardar
segredo, e quem protege o fluxo é o PKCE. Não confundir com o client `claude`,
que é o conector do claude.ai e tem outro redirect registrado.

Não fixamos `callbackPort`: o Claude Code sorteia uma porta a cada tentativa, e
o servidor aceita qualquer porta de loopback (RFC 8252 §7.3). Fixar a porta
faria o fluxo falhar sempre que ela estivesse ocupada na máquina do usuário.

## Apontar para staging

Durante uma validação, troque a `url` do `.mcp.json` para
`https://api.ww2.granatum.com.br/v1/mcp`. **Devolva para produção antes
de publicar ou submeter** — é uma troca fácil de esquecer, e o plugin publicado
apontando para staging não funciona para ninguém.

## Publicar uma versão

1. Suba a `version` no `plugin.json` do plugin. Sem isso, quem já instalou não
   recebe a atualização.
2. Mantenha a `metadata.version` do `marketplace.json` coerente com ela.
3. Commit, push e tag:

   ```bash
   git tag -a v1.0.0 -m "descrição da versão"
   git push origin v1.0.0
   ```

   A tag é o que permite ao usuário fixar a versão com `@v1.0.0`.

## Submeter ao diretório da comunidade

O repositório precisa ser público: a aprovação fixa um commit SHA no catálogo
`anthropics/claude-plugins-community`, e o CI atualiza o pin conforme você faz
push. Rode `claude plugin validate` antes.

Formulário: [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)
(autores individuais) ou o portal de diretório do claude.ai (orgs Team e
Enterprise). Nenhum dos dois leva ao marketplace oficial da Anthropic, que é
curado a critério dela.

O Connectors Directory é outra submissão, do servidor MCP sozinho — não deste
repositório.
