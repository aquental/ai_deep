# func-call — POC de Function Calling com DeepSeek

Proof of concept demonstrando function calling (tool use) com a API do DeepSeek, usando o SDK `openai` no modo compatível.

## O que o programa faz

1. Registra três ferramentas no schema da API:
   - `add` — soma dois números
   - `multiply` — multiplica dois números
   - `final_answer` — sinaliza que a tarefa está concluída e retorna a resposta final

2. Envia uma pergunta (`"Compute 15 + 27"`) para o modelo `deepseek-chat`.

3. O modelo decide se precisa chamar uma ferramenta. Se sim, o programa executa a função correspondente localmente (`add` ou `multiply`) e imprime o resultado.

4. Em cenários multi-step, o modelo pode encadear várias chamadas de ferramenta até invocar `final_answer`.

## Pré-requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) instalado
- Chave de API do DeepSeek (começa com `sk-`)

## Configuração

Crie um arquivo `.env` na raiz do projeto com as variáveis de ambiente:

```env
DEEPSEEK_API_KEY=sk-sua-chave-aqui
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | Sim | — | Chave da API do DeepSeek |
| `DEEPSEEK_BASE_URL` | Não | `https://api.deepseek.com` | Base URL da API |
| `DEEPSEEK_MODEL` | Não | `deepseek-chat` | Modelo a ser usado |

## Como rodar

```bash
# Instalar dependências (uma única vez)
uv sync

# Executar o programa
uv run main.py
```

### Saída esperada

```
Executed add with args {'a': 15, 'b': 27} -> result: 42
```

## Dependências

| Pacote | Uso |
|---|---|
| `openai>=2.38.0` | SDK compatível com a API do DeepSeek |
| `python-dotenv>=1.2.2` | Carrega variáveis do `.env` |
