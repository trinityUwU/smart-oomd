"""Simule une fuite mémoire progressive — alloue par paliers pour tester la prédiction."""

import sys
import time

CHUNK_MB = 10
DEFAULT_INTERVAL_SECONDS = 0.3

if __name__ == "__main__":
    interval = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INTERVAL_SECONDS
    chunks: list[bytearray] = []
    total_mb = 0
    while True:
        chunks.append(bytearray(CHUNK_MB * 1024 * 1024))
        total_mb += CHUNK_MB
        print(f"alloué: {total_mb}MB (intervalle {interval}s)", flush=True)
        time.sleep(interval)
