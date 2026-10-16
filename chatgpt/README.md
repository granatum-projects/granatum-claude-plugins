# Skill do ChatGPT

`granatum-financeiro/` é a fonte da skill do Granatum Financeiro publicada no ChatGPT
(`SKILL.md` + `references/`, incluídos no pacote OpenAI completo).

- **Deriva das skills do plugin.** As referências são as skills de
  `plugins/granatum-financeiro/skills/` consolidadas numa só: cada `SKILL.md` do plugin
  vira um arquivo em `references/` (`regras-de-campo.md` e `pagamento-e-anexos.md` vêm das
  `references/` das skills), com os caminhos entre arquivos ajustados para a pasta plana.
  O `SKILL.md` daqui é o índice e está em inglês, como foi publicado; as referências
  são em português. Ao mudar uma skill do plugin, refaça a referência correspondente e suba a
  `version` do `metadata`.
- **A versão publicada é a do `metadata.version`** do `SKILL.md`, e acompanha a do plugin
  (`plugins/granatum-financeiro/.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json`):
  a mudança seguinte sobe as três juntas (decisão do humano em 2026-10-15; 1.2.4 foi a primeira
  alinhada). O histórico desta pasta mostra o que estava publicado (1.0.0) e o que mudou.
- **Publicação é manual, por ZIP completo do plugin OpenAI.** Na raiz do repositório:

  ```bash
  python3 scripts/gerar_pacote_openai.py
  ```

  O resultado é `~/Downloads/granatum-financeiro-openai-<versão>.zip`, com manifesto
  nativo, configuração MCP, skill consolidada e ícone. A pasta desta skill sozinha
  não é o pacote completo. Fontes, validações e instruções de envio estão em
  [`openai/README.md`](../openai/README.md).

  O humano faz o upload no painel da OpenAI no dia do deploy do MCP em production
  (`docs/operacao/DEPLOYMENT.md`, passo 3, do `granatum-v2`). Nada aqui é publicado por pipeline.
