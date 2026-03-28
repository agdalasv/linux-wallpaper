# Main application file

import sys
import os
import os
xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
if 'wayland' in os.environ.get('WAYLAND_DISPLAY', '').lower():
    os.environ['QT_QPA_PLATFORM'] = 'wayland'
elif 'cinnamon' in xdg_desktop:
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
else:
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

import requests
import json
import io
import subprocess
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QScrollArea, QGridLayout, QSizePolicy, QProgressBar,
                             QDialog, QMessageBox)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QImage, QFont
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup, QAbstractAnimation
from PyQt6.QtCore import pyqtSignal

try:
    from PIL import Image
except ImportError:
    print("Pillow library not found. Please install it: pip install Pillow")
    Image = None

GITHUB_REPO_URL = "https://api.github.com/repos/agdalasv/Linux/contents"
CACHE_DIR = os.path.expanduser("~/.cache/linux_wallpaper_app")
CACHE_FILE = os.path.join(CACHE_DIR, "repo_cache.json")

GOOGLE_SHEET_ID = "1q_3PUABceqZ-AcK2VIfrv5JXHF_4kV2IrZBJ1YdqQH0"
GOOGLE_API_KEY = "AIzaSyBrxwJOgMo1DcTqIPq4oU0dJA4Sm4GerUo"
GOOGLE_SHEETS_API_URL = "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values/{range}?alt=json"

likes_cache = {}
likes_cache_file = os.path.join(CACHE_DIR, "likes_cache.json")

image_cache = {}
image_cache_dir = os.path.expanduser("~/.cache/linux_wallpaper_app/images")
os.makedirs(image_cache_dir, exist_ok=True)


def load_likes_cache():
    global likes_cache
    if os.path.exists(likes_cache_file):
        try:
            with open(likes_cache_file, 'r') as f:
                likes_cache = json.load(f)
        except:
            pass


def save_likes_cache():
    try:
        with open(likes_cache_file, 'w') as f:
            json.dump(likes_cache, f)
    except:
        pass


def get_google_sheet_id():
    global GOOGLE_SHEET_ID
    if not GOOGLE_SHEET_ID:
        GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', '')
    return GOOGLE_SHEET_ID


