import math
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (QColor, QFont, QPainter, QPen,
                           QLinearGradient, QPixmap, QPolygonF,
                           QFontDatabase, QPainterPath)
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton

ASSETS = Path(__file__).parent / "assets"
HERE = Path(__file__).parent

STEPS = ["waiting for game...", "loading anticheat...",
         "checking integrity...", "authenticating snake...",
         "launching gothinc"]

W, H = 640, 400
STRIP = 56
PX = 5

class Splash(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy Anti-Snake")
        self.setFixedSize(W, H)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.mode = "loading"
        self.step = 0
        self.phase = 0.0
        self._drag = None

        self.art = QPixmap(str(ASSETS / "goth.png"))
        fid = QFontDatabase.addApplicationFont(str(ASSETS / "luckiest.ttf"))
        self.title_font = (QFontDatabase.applicationFontFamilies(fid)[0]
                           if fid >= 0 else "Verdana")

        self.msg = QLabel(STEPS[0], self)
        self.msg.setGeometry(20, H - STRIP + 21, 300, 18)
        self.msg.setStyleSheet("color:#b89aa3; font-family:Segoe UI;"
                               " font-size:9px;background:transparent;")

        self.x = QPushButton("×", self)
        self.x.setGeometry(W - 32, 10, 22, 22)
        self.x.setStyleSheet(
            "QPushButton{color:rgba(255,255,255,130);background:rgba(0,0,0,60);"
            "border-radius:11px;font-family:Segoe UI;font-size:12px;"
            "padding-bottom:2px}"
            "QPushButton:hover{color:#fff;background:#c0392b}")
        self.x.clicked.connect(self.close)

        self.t = QTimer(self)
        self.t.setInterval(30)
        self.t.timeout.connect(self._tick)
        self.t.start()

        self.stepper = QTimer(self)
        self.stepper.setInterval(1300)
        self.stepper.timeout.connect(self._next)
        self.stepper.start()

    def _next(self):
        self.step += 1
        if self.step >= len(STEPS):
            self.stepper.stop()
            subprocess.Popen([sys.executable, str(HERE / "login.py")],
                             cwd=str(HERE))
            self.close()
            return
        self.msg.setText(STEPS[self.step])

    def _tick(self):
        self.phase += 0.055
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, W, H), 12, 12)
        p.setClipPath(clip)

        g = QLinearGradient(0, 0, W, H)
        g.setColorAt(0, QColor("#101014"))
        g.setColorAt(0.55, QColor("#0a0a0d"))
        g.setColorAt(1, QColor("#050507"))
        p.fillRect(0, 0, W, H, g)

        p.setPen(QPen(QColor(160, 160, 190, 9), 1))
        p.setBrush(Qt.NoBrush)
        r = 14
        for row in range(-1, int(H / (r * 1.5)) + 2):
            for col in range(-1, int(W / (r * 1.73)) + 2):
                cx = col * r * 1.732 + (r * 0.866 if row % 2 else 0)
                cy = row * r * 1.5
                pts = QPolygonF([QPointF(cx + r * math.cos(a),
                                         cy + r * math.sin(a))
                                 for a in [math.radians(30 + k * 60)
                                           for k in range(6)]])
                p.drawPolygon(pts)

        g2 = QLinearGradient(W - 320, 0, W - 60, 0)
        g2.setColorAt(0, QColor(190, 90, 130, 0))
        g2.setColorAt(1, QColor(190, 90, 130, 30))
        p.fillRect(W - 320, 0, 320, H, g2)

        ah = 430
        aw = int(self.art.width() * ah / self.art.height())
        p.drawPixmap(W - aw + 30, -20, aw, ah, self.art)

        g3 = QLinearGradient(0, H - 190, 320, H)
        g3.setColorAt(0, QColor(4, 4, 6, 160))
        g3.setColorAt(1, QColor(4, 4, 6, 0))
        p.fillRect(0, H - 190, 320, 190, g3)

        f = QFont(self.title_font)
        f.setPixelSize(44)
        p.setFont(f)
        p.setPen(QColor("#f0f0f4"))
        p.drawText(34, H - 176, "GOTHINC")
        p.setPen(QColor("#d98ba0"))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(40, H - 154, "made by pymensol")
        p.setPen(QColor("#6b4a55"))
        p.setFont(QFont("Segoe UI", 7))
        p.drawText(40, H - STRIP - 14,
                   "open source - free to use - credit partially needed")

        if self.mode == "loading":
            p.fillRect(0, H - STRIP, W, STRIP, QColor("#0b0b0e"))
            p.setPen(QPen(QColor("#1d1d24"), 1))
            p.drawLine(0, H - STRIP, W, H - STRIP)

            cx, cy, r = W - 46, H - STRIP + 28, 11
            p.setPen(QPen(QColor("#2a2a33"), 2.5, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(cx - r, cy - r, r * 2, r * 2, 0, 360 * 16)
            p.setPen(QPen(QColor("#e8e8ef"), 2.5, Qt.SolidLine, Qt.RoundCap))
            a = int((self.phase * 260) % 360)
            p.drawArc(cx - r, cy - r, r * 2, r * 2,
                      -a * 16, 100 * 16)
        p.end()

    def mousePressEvent(self, e):
        self._drag = e.globalPosition() - self.pos()

    def mouseMoveEvent(self, e):
        if self._drag is not None:
            self.move(e.globalPosition().toPoint() - self._drag.toPoint())

    def mouseReleaseEvent(self, e):
        self._drag = None

def launch():
    app = QApplication(sys.argv)
    w = Splash()
    w.show()
    if "--shot" in sys.argv:
        QTimer.singleShot(3000, lambda:
            w.grab().toImage().save("shots/splash.png"))
    app.exec()

if __name__ == "__main__":
    launch()
