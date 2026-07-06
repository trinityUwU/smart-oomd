"""Exécution du kill préventif — toujours loggé, jamais silencieux."""

import os
import signal

from loguru import logger

from scoring.scorer import ScoredCandidate


def kill_candidate(candidate: ScoredCandidate, dry_run: bool) -> bool:
    reason = (
        f"pid={candidate.pid} name={candidate.name} rss={candidate.rss_kb}kB "
        f"growth={candidate.growth_kb_per_s:.0f}kB/s score={candidate.score:.3f}"
    )
    if dry_run:
        logger.warning(f"[DRY-RUN] aurait tué {reason}")
        return True

    try:
        os.kill(candidate.pid, signal.SIGTERM)
        logger.warning(f"kill préventif SIGTERM {reason}")
        return True
    except ProcessLookupError:
        logger.info(f"process déjà terminé avant le kill: pid={candidate.pid}")
        return False
    except PermissionError as exc:
        logger.error(f"permission refusée pour tuer pid={candidate.pid}: {exc}")
        return False
