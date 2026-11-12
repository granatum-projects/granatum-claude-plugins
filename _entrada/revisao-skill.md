# Revisão da skill contra o servidor (12/11/2026)

Goldens de `_entrada/`: `*-integracao` = main + specs 085, 082, 086 (sem a 089); `*-089` = main + 089 (tem
`anexar_arquivo_por_url`). Depois do deploy: Claude e demais clientes veem **23 tools (12 de consulta, 11 que gravam)**:
as 18 de antes + `obter_conciliacoes_pendentes`, `conciliar`, `desconciliar`, `ignorar_movimentos`,
`anexar_arquivo_por_url`. ChatGPT e Codex veem **24** (mais `anexar_arquivo_direto`, só para eles).

## 1. Conciliação (085) nunca sincronizada no plugin

A fonte certa é `_entrada/skill-conciliacao-085.md` (do monorepo, spec 085 etapa 5; tirar o comentário das linhas 6-10).
Na skill `plugins/granatum-financeiro/skills/conciliacao/SKILL.md` (versão da 050) estão errados:
- ":8 'três tools'" e ":19 'as três tools recusam'": são quatro (`ignorar_movimentos`).
- ":95 'vários lançamentos a um movimento' como coisa da tela": `conciliar` aceita `lancamento_ids` (soma exata, dividido
  inteiro). Só "vários movimentos para um lançamento" continua na tela.
- ":97 ignorar/restaurar na tela": hoje é `ignorar_movimentos` (`desfazer: true` restaura).
- ":88 'só aquele vínculo sai'": desconciliar desfaz o grupo inteiro (`pelo_grupo: true` na prévia).
- Faltam: soma/dividido (`lancamento_ids`, `agrupar_divididos: true`, `ids_dos_itens`, `parte_de_dividido`, códigos
  `lancamento_id_ou_lancamento_ids_obrigatorio`, `lancamento_id_e_lancamento_ids`); impedidos soma diferente e mesmo
  dividido em dois pares; `conciliados` (lançamentos) × `movimentos_conciliados`; seção ignorar/restaurar com recusas
  `movimento_conciliado`, `movimento_ja_ignorado`, `movimento_nao_ignorado`, `movimento_de_importacao_csv`; regra
  "conciliado não se edita, não se paga nem se exclui: proponha desconciliar"; status `ignorado`/`restaurado`; gatilhos
  no front-matter ("ignora esse movimento", "é a soma de dois lançamentos").

## 2. README do plugin
- ":161 '21 ferramentas: 12 de consulta e 9 que gravam'": 23 (12 + 11) no Claude.
- ":79-80" o MCP "não faz" vários lançamentos para um movimento: faz (085).
- ":81-83" e ":150-152" anexos dependem de comando/terminal: `obter_anexo` lê o conteúdo; `anexar_arquivo_por_url` não
  depende de terminal; ChatGPT envia direto.
- ":33-35" lista de tools que gravam sem `ignorar_movimentos`. ":77-80" sem ignorar e soma/dividido. ":147-148"
  conciliado: dizer que a saída é desconciliar antes.

## 3. granatum-fundamentos/SKILL.md
- ":73-74" lista de tools que gravam sem `ignorar_movimentos`; `anexar_arquivo_direto` deve dizer "(onde existir)".
- ":115-118" "não gravam na primeira vez": incluir as de anexar com `este_e_proximos` (`confirmacao_necessaria`) e a
  prévia obrigatória de `conciliar`, `desconciliar`, `ignorar_movimentos`.

## 4. escrita-avancada/SKILL.md e references/pagamento-e-anexos.md
- escrita-avancada ":97, :213" e pagamento-e-anexos ":35, :45": conciliado é impedimento, mas a saída é `desconciliar`
  (perfis Administrador e Lançamentos).
- pagamento-e-anexos ":116": `escopo_serie` também é recusado no anexo de série que ficou num lançamento só (ver
  `excluir_anexo` no golden 089).
- pagamento-e-anexos ":51": trocar o vago "servidor que não devolve conteúdo" pela tabela de formatos lidos e os
  estados `nao_lido`/`indisponivel` (a versão do Kiro já tem).

## 5. extrato/SKILL.md e granatum-fundamentos/references/regras-de-campo.md
- extrato ":75-77": `obter_anexo` traz o conteúdo, não só o link. Citar `agrupar_divididos`.
- regras-de-campo ":69": citar o campo `conciliado` em cada lançamento.

## 6. ChatGPT
- `chatgpt/granatum-financeiro/references/*` são cópias das skills: refazer depois (inclusive `conciliacao.md`).
- Versão continua 1.3.0; o `chatgpt/README.md` manda subir a versão a cada mudança de skill.

## 7. Duas sincronizações da 089
`origin/skill/089-anexos-url` (651026e, Kiro) × `skill/089-anexos-por-url` (8d0b4ea, esta base). Partem de 97d18e6 e
diferem em 11 arquivos. A do Kiro já corrige README :81-83/:150-152, a tabela de formatos do `obter_anexo`, o
`excluir_anexo` com um só lançamento restante, o conteúdo no extrato e as tools de anexar na lista de prévia. Só esta base
tem o bloco "Contrato de arquivo da OpenAI / Se falhar" e a regra do `xn--`. Juntar as duas, ficando com o melhor de cada.
