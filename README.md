# Linux Wallpaper App

Explora y descarga wallpapers para Linux desde GitHub. Aplicación desarrollada con PyQt6.

![Linux Wallpaper App](logo.png)

## Capturas de pantalla

![Screenshot](https://raw.githubusercontent.com/agdalasv/linux-wallpaper/main/1.png)

## Características

- Explora wallpapers por categorías desde un repositorio GitHub
- Descarga wallpapers localmente
- Aplica wallpapers directamente en tu escritorio
- Sistema de likes/dislikes con sincronización a Google Sheets
- Soporta múltiples entornos de escritorio: GNOME, KDE, XFCE, MATE, Cinnamon, Deepin, Sway
- Tema oscuro con animaciones

## Requisitos

### Dependencias comunes
- Python 3.x
- PyQt6
- requests
- Pillow

---

## Instalación

### Arch Linux

#### Opción 1: Desde AUR (recomendado)
```bash
# Instalar dependencias
sudo pacman -S python-pyqt6 python-requests python-pillow

# Clonar y compilar
git clone https://github.com/agdalasv/linux_wallpaper_app.git
cd linux_wallpaper_app
makepkg -sri
```

#### Opción 2: Instalación manual
```bash
# Instalar dependencias
sudo pacman -S python-pyqt6 python-requests python-pillow

# Copiar archivos
sudo cp -r linux_wallpaper_app /opt/
sudo cp linux-wallpaper-app.sh /usr/bin/linux-wallpaper-app
sudo cp linux-wallpaper-app.desktop /usr/share/applications/
sudo cp linux-wallpaper-app.png /usr/share/pixmaps/linux-wallpaper-app.png

# Actualizar base de datos
update-desktop-database /usr/share/applications/
```

#### Opcional: Agregar al inicio automático
```bash
mkdir -p ~/.config/autostart
cp linux-wallpaper-app.desktop ~/.config/autostart/
```

---

### Ubuntu / Debian

#### Opción 1: Compilar paquete .deb
```bash
# Instalar dependencias
sudo apt install python3-pyqt6 python3-requests python3-pillow build-essential

# Compilar
cd linux_wallpaper_app
dpkg-buildpackage -us -uc

# Instalar
sudo dpkg -i ../linux-wallpaper-app_1.0_all.deb
sudo apt install -f  # Instalar dependencias faltantes
```

#### Opción 2: Instalación manual
```bash
# Instalar dependencias
sudo apt install python3-pyqt6 python3-requests python3-pillow

# Copiar archivos
sudo cp -r linux_wallpaper_app /opt/
sudo cp linux-wallpaper-app.sh /usr/bin/linux-wallpaper-app
sudo cp linux-wallpaper-app.desktop /usr/share/applications/
sudo cp linux-wallpaper-app.png /usr/share/pixmaps/

# Actualizar
update-desktop-database /usr/share/applications/
```

---

### Fedora

#### Instalación
```bash
# Instalar dependencias
sudo dnf install python3-pyqt6 python3-requests python3-pillow

# Copiar archivos
sudo cp -r linux_wallpaper_app /opt/
sudo cp linux-wallpaper-app.sh /usr/bin/linux-wallpaper-app
sudo cp linux-wallpaper-app.desktop /usr/share/applications/
sudo cp linux-wallpaper-app.png /usr/share/pixmaps/

# Actualizar
update-desktop-database /usr/share/applications/
```

---

## Uso

### Desde terminal
```bash
linux-wallpaper-app
```

### Desde el menú de aplicaciones
Busca **"Linux Wallpaper App"** en tu menú de aplicaciones.

---

## Configuración

### Variables de entorno
La aplicación detecta automáticamente el entorno de escritorio:
- X11: usa `xcb`
- Wayland: usa `wayland`

Para forzar un modo específico:
```bash
QT_QPA_PLATFORM=xcb linux-wallpaper-app
# o
QT_QPA_PLATFORM=wayland linux-wallpaper-app
```

### Sincronización con Google Sheets
Para habilitar la sincronización de likes/dislikes:
1. Obtén una API Key de Google Cloud
2. Configura las variables de entorno:
```bash
export GOOGLE_SHEET_ID="tu_sheet_id"
export GOOGLE_API_KEY="tu_api_key"
```

---

## Estructura del proyecto

```
linux_wallpaper_app/
├── main.py                    # Código principal
├── styles.qss                 # Estilos de la interfaz
├── logo.png                   # Logo de la aplicación
├── linux-wallpaper-app.sh     # Script de ejecución
├── linux-wallpaper-app.desktop # Entrada de escritorio
├── linux-wallpaper-app.png    # Icono
├── PKGBUILD                   # Para Arch Linux
├── debian/                    # Para Debian/Ubuntu
│   ├── control
│   ├── rules
│   └── ...
└── README.md                  # Este archivo
```

---

## Desinstalación

### Arch Linux
```bash
sudo pacman -R linux-wallpaper-app
```

### Ubuntu/Debian
```bash
sudo dpkg -r linux-wallpaper-app
```

### Fedora
```bash
sudo rm -rf /opt/linux_wallpaper_app
sudo rm /usr/bin/linux-wallpaper-app
sudo rm /usr/share/applications/linux-wallpaper-app.desktop
sudo rm /usr/share/pixmaps/linux-wallpaper-app.png
```

---

## Donaciones

Si te gusta el proyecto y quieres apoyarme, puedes donate:

### Bitcoin (BTC)
```
3L8f3v6BWwL7KBcb8AMZQ2bpE3ACne2EUf
```

---

## Licencia

MIT License - ver archivo `LICENSE` para más detalles.

---

## Autor

Desarrollado por [Agdala](https://github.com/agdalasv)
