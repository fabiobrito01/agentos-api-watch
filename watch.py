"""Monitor leve de sites e APIs, sem dependências externas."""
import argparse
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone


def check(url, timeout=10, retries=0, expected=None, headers=None, fail_slow_ms=None):
    """Consulta uma URL e retorna um resultado estruturado e serializável."""
    attempts = 0
    last_error = None
    started = time.perf_counter()
    while attempts <= retries:
        attempts += 1
        try:
            request = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = response.status
            accepted = expected or range(200, 400)
            elapsed = round((time.perf_counter() - started) * 1000)
            status_ok = status in accepted
            latency_ok = fail_slow_ms is None or elapsed <= fail_slow_ms
            return {
                "url": url,
                "ok": status_ok and latency_ok,
                "status": status,
                "ms": elapsed,
                "reason": "slow" if status_ok and not latency_ok else None,
                "attempts": attempts,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:  # urllib expõe exceções diferentes por falha
            last_error = str(exc)
    return {
        "url": url,
        "ok": False,
        "error": last_error,
        "ms": round((time.perf_counter() - started) * 1000),
        "attempts": attempts,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Monitore sites e APIs localmente")
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--json", action="store_true", help="saída JSON")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--expect", type=int, action="append", help="status HTTP aceito; pode repetir")
    parser.add_argument("--output", help="salva o relatório JSON neste arquivo")
    parser.add_argument("--workers", type=int, default=4, help="consultas paralelas (padrão: 4)")
    parser.add_argument("--fail-slow-ms", type=int, help="considera DOWN acima desta latência")
    parser.add_argument("--header", action="append", default=[], metavar="NOME:VALOR", help="cabeçalho HTTP; pode repetir")
    args = parser.parse_args(argv)
    headers = {}
    for item in args.header:
        if ":" not in item:
            parser.error(f"cabeçalho inválido: {item!r}; use NOME:VALOR")
        name, value = item.split(":", 1)
        if not name.strip():
            parser.error("o nome do cabeçalho não pode estar vazio")
        headers[name.strip()] = value.strip()
    workers = max(1, min(args.workers, len(args.urls), 32))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(lambda url: check(url, args.timeout, max(0, args.retries), args.expect, headers, args.fail_slow_ms), args.urls))
    report = json.dumps(rows, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as output:
            output.write(report + "\n")
    if args.json:
        print(report)
    else:
        for row in rows:
            status = row.get("status", row.get("error", "erro"))
            reason = " lento" if row.get("reason") == "slow" else ""
            print(f"{'UP' if row['ok'] else 'DOWN'}{reason} {row['url']} {status} {row['ms']}ms ({row['attempts']} tentativa(s))")
    return 0 if all(row["ok"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
