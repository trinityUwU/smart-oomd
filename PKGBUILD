# Maintainer: trinityUwU
pkgname=smart-oomd-git
pkgver=r1
pkgrel=1
pkgdesc="Daemon userspace de kill mémoire préventif par prédiction de tendance (alternative earlyoom)"
arch=('any')
url="https://github.com/trinityUwU/smart-oomd"
license=('MIT')
depends=('python' 'python-loguru')
makedepends=('git')
provides=('smart-oomd')
conflicts=('smart-oomd')
source=("$pkgname::git+$url.git")
sha256sums=('SKIP')

pkgver() {
    cd "$pkgname"
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
    cd "$pkgname"
    install -dm755 "$pkgdir/usr/lib/smart-oomd"
    cp -r monitor scoring killer daemon "$pkgdir/usr/lib/smart-oomd/"
    install -Dm644 systemd/smart-oomd.service "$pkgdir/usr/lib/systemd/user/smart-oomd.service"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
