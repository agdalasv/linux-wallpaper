pkgname=linux-wallpaper-app
pkgver=1.0
pkgrel=1
pkgdesc="Explora y descarga wallpapers para Linux"
arch=('any')
url="https://github.com/agdalasv/linux_wallpaper_app"
license=('MIT')
depends=('python-pyqt6' 'python-requests' 'python-pillow')
optdepends=('feh' 'nitrogen')
source=("git+https://github.com/agdalasv/linux_wallpaper_app.git")
md5sums=('SKIP')

package() {
    cp -r "$srcdir/linux_wallpaper_app" "$pkgdir/opt/"
    install -Dm755 "$srcdir/linux_wallpaper_app/linux-wallpaper-app.sh" "$pkgdir/usr/bin/linux-wallpaper-app"
    install -Dm644 "$srcdir/linux_wallpaper_app/linux-wallpaper-app.desktop" "$pkgdir/usr/share/applications/linux-wallpaper-app.desktop"
    install -Dm644 "$srcdir/linux_wallpaper_app/logo.png" "$pkgdir/usr/share/pixmaps/linux-wallpaper-app.png"
}
