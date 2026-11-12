import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QRectF, QPropertyAnimation
from PySide6.QtGui import (QColor, QFont, QPainter, QPen, QPixmap,
                           QLinearGradient, QFontDatabase, QPainterPath,
                           QIcon)
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                               QLineEdit)

ASSETS = Path(__file__).parent / "assets"
ACCOUNTS = Path(__file__).parent / "accounts.json"

W, H = 360, 440

FIELD = ("QLineEdit{background:rgba(255,255,255,14);border:1px solid #2a2a30;"
         "border-radius:8px;color:#eeeef2;padding:6px 12px 6px 34px;"
         "font-family:Segoe UI;font-size:11px}"
         "QLineEdit:focus{border:1px solid #9090a0;"
         "background:rgba(255,255,255,22)}")

def hashed(u, p):
    return hashlib.sha256(f"fortpy:{u}:{p}".encode()).hexdigest()

def load_accounts():
    if ACCOUNTS.exists():
        try:
            return json.loads(ACCOUNTS.read_text())
        except Exception:
            pass
    return {}

def icon(kind):
    pm = QPixmap(18, 18)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor("#8a8a95"), 1.6, Qt.SolidLine,
                  Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    if kind == "user":
        p.drawEllipse(5, 2, 8, 8)
        p.drawArc(2, 10, 14, 10, 20 * 16, 140 * 16)
    elif kind == "mail":
        p.drawRoundedRect(1, 4, 16, 11, 2, 2)
        p.drawLine(1, 5, 9, 10)
        p.drawLine(17, 5, 9, 10)
    elif kind == "lock":
        p.drawRoundedRect(3, 8, 12, 9, 2, 2)
        p.drawArc(5, 1, 8, 9, 0, 180 * 16)
    elif kind == "eye":
        p.drawEllipse(1, 4, 16, 10)
        p.drawEllipse(7, 7, 4, 4)
    p.end()
    return QIcon(pm)

