"""Simule une appli légitime (jeu, VM) : montée rapide puis plateau — pas une fuite."""

import sys
import time

TARGET_MB = int(sys.argv[1]) if len(sys.argv) > 1 else 250
STEPS = 15

if __name__ == "__main__":
    chunks: list[bytearray] = []
    total_mb = 0
    for step in range(1, STEPS + 1):
        remaining = TARGET_MB - total_mb
        chunk_mb = max(remaining // (STEPS - step + 1), 1)
        chunks.append(bytearray(chunk_mb * 1024 * 1024))
        total_mb += chunk_mb
        interval = 0.05 * step
        print(f"alloué: {total_mb}MB (palier {step}/{STEPS}, ralentit)", flush=True)
        time.sleep(interval)

    print(f"plateau atteint à {total_mb}MB, stable", flush=True)
    time.sleep(3600)
