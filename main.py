#!/usr/bin/env python3
"""DeepSeek CLI — envia um prompt via stdin para a API do DeepSeek.

Configuração via arquivo .env (ou variáveis de ambiente):
    DEEPSEEK_API_KEY   — chave da API (obrigatória)
    DEEPSEEK_BASE_URL  — URL base da API (padrão: https://api.deepseek.com)
    DEEPSEEK_MODEL     — modelo a usar (padrão: deepseek-chat)
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    # Carrega .env do diretório atual (não sobrescreve vars já definidas)
    load_dotenv(override=False)

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Erro: DEEPSEEK_API_KEY não definida.", file=sys.stderr)
        print("Crie um arquivo .env com DEEPSEEK_API_KEY=sk-...", file=sys.stderr)
        sys.exit(1)
    else:
        print("DEEPSEEK_API_KEY encontrada, continuando...")

    if not api_key.startswith("sk-"):
        print("Erro: DEEPSEEK_API_KEY inválida.", file=sys.stderr)
        print("Crie um arquivo .env com DEEPSEEK_API_KEY=sk-...", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    print(f"Usando DEEPSEEK_BASE_URL={base_url}")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    print(f"Usando DEEPSEEK_MODEL={model}")

    # Lê todo o conteúdo do stdin como prompt
    prompt = sys.stdin.read().strip()
    if not prompt:
        print("Erro: stdin vazio. Envie um prompt.", file=sys.stderr)
        print("Uso: echo 'seu prompt' | uv run main.py", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
    except Exception as e:
        print(f"Erro na chamada da API: {e}", file=sys.stderr)
        sys.exit(2)

    content = response.choices[0].message.content
    if content:
        print(content)
    else:
        print("(resposta vazia)", file=sys.stderr)


if __name__ == "__main__":
    main()
