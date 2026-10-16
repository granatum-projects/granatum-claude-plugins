# Gerar o pacote OpenAI

Na raiz deste repositório, com Python 3.10 ou superior (sem dependências externas):

```bash
python3 scripts/gerar_pacote_openai.py
```

Gera `~/Downloads/granatum-financeiro-openai-<versão>.zip`. Para escolher outra pasta:

```bash
python3 scripts/gerar_pacote_openai.py --destino /tmp/pacotes-granatum
```

O caminho do repositório é calculado a partir do script; também funciona em outro
worktree ou quando chamado por caminho absoluto. A geração não altera os fontes.
Se o ZIP já existir, o script encerra com erro: escolha outra pasta ou mova o ZIP
anterior para preservá-lo antes de gerar novamente.

## Fontes do pacote

- `plugins/granatum-financeiro/.claude-plugin/plugin.json`: versão,
  autor, repositório, licença e palavras-chave.
- `.claude-plugin/marketplace.json`: conferência da versão.
- `chatgpt/granatum-financeiro/`: skill consolidada e referências Markdown,
  copiadas sem alterar seu conteúdo. Atualize as referências quando mudar as
  skills do plugin Claude; o gerador não faz essa consolidação.
- `plugins/granatum-financeiro/.mcp.json`: endereço do servidor. Deve ser
  `https://api.ww2.granatum.com.br/v1/mcp`; staging causa erro. O campo Claude
  `type: "http"` é removido na configuração Codex. Outros campos exigem revisão
  explícita da conversão, evitando descartá-los silenciosamente.
- `plugins/granatum-financeiro/assets/icon.png` e `LICENSE`: imagem e licença.
- `openai/listing.json`: identificador `name`, texto da listagem e metadados
  específicos da OpenAI.
  O texto principal e as sugestões estão em português do Brasil; há tradução
  opcional da listagem em `en-US`. Revise os links de suporte,
  privacidade e termos antes do envio. Versão e caminhos de componentes são
  definidos pelo gerador, sem duplicação neste arquivo.

As versões do plugin, do marketplace e do `metadata.version` da skill devem
coincidir. Para uma nova versão, atualize os três antes de executar o script.

## Estrutura do ZIP

```text
.codex-plugin/plugin.json
.mcp.json
skills/granatum-financeiro/SKILL.md
skills/granatum-financeiro/references/*.md
assets/icon.png
LICENSE
```

Esses arquivos ficam diretamente na raiz do ZIP. Não compacte a pasta do
marketplace nem envie somente a pasta da skill. O manifesto nativo declara
`skills: "./skills/"` e `mcpServers: "./.mcp.json"`.

O script verifica versões, endpoint de produção, campos básicos da listagem,
caminhos de imagens, dimensões do ícone PNG, links Markdown locais e integridade
do ZIP. Usa uma pasta temporária limpa e uma lista explícita de fontes, sem
incluir `.git`, credenciais ou ZIPs anteriores. Imprime o SHA256 do resultado.
As mesmas entradas geram o mesmo ZIP no mesmo ambiente Python/zlib.

## Identificador do plugin existente

O `name` OpenAI vem de `openai/listing.json` e deve permanecer
`app-6a32a7da351c81919db830cd602abcf5`, conforme o identificador exigido pelo
portal para atualizar o plugin existente. Ele é independente do nome do plugin
Claude (`granatum-financeiro`) e do nome exibido (`interface.displayName`,
“Granatum Financeiro”). Não substitua esse identificador ao gerar novas versões
para o mesmo plugin; o portal recusa o ZIP se o `name` não corresponder.

## Categoria e propósito

Use `interface.category: "Finance"`: o propósito principal é gestão financeira
empresarial para empresários e equipes financeiras. Subtítulo, descrição,
capacidades e exemplos devem deixar claras as tarefas de contas a pagar e a
receber, saldos, fluxo de caixa, DRE e registros de receitas e despesas no Granatum.
A categoria anterior, `Productivity`, era genérica para esse propósito.

A categoria `Finance` consta na [lista oficial de categorias aceitas](https://developers.openai.com/plugins/deploy/submission-errors#listing-and-interface-errors).
A compatibilidade semântica entre categoria e listagem é avaliada pelo portal;
a validação local do ZIP não garante sua aprovação. Depois de reenviar, confira
se a categoria do rascunho no painel também está em `Finance`.

## Idioma da listagem

Os campos principais de `interface` e as sugestões de conversa estão em
português do Brasil, conforme o público do Granatum. A documentação da OpenAI
orienta usar inglês como base, mas também informa que `publication.translations`
ainda não altera o texto exibido no diretório. Por decisão do usuário em
2026-10-15, o pacote usa português nos campos principais para apresentar esse
idioma no painel e na listagem. A tradução `en-US` fica disponível no manifesto;
a aprovação da listagem é conferida pelo portal.

## Enviar à OpenAI

Envie o ZIP completo em **Upload plugin**, no portal da OpenAI. O MCP deve estar
incluído desde o primeiro upload; a documentação informa que adicionar um MCP a
um plugin existente que contém apenas skills ainda não é suportado.

A validação local não comprova aceitação pelo portal, disponibilidade dos links,
compatibilidade OAuth ou aprovação da revisão. Confira **Metadata & Skills** e
**MCPs** depois do upload. Credenciais de revisão, demonstração e demais materiais
exigidos são preenchidos no portal; nenhuma credencial deve entrar no ZIP.
**Este repositório é público:** login e senha da conta de teste dos revisores nunca
entram aqui (nem em `listing.json`, nem em commit), só no formulário do portal.

Referências oficiais consultadas em 2026-10-15:

- [Formato do pacote](https://developers.openai.com/plugins/build/plugins).
- [Upload, campos do manifesto e revisão](https://developers.openai.com/plugins/deploy/submission).

O envio e a publicação continuam manuais, feitos pelo humano.
