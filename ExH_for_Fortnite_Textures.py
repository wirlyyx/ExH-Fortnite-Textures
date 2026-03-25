import base64
import os
import platform
import random
import subprocess
import sys
import webbrowser
import requests
import os
import sys
import json
import shutil
import glob
import hashlib
import builtins
import types
import ctypes
from ctypes import wintypes
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QThread, pyqtSignal, \
    QEasingCurve, QRectF, pyqtProperty, QSize, QRect, qInstallMessageHandler, QtMsgType
from PyQt5.QtGui import QColor, QPainter, QPixmap, QIcon, QPen, QPainterPath, QRegion
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QLabel, QMainWindow, QGraphicsOpacityEffect, \
    QToolButton, QScrollArea, QGridLayout, QSlider, QSizePolicy

marc = """
############################################################################
# _____        _   _   ____          __        __ _        _               #
#| ____|__  __| | | | | __ )  _   _  \ \      / /(_) _ __ | | _   _  _   _ #
#|  _|  \ \/ /| |_| | |  _ \ | | | |  \ \ /\ / / | || '__|| || | | || | | |#
#| |___  >  < |  _  | | |_) || |_| |   \ V  V /  | || |   | || |_| || |_| |#
#|_____|/_/\_\|_| |_| |____/  \__, |    \_/\_/   |_||_|   |_| \__, | \__, |#
#                             |___/                           |___/  |___/ #
############################################################################
"""
print(marc)

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')
sys.tracebacklimit = 0
builtins.print = lambda *a, **k: None
sys.excepthook = lambda *a, **k: None
def _no_repr(*args, **kwargs):
    return ""
builtins.repr = _no_repr



def _setup_library_path():
    base_path = os.path.dirname(os.path.abspath(__file__))

    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    return base_path
_PROGRAM_PATH = _setup_library_path()

import ExHbyWirlyyP
import ExHbyWirlyyS

