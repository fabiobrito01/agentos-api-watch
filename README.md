![AgentOS API Watch](assets/banner.svg)

# AgentOS API Watch
Monitor leve e sem dependências para sites e APIs, com tentativas automáticas, status esperado e relatórios JSON.
```bash
python watch.py https://example.com https://api.github.com --json
python watch.py https://example.com --retries 2 --timeout 5 --output relatorio.json
python watch.py https://example.com/health --expect 200 --expect 204
```
Retorna código `0` quando todos os alvos estão saudáveis e `1` quando algum falha, facilitando o uso em automações e CI.
Projeto AgentOStudio · MIT.

