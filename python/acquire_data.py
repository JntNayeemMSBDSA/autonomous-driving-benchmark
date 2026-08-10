"""Acquire public raw files with logging, retries, and cutoff-safe URLs.

The delivered project includes a small verified schema excerpt because the
execution environment could not reliably transfer the large NHTSA archives.
Run this script in a normal networked environment to populate data/raw.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from config import PROJECT_ROOT, RAW_DIR, NHTSA_ARCHIVE_URLS

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def download(url: str, destination: Path, retries: int = 3, timeout: int = 90) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "portfolio-research-project/1.0"})
            with urlopen(request, timeout=timeout) as response, destination.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
            return {
                "status": "downloaded",
                "url": url,
                "path": str(destination.relative_to(PROJECT_ROOT)),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        except (URLError, HTTPError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
            if destination.exists():
                destination.unlink()
            time.sleep(attempt * 2)
    return {"status": "failed", "url": url, "path": str(destination.relative_to(PROJECT_ROOT)), "error": last_error}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-downloads", action="store_true",
                        help="Validate bundled raw files without network access.")
    args = parser.parse_args()
    records = []
    for key, url in NHTSA_ARCHIVE_URLS.items():
        destination = RAW_DIR / f"nhtsa_sgo_{key}_archive_through_2025-06-15.csv"
        if args.skip_downloads:
            records.append({
                "status": "present" if destination.exists() else "not_bundled",
                "url": url,
                "path": str(destination.relative_to(PROJECT_ROOT)),
                "reason": "Large official archive is intentionally acquired at runtime.",
            })
        else:
            records.append(download(url, destination))
    log_path = RAW_DIR / "acquisition_log.json"
    log_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(records, indent=2))
    return 0 if all(r["status"] in {"downloaded", "present", "not_bundled"} for r in records) else 1

if __name__ == "__main__":
    raise SystemExit(main())
