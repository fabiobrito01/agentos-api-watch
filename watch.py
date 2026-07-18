"""Monitor leve de sites e APIs, sem dependências externas."""
import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone


def check(url, timeout=10, retries=0, expected=None):
    """Consulta uma URL e retorna um resultado estruturado e serializável."""
    attempts = 0
    last_error = None
    started = time.perf_counter()
    while attempts <= retries:
        attempts += 1
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                status = response.status
            accepted = expected or range(200, 400)
            return {
                "url": url,
                "ok": status in accepted,
                "status": status,
                "ms": round((time.perf_counter() - started) * 1000),
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
    args = parser.parse_args(argv)
    rows = [check(url, args.timeout, max(0, args.retries), args.expect) for url in args.urls]
    report = json.dumps(rows, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as output:
            output.write(report + "\n")
    if args.json:
        print(report)
    else:
        for row in rows:
            status = row.get("status", row.get("error", "erro"))
            print(f"{'UP' if row['ok'] else 'DOWN'} {row['url']} {status} {row['ms']}ms ({row['attempts']} tentativa(s))")
    return 0 if all(row["ok"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
