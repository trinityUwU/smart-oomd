# Architecture — smart-oomd

## Domaines

- `monitor/` — lecture brute du système : process (`/proc/[pid]/{status,statm}`),
  mémoire système (`/proc/meminfo`), cgroups (`cgroup.procs`), et l'historique
  glissant (régression linéaire) par PID.
- `scoring/` — décision : prédiction du temps avant épuisement (`predictor.py`),
  liste des process protégés (`criticality.py`), score composite de victime
  (`scorer.py`).
- `killer/` — exécution du kill (SIGTERM), toujours loggée, jamais silencieuse.
- `daemon/` — configuration (env vars) et boucle principale qui orchestre les
  trois domaines ci-dessus.

## Frontière

`daemon/main.py` est le seul point qui connaît les trois domaines. `monitor`,
`scoring` et `killer` ne s'importent jamais entre eux sauf `scoring` qui lit
les types de `monitor` (ProcessSample, HistoryTracker) — dépendance à sens
unique, jamais l'inverse.

## Algorithme

1. Tendance mémoire système : régression linéaire sur `MemAvailable` (fenêtre
   glissante `SMART_OOMD_HISTORY_WINDOW`) → pente kB/s.
2. Si la pente est négative, extrapolation du temps avant épuisement complet.
3. Détection de courbure : pente de la première moitié de la fenêtre vs pente
   de la seconde moitié. Si la perte ralentit (`recent_slope > older_slope`,
   les deux négatives), la croissance est taguée `is_decelerating` — usage
   légitime qui approche un plateau, jamais une cible.
4. Un kill n'est envisagé que si les 3 conditions sont réunies :
   mémoire disponible sous `SMART_OOMD_MIN_AVAILABLE_PERCENT` du total,
   épuisement prédit sous `SMART_OOMD_THRESHOLD`, et **pas** `is_decelerating`.
   Doit rester vrai `SMART_OOMD_CONFIRMATIONS` cycles consécutifs (anti-bruit).
5. Sélection de la victime : score = 0.6 × croissance_normalisée +
   0.4 × taille_normalisée, parmi les process non protégés (pid 1,
   oom_score_adj ≤ -1000, liste de noms critiques).
6. Kill SIGTERM du meilleur candidat, ou dry-run log si `SMART_OOMD_DRY_RUN=true`.
