"""Simule une fuite mémoire progressive — alloue par paliers pour tester la prédiction."""

import sys
import time

DEFAULT_INTERVAL_SECONDS = 0.3
DEFAULT_CHUNK_MB = 10
DEFAULT_MAX_MB = 4000

if __name__ == "__main__":
    interval = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INTERVAL_SECONDS
    chunk_mb = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CHUNK_MB
    max_mb = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_MAX_MB

    chunks: list[bytearray] = []
    total_mb = 0
    while total_mb < max_mb:
        chunks.append(bytearray(chunk_mb * 1024 * 1024))
        total_mb += chunk_mb
        print(f"alloué: {total_mb}MB (intervalle {interval}s, plafond {max_mb}MB)", flush=True)
        time.sleep(interval)

    print(f"plafond {max_mb}MB atteint, arrêt de l'allocation", flush=True)
    time.sleep(3600)