class ModernToggle(QWidget):
    def __init__(self, parent=None, reverse=False, checked=False):
        super().__init__(parent)
        self.reverse = reverse
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(40, 24)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self._pos = 0.0
        self.is_on = bool(checked)
        self.on_callback = None
        self.off_callback = None

        self.anim = QPropertyAnimation(self, b"pos", self)
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        target = 1.0 if self.is_on else 0.0
        if self.reverse:
            target = 1.0 - target
        self._pos = target

    def on_toggled(self, on_func=None, off_func=None):
        self.on_callback = on_func
        self.off_callback = off_func
        return self

    @pyqtProperty(float)
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, v):
        self._pos = v
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle()
        super().mouseReleaseEvent(event)

    def toggle(self):
        self.is_on = not self.is_on
        target = 1.0 if self.is_on else 0.0
        if self.reverse:
            target = 1.0 - target

        self.anim.stop()
        self.anim.setStartValue(self._pos)
        self.anim.setEndValue(target)
        self.anim.start()

        if self.is_on and self.on_callback:
            self.on_callback()
        elif not self.is_on and self.off_callback:
            self.off_callback()

    def setChecked(self, checked):
        if bool(checked) != self.is_on:
            self.toggle()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        try:
            w, h = self.width(), self.height()
            if w < 40 or h < 24: return

            margin = max(3, h // 10)
            knob = h - 2 * margin

            on_color, off_color = QColor(60, 60, 60), QColor(140, 140, 140)
            alpha_off, alpha_on = 0.80, 0.70

            pos_clamped = max(0.0, min(1.0, self._pos))
            alpha = alpha_off + (alpha_on - alpha_off) * pos_clamped
            alpha = max(0.0, min(1.0, alpha))

            bg = QColor()
            bg.setRgbF(
                off_color.redF() + (on_color.redF() - off_color.redF()) * pos_clamped,
                off_color.greenF() + (on_color.greenF() - off_color.greenF()) * pos_clamped,
                off_color.blueF() + (on_color.blueF() - off_color.blueF()) * pos_clamped,
                alpha
            )

            p.setBrush(bg)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(0, 0, w, h, h // 2, h // 2)

            draw_pos = 1.0 - pos_clamped if self.reverse else pos_clamped
            x = margin + (w - knob - 2 * margin) * draw_pos

            p.setBrush(Qt.white)
            p.setPen(QPen(QColor("#00000020"), max(1.5, knob * 0.06)))
            p.drawEllipse(QRectF(x, margin, knob, knob))
        finally:
            p.end()


class DownloadThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, file_url, save_path):
        super().__init__()
        self.file_url = file_url.replace("dl=0", "dl=1").strip()
        self.save_path = save_path

    def run(self):
        try:
            resp = requests.get(self.file_url, stream=True, timeout=120)
            if resp.status_code == 200 and 'text/html' not in resp.headers.get('Content-Type', ''):
                tmp = self.save_path + ".tmp"
                with open(tmp, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                    f.flush();
                    os.fsync(f.fileno())
                os.replace(tmp, self.save_path)
                if os.path.getsize(self.save_path) > 1024:
                    self.finished.emit(self.save_path)
                    return
        except Exception as e:
            pass
        finally:
            self.quit()


class ApplyThread(QThread):
    apply_complete_signal = pyqtSignal()

    def __init__(self, nip_path, exe_path, temp_dir, xml_content):
        super().__init__()
        self.nip_path = nip_path
        self.exe_path = exe_path
        self.temp_dir = temp_dir
        self.xml_content = xml_content

    def run(self):
        try:
            with open(self.nip_path, "w", encoding="utf-16") as f:
                f.write(self.xml_content)

            proc = subprocess.Popen([self.exe_path, self.nip_path], cwd=self.temp_dir)
            proc.wait()

            for p in [self.exe_path, self.nip_path]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except:
                        pass
        except Exception as e:
            pass
        finally:
            self.apply_complete_signal.emit()
            self.quit()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Star:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.uniform(0.5, 2.5)
        c = random.randint(150, 220)
        self.color = QColor(c, c, c)
        self.opacity = random.uniform(0.1, 1)
        self.speed = random.uniform(0.005, 0.02)
        self.increasing = random.choice([True, False])

    def update(self, width, height):
        if self.increasing:
            self.opacity += self.speed
            if self.opacity >= 1.0:
                self.opacity = 1.0
                self.increasing = False
        else:
            self.opacity -= self.speed
            if self.opacity <= 0.0:
                self.opacity = 0.0
                self.increasing = True
                self.x = random.randint(0, width)
                self.y = random.randint(0, height)


class StarField(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.stars = [Star(615, 300) for _ in range(60)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(20)
        self._stars_data = []

    def animate(self):
        if not self.isVisible():
            return
        for star in self.stars:
            star.update(self.width(), self.height())
        self.update()

    def paintEvent(self, event):
        if not self.isVisible():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        try:
            for star in self.stars:
                color = QColor(star.color)
                alpha = max(0.0, min(1.0, star.opacity))
                color.setAlphaF(alpha)
                painter.setPen(Qt.NoPen)
                painter.setBrush(color)
                painter.drawEllipse(QRectF(star.x, star.y, star.size, star.size))
        finally:
            painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ExH for Fortnite Textures')
        self.setGeometry(300, 300, 635, 320)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.old_position = None
        self.dragging = False
        self.has_nvidia = False
        self.soap_skins = False
        self.paks_del = False
        self.trash = False
        self.localizations = {lang: False for lang in
                              ["en", "ru", "fr", "cs", "de", "es", "id", "it", "ja", "ko", "nl", "pl", "pt", "th", "tr",
                               "vi", "zh"]}

        self.des_icon = "iVBORw0KGgoAAAANSUhEUgAAA0gAAANbCAYAAAB4pb/uAAAgAElEQVR4nOzdf0yb950H8LeN4xBizI8Qh7iEOoRfISklGaVcxtIsTdKsy3pZV3XdVq1dq7vdpl2lm6bT7W53N5100mnaSbupq6redmu7LuOqLMplaZImKSGEMEYpZYQAAUMc4jjEGIMNGGOMfX+U5+ljYwjwPMADfr8kK4QfD28eP78+z/f7fL+acDgchoKGhoag1CI1Gg1SU1MVWZaA+eRhPvnUnpH55GE++dSekfnkYT7lqD0r88nDfMqZb1YdAMX+OGFZSi9PScwnf3nxlk+j0XAfkbk8JTGf/OVxH5G/POaTt7x4zcd9Rf7ylMR88pe3WvcVrWK/mYiIiIiIaIVjgURERERERDSFBRIREREREdEUFkhERERERERTWCARERERERFNYYFEREREREQ0hQUSERERERHRFBZIREREREREU1ggERERERERTWGBRERERERENIUFEhERERER0RQWSERERERERFNYIBEREREREU1hgURERERERDRF1QWSRqNBOBxe7hgzYj55mE8+tWdkPnmYTz61Z2Q+eZhPOWrPynzyMN/8qLpACofD0Gg0yx1jRswnD/PJp/aMzCcP88mn9ozMJw/zKUftWZlPHuabH1UXSEREREREREtJp+TClK7+lK4kmU8e5pNP7RmZTx7mk0/tGZlPHuZTjtqzMp88zKechWTVDQ0NKdbnT6PRwGg0KvpHejwe5pOB+eTxeDwAoPqMzLdwzCcP9xH5mE+elZRPyecs4n1dysV88qz2fUUXDocVfShqMSpU5ls45pNHyKb2jMy3cMwnD/cR+ZhPnpWWbyVllYv55In3fMuZlc8gERERERERTVF1gaS2ES2iMZ88zCef2jMynzzMJ5/aMzKfPMynHLVnZT55mG9+VF0gKdn/cDEwnzzMJ5/aMzKfPMwnn9ozMp88zKcctWdlPnmYb35UXSAREREREREtJRZIREREREREU1ggERERERERTWGBRERERERENIUFEhERERER0RQWSERERERERFNYIBEREREREU1hgURERERERDSFBRIREREREdEUFkhERERERERTWCARERERERFNYYFEREREREQ0RZECKRwOK7GYRcN88jCffGrPyHzyMJ98as/IfPIwn3LUnpX55GE+5cjJqkiBpNFolFjMomE+eZhPPrVnZD55mE8+tWdkPnmYTzlqz8p88jCfcuRk1Sn5hy7GSmM+9SyT+dS3PKWXyXzqWdZiLFPt+RZjeUovk/nUs6zFWOZi51tJWdW0rMVYJvOpZ1mxlrncWTXhTygWwuPxKNb8ptFokJKSosiyBMwnTzzm02g0ijYpx+M6VBLzycN9RD7mkyee83FfWTjmk2el5VvufUWn2G+eEg6HVd0/kfnkYT751J6R+eRhPvnUnpH55GE+5ag9K/PJw3zKmW/WRRvFTu0rjPnkYT751J6R+eRhPvnUnpH55GE+5ag9K/PJw3zKmWvWRSuQ1P4QF/PJw3zyqT0j88nDfPKpPSPzycN8ylF7VuaTh/mUM9esnAeJiIiIiIhoCgskIiIiIiKiKSyQiIiIiIiIprBAIiIiIiIimsICiYiIiIiIaAoLJCIiIiIioikskIiIiIiIiKawQCIiIiIiIprCAomIiIiIiGgKCyQiIiIiIqIpLJCIiIiIiIimsEAiIiIiIiKaouoCSaPRIBwOL3eMGTGfPMwnn9ozMp88zCef2jMynzzMpxy1Z2U+eZhvflRdIIXDYWg0muWOMSPmk4f55FN7RuaTh/nkU3tG5pOH+ZSj9qzMJw/zzY+qCyQiIiIiIqKlpFNyYUpXf0pXkswnD/PJp/aMzCcP88mn9ozMJw/zKUftWZlPHuZTzkKy6oaGhhTr86fRaGA0GhX9Iz0eD/PJwHzyeDweAFB9RuZbOOaTh/uIfMwnz0rKp+RzFvG+LuViPnlW+76iC4fDij4UtRgVKvMtHPPJI2RTe0bmWzjmk4f7iHzMJ89Ky7eSssrFfPLEe77lzMpnkIiIiIiIiKaoukBS24gW0ZhPHuaTT+0ZmU8e5pNP7RmZTx7mU47aszKfPMw3P6oukJTsf7gYmE8e5pNP7RmZTx7mk0/tGZlPHuZTjtqzMp88zDc/qi6QiIiIiIiIlhILJCIiIiIioikskIiIiIiIiKawQCIiIiIiIprCAomIiIiIiGgKCyQiIiIiIqIpLJCIiIiIiIimsEAiIiIiIiKawgKJiIiIiIhoCgskIiIiIiKiKSyQiIiIiIiIprBAIiIiIiIimqJIgRQOh5VYzKJhPnmYTz61Z2Q+eZhPPrVnZD55mE85as/KfPIwn3LkZFWkQNJoNEosZtEwnzzMJ5/aMzKfPMwnn9ozMp88zKcctWdlPnmYTzlysuqU/EMXY6Uxn3qWyXzqW57Sy2Q+9SxrMZap9nyLsTyll8l86lnWYixzsfOtpKxqWtZiLJP51LOsWMtc7qya8CcUC+HxeBRrftNoNEhJSVFkWQLmkyce82k0GkWblONxHSqJ+eThPiIf88kTz/m4rywc88mz0vIt976iU+w3TwmHw6run8h88jCffGrPyHzyMJ98as/IfPIwn3LUnpX55GE+5cw366KNYqf2FcZ88jCffGrPyHzyMJ98as/IfPIwn3LUnpX55GE+5cw166IVSGp/iIv55GE++dSekfnkYT751J6R+eRhPuWoPSvzycN8yplrVs6DRERERERENIUFEhERERER0RQWSERERERERFNYIBEREREREU1hgURERERERDSFBRIREREREdEUFkhERERERERTWCARERERERFNYYFEREREREQ0hQUSERERERHRFBZIREREREREU1ggERERERERTVF1gaTRaBAOh5c7xoyYTx7mk0/tGZlPHuaTT+0ZmU8e5lOO2rMynzzMNz+qLpDC4TA0Gs1yx5gR88nDfPKpPSPzycN88qk9I/PJw3zKUXtW5pOH+eZH1QUSERERERHRUtIpuTClqz+lK0nmk4f55FN7RuaTh/nkU3tG5pOH+ZSj9qzMJw/zKWchWXVDQ0OK9fnTaDQwGo2K/pEej4f5ZGA+eTweDwCoPiPzLRzzycN9RD7mk2cl5VPyOYt4X5dyMZ88q31f0YXDYUUfilqMCpX5Fo755BGyqT0j8y0c88nDfUQ+5pNnpeVbSVnlYj554j3fcmblM0hERERERERTVF0gqW1Ei2jMJw/zyaf2jMwnD/PJp/aMzCcP8ylH7VmZTx7mmx9VF0hK9j9cDMwnD/PJp/aMzCcP88mn9ozMJw/zKUftWZlPHuabH1UXSEREREREREuJBRIREREREdEUFkhERERERERTWCARERERERFNYYFEREREREQ0hQUSERERERHRFBZIREREREREU1ggERERERERTWGBRERERERENIUFEhERERER0RQWSERERERERFNYIBEREREREU1RpEAKh8NKLGbRMJ88zCef2jMynzzMJ5/aMzKfPMynHLVnZT55mE85crIqUiBpNBolFrNomE8e5pNP7RmZTx7mk0/tGZlPHuZTjtqzMp88zKccOVl1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"
        self.white_icon_des = self.get_colored_icon(self.des_icon, "#dddddd")

        self.yt_icon = "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"
        self.white_icon_yt = self.get_colored_icon(self.yt_icon, "#dddddd")


        self.container = QWidget(self)
        self.container.setGeometry(10, 10, 615, 300)
        self.container.setStyleSheet("""
            background:
                #050505
                qradialgradient(cx:0.18, cy:0.22, radius:1.1, fx:0.25, fy:0.15,
                    stop:0 #050505, stop:0.35 #1e1e1e, stop:0.55 #111111, stop:0.75 #0a0a0a),
                qradialgradient(cx:0.78, cy:0.82, radius:0.95, fx:0.85, fy:0.90,
                    stop:0 #050505, stop:0.3 #222222, stop:0.5 #151515, stop:0.7 #0c0c0c),
                qradialgradient(cx:0.55, cy:0.48, radius:0.65, fx:0.60, fy:0.52,
                    stop:0 #050505, stop:0.4 #282828, stop:0.6 #1a1a1a),
                qradialgradient(cx:0.88, cy:0.12, radius:0.7, fx:0.92, fy:0.08,
                    stop:0 #050505, stop:0.45 #202020, stop:0.65 #121212);
            border-radius: 28px;
            border: 2px solid rgba(60,60,60,0.6);
        """)


        self.stars_layer = StarField(self.container)
        self.stars_layer.setGeometry(0, 0, 615, 300)

        self.containero = QGraphicsOpacityEffect(self.container)
        self.containero.setOpacity(1.0)
        self.container.setGraphicsEffect(self.containero)
        self.container.hide()

        self.welc_fon_container = QWidget(self)
        self.welc_fon_container.setGeometry(10, 10, 615, 300)
        self.welc_fon_container.setStyleSheet("""
            background-color: rgba(0,0,0, 1);
            border-radius: 20px;
        """)
        self.welc_fon_containero = QGraphicsOpacityEffect(self.welc_fon_container)
        self.welc_fon_containero.setOpacity(0)
        self.welc_fon_container.setGraphicsEffect(self.welc_fon_containero)
        self.welc_fon_container.show()

        self.welc_container = QWidget(self)
        self.welc_container.setGeometry(165, 60, 300, 200)
        self.welc_container.setStyleSheet("""
            background-color: rgba(20,20,20, 0.8);
            border-radius: 20px;
            border: 1px solid rgba(100,100,100,0.8);
        """)
        self.welc_container.hide()

        pc_name = os.getlogin()

        self.welc_name = QLabel(f"Welcome, {pc_name}!", self.welc_container)
        self.welc_name.setStyleSheet("""
            font-size: 20px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(0, 0, 0, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.welc_name.setGeometry(0, 10, 300, 60)
        self.welc_name.setAlignment(Qt.AlignHCenter)
        self.welc_name.setWordWrap(True)

        self.welc_sub = QLabel(f"Join our social media to stay updated.", self.welc_container)
        self.welc_sub.setStyleSheet("""
            font-size: 16px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(0, 0, 0, 0);
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.welc_sub.setGeometry(0, 30, 300, 60)
        self.welc_sub.setAlignment(Qt.AlignHCenter)
        self.welc_sub.setWordWrap(True)

        self.welc_TH = QLabel(f"Thanks for using", self.welc_container)
        self.welc_TH.setStyleSheet("""
            font-size: 15px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(0, 0, 0, 0);
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.welc_TH.setGeometry(0, 170, 300, 60)
        self.welc_TH.setAlignment(Qt.AlignHCenter)
        self.welc_TH.setWordWrap(True)

        self.ico_des = QToolButton(self.welc_container)
        self.ico_des.setText("Discord")
        self.ico_des.setGeometry(46, 75, 90, 90)
        self.ico_des.setIcon(self.white_icon_des)
        self.ico_des.setIconSize(QSize(60, 50))
        self.ico_des.setStyleSheet("""
            QToolButton {
                background: qlineargradient(
                            x1:0 y1:0, x2:0 y2:1,
                            stop:0 rgba(40, 40, 40, 0.05),
                            stop:1 rgba(40, 40, 40, 0.1)
                        );
                border-radius: 8px;
                border: 1px solid #454545;
                color: #dddddd;
                font-family: "Arial";
                font-size: 13px;
                padding-top: 10px;
                font-weight: 500;
                padding-bottom: 5px;
            }
            QToolButton:hover {
                background: qlineargradient(
                            x1:0 y1:0, x2:0 y2:1,
                            stop:0 rgba(60, 60, 60, 0.1),
                            stop:1 rgba(60, 60, 60, 0.15)
                        );
                border: 1px solid #666666;
            }
            QToolButton:pressed {
                background: rgba(30, 30, 30, 0.1);
            }
        """)
        self.ico_des.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.ico_des.clicked.connect(lambda: webbrowser.open("https://discord.com/invite/34eM8xvxGS"))

        self.ico_yt = QToolButton(self.welc_container)
        self.ico_yt.setText("Youtube")
        self.ico_yt.setGeometry(164, 75, 90, 90)
        self.ico_yt.setIcon(self.white_icon_yt)
        self.ico_yt.setIconSize(QSize(60, 50))
        self.ico_yt.setStyleSheet("""
            QToolButton {
                background: qlineargradient(
                            x1:0 y1:0, x2:0 y2:1,
                            stop:0 rgba(40, 40, 40, 0.05),
                            stop:1 rgba(40, 40, 40, 0.1)
                        );
                border-radius: 8px;
                border: 1px solid #454545;
                color: #dddddd;
                font-family: "Arial";
                font-size: 13px;
                padding-top: 10px;
                font-weight: 500;
                padding-bottom: 5px;
            }
            QToolButton:hover {
                background: qlineargradient(
                            x1:0 y1:0, x2:0 y2:1,
                            stop:0 rgba(60, 60, 60, 0.1),
                            stop:1 rgba(60, 60, 60, 0.15)
                        );
                border: 1px solid #666666;
            }
            QToolButton:pressed {
                background: rgba(30, 30, 30, 0.1);
            }
        """)
        self.ico_yt.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.ico_yt.clicked.connect(lambda: webbrowser.open("https://www.youtube.com/@w1rlyy?sub_confirmation=1"))

        self.close_welc = QPushButton("✕", self.welc_container)
        self.close_welc.setStyleSheet("""
        QPushButton {
            background-color: rgba(40, 40, 40, 0);
            color: rgba(200,200,200,1);
            padding: 0px;
            border:none;
            border-radius: 13px;
        }
        QPushButton:hover {
            background-color: rgba(40, 40, 40, 0);
            border:none;
        }
        QPushButton:pressed {
            background-color: rgba(40, 40, 40, 0);
            border:none;
        }
        """)
        self.close_welc.setGeometry(265, 5, 30, 30)
        self.close_welc.clicked.connect(self.welc_anim_x)

        self.container1 = QWidget(self)
        self.container1.setGeometry(10, 10, 615, 300)
        self.container1.setStyleSheet("""
            background:
                #050505
                qradialgradient(cx:0.18, cy:0.22, radius:1.1, fx:0.25, fy:0.15,
                    stop:0 #050505, stop:0.35 #1e1e1e, stop:0.55 #111111, stop:0.75 #0a0a0a),
                qradialgradient(cx:0.78, cy:0.82, radius:0.95, fx:0.85, fy:0.90,
                    stop:0 #050505, stop:0.3 #222222, stop:0.5 #151515, stop:0.7 #0c0c0c),
                qradialgradient(cx:0.55, cy:0.48, radius:0.65, fx:0.60, fy:0.52,
                    stop:0 #050505, stop:0.4 #282828, stop:0.6 #1a1a1a),
                qradialgradient(cx:0.88, cy:0.12, radius:0.7, fx:0.92, fy:0.08,
                    stop:0 #050505, stop:0.45 #202020, stop:0.65 #121212);
            border-radius: 28px;
            border: 2px solid rgba(60,60,60,0.6);
        """)

        self.stars_layer1 = StarField(self.container1)
        self.stars_layer1.setGeometry(0, 0, 615, 300)

        self.containero1 = QGraphicsOpacityEffect(self.container1)
        self.containero1.setOpacity(1.0)
        self.container1.setGraphicsEffect(self.containero1)
        self.container1.hide()

        self.top_bar = QFrame(self.container)
        self.top_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.2);
            border-radius: 20px;
            border: 1px solid rgba(60,60,60,0.8);
        """)
        self.top_bar.setGeometry(5, 5, 605, 40)

        self.st_bar = QFrame(self.container)
        self.st_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.1);
            border-radius: 15px;
            border: 1px solid rgba(60,60,60,0.7);
        """)
        self.st_bar.setGeometry(155, 245, 305, 40)

        self.st_baro = QGraphicsOpacityEffect(self.st_bar)
        self.st_baro.setOpacity(1)
        self.st_bar.setGraphicsEffect(self.st_baro)
        self.st_bar.hide()

        self.close_program = QPushButton("✕", self.top_bar)
        self.close_program.setStyleSheet("""
        QPushButton {
            background-color: rgba(140, 140, 140, 0.1);
            color: rgba(200,200,200,1);
            padding: 0px;
            border-radius: 13px;
        }
        QPushButton:hover {
            background-color: rgba(40, 40, 40, 0.9);
            border: 1px solid rgba(120, 120, 120, 0.6);
        }
        QPushButton:pressed {
            background-color: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(80, 80, 80, 0.7);
        }
        """)
        self.close_program.setGeometry(570, 5, 30, 30)
        self.close_program.clicked.connect(self.end_animations_close)

        self.minimize_button = QPushButton("🗕", self.top_bar)
        self.minimize_button.setStyleSheet("""
        QPushButton {
            background-color: rgba(140, 140, 140, 0.1);
            color: rgba(200,200,200,1);
            padding: 0px;
            border-radius: 13px;
        }
        QPushButton:hover {
            background-color: rgba(40, 40, 40, 0.9);
            border: 1px solid rgba(120, 120, 120, 0.6);
        }
        QPushButton:pressed {
            background-color: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(80, 80, 80, 0.7);
        }
        """)
        self.minimize_button.setGeometry(535, 5, 30, 30)
        self.minimize_button.clicked.connect(self.showMinimized)

        self.nameLabel = QLabel("ExH for Fortnite Textures", self.top_bar)
        self.nameLabel.setStyleSheet("""
            font-size: 20px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(80,80,80, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(60,60,60,0.3);
            padding: 2px 6px;
            font-weight: bold;
        """)
        self.nameLabel.setGeometry(165, 5, 280, 30)
        self.nameLabel.setAlignment(Qt.AlignHCenter)


        self.soap_bar = QFrame(self.container)
        self.soap_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(60,60,60,0.8);
        """)
        self.soap_bar.setGeometry(320, 55, 280, 180)

        self.soap_bar_hide = QFrame(self.container)
        self.soap_bar_hide.setStyleSheet("""
            background-color: rgba(0,0,0, 0.8);
            border-radius: 20px;
        """)
        self.soap_bar_hide.setGeometry(320, 65, 280, 180)

        self.soap_name_hide = QLabel("For Nvidia Graphics Cards Only", self.soap_bar_hide)
        self.soap_name_hide.setStyleSheet("""
            font-size: 20px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(0, 0, 0, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.soap_name_hide.setGeometry(0, 60, 280, 60)
        self.soap_name_hide.setAlignment(Qt.AlignHCenter)
        self.soap_name_hide.setWordWrap(True)

        self.soap_name = QLabel("Soap Textures", self.soap_bar)
        self.soap_name.setStyleSheet("""
            font-size: 23px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(140, 140, 140, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.soap_name.setGeometry(0, 15, 280, 30)
        self.soap_name.setAlignment(Qt.AlignHCenter)

        self.soap_apply = QPushButton("Apply", self.soap_bar)
        self.soap_apply.setStyleSheet("""
        QPushButton {
            background-color: rgba(30, 30, 30, 0.8);
            color: rgba(200,200,200,1);
            padding: 8px 16px;
            border-radius: 15px;
            font-size: 18px;
            font-family: 'Georgia';
            font-weight: 550;
            border: 1px solid rgba(100, 100, 100, 0.5);
        }
        QPushButton:hover {
            background-color: rgba(40, 40, 40, 0.9);
            border: 1px solid rgba(120, 120, 120, 0.6);
        }
        QPushButton:pressed {
            background-color: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(80, 80, 80, 0.7);
        }
        """)
        self.soap_apply.setGeometry(60, 120, 160, 40)
        self.soap_apply.clicked.connect(self.apply_soap_textures)

        self.strength_soap = QLabel(self.soap_bar)
        self.strength_soap.setText('Strength: 3')
        self.strength_soap.setAlignment(Qt.AlignCenter)
        self.strength_soap.setStyleSheet('color: rgba(200,200,200,1); background-color: none; font-size: 16px; font-weight: bold; border: none;')
        self.strength_soap.setGeometry(0, 60, 280, 30)

        self.slider_soap = QSlider(Qt.Horizontal, self.soap_bar)
        self.slider_soap.setRange(0, 24)
        self.slider_soap.setValue(3)
        self.slider_soap.setTickPosition(QSlider.TicksBelow)
        self.slider_soap.setTickInterval(1)
        self.slider_soap.setGeometry(40, 80, 200, 40)

        self.slider_soap.setStyleSheet('''
            QSlider {
                border: none;
                background-color: none;
            }
            QSlider::groove:horizontal {
                background: rgba(140, 140, 140, 0.5);
                height: 8px;
                border-radius: 4px;
            }

            QSlider::sub-page:horizontal {
                background: rgba(90, 90, 90, 0.2);
                height: 8px;
                border-radius: 4px;
            }

            QSlider::add-page:horizontal {
                background: rgba(140, 140, 140, 0.5);
                height: 8px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #222222;
                width: 15px;
                height: 4px;
                margin: -4px 0;
                border-radius: 7px;
            }

            QSlider::handle:horizontal:hover {
                background: #333333;
            }
        ''')
        self.slider_soap.valueChanged.connect(self.update_label)
        self.has_nvidia = self.check_nvidia()
        if self.has_nvidia:
            self.soap_bar_hide.hide()


        self.strip_bar = QFrame(self.container)
        self.strip_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(60,60,60,0.8);
        """)
        self.strip_bar.setGeometry(15, 55, 280, 180)

        self.strip_name = QLabel("Strip", self.strip_bar)
        self.strip_name.setStyleSheet("""
            font-size: 23px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(140, 140, 140, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.strip_name.setGeometry(105, 15, 70, 30)
        self.strip_name.setAlignment(Qt.AlignHCenter)

        self.strip_info = QLabel("""To get everything back, simply verify files in the Epic Games Launcher (three dots in Fortnite > Controls > Verify Files).
IMPORTANT: After updating Fortnite, all files are restored, meaning you'll need to re-strip.""", self.strip_bar)
        self.strip_info.setStyleSheet("""
            font-size: 9px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(140, 140, 140, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.strip_info.setGeometry(10, 110, 260, 65)
        self.strip_info.setAlignment(Qt.AlignHCenter)
        self.strip_info.setWordWrap(True)


        self.strip_apply = QPushButton("Apply", self.strip_bar)
        self.strip_apply.setStyleSheet("""
        QPushButton {
            background-color: rgba(30, 30, 30, 0.8);
            color: rgba(200,200,200,1);
            padding: 8px 16px;
            border-radius: 15px;
            font-size: 18px;
            font-family: 'Georgia';
            font-weight: 550;
            border: 1px solid rgba(100, 100, 100, 0.5);
        }
        QPushButton:hover {
            background-color: rgba(40, 40, 40, 0.9);
            border: 1px solid rgba(120, 120, 120, 0.6);
        }
        QPushButton:pressed {
            background-color: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(80, 80, 80, 0.7);
        }
        """)
        self.strip_apply.setGeometry(25, 60, 110, 40)
        self.strip_apply.clicked.connect(self.apply_strip)

        self.strip_settings = QPushButton("Settings", self.strip_bar)
        self.strip_settings.setStyleSheet("""
        QPushButton {
            background-color: rgba(30, 30, 30, 0.8);
            color: rgba(200,200,200,1);
            padding: 0px 0px;
            border-radius: 15px;
            font-size: 18px;
            font-family: 'Georgia';
            font-weight: 550;
            border: 1px solid rgba(100, 100, 100, 0.5);
        }
        QPushButton:hover {
            background-color: rgba(40, 40, 40, 0.9);
            border: 1px solid rgba(120, 120, 120, 0.6);
        }
        QPushButton:pressed {
            background-color: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(80, 80, 80, 0.7);
        }
        """)
        self.strip_settings.setGeometry(145, 60, 110, 40)
        self.strip_settings.clicked.connect(self.settings_animations)

        self.strip_back = QPushButton("Back", self.container1)
        self.strip_back.setStyleSheet("""
        QPushButton {
            background-color: rgba(30, 30, 30, 0.8);
            color: rgba(200,200,200,1);
            padding: 0px 0px;
            border-radius: 15px;
            font-size: 18px;
            font-family: 'Georgia';
            font-weight: 550;
            border: 1px solid rgba(100, 100, 100, 0.5);
        }
        QPushButton:hover {
            background-color: rgba(40, 40, 40, 0.9);
            border: 1px solid rgba(120, 120, 120, 0.6);
        }
        QPushButton:pressed {
            background-color: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(80, 80, 80, 0.7);
        }
        """)
        self.strip_back.setGeometry(155, 245, 305, 35)
        self.strip_back.clicked.connect(self.back_settings_animations)

        self.locals_bar = QFrame(self.container1)
        self.locals_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(60,60,60,0.8);
        """)
        self.locals_bar.setGeometry(15, 55, 280, 180)

        self.locals_name = QLabel("Delete Localization", self.locals_bar)
        self.locals_name.setStyleSheet("""
            font-size: 23px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(140, 140, 140, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.locals_name.setGeometry(0, 15, 280, 30)
        self.locals_name.setAlignment(Qt.AlignHCenter)

        loc_btn_style = "QPushButton {background-color: rgba(30,30,30,0.8); color: rgba(200,200,200,1); border-radius: 10px; font-size: 13px; font-family: Georgia; font-weight: 550; border: 1px solid rgba(100,100,100,0.5);} QPushButton:hover {background-color: rgba(40,40,40,0.9); border: 1px solid rgba(120,120,120,0.6);} QPushButton:pressed {background-color: rgba(20,20,20,0.9); border: 1px solid rgba(80,80,80,0.7);}"

        scroll_area = QScrollArea(self.locals_bar)
        scroll_area.setGeometry(10, 50, 260, 120)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.verticalScrollBar().setSingleStep(5)
        scroll_area.setStyleSheet(
            "QScrollArea {background-color: rgba(80,80,80,0.01); border-radius: 20px; border: 1px solid rgba(60,60,60,0.8);}")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        layout = QGridLayout(scroll_content)
        layout.setSpacing(5)

        for i, lang in enumerate(self.localizations.keys()):
            btn = QPushButton(lang.capitalize(), scroll_content)
            btn.setStyleSheet(loc_btn_style)
            btn.setFixedSize(55, 35)
            btn.clicked.connect(lambda checked, l=lang: self.toggle_localization(l))
            self.localizations[lang] = btn
            layout.addWidget(btn, i // 4, i % 4)
        scroll_area.setWidget(scroll_content)

        path = QPainterPath()
        path.addRoundedRect(1, 1, scroll_area.width() - 2, scroll_area.height() - 2, 20, 20)
        scroll_area.viewport().setMask(QRegion(path.toFillPolygon().toPolygon()))

        self.paks_bar = QFrame(self.container1)
        self.paks_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(60,60,60,0.8);
        """)
        self.paks_bar.setGeometry(305, 55, 295, 50)

        self.paks_name = QLabel("Delete .pak Files", self.paks_bar)
        self.paks_name.setStyleSheet("""
            font-size: 17px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(140, 140, 140, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.paks_name.setGeometry(5, 10, 200, 30)

        self.paks_toggle = ModernToggle(self.paks_bar, reverse=True)
        self.paks_toggle.setGeometry(235, 13, 45, 25)
        self.paks_toggle.on_toggled(
            on_func=lambda: self.update_on_off(True, 'paks'),
            off_func=lambda: self.update_on_off(False, 'paks')
        )

        self.soap_skins_bar = QFrame(self.container1)
        self.soap_skins_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(60,60,60,0.8);
        """)
        self.soap_skins_bar.setGeometry(305, 120, 295, 50)

        self.soap_skins_name = QLabel("Soap Skins", self.soap_skins_bar)
        self.soap_skins_name.setStyleSheet("""
            font-size: 17px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(140, 140, 140, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.soap_skins_name.setGeometry(5, 10, 200, 30)

        self.soap_skins_toggle = ModernToggle(self.soap_skins_bar, reverse=True)
        self.soap_skins_toggle.setGeometry(235, 13, 45, 25)
        self.soap_skins_toggle.on_toggled(
            on_func=lambda: self.update_on_off(True, 'soap_skins'),
            off_func=lambda: self.update_on_off(False, 'soap_skins')
        )

        self.trash_bar = QFrame(self.container1)
        self.trash_bar.setStyleSheet("""
            background-color: rgba(80,80,80, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(60,60,60,0.8);
        """)
        self.trash_bar.setGeometry(305, 185, 295, 50)

        self.trash_name = QLabel("Delete Trash Files", self.trash_bar)
        self.trash_name.setStyleSheet("""
            font-size: 17px;
            color: rgba(200,200,200,1);
            font-family: 'Georgia ';
            background-color: rgba(140, 140, 140, 0);
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            border: none;
        """)
        self.trash_name.setGeometry(5, 10, 200, 30)

        self.trash_toggle = ModernToggle(self.trash_bar, reverse=True)
        self.trash_toggle.setGeometry(235, 13, 45, 25)
        self.trash_toggle.on_toggled(
            on_func=lambda: self.update_on_off(True, 'trash'),
            off_func=lambda: self.update_on_off(False, 'trash')
        )
        self.start_program_anim()

    def qt_message_handler(msg_type, context, message):
        if "QPainter::begin" in message or "QPainter::translate" in message:
            return

    qInstallMessageHandler(qt_message_handler)

    def toggle_localization(self, name):
        btn = self.localizations[name]
        if "🗑" in btn.text():
            btn.setText(name.capitalize())
        else:
            btn.setText(f"{name.capitalize()} 🗑")




    def update_on_off(self, will_be_enabled, name):
        if name == 'paks':
            if will_be_enabled:
                self.paks_del = True
            else:
                self.paks_del = False

        if name == 'soap_skins':
            if will_be_enabled:
                self.soap_skins = True
            else:
                self.soap_skins = False

        if name == 'trash':
            if will_be_enabled:
                self.trash = True
            else:
                self.trash = False


    def get_colored_icon(self, base64_data, color_hex):
        try:
            image_data = base64.b64decode(base64_data)
            source_pixmap = QPixmap()
            source_pixmap.loadFromData(image_data)
            if source_pixmap.isNull():
                return QIcon()
            mask = source_pixmap.createMaskFromColor(QColor(0, 0, 0), Qt.MaskOutColor)
            colored_pixmap = QPixmap(source_pixmap.size())
            colored_pixmap.fill(QColor(color_hex))
            colored_pixmap.setMask(mask)
            return QIcon(colored_pixmap)

        except Exception as e:
            pass
            return QIcon()

    def apply_soap_textures(self):
        self.soap_apply.setEnabled(False)
        temp_dir = os.environ.get('TEMP')
        exe_path = os.path.join(temp_dir, "apply.exe")
        nip_path = os.path.join(temp_dir, "saop.nip")
        url = "https://www.dropbox.com/scl/fi/rz0vknbi84uw5yxk0kgx8/nvidiaProfileInspector.exe?rlkey=e0pgsiqwis6zofuv3uqgtyyem&st=iq9hlaff&dl=0"

        for p in [exe_path, nip_path]:
            if os.path.exists(p): os.remove(p)

        self.dl_thread = DownloadThread(url, exe_path)
        self.dl_thread.finished.connect(lambda p: self._on_dl_done(p, nip_path, temp_dir) if p else None)
        self.dl_thread.start()

    def _on_dl_done(self, exe_path, nip_path, temp_dir):
        val = self.slider_soap.value()
        lod_val = str(val) if val > 0 else "0"
        aa_val = "8" if val > 0 else "0"
        unk_val = "30" if val > 0 else "0"

        xml = f"""<?xml version="1.0" encoding="utf-16"?>
<ArrayOfProfile>
  <Profile>
    <ProfileName>Fortnite</ProfileName>
    <Executeables>
      <string>fortnitelauncher.exe</string>
      <string>fortniteclient-win64-shipping_be.exe</string>
      <string>fortniteclient-win64-shipping_eac_eos.exe</string>
      <string>fortniteclient.exe</string>
      <string>fortniteclient-win64-shipping.exe</string>
      <string>fortniteclient-win64-test.exe</string>
      <string>fortniteclient-win64-shipping_eac.exe</string>
    </Executeables>
    <Settings>
      <ProfileSetting>
        <SettingNameInfo>Texture filtering - LOD Bias</SettingNameInfo>
        <SettingID>7573135</SettingID>
        <SettingValue>{lod_val}</SettingValue>
        <ValueType>Dword</ValueType>
      </ProfileSetting>
      <ProfileSetting>
        <SettingNameInfo>Antialiasing - Transparency Supersampling</SettingNameInfo>
        <SettingID>282364549</SettingID>
        <SettingValue>{aa_val}</SettingValue>
        <ValueType>Dword</ValueType>
      </ProfileSetting>
      <ProfileSetting>
        <SettingNameInfo />
        <SettingID>541081465</SettingID>
        <SettingValue>{unk_val}</SettingValue>
        <ValueType>Dword</ValueType>
      </ProfileSetting>
    </Settings>
  </Profile>
</ArrayOfProfile>"""

        self.apply_thread = ApplyThread(nip_path, exe_path, temp_dir, xml)
        self.apply_thread.finished.connect(lambda: self.soap_apply.setEnabled(True))
        self.apply_thread.start()

    def update_label(self, value):
        self.strength_soap.setText(f'Strength: {value}')

    def check_nvidia(self):
        if platform.system() == "Windows":
            try:
                import wmi
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    if "NVIDIA" in gpu.Name:
                        return True
            except:
                pass
        try:
            subprocess.check_output(["nvidia-smi"])
            return True
        except:
            pass

        return False
    def welc_anim_x(self):
        self.animation_welc_fon_container = QPropertyAnimation(self.welc_fon_containero, b"opacity")
        self.animation_welc_fon_container.stop()
        self.animation_welc_fon_container.setDuration(400)
        self.animation_welc_fon_container.setStartValue(0.4)
        self.animation_welc_fon_container.setEndValue(0)
        self.animation_welc_fon_container.setEasingCurve(QEasingCurve.InOutQuad)
        self.welc_fon_container.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.animation_welc_fon_container.finished.connect(lambda: self.welc_fon_container.setVisible(False))
        self.animation_welc_fon_container.start()


        self.animation_welc_container = QPropertyAnimation(self.welc_container, b"geometry")
        self.animation_welc_container.stop()
        self.animation_welc_container.setDuration(300)
        self.animation_welc_container.setStartValue(QRect(165, 60, 300, 200))
        self.animation_welc_container.setEndValue(QRect(165, 400, 300, 200))
        self.welc_container.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.animation_welc_container.finished.connect(
            lambda: (self.welc_container.setVisible(False), self.st_anim()))
        self.animation_welc_container.start()


    def st_anim(self):
        self.ico_des.setParent(self.st_bar)
        self.ico_des.setText("")
        self.ico_des.setGeometry(28, -1, 40, 40)
        self.ico_des.setIconSize(QSize(40, 40))
        self.ico_des.setStyleSheet("""
            QToolButton {
                background-color: rgba(80,80,80, 0);
                border: none;
            }
        """)
        self.ico_des.show()
        self.ico_yt.setParent(self.st_bar)
        self.ico_yt.setText("")
        self.ico_yt.setGeometry(88, -1, 40, 40)
        self.ico_yt.setIconSize(QSize(50, 50))
        self.ico_yt.setStyleSheet("""
            QToolButton {
                background-color: rgba(80,80,80, 0);
                border: none;
            }
        """)
        self.ico_yt.show()
        self.st_bar.setParent(self)
        self.st_bar.setGeometry(240, 255, 155, 40)
        self.animation_st_bar = QPropertyAnimation(self.st_baro, b"opacity")
        self.animation_st_bar.stop()
        self.animation_st_bar.setDuration(800)
        self.animation_st_bar.setStartValue(0)
        self.animation_st_bar.setEndValue(1)
        self.animation_st_bar.setEasingCurve(QEasingCurve.InOutQuad)
        self.st_bar.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.st_bar.show()
        self.animation_st_bar.finished.connect(
            lambda: (self.st_bar.setParent(self.container),self.st_bar.setGeometry(230, 245, 155, 40),self.st_bar.show()))
        self.animation_st_bar.start()

    def welc_anim(self):
        self.animation_welc_fon_container = QPropertyAnimation(self.welc_fon_containero, b"opacity")
        self.animation_welc_fon_container.stop()
        self.animation_welc_fon_container.setDuration(400)
        self.animation_welc_fon_container.setStartValue(0)
        self.animation_welc_fon_container.setEndValue(0.4)
        self.animation_welc_fon_container.setEasingCurve(QEasingCurve.InOutQuad)
        self.welc_fon_container.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.welc_fon_container.setVisible(True)
        self.animation_welc_fon_container.start()

        self.animation_welc_container = QPropertyAnimation(self.welc_container, b"geometry")
        self.animation_welc_container.stop()
        self.animation_welc_container.setStartValue(QRect(165, 500, 300, 200))
        self.animation_welc_container.setEndValue(QRect(165, 60, 300, 200))
        self.welc_container.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.welc_container.setVisible(True)
        self.animation_welc_container.start()

    def start_program_anim(self):
        self.animation_container = QPropertyAnimation(self.containero, b"opacity")
        self.animation_container.stop()
        self.animation_container.setDuration(800)
        self.animation_container.setStartValue(0)
        self.animation_container.setEndValue(1)
        self.animation_container.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_container.finished.connect(self.welc_anim)
        self.container.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.container.setVisible(True)
        self.animation_container.start()


    def end_animations_close(self):

        self.container.raise_()
        self.top_bar.setParent(self.container)
        self.top_bar.raise_()
        self.top_bar.show()
        self.top_bar.setGeometry(5, 5, 605, 40)
        self.nameLabel.setText('ExH for Fortnite Textures')
        self.nameLabel.setGeometry(165, 5, 280, 30)
        self.container1.hide()

        self.animation_container = QPropertyAnimation(self.containero, b"opacity")
        self.animation_container.stop()
        self.animation_container.setDuration(800)
        self.animation_container.setStartValue(self.windowOpacity())
        self.animation_container.setEndValue(0)
        self.animation_container.setEasingCurve(QEasingCurve.InOutQuad)
        self.container.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.container.setVisible(True)
        self.animation_container.finished.connect(self.perform_close)
        self.animation_container.start()

    def settings_animations(self):
        self.nameLabel.setText('Settings')
        self.top_bar.setParent(self)
        self.top_bar.setGeometry(15, 15, 605, 40)
        self.nameLabel.setGeometry(225, 5, 180, 30)
        self.container1.raise_()
        self.top_bar.raise_()
        self.top_bar.show()

        self.animation_container1 = QPropertyAnimation(self.containero1, b"opacity")
        self.animation_container1.stop()
        self.animation_container1.setDuration(800)
        self.animation_container1.setStartValue(0)
        self.animation_container1.setEndValue(1)
        self.animation_container1.setEasingCurve(QEasingCurve.InOutQuad)
        self.container1.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.container1.setVisible(True)
        self.animation_container1.start()

    def back_settings_animations(self):
        self.container.raise_()
        self.top_bar.setGeometry(15, 15, 605, 40)
        self.nameLabel.setGeometry(175, 5, 280, 30)
        self.top_bar.raise_()
        self.top_bar.show()

        self.nameLabel.setText('ExH for Fortnite Textures')
        self.animation_container = QPropertyAnimation(self.containero, b"opacity")
        self.animation_container.stop()
        self.animation_container.setDuration(800)
        self.animation_container.setStartValue(0)
        self.animation_container.setEndValue(1)
        self.animation_container.setEasingCurve(QEasingCurve.InOutQuad)
        self.container.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.container.setVisible(True)
        self.animation_container.start()

    def apply_strip(self):
        paths = ExHbyWirlyyS.get_paths()
        processes = ExHbyWirlyyS.get_processes()
        local_path = ExHbyWirlyyS.find_game_path()
        appdata_path = os.environ.get('LOCALAPPDATA')

        for proc in processes:
            if proc:
                try:
                    os.system(f'taskkill /f /im "{proc}" 2>nul')
                except Exception as e:
                    pass

        if self.soap_skins:
            file_path = os.path.join(local_path, paths["soap_skin_file"])
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    pass
        if self.paks_del:
            paks_dir = os.path.join(local_path, "FortniteGame", "Content", "Paks")
            if os.path.exists(paks_dir):
                for f in os.listdir(paks_dir):
                    if paths["paks_filter"] in f.lower():
                        try:
                            os.remove(os.path.join(paks_dir, f))
                        except Exception as e:
                            pass
        for folder in paths["local_folders"]:
            folder_path = os.path.join(local_path, folder)
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    pass
        for file in paths["local_files"]:
            file_path = os.path.join(local_path, file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    pass
        for folder in paths["appdata_folders"]:
            folder_path = os.path.join(appdata_path, folder)
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    pass
        wc_folders = glob.glob(os.path.join(appdata_path, "EpicGamesLauncher", "Saved", "webcache_*"))
        if wc_folders:
            try:
                shutil.rmtree(wc_folders[0])
            except Exception as e:
                pass
        loc_path = os.path.join(local_path, paths["localization_path"])
        if os.path.exists(loc_path):
            for lang, btn in self.localizations.items():
                if hasattr(btn, 'text') and "🗑" in btn.text():
                    for filename in os.listdir(loc_path):
                        if filename.lower().startswith(lang):
                            try:
                                os.remove(os.path.join(loc_path, filename))
                            except Exception as e:
                                pass

    def perform_close(self):
        if self.container:
            self.container.hide()
            self.container.setParent(None)
            self.container.deleteLater()
            sys.exit()
        self.hide()
        self.setAttribute(Qt.WA_DeleteOnClose)
        if hasattr(self, "_pending_close_event") and self._pending_close_event:
            self._pending_close_event.accept()
            self._pending_close_event = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.top_bar.geometry().contains(event.pos()):
            self.old_position = event.globalPos() - self.frameGeometry().topLeft()
            self.dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.old_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    icon_path = resource_path("icon.ico")
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec_())
