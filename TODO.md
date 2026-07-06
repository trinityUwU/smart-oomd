# TODO — smart-oomd

## En cours
- [ ] Valider le comportement en cgroup isolé (`scripts/test_cgroup.sh`)

## Backlog
- [ ] Unité tests pour `HistoryTracker`/`select_victim` (pytest)
- [ ] systemd unit file pour lancer smart-oomd au boot (après validation manuelle)
- [ ] Packaging AUR si le comportement se confirme fiable
- [ ] Comparer empiriquement vs earlyoom sur une charge de test identique
