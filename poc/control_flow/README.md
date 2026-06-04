# Control Flow — Loop agêntico com function calling

Prova de conceito de um loop agêntico baseado no fluxo de controle do DeepSeek/OpenAI Responses API.

## O que o `main.py` faz

Implementa um **agentic loop** que orquestra chamadas de função (function calling) via API:

1. **Define tools** — expõe duas operações matemáticas (`add`, `multiply`) e uma ferramenta especial `final_answer` que encerra o loop.

2. **Executa o loop** — a cada passo:
   - Envia o contexto acumulado para o modelo com `tool_choice="required"` (o modelo é obrigado a chamar uma ferramenta).
   - Processa cada `function_call` retornado, executando a função correspondente localmente.
   - Adiciona o resultado (`function_call_output`) de volta ao contexto, fechando o ciclo de feedback.

3. **Critério de parada** — o loop para quando o modelo chama `final_answer` ou quando atinge o limite de 5 passos.

4. **Tarefa exemplo** — o prompt embutido é _"What is 15 + 27? Then multiply the result by 3."_, que exige dois passos encadeados: `add(15, 27)` → `multiply(42, 3)` → `final_answer`.

## Estrutura

```
control_flow/
├── main.py           # Loop agêntico com function calling
├── pyproject.toml    # Dependências (openai)
└── README.md
```

## Executar

```bash
uv run main.py
```

A saída mostra cada passo do loop com as chamadas de função e resultados intermediários.