class Auth(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("gothinc login")
        self.setFixedSize(W, H)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.mode = "register"
        self._drag = None

        fid = QFontDatabase.addApplicationFont(str(ASSETS / "luckiest.ttf"))
        self.title_font = (QFontDatabase.applicationFontFamilies(fid)[0]
                           if fid >= 0 else "Verdana")

        self.user = self._field("username", "user", 40, 168)
        self.email = self._field("email", "mail", 40, 210)
        self.pw = self._field("password", "lock", 40, 252)
        self.pw.setEchoMode(QLineEdit.Password)

        self.eye = QPushButton(self.pw)
        self.eye.setIcon(icon("eye"))
        self.eye.setGeometry(self.pw.width() - 28, 8, 20, 20)
        self.eye.setCursor(Qt.PointingHandCursor)
        self.eye.setStyleSheet("background:transparent;border:0;")
        self.eye.setCheckable(True)
        self.eye.toggled.connect(
            lambda on: self.pw.setEchoMode(
                QLineEdit.Normal if on else QLineEdit.Password))
        self.eye.show()

        self.go = QPushButton("create account", self)
        self.go.setGeometry(40, 304, W - 80, 36)
        self.go.setCursor(Qt.PointingHandCursor)
        self.go.setStyleSheet(
            "QPushButton{border:0;border-radius:8px;color:#0a0a0c;"
            "font-family:Segoe UI;font-size:11px;font-weight:700;"
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #e8e8ee, stop:1 #b8b8c4)}"
            "QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #ffffff, stop:1 #d0d0da)}"
            "QPushButton:pressed{background:#9a9aa4}")
        self.go.clicked.connect(self._go)

        self.flip = QPushButton("already have one? login", self)
        self.flip.setGeometry(40, 348, W - 80, 22)
        self.flip.setCursor(Qt.PointingHandCursor)
        self.flip.setStyleSheet(
            "QPushButton{background:transparent;color:#6a6a72;border:0;"
            "font-family:Segoe UI;font-size:9px}"
            "QPushButton:hover{color:#e8e8ee}")
        self.flip.clicked.connect(self._flip)

        self.status = QLabel("", self)
        self.status.setGeometry(40, 380, W - 80, 16)
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("color:#c9c9d0;font-family:Segoe UI;"
                                  "font-size:9px;background:transparent;")

        self.x = QPushButton("×", self)
        self.x.setGeometry(W - 34, 12, 22, 22)
        self.x.setStyleSheet(
            "QPushButton{color:rgba(255,255,255,120);background:rgba(0,0,0,60);"
            "border-radius:11px;font-family:Segoe UI;font-size:12px;"
            "padding-bottom:2px}"
            "QPushButton:hover{color:#fff;background:#c0392b}")
        self.x.clicked.connect(self.close)

        self.setWindowOpacity(0.0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(350)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)

    def _field(self, ph, ic, x, y):
        le = QLineEdit(self)
        le.setPlaceholderText(ph)
        le.setGeometry(x, y, W - 80, 36)
        le.setStyleSheet(FIELD)
        lab = QLabel(le)
        lab.setPixmap(icon(ic).pixmap(18, 18))
        lab.setGeometry(10, 9, 18, 18)
        lab.setStyleSheet("background:transparent;")
        lab.show()
        return le

    def show(self):
        super().show()
        self.anim.start()

    def _flip(self):
        self.mode = "login" if self.mode == "register" else "register"
        reg = self.mode == "register"
        self.email.setVisible(reg)
        self.pw.setGeometry(40, 252 if reg else 210, W - 80, 36)
        self.go.setGeometry(40, 304 if reg else 262, W - 80, 36)
        self.go.setText("create account" if reg else "login")
        self.flip.setGeometry(40, 348 if reg else 306, W - 80, 22)
        self.flip.setText("already have one? login" if reg
                          else "no account? register")
        self.status.setGeometry(40, 380 if reg else 336, W - 80, 16)
        self.status.setText("")
        self.update()

    def _go(self):
        if self.mode == "register":
            u, em, pw = (self.user.text().strip(),
                         self.email.text().strip(), self.pw.text())
            accts = load_accounts()
            if not u or not em or not pw:
                self.status.setText("fill all the fields first")
            elif "@" not in em or "." not in em:
                self.status.setText("that email looks fake lol")
            elif u in accts:
                self.status.setText("that names taken, try another")
            else:
                accts[u] = {"pw": hashed(u, pw), "email": em}
                ACCOUNTS.write_text(json.dumps(accts))
                self.status.setText("account made - login now")
                self._flip()
        else:
            u, pw = self.user.text().strip(), self.pw.text()
            accts = load_accounts()
            rec = accts.get(u)
            ok = (rec["pw"] == hashed(u, pw) if isinstance(rec, dict)
                  else rec == hashed(u, pw))
            if ok:
                self.status.setStyleSheet(
                    "color:#a8e063;font-family:Segoe UI;font-size:9px;"
                    "background:transparent;")
                self.status.setText(f"welcome back {u}. launching...")
                for w in (self.user, self.pw, self.go, self.flip):
                    w.setEnabled(False)
                def _open():
                    subprocess.Popen([sys.executable,
                                      str(Path(__file__).parent / "app.py"),
                                      u],
                                     cwd=str(Path(__file__).parent))
                    self.close()
                QTimer.singleShot(1200, _open)
            else:
                self.status.setText("wrong user or password")

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0.5, 0.5, W - 1, H - 1), 14, 14)
        p.setClipPath(clip)

        g = QLinearGradient(0, 0, W, H)
        g.setColorAt(0, QColor("#0e0e10"))
        g.setColorAt(1, QColor("#050506"))
        p.fillRect(0, 0, W, H, g)

        p.setPen(QPen(QColor("#26262c"), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, W - 1, H - 1), 14, 14)

        f = QFont(self.title_font)
        f.setPixelSize(24)
        p.setFont(f)
        p.setPen(QColor("#f0f0f4"))
        tw = p.fontMetrics().horizontalAdvance("FORTPY")
        p.drawText((W - tw) / 2, 66, "GOTHINC")

        t = "REGISTER" if self.mode == "register" else "LOGIN"
        f2 = QFont("Segoe UI Semibold", 12)
        p.setFont(f2)
        p.setPen(QColor("#eaeaf0"))
        tw = p.fontMetrics().horizontalAdvance(t)
        tx = (W - tw) / 2
        p.drawText(tx, 108, t)
        p.setPen(QPen(QColor("#e8e8ee"), 2))
        p.drawLine(tx, 116, tx + tw, 116)

        sub = "make an account to keep playing" if self.mode == "register" \
            else "good to see you again"
        p.setPen(QColor("#63636b"))
        p.setFont(QFont("Segoe UI", 8))
        sw = p.fontMetrics().horizontalAdvance(sub)
        p.drawText((W - sw) / 2, 138, sub)

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
    w = Auth()
    w.show()
    if "--shot" in sys.argv:
        def snap():
            w.setWindowOpacity(1.0)
            w.grab().toImage().save("shots/register.png")
            app.quit()
        QTimer.singleShot(700, snap)
    app.exec()

if __name__ == "__main__":
    launch()
