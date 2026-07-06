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
- `SMART_OOMD_CGROUP_SCOPE` — confine la surveillance à un cgroup v2 (tests)

## Tester sans risque (cgroup isolé)

```bash
./scripts/test_cgroup.sh
```

Crée un cgroup v2 limité en mémoire, y lance `stress-ng` pour simuler une fuite,
et affiche la commande pour lancer le daemon scopé à ce seul cgroup. Le kill
préventif ne peut affecter que les process du cgroup de test.

## Stack

Python 3.14, venv, loguru. Aucune dépendance externe hors stdlib + loguru.
