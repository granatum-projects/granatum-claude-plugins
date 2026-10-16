#!/usr/bin/env python3
"""Gera o ZIP OpenAI com a biblioteca padrão do Python 3.10+."""

import argparse
import hashlib
import json
import re
import shutil
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PRODUCAO = 'https://api.ww2.granatum.com.br/v1/mcp'


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def ler_json(caminho):
    return json.loads(caminho.read_text(encoding='utf-8'))


def gerar(destino):
    plugin = RAIZ / 'plugins/granatum-financeiro'
    skill = RAIZ / 'chatgpt/granatum-financeiro'
    legado = ler_json(plugin / '.claude-plugin/plugin.json')
    versao = legado['version']
    exigir(re.fullmatch(r'\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?', versao), 'Versão inválida no plugin.')
    texto = (skill / 'SKILL.md').read_text(encoding='utf-8')
    frontmatter = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', texto, re.S)
    exigir(frontmatter, 'SKILL.md precisa de frontmatter YAML.')
    versao_skill = re.search(r'^  version: [\'"]?([^\'"\s]+)[\'"]?\s*$', frontmatter[1], re.M)
    exigir(versao_skill and versao_skill[1] == versao, 'Versões do plugin e da skill divergentes.')
    marketplace = ler_json(RAIZ / '.claude-plugin/marketplace.json')
    exigir(marketplace['metadata']['version'] == versao, 'Versão do marketplace divergente.')
    mcp_original = ler_json(plugin / '.mcp.json')
    exigir(set(mcp_original['mcpServers']) == {'Granatum'}, 'Esperado somente o MCP Granatum.')
    servidor = mcp_original['mcpServers']['Granatum']
    exigir(servidor.get('url') == PRODUCAO, 'MCP deve apontar para produção antes de empacotar.')
    exigir(set(servidor) <= {'type', 'url'}, 'Configuração MCP contém campos não previstos; revise a conversão OpenAI.')
    exigir(servidor.get('type', 'http') == 'http', 'Transporte MCP não previsto.')
    mcp = {'mcpServers': {'Granatum': {'url': PRODUCAO}}}
    manifesto = {k: legado[k] for k in ('version', 'author', 'repository', 'license', 'keywords')}
    listing = ler_json(RAIZ / 'openai/listing.json')
    exigir(set(listing) == {'name', 'description', 'homepage', 'interface', 'extensions'}, 'Campos inesperados em openai/listing.json.')
    exigir(isinstance(listing['name'], str) and len(listing['name']) <= 64 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', listing['name']), 'Nome OpenAI inválido em openai/listing.json.')
    manifesto.update(listing)
    manifesto.update(skills='./skills/', mcpServers='./.mcp.json')
    interface = manifesto['interface']
    for campo, limite in [('displayName', 30), ('shortDescription', 30), ('longDescription', 4000), ('developerName', 80)]:
        exigir(isinstance(interface[campo], str) and 0 < len(interface[campo]) <= limite, f'Campo inválido: {campo}.')
    for campo in ('websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL'):
        exigir(interface[campo].startswith('https://'), f'{campo} precisa de HTTPS.')
    with tempfile.TemporaryDirectory(prefix='granatum-openai-') as temporario:
        pacote = Path(temporario).resolve()
        (pacote / '.codex-plugin').mkdir()
        arquivos = [(RAIZ / 'LICENSE', Path('LICENSE')), (plugin / 'assets/icon.png', Path('assets/icon.png'))]
        # Lista explícita: não inclui credenciais, arquivos locais ou artefatos antigos.
        arquivos.extend((arquivo, Path('skills/granatum-financeiro') / arquivo.relative_to(skill))
                        for arquivo in sorted(skill.rglob('*')) if arquivo.is_file() and arquivo.suffix == '.md')
        for origem, relativo in arquivos:
            exigir(not any(p.is_symlink() for p in (origem, *origem.parents)), f'Link simbólico não permitido: {origem}')
            alvo = pacote / relativo
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origem, alvo)
        for relativo, dados in [('.codex-plugin/plugin.json', manifesto), ('.mcp.json', mcp)]:
            (pacote / relativo).write_text(json.dumps(dados, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for campo in ('logo', 'composerIcon'):
            caminho = (pacote / interface[campo]).resolve()
            exigir(caminho.is_relative_to(pacote) and caminho.is_file(), f'Imagem ausente ou fora do pacote: {campo}.')
        for arquivo in (pacote / 'skills').rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', arquivo.read_text(encoding='utf-8')):
                if '://' not in link and not link.startswith('#'):
                    alvo = (arquivo.parent / link.split('#')[0]).resolve()
                    exigir(alvo.is_relative_to(pacote) and alvo.exists(), f'Link local inválido em {arquivo.name}: {link}')
        icone = (pacote / 'assets/icon.png').read_bytes()
        exigir(icone[:8] == b'\x89PNG\r\n\x1a\n', 'Ícone não é PNG.')
        largura, altura = struct.unpack('>II', icone[16:24])
        exigir(largura == altura and 48 <= largura <= 4096 and len(icone) <= 5 * 1024 * 1024, 'Dimensões ou tamanho do ícone inválidos.')
        # Ordem, data e permissões fixas tornam o ZIP reproduzível.
        zip_temporario = pacote / 'pacote.zip'
        with zipfile.ZipFile(zip_temporario, 'w', zipfile.ZIP_DEFLATED) as arquivo_zip:
            for arquivo in sorted(p for p in pacote.rglob('*') if p.is_file() and p != zip_temporario):
                entrada = zipfile.ZipInfo(arquivo.relative_to(pacote).as_posix(), (2020, 1, 1, 0, 0, 0))
                entrada.create_system = 3
                entrada.external_attr = 0o100644 << 16
                entrada.compress_type = zipfile.ZIP_DEFLATED
                arquivo_zip.writestr(entrada, arquivo.read_bytes())
        with zipfile.ZipFile(zip_temporario) as arquivo_zip:
            exigir(arquivo_zip.testzip() is None, 'Falha de integridade do ZIP.')
            exigir('skills/granatum-financeiro/SKILL.md' in arquivo_zip.namelist(), 'Skill ausente no ZIP.')
        destino.mkdir(parents=True, exist_ok=True)
        saida = destino / f'granatum-financeiro-openai-{versao}.zip'
        # Nunca substitui silenciosamente um pacote já gerado.
        with saida.open('xb') as arquivo:
            arquivo.write(zip_temporario.read_bytes())
    print(f'ZIP: {saida}')
    print(f'SHA256: {hashlib.sha256(saida.read_bytes()).hexdigest()}')
    print('Validação local: manifesto, versões, MCP de produção, ícone, links e integridade OK.')
    return saida


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', type=Path, default=Path.home() / 'Downloads', help='Pasta de saída (padrão: ~/Downloads).')
    args = parser.parse_args()
    try:
        gerar(args.destino.expanduser().resolve())
    except (OSError, ValueError, KeyError, TypeError, struct.error) as erro:
        print(f'Erro: {erro}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
