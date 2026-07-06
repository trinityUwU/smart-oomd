# TODO — smart-oomd

## Fait récemment
- [x] Garde-fou anti-faux-positif : `SMART_OOMD_MIN_AVAILABLE_PERCENT` (défaut 10%)
      + `SMART_OOMD_CONFIRMATIONS` (défaut 3) — un pic de charge légitime (jeu, VM,
      compilation) avec beaucoup de marge réelle ne déclenche plus de kill
- [x] Détection de ralentissement (courbure) : compare la pente ancienne vs
      récente de la fenêtre — une croissance qui ralentit (jeu qui charge son
      monde, ex: Minecraft 6GB→25GB) n'est jamais tuée, même sous le plancher.
      Testé : un process qui plafonne à 280MB dans un cgroup à 300MB survit.

## Connu et accepté
- Sur un cgroup à très petit budget (<1GB), les défauts (poll 1s, 3 confirmations)
  peuvent perdre la course contre le OOM killer du kernel — il faut resserrer
  `SMART_OOMD_POLL_INTERVAL`/`SMART_OOMD_CONFIRMATIONS` pour ce cas. Sur la
  machine réelle de Chris (46GB), la marge de 10% (~4.6GB) laisse largement le
  temps de confirmer sans jamais perdre cette course — non applicable en usage
  normal.

## Bloqué — pas de notre fait
- [ ] Soumission AUR réelle : **inscriptions AUR suspendues par Arch depuis
      début juin 2026** suite à un incident de sécurité (~1500 paquets AUR
      compromis/malveillants détectés). Le formulaire d'inscription renvoie un
      503 volontairement — ce n'est pas un bug de notre côté, pas de
      contournement légitime. PKGBUILD déjà corrigé et testé (`makepkg -f`
      passe), clé SSH dédiée générée (`~/.ssh/id_ed25519_aur`), service
      systemd de packaging en `dry_run=true` par défaut — tout est prêt.
      Dès que Chris peut créer un compte AUR, on pousse en quelques minutes.

## Backlog
- [ ] Comparer empiriquement vs earlyoom sur une charge de test identique
