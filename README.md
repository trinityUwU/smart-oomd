# smart-oomd

Daemon userspace de kill mémoire préventif. Alternative à earlyoom/nohang qui,
au lieu d'un seuil statique, prédit l'épuisement mémoire par régression sur la
tendance système et choisit la victime via un score composite (vitesse de
croissance + taille), en respectant une liste de process protégés.

Ne touche jamais au kernel — tourne à côté du OOM killer natif, purement en
espace utilisateur.

## Lancer manuellement

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m daemon.main
```

## Lancer en daemon

```bash
./start.sh
./stop.sh
./restart.sh
```

## Configuration

Voir `.env.example`. Variables clés :
- `SMART_OOMD_DRY_RUN` — `true` par défaut, log les kills sans les exécuter
- `SMART_OOMD_THRESHOLD` — secondes avant épuisement estimé qui déclenchent un kill
- `SMART_OOMD_MIN_AVAILABLE_PERCENT` — un kill n'est envisagé que si la mémoire
  disponible passe sous ce % du total (défaut 10%). Empêche un pic de charge
  légitime (jeu, VM, compilation) avec plein de marge réelle de déclencher un
  kill juste parce qu'il alloue vite.
- `SMART_OOMD_CONFIRMATIONS` — nombre de cycles consécutifs en zone de danger
  avant d'agir (défaut 3). Absorbe les pics isolés/bruit de mesure.
- `SMART_OOMD_CGROUP_SCOPE` — confine la surveillance à un cgroup v2 (tests)

## Tester sans risque (cgroup isolé)

```bash
./scripts/test_cgroup.sh
```

Crée un scope `systemd --user` limité en mémoire (sans root), y simule une
fuite mémoire progressive (`scripts/leak_sim.py`), et lance le daemon scopé à
ce seul cgroup. Le kill préventif ne peut affecter que ce process de test.

## Installer comme service (dry-run par défaut)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/smart-oomd.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now smart-oomd.service
journalctl --user -u smart-oomd -f
```

Par défaut `SMART_OOMD_DRY_RUN=true` — le service log ce qu'il *aurait* tué
sans rien tuer réellement. Passe à `false` dans le fichier unit une fois que
tu as observé son comportement sur ta session pendant quelques jours.

## Tests

```bash
.venv/bin/pip install pytest
.venv/bin/python -m pytest tests/
```

## Stack

Python 3.14, venv, loguru. Aucune dépendance externe hors stdlib + loguru.
