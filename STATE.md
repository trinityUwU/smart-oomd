# STATE — smart-oomd

MVP fonctionnel : boucle de surveillance, prédiction par régression linéaire,
scoring composite, kill préventif. Non testé en conditions réelles (cgroup) —
prochaine étape avant tout packaging AUR.

## Fait
- Lecture process/mémoire via /proc (monitor/)
- Historique glissant + régression linéaire (croissance par process et système)
- Scoring composite (croissance + taille) avec liste de protection
- Kill SIGTERM avec dry-run par défaut
- Scripts start/stop/restart + harnais de test cgroup v2 isolé

## À valider
- Exécuter `scripts/test_cgroup.sh` + daemon scopé, confirmer qu'il tue le bon
  process avant l'OOM kill du cgroup
- Ajuster les poids/seuils si le kill arrive trop tôt ou trop tard