def sync_likes_to_sheet(image_name, action):
    global GOOGLE_SHEET_ID, GOOGLE_API_KEY
    
    print(f"[SYNC] Intentando {action} para: {image_name}")
    
    if not GOOGLE_SHEET_ID or not GOOGLE_API_KEY:
        print("[SYNC] ERROR: Sheet no configurado")
        return "Sheet no configurado"
    
    try:
        range_name = "A:C"
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{range_name}?key={GOOGLE_API_KEY}"
        print(f"[SYNC] URL: {url}")
        response = requests.get(url)
        print(f"[SYNC] GET response: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[SYNC] ERROR: {response.status_code} - {response.text}")
            return f"Error: {response.status_code}"
        
        data = response.json()
        values = data.get('values', [])
        print(f"[SYNC] Valores actuales: {values}")
        
        row_to_update = -1
        for i, row in enumerate(values):
            if row and row[0] == image_name:
                row_to_update = i + 1
                break
        
        if action == "like":
            if row_to_update > 0:
                current_likes = int(values[row_to_update-1][1]) if len(values[row_to_update-1]) > 1 and values[row_to_update-1][1] else 0
                new_likes = current_likes + 1
                update_range = f"A{row_to_update}:C{row_to_update}"
                patch_url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{update_range}?valueInputOption=USER_ENTERED&key={GOOGLE_API_KEY}"
                print(f"[SYNC] PUT URL: {patch_url}")
                print(f"[SYNC] Actualizando like: {image_name} -> {new_likes}")
                resp = requests.put(patch_url, json={"values": [[image_name, new_likes, values[row_to_update-1][2] if len(values[row_to_update-1]) > 2 else 0]]})
                print(f"[SYNC] PUT response: {resp.status_code} - {resp.text}")
            else:
                post_url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{range_name}:append?valueInputOption=USER_ENTERED&key={GOOGLE_API_KEY}"
                print(f"[SYNC] POST URL: {post_url}")
                print(f"[SYNC] Creando nuevo: {image_name}")
                resp = requests.post(post_url, json={"values": [[image_name, 1, 0]]})
                print(f"[SYNC] POST response: {resp.status_code} - {resp.text}")
        
        elif action == "dislike":
            if row_to_update > 0:
                current_dislikes = int(values[row_to_update-1][2]) if len(values[row_to_update-1]) > 2 and values[row_to_update-1][2] else 0
                new_dislikes = current_dislikes + 1
                update_range = f"A{row_to_update}:C{row_to_update}"
                patch_url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{update_range}?valueInputOption=USER_ENTERED&key={GOOGLE_API_KEY}"
                resp = requests.put(patch_url, json={"values": [[image_name, values[row_to_update-1][1] if len(values[row_to_update-1]) > 1 else 0, new_dislikes]]})
                print(f"[SYNC] PUT response: {resp.status_code}")
            else:
                post_url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{range_name}:append?valueInputOption=USER_ENTERED&key={GOOGLE_API_KEY}"
                resp = requests.post(post_url, json={"values": [[image_name, 0, 1]]})
                print(f"[SYNC] POST response: {resp.status_code}")
        
        print("[SYNC] Completado exitosamente")
        return None
    except Exception as e:
        print(f"[SYNC] EXCEPTION: {str(e)}")
        return str(e)

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def load_cached_data():
    ensure_cache_dir()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def save_cached_data(data):
    ensure_cache_dir()
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def fetch_repo_data(url):
    """Fetches data from a GitHub repository URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def get_wallpaper_categories():
    cached = load_cached_data()
    
    print("Fetching repository structure from GitHub...")
    categories = {}
    
    folders = fetch_repo_data(GITHUB_REPO_URL)
    if not folders:
        return cached if cached else {"Error": []}
    
    new_categories_found = False
    
    for folder in folders:
        if folder.get('type') == 'dir':
            category_name = folder.get('name')
            print(f"Processing category: {category_name}")
            
            images = []
            folder_url = f"{GITHUB_REPO_URL}/{category_name}"
            contents = fetch_repo_data(folder_url)
            
            if contents:
                for item in contents:
                    if item.get('type') == 'file' and item.get('name', '').lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        images.append({
                            'name': item.get('name'),
                            'download_url': item.get('download_url'),
                            'path': f"{category_name}/{item.get('name')}"
                        })
            
            categories[category_name] = images
            
            if not cached or category_name not in cached:
                new_categories_found = True
    
    if cached:
        for category_name in cached:
            if category_name not in categories:
                categories[category_name] = cached[category_name]
    
    if new_categories_found or categories != cached:
        print("New categories detected, updating cache...")
        save_cached_data(categories)
    else:
        print("Loading from cache...")
    
    return categories

def get_desktop_environment():
    xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
    
    if 'gnome' in xdg_current_desktop or 'gnome' in desktop_session:
        return 'gnome'
    elif 'kde' in xdg_current_desktop or 'plasma' in xdg_current_desktop:
        return 'kde'
    elif 'xfce' in xdg_current_desktop or 'xfce' in desktop_session:
        return 'xfce'
    elif 'mate' in xdg_current_desktop:
        return 'mate'
    elif 'cinnamon' in xdg_current_desktop:
        return 'cinnamon'
    elif 'deepin' in xdg_current_desktop:
        return 'deepin'
    elif 'sway' in desktop_session:
        return 'sway'
    return 'generic'

def set_wallpaper(image_path, image_url):
    download_dir = os.path.expanduser("~/Imágenes/Wallpapers")
    os.makedirs(download_dir, exist_ok=True)
    
    image_name = os.path.basename(image_path) if image_path else "wallpaper.jpg"
    local_path = os.path.join(download_dir, image_name)
    
    try:
        if image_url:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        print(f"Error downloading wallpaper: {e}")
        return False
    
    de = get_desktop_environment()
    print(f"Setting wallpaper for: {de}")
    
    try:
        if de == 'gnome':
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file://{local_path}'], check=True)
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', f'file://{local_path}'], check=True)
        elif de == 'kde':
            result = subprocess.run(['kreadconfig5', '--file', 'plasma-desktop', '--group', 'Wallpaper', '--key', 'Image'], capture_output=True, text=True)
            subprocess.run(['kwriteconfig5', '--file', 'plasma-desktop', '--group', 'Wallpaper', '--key', 'Image', local_path], check=True)
            subprocess.run(['qdbus', 'org.kde.plasmashell', '/PlasmaShell', 'org.kde.PlasmaShell.evaluateScript', f'''
                var allDesktops = desktops();
                for (i=0;i<allDesktops.length;i++) {{
                    d = allDesktops[i];
                    d.wallpaperPlugin = "org.kde.image";
                    d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                    d.writeConfig("Image", "file://{local_path}");
                }}
            '''], check=True)
        elif de == 'xfce':
            subprocess.run(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/backdrop/screen0/monitor0/workspace0/last-image', '-s', local_path], check=True)
        elif de == 'mate':
            subprocess.run(['gsettings', 'set', 'org.mate.background', 'picture-filename', local_path], check=True)
        elif de == 'cinnamon':
            subprocess.run(['gsettings', 'set', 'org.cinnamon.desktop.background', 'picture-uri', f'file://{local_path}'], check=True)
        elif de == 'deepin':
            subprocess.run(['gsettings', 'set', 'com.deepin.dde.appearance', 'background', local_path], check=True)
        elif de == 'sway':
            subprocess.run(['swaymsg', 'output * background', local_path, 'fill'], check=True)
        else:
            if shutil.which('feh'):
                subprocess.run(['feh', '--bg-scale', local_path], check=True)
            elif shutil.which('nitrogen'):
                subprocess.run(['nitrogen', '--set-zoom-fill', local_path], check=True)
            else:
                print("No wallpaper setter found. Downloaded to:", local_path)
                return False
        print(f"Wallpaper set successfully: {local_path}")
        return True
    except Exception as e:
        print(f"Error setting wallpaper: {e}")
        return False

def get_icon(icon_name):
    """Creates a QIcon with proper shapes."""
    pixmap = QPixmap(48, 48)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    if icon_name == "download":
        pen = QPen(QColor("#2ECC71"), 3)
        painter.setPen(pen)
        painter.setBrush(QColor("#2ECC71"))
        painter.drawRoundedRect(8, 6, 32, 28, 4, 4)
        painter.setPen(QPen(QColor("white"), 3))
        painter.drawLine(24, 14, 24, 28)
        painter.drawLine(18, 22, 24, 28)
        painter.drawLine(30, 22, 24, 28)
    elif icon_name == "wallpaper":
        pen = QPen(QColor("#9B59B6"), 3)
        painter.setPen(pen)
        painter.setBrush(QColor("#9B59B6"))
        painter.drawRoundedRect(6, 4, 36, 28, 4, 4)
        painter.setBrush(QColor("#34495E"))
        painter.drawRect(10, 10, 28, 16)
    else:
        pen = QPen(QColor("#3498DB"), 3)
        painter.setPen(pen)
        painter.setBrush(QColor("#3498DB"))
        painter.drawEllipse(12, 12, 24, 24)

    painter.end()
    return QIcon(pixmap)

class WallpaperCard(QWidget):
    def __init__(self, image_info, parent=None):
        super().__init__(parent)
        self.image_info = image_info
        self.liked = False
        self.disliked = False
        self.setFixedSize(320, 400)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        self.setObjectName("wallpaperCard")

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(300, 200)
        self.image_label.setMaximumSize(300, 200)
        self.image_label.setStyleSheet("border-radius: 12px; border: 2px solid #0f3460;")
        self.layout.addWidget(self.image_label)

        self.download_row = QHBoxLayout()
        self.download_row.setSpacing(10)
        
        self.download_button = QPushButton()
        self.download_button.setIcon(get_icon("download"))
        self.download_button.setText(" Descargar")
        self.download_button.setObjectName("actionButton")
        self.download_button.clicked.connect(self.on_download_clicked)
        self.download_row.addWidget(self.download_button)

        self.wallpaper_button = QPushButton()
        self.wallpaper_button.setIcon(get_icon("wallpaper"))
        self.wallpaper_button.setText(" Aplicar")
        self.wallpaper_button.setObjectName("actionButton")
        self.wallpaper_button.clicked.connect(self.on_set_wallpaper_clicked)
        self.download_row.addWidget(self.wallpaper_button)

        self.layout.addLayout(self.download_row)

        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(15)
        
        self.like_button = QPushButton("♥ Like")
        self.like_button.setObjectName("likeButton")
        self.like_button.setFixedWidth(80)
        self.like_button.clicked.connect(self.on_like_clicked)
        self.stats_row.addWidget(self.like_button)

        self.like_label = QLabel("0")
        self.like_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.like_label.setObjectName("likeLabel")
        self.stats_row.addWidget(self.like_label)

        self.dislike_button = QPushButton("✗ Dislike")
        self.dislike_button.setObjectName("dislikeButton")
        self.dislike_button.setFixedWidth(80)
        self.dislike_button.clicked.connect(self.on_dislike_clicked)
        self.stats_row.addWidget(self.dislike_button)

        self.dislike_label = QLabel("0")
        self.dislike_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dislike_label.setObjectName("dislikeLabel")
        self.stats_row.addWidget(self.dislike_label)

        self.layout.addLayout(self.stats_row)

        self.opacity = 0
        self.setStyleSheet("WallpaperCard { background-color: #1f4068; border-radius: 16px; }")
        QTimer.singleShot(50, self.load_image)
        
        self._animate_appearance()
        self._load_likes_from_cache()

    def _load_likes_from_cache(self):
        image_name = self.image_info.get('name', '')
        if image_name in likes_cache:
            data = likes_cache[image_name]
            self._update_stats(data.get('likes', 0), data.get('dislikes', 0))

    def _update_stats(self, likes, dislikes):
        self.like_label.setText(f"♥ {likes}")
        self.dislike_label.setText(f"✗ {dislikes}")

    def _animate_appearance(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def load_image(self):
        """Loads the actual image from the URL with caching."""
        if not self.image_info or not self.image_info.get('download_url'):
            self.display_placeholder("No URL")
            return

        if Image is None:
            self.display_placeholder("Pillow missing")
            return

        img_name = self.image_info.get('name', 'image')
        cache_key = os.path.join(image_cache_dir, img_name.replace('/', '_'))
        
        try:
            if os.path.exists(cache_key):
                pixmap = QPixmap(cache_key)
            else:
                response = requests.get(self.image_info['download_url'], stream=True, timeout=10)
                response.raise_for_status()
                
                image_bytes = response.content
                img = Image.open(io.BytesIO(image_bytes))
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.thumbnail((400, 300), Image.Resampling.LANCZOS)
                img.save(cache_key, quality=85)
                
                qimage = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)

            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.display_placeholder("Cargando...")

    def display_placeholder(self, text="Loading Image..."):
        """Displays a placeholder message on the image label."""
        placeholder_width = max(self.image_label.minimumWidth(), 200)
        placeholder_height = max(self.image_label.minimumHeight(), 150)
        
        pixmap = QPixmap(placeholder_width, placeholder_height)
        pixmap.fill(QColor("#E0E0E0")) # Light grey placeholder
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.gray)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.image_label.setMinimumSize(QSize(placeholder_width, placeholder_height))

    def on_download_clicked(self):
        """Handles the download button click."""
        print(f"Download clicked for: {self.image_info.get('name')}")
        if not self.image_info or not self.image_info.get('download_url'):
            print("Cannot download: no URL available.")
            return

        image_url = self.image_info['download_url']
        image_name = self.image_info.get('name', 'wallpaper.jpg') # Default name if none

        # Define download directory relative to the script's execution path
        download_dir = os.path.join(".", "downloads") # Save in a 'downloads' subdirectory
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
                print(f"Created download directory: {download_dir}")
            except OSError as e:
                print(f"Error creating download directory {download_dir}: {e}")
                return

        save_path = os.path.join(download_dir, image_name)

        try:
            print(f"Downloading {image_url} to {save_path}")
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Successfully downloaded {image_name}")
            # TODO: Add a user-facing confirmation message (e.g., a status bar message)

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {image_name}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during download: {e}")

    def on_set_wallpaper_clicked(self):
        print(f"Set Wallpaper clicked for: {self.image_info.get('name')}")
        if self.image_info and self.image_info.get('download_url'):
            set_wallpaper(self.image_info.get('path'), self.image_info.get('download_url'))

    def on_like_clicked(self):
        image_name = self.image_info.get('name', '')
        if not self.liked:
            self.liked = True
            self.like_button.setProperty("liked", "true")
            self.like_button.style().unpolish(self.like_button)
            self.like_button.style().polish(self.like_button)
            result = sync_likes_to_sheet(image_name, "like")
            if result:
                QMessageBox.information(self, "Error", f"No se pudo sincronizar: {result}")
            likes_cache[image_name] = likes_cache.get(image_name, {'likes': 0, 'dislikes': 0})
            likes_cache[image_name]['likes'] = likes_cache[image_name].get('likes', 0) + 1
            save_likes_cache()
            self._update_stats(likes_cache[image_name].get('likes', 0), likes_cache[image_name].get('dislikes', 0))

    def on_dislike_clicked(self):
        image_name = self.image_info.get('name', '')
        if not self.disliked:
            self.disliked = True
            self.dislike_button.setProperty("disliked", "true")
            self.dislike_button.style().unpolish(self.dislike_button)
            self.dislike_button.style().polish(self.dislike_button)
            result = sync_likes_to_sheet(image_name, "dislike")
            if result:
                QMessageBox.information(self, "Error", f"No se pudo sincronizar: {result}")
            likes_cache[image_name] = likes_cache.get(image_name, {'likes': 0, 'dislikes': 0})
            likes_cache[image_name]['dislikes'] = likes_cache[image_name].get('dislikes', 0) + 1
            save_likes_cache()
            self._update_stats(likes_cache[image_name].get('likes', 0), likes_cache[image_name].get('dislikes', 0))

class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self, wallpaper_data, parent=None):
        super().__init__(parent)
        self.wallpaper_data = wallpaper_data
        self.setWindowTitle("Linux Wallpaper App")
        self.setGeometry(100, 100, 1200, 800) # x, y, width, height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # --- Sidebar for Categories ---
        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(10)
        self.sidebar_widget.setFixedWidth(250) # Fixed width for sidebar
        self.sidebar_widget.setObjectName("sidebarWidget") # For QSS styling

        self.category_label = QLabel("Categories")
        self.category_label.setObjectName("sidebarHeader") # For QSS styling
        self.sidebar_layout.addWidget(self.category_label)

        self.category_list = QListWidget()
        self.category_list.setObjectName("categoryList") # For QSS styling
        self.category_list.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.populate_categories()
        self.category_list.currentRowChanged.connect(self.display_images_for_category)
        self.sidebar_layout.addWidget(self.category_list)

        self.refresh_button = QPushButton("🔄 Actualizar")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.refresh_categories)
        self.sidebar_layout.addWidget(self.refresh_button)

        self.settings_button = QPushButton("⚙️ Ajustes")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.clicked.connect(self.show_settings)
        self.sidebar_layout.addWidget(self.settings_button)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(self.status_label)

        # --- Main Content Area for Wallpapers ---
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        self.content_widget.setObjectName("contentWidget") # For QSS styling

        self.current_category_label = QLabel("Select a category")
        self.current_category_label.setObjectName("contentHeader") # For QSS styling
        self.content_layout.addWidget(self.current_category_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("wallpaperScrollArea") # For QSS styling

        self.wallpaper_grid_widget = QWidget()
        self.wallpaper_grid_layout = QGridLayout(self.wallpaper_grid_widget)
        self.wallpaper_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.wallpaper_grid_layout.setSpacing(15) # Spacing between cards in grid
        self.wallpaper_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.wallpaper_grid_widget)
        self.content_layout.addWidget(self.scroll_area)

        # Add sidebar and content to main layout
        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.content_widget)

        self.load_stylesheet()
        self.load_initial_wallpapers()

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajustes")
        dialog.setFixedSize(450, 450)
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Linux Wallpaper App")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #e94560;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        created = QLabel("Creado por Agdala 2026")
        created.setStyleSheet("font-weight: bold; color: #2ecc71; font-size: 14px;")
        created.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(created)
        
        layout.addSpacing(20)
        
        info = QLabel("Aplicación para explorar y descargar\nwallpapers para Linux.\n\nDesarrollada con PyQt6.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(info)
        
        layout.addSpacing(30)
        
        donate = QLabel("☕ Invita un café")
        donate.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 16px;")
        donate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(donate)
        
        btc_btn = QPushButton("BTC: 3L8f3v6BWwL7KBcb8AMZQ2bpE3ACne2EUf")
        btc_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
            }
        """)
        btc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btc_btn.clicked.connect(lambda: self.copy_to_clipboard("3L8f3v6BWwL7KBcb8AMZQ2bpE3ACne2EUf", btc_btn))
        layout.addWidget(btc_btn)
        
        email_btn = QPushButton("📧 agdala.sv@gmail.com")
        email_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        email_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        email_btn.clicked.connect(lambda: self.copy_to_clipboard("agdala.sv@gmail.com", email_btn))
        layout.addWidget(email_btn)
        
        layout.addStretch()
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.close)
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
            }
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
        """)
        
        dialog.exec()

    def copy_to_clipboard(self, text, button):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        original_text = button.text()
        button.setText("¡Copiado!")
        QTimer.singleShot(1500, lambda: button.setText(original_text))

    def load_stylesheet(self):
        """Loads the QSS stylesheet."""
        try:
            with open("styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Error: styles.qss not found.")
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

    def populate_categories(self):
        """Populates the category list widget."""
        if not self.wallpaper_data:
            self.category_list.addItem("No Categories Found")
            return

        for category_name in self.wallpaper_data.keys():
            self.category_list.addItem(category_name)
        
        # Select the first category by default if available
        if self.wallpaper_data:
            self.category_list.setCurrentRow(0)

    def display_images_for_category(self, row):
        """Displays images for the selected category."""
        if not self.wallpaper_data or row < 0 or row >= len(self.wallpaper_data):
            self.current_category_label.setText("Select a category")
            self.clear_grid_layout()
            return

        categories = list(self.wallpaper_data.keys())
        selected_category_name = categories[row]
        self.current_category_label.setText(selected_category_name)
        
        images_in_category = self.wallpaper_data.get(selected_category_name, [])
        self.display_wallpapers_in_grid(images_in_category)

    def load_initial_wallpapers(self):
        """Loads wallpapers for the default selected category on startup."""
        if self.wallpaper_data and self.category_list.currentItem():
            self.display_images_for_category(self.category_list.currentRow())
        else:
            self.current_category_label.setText("No wallpapers available.")
            self.clear_grid_layout()

    def refresh_categories(self):
        """Actualiza las categorías desde GitHub."""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Actualizando...")
        QApplication.processEvents()
        
        new_data = get_wallpaper_categories()
        self.wallpaper_data = new_data
        
        current_category = self.category_list.currentItem()
        current_row = self.category_list.currentRow()
        
        self.category_list.clear()
        self.populate_categories()
        
        if current_category and current_row >= 0:
            self.category_list.setCurrentRow(current_row)
        
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("🔄 Actualizar")
        
    def display_wallpapers_in_grid(self, images):
        """Clears the current grid and displays new wallpaper cards."""
        self.clear_grid_layout()
        
        if not images:
            self.current_category_label.setText("No wallpapers in this category.")
            return

        grid_columns = 3 
        
        for index, image_info in enumerate(images):
            card = WallpaperCard(image_info)
            
            row = index // grid_columns
            col = index % grid_columns
            self.wallpaper_grid_layout.addWidget(card, row, col)
            
            self.wallpaper_grid_layout.setRowStretch(row, 0)
            self.wallpaper_grid_layout.setColumnStretch(col, 0)

    def clear_grid_layout(self):
        """Clears all widgets from the wallpaper grid layout."""
        while self.wallpaper_grid_layout.count():
            item = self.wallpaper_grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 350)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        container = QWidget()
        container.setObjectName("splashContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(logo_label)
        
        title_label = QLabel("Wallpaper App")
        title_label.setObjectName("splashTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Power by Agdala")
        subtitle_label.setObjectName("splashSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(subtitle_label)
        
        container_layout.addSpacing(20)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("splashProgressBar")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        container_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Cargando...")
        self.status_label.setObjectName("splashStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.status_label)
        
        layout.addWidget(container)
        self.setStyleSheet("""
            QWidget#splashContainer {
                background-color: #1a1a2e;
                border-radius: 20px;
                border: 2px solid #0f3460;
            }
            QLabel#splashTitle {
                color: #e94560;
                font-size: 28px;
                font-weight: bold;
            }
            QLabel#splashSubtitle {
                color: #a0a0a0;
                font-size: 14px;
            }
            QProgressBar#splashProgressBar {
                border: 2px solid #0f3460;
                border-radius: 10px;
                text-align: center;
                background-color: #16213e;
                color: white;
                font-weight: bold;
            }
            QProgressBar#splashProgressBar::chunk {
                background-color: #e94560;
                border-radius: 8px;
            }
            QLabel#splashStatus {
                color: #a0a0a0;
                font-size: 12px;
            }
        """)
        
        self.center_on_screen()
    
    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.geometry()
            x = (rect.width() - self.width()) // 2
            y = (rect.height() - self.height()) // 2
            self.move(x, y)
    
    def update_progress(self, value, status=""):
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(logo_path):
        app_icon = QIcon(logo_path)
        app.setWindowIcon(app_icon)
    
    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()
    
    load_likes_cache()
    ensure_cache_dir()
    
    splash.update_progress(10, "Cargando categorías...")
    QApplication.processEvents()
    
    wallpaper_categories_data = get_wallpaper_categories()
    
    total_images = sum(len(images) for images in wallpaper_categories_data.values() if isinstance(images, list))
    
    if total_images > 0:
        splash.update_progress(30, f"Categorías: {len(wallpaper_categories_data)}")
        QApplication.processEvents()
        
        loaded = 0
        for category, images in wallpaper_categories_data.items():
            if isinstance(images, list):
                for img in images:
                    loaded += 1
                    progress = 30 + int((loaded / total_images) * 50)
                    splash.update_progress(progress, f"Cargando...")
                    QApplication.processEvents()
    else:
        splash.update_progress(50, "Cargando desde caché...")
        QApplication.processEvents()
    
    import time
    splash.update_progress(80, "Preparando interfaz...")
    QApplication.processEvents()
    time.sleep(0.5)
    
    splash.update_progress(100, "¡Listo!")
    QApplication.processEvents()
    time.sleep(2)
    splash.close()
    
    main_window = MainWindow(wallpaper_categories_data)
    main_window.show()
    
    sys.exit(app.exec())
