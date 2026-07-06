# STATE — smart-oomd

MVP validé en conditions réelles (cgroup isolé, fuite mémoire progressive
simulée) : le daemon détecte la tendance et tue préventivement bien avant la
limite mémoire, sans jamais déclencher le OOM killer du kernel. 9 tests
unitaires passent. Publié publiquement sur GitHub.

## Fait
- Lecture process/mémoire via /proc, scopable à un cgroup v2 (monitor/)
- Historique glissant + régression linéaire (croissance par process et système)
- Scoring composite (croissance + taille) avec liste de protection
- Kill SIGTERM avec dry-run par défaut
- Scripts start/stop/restart + harnais de test sans sudo (systemd-run --user)
- Tests unitaires (tests/) — 9/9 passent
- Service systemd --user (dry-run par défaut) pour tourner en continu
- PKGBUILD ébauché (non fonctionnel tel quel, voir TODO)

## À valider
- Observer en dry-run sur la session réelle avant d'activer les kills en vrai
- Comparer empiriquement vs earlyoom
