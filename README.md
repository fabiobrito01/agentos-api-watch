![AgentOS API Watch](assets/banner.svg)

# AgentOS API Watch
Monitor leve e sem dependências para sites e APIs, com tentativas automáticas, status esperado e relatórios JSON.
```bash
python watch.py https://example.com https://api.github.com --json
python watch.py https://example.com --retries 2 --timeout 5 --output relatorio.json
python watch.py https://example.com/health --expect 200 --expect 204
python watch.py https://site-a.com https://site-b.com --workers 2 --fail-slow-ms 1500
python watch.py https://api.exemplo.com/health --header "Authorization:Bearer TOKEN"
```
As consultas são paralelas por padrão, mas o relatório mantém a ordem informada. `--fail-slow-ms` permite detectar degradação antes da indisponibilidade, e `--header` suporta APIs autenticadas sem registrar o valor no relatório. Retorna código `0` quando todos os alvos estão saudáveis e `1` quando algum falha ou ultrapassa a latência definida.
Projeto AgentOStudio · MIT.

