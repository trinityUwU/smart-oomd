"""Simule une fuite mémoire progressive — alloue par paliers pour tester la prédiction."""

import time

CHUNK_MB = 10
INTERVAL_SECONDS = 0.3

if __name__ == "__main__":
    chunks: list[bytearray] = []
    total_mb = 0
    while True:
        chunks.append(bytearray(CHUNK_MB * 1024 * 1024))
        total_mb += CHUNK_MB
        print(f"alloué: {total_mb}MB", flush=True)
        time.sleep(INTERVAL_SECONDS)
