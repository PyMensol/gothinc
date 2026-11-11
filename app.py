import sys
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QTimer, QPointF, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import (QColor, QFont, QPainter, QPen, QPixmap,
                           QLinearGradient, QFontDatabase, QPainterPath,
                           QIcon)
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton,
                               QLabel, QFrame, QSlider, QComboBox,
                               QLineEdit)

ASSETS = Path(__file__).parent / "assets"

W, H = 720, 420
SB = 148

NAV = [("home", "welcome"), ("swords", "aimbot"), ("eye", "visuals"),
       ("gear", "misc"), ("user", "config")]

def icon(kind, col="#8a8a95"):
    pm = QPixmap(16, 16)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(col), 1.5, Qt.SolidLine,
                  Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    if kind == "home":
        p.drawLine(2, 8, 8, 2)
        p.drawLine(8, 2, 14, 8)
        p.drawLine(3, 8, 3, 14)
        p.drawLine(13, 8, 13, 14)
        p.drawLine(3, 14, 13, 14)
    elif kind == "swords":
        p.drawLine(3, 3, 13, 13)
        p.drawLine(13, 3, 3, 13)
        p.drawLine(3, 3, 1, 1)
        p.drawLine(13, 3, 15, 1)
        p.drawLine(3, 13, 1, 15)
        p.drawLine(13, 13, 15, 15)
    elif kind == "gear":
        p.drawEllipse(5, 5, 6, 6)
        for a in range(8):
            import math
            x = 8 + 6 * math.cos(a * 0.785)
            y = 8 + 6 * math.sin(a * 0.785)
            x2 = 8 + 7.5 * math.cos(a * 0.785)
            y2 = 8 + 7.5 * math.sin(a * 0.785)
            p.drawLine(int(x), int(y), int(x2), int(y2))
    elif kind == "eye":
        p.drawEllipse(1, 4, 14, 9)
        p.drawEllipse(6, 6, 4, 4)
    elif kind == "user":
        p.drawEllipse(5, 1, 7, 7)
        p.drawArc(2, 9, 12, 8, 20 * 16, 140 * 16)
    p.end()
    return QIcon(pm)

class Toggle(QPushButton):
    def __init__(self, parent, x, y, on=False):
        super().__init__(parent)
        self.setGeometry(x, y, 34, 18)
        self.setCheckable(True)
        self.setChecked(on)
        self.setCursor(Qt.PointingHandCursor)
        self._pos = 1.0 if on else 0.0
        self.anim = QPropertyAnimation(self, b"knob")
        self.anim.setDuration(140)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.toggled.connect(self._slide)

    def _slide(self, on):
        self.anim.stop()
        self.anim.setStartValue(self._pos)
        self.anim.setEndValue(1.0 if on else 0.0)
        self.anim.start()

    def get_knob(self):
        return self._pos

    def set_knob(self, v):
        self._pos = v
        self.update()

    knob = Property(float, get_knob, set_knob)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        on = self.isChecked()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#e8e8ee") if on else QColor("#26262c"))
        p.drawRoundedRect(QRectF(0, 0, 34, 18), 9, 9)
        kx = 2 + self._pos * 16
        p.setBrush(QColor("#0a0a0c") if on else QColor("#6a6a72"))
        p.drawEllipse(QRectF(kx, 2, 14, 14))
        p.end()

class Banner(QFrame):
    def __init__(self, parent, user, art, title_font):
        super().__init__(parent)
        self.setGeometry(0, 0, W - SB - 32, 150)
        self.user = user
        self.art = art
        self.font = title_font

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, self.width(), self.height()),
                            10, 10)
        p.setClipPath(clip)
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, QColor("#15151b"))
        g.setColorAt(1, QColor("#0a0a0d"))
        p.fillRect(0, 0, self.width(), self.height(), g)

        ah = 178
        aw = int(self.art.width() * ah / self.art.height())
        p.drawPixmap(self.width() - aw + 40, -14, aw, ah, self.art)

        g2 = QLinearGradient(self.width() - 260, 0, self.width(), 0)
        g2.setColorAt(0, QColor(10, 10, 13, 0))
        g2.setColorAt(1, QColor(10, 10, 13, 150))
        p.fillRect(self.width() - 260, 0, 260, self.height(), g2)

        p.setPen(QColor("#fff"))
        p.setFont(QFont("Segoe UI Semibold", 16))
        p.drawText(20, 52, f"welcome back, {self.user}!")
        p.setPen(QColor("#6a6a72"))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(20, 74, "session started - nothing detected yet")
        p.setPen(QPen(QColor("#26262c"), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1,
                                 self.height() - 1), 10, 10)
        p.end()


class ImgCard(QFrame):
    def __init__(self, parent, x, y, w, h, img, tag, caption, btn,
                 side=False):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.pm = QPixmap(str(img))
        self.tag = tag
        self.caption = caption
        self.side = side
        if btn:
            b = QPushButton(btn, self)
            b.setGeometry(14, h - 38, 92, 26)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(
                "QPushButton{background:#e8e8ee;color:#0a0a0c;border:0;"
                "border-radius:13px;font-family:Segoe UI;font-size:10px;"
                "font-weight:600}"
                "QPushButton:hover{background:#fff}")

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        p.setClipPath(clip)
        if self.side:
            p.fillRect(0, 0, w, h, QColor("#101014"))
            ah = h + 40
            aw = int(self.pm.width() * ah / self.pm.height())
            p.drawPixmap(w - aw + 24, -20, aw, ah, self.pm)
            g = QLinearGradient(w - 150, 0, w, 0)
            g.setColorAt(0, QColor(16, 16, 20, 0))
            g.setColorAt(1, QColor(16, 16, 20, 190))
            p.fillRect(w - 150, 0, 150, h, g)
            p.setPen(QColor("#fff"))
            p.setFont(QFont("Segoe UI Semibold", 14))
            p.drawText(14, 44, self.tag)
            p.setPen(QColor("#9a9aa2"))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(14, 62, self.caption)
        else:
            s = max(w / self.pm.width(), h / self.pm.height())
            dw, dh = self.pm.width() * s, self.pm.height() * s
            p.drawPixmap(int((w - dw) / 2), int((h - dh) / 2),
                         int(dw), int(dh), self.pm)
            g = QLinearGradient(0, h - 90, 0, h)
            g.setColorAt(0, QColor(5, 5, 6, 0))
            g.setColorAt(1, QColor(5, 5, 6, 220))
            p.fillRect(0, h - 90, w, 90, g)
            p.setPen(QColor("#fff"))
            p.setFont(QFont("Segoe UI Semibold", 12))
            p.drawText(14, 30, self.tag)
            p.setPen(QColor("#9a9aa2"))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(14, h - 46, self.caption)
        p.setPen(QPen(QColor("#1d1d22"), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 10, 10)
        p.end()

class Row(QFrame):
    def __init__(self, parent, y, title, sub, widget):
        super().__init__(parent)
        self.setGeometry(0, y, W - SB - 32, 46)
        t = QLabel(title, self)
        t.setGeometry(0, 0, 300, 20)
        t.setStyleSheet("color:#eaeaf0;font-family:Segoe UI;font-size:11px;")
        s = QLabel(sub, self)
        s.setGeometry(0, 20, 300, 16)
        s.setStyleSheet("color:#55555e;font-family:Segoe UI;font-size:9px;")
        widget.setParent(self)
        widget.move(W - SB - 32 - widget.width() - 6,
                    14 if widget.height() < 30 else 8)

def _slider(parent, lo, hi, val, unit=""):
    s = QSlider(Qt.Horizontal, parent)
    s.setRange(lo, hi)
    s.setValue(val)
    s.setFixedSize(140, 18)
    s.setStyleSheet(
        "QSlider::groove:horizontal{height:3px;background:#26262c;"
        "border-radius:1px}"
        "QSlider::sub-page:horizontal{background:#e8e8ee;"
        "border-radius:1px}"
        "QSlider::handle:horizontal{width:11px;height:11px;margin:-5px 0;"
        "border-radius:5px;background:#e8e8ee}")
    lab = QLabel(f"{val}{unit}", parent)
    lab.setFixedSize(46, 18)
    lab.setStyleSheet("color:#8a8a95;font-family:Segoe UI;font-size:10px;")
    s.valueChanged.connect(lambda v: lab.setText(f"{v}{unit}"))
    return s, lab

def _combo(parent, items, cur=0):
    c = QComboBox(parent)
    c.addItems(items)
    c.setCurrentIndex(cur)
    c.setFixedSize(116, 22)
    c.setStyleSheet(
        "QComboBox{background:#1b1b20;border:1px solid #26262c;"
        "border-radius:5px;color:#cfcfd6;padding:0 8px;"
        "font-family:Segoe UI;font-size:9px}"
        "QComboBox:hover{border-color:#3a3a42}"
        "QComboBox::drop-down{border:0;width:18px}"
        "QComboBox QAbstractItemView{background:#15151a;color:#cfcfd6;"
        "border:1px solid #26262c;selection-background-color:#26262c}")
    return c

def _field(parent, txt):
    f = QLineEdit(txt, parent)
    f.setFixedSize(150, 22)
    f.setStyleSheet(
        "QLineEdit{background:#1b1b20;border:1px solid #26262c;"
        "border-radius:5px;color:#cfcfd6;padding:0 8px;"
        "font-family:Segoe UI;font-size:9px}"
        "QLineEdit:focus{border-color:#9090a0}")
    return f

class KeyBtn(QPushButton):
    def __init__(self, parent, bind):
        super().__init__(bind, parent)
        self.setFixedSize(92, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QPushButton{background:#1b1b20;border:1px solid #26262c;"
            "border-radius:5px;color:#cfcfd6;"
            "font-family:Segoe UI;font-size:9px}"
            "QPushButton:hover{border-color:#3a3a42}")
        self.clicked.connect(self._arm)

    def _arm(self):
        self.setText("press a key")
        self.setStyleSheet(
            "QPushButton{background:#26262c;border:1px solid #9090a0;"
            "border-radius:5px;color:#fff;"
            "font-family:Segoe UI;font-size:9px}")
        self.setFocus()

    def keyPressEvent(self, e):
        if self.text() == "press a key":
            self.setText(e.text().upper() if e.text()
                         else f"k{e.key()}")
            self.setStyleSheet(
                "QPushButton{background:#1b1b20;border:1px solid #26262c;"
                "border-radius:5px;color:#cfcfd6;"
                "font-family:Segoe UI;font-size:9px}")
        else:
            super().keyPressEvent(e)

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("gothinc")
        self.setFixedSize(W, H)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.page = "welcome"
        self.user = sys.argv[1] if len(sys.argv) > 1 else "user"
        self._drag = None

        fid = QFontDatabase.addApplicationFont(str(ASSETS / "luckiest.ttf"))
        self.title_font = (QFontDatabase.applicationFontFamilies(fid)[0]
                           if fid >= 0 else "Verdana")
        self.art = QPixmap(str(ASSETS / "goth.png"))

        self.btns = {}
        for i, (ic, name) in enumerate(NAV):
            b = QPushButton(self)
            b.setGeometry(12, 70 + i * 38, SB - 24, 30)
            b.setIcon(icon(ic))
            b.setText("  " + name)
            b.setCursor(Qt.PointingHandCursor)
            b.setCheckable(True)
            b.setStyleSheet(
                "QPushButton{text-align:left;color:#8a8a95;border:0;"
                "border-radius:6px;font-family:Segoe UI;font-size:10px;"
                "padding-left:10px}"
                "QPushButton:hover{background:#1b1b20;color:#eaeaf0}"
                "QPushButton:checked{background:#26262c;color:#fff}")
            b.clicked.connect(lambda _, n=name: self._nav(n))
            self.btns[name] = b
        self.btns["welcome"].setChecked(True)

        self.x = QPushButton("×", self)
        self.x.setGeometry(W - 34, 12, 22, 22)
        self.x.setStyleSheet(
            "QPushButton{color:rgba(255,255,255,120);background:rgba(0,0,0,60);"
            "border-radius:11px;font-family:Segoe UI;font-size:12px;"
            "padding-bottom:2px}"
            "QPushButton:hover{color:#fff;background:#c0392b}")
        self.x.clicked.connect(self.close)

        self.rows = {}
        for name in ("welcome", "aimbot", "visuals", "misc", "config"):
            holder = QFrame(self)
            holder.setGeometry(SB + 16, 60, W - SB - 32, H - 76)
            holder.setStyleSheet("background:transparent;")
            self.rows[name] = holder
            self._fill(name, holder)
        self.rows["welcome"].show()

    def _row(self, holder, col, y, label, ctl, val=None):
        CW2 = 262
        x = col * (CW2 + 14)
        t = QLabel(label, holder)
        t.setGeometry(x, y + 3, 150, 16)
        t.setStyleSheet("color:#b8b8c0;font-family:Segoe UI;font-size:10px;")
        ctl.setParent(holder)
        cw2 = ctl.width()
        ctl.move(x + CW2 - cw2 - (50 if val else 0), y)
        if val:
            val.setParent(holder)
            val.move(x + CW2 - 48, y + 2)

    def _head(self, holder, col, y, txt):
        CW2 = 262
        x = col * (CW2 + 14)
        h = QLabel(txt, holder)
        h.setGeometry(x, y, CW2, 14)
        h.setStyleSheet("color:#55555e;font-family:Segoe UI;font-size:8px;"
                        "font-weight:700;letter-spacing:1px;")

    def _fill(self, name, holder):
        if name == "welcome":
            cw = W - SB - 32
            Banner(holder, self.user, self.art, self.title_font)

            b = QPushButton("browse ->", holder)
            b.setGeometry(20, 102, 96, 26)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(
                "QPushButton{background:#e8e8ee;color:#0a0a0c;border:0;"
                "border-radius:13px;font-family:Segoe UI;font-size:10px;"
                "font-weight:600}"
                "QPushButton:hover{background:#fff}")
            b.clicked.connect(lambda: self._nav("aimbot"))

            self.card1 = ImgCard(holder, 0, 162, (cw - 12) // 2, 150,
                                 ASSETS / "bunny.png", "games",
                                 "jump into a server", "open ->",
                                 side=True)
            self.card2 = ImgCard(holder, (cw + 12) // 2, 162,
                                 (cw - 12) // 2, 150,
                                 ASSETS / "card2.png", "start your new project",
                                 "whatever youre building next", None, side=True)
        elif name == "aimbot":
            self._head(holder, 0, 4, "MAIN SWITCHES")
            self._head(holder, 1, 4, "KEYS & INPUTS")
            r = 26
            self._row(holder, 0, r * 1, "enable module",
                      Toggle(holder, 0, 0, True))
            self._row(holder, 0, r * 2, "silent mode",
                      Toggle(holder, 0, 0))
            sl, lb = _slider(holder, 0, 100, 71, "%")
            self._row(holder, 0, r * 3, "smooth", sl, lb)
            sl, lb = _slider(holder, 1, 300, 35)
            self._row(holder, 0, r * 4, "fov radius", sl, lb)
            self._row(holder, 0, r * 5, "visible check",
                      Toggle(holder, 0, 0))
            sl, lb = _slider(holder, 0, 500, 45, " ms")
            self._row(holder, 0, r * 6, "reaction time", sl, lb)
            self._row(holder, 0, r * 7, "field preset",
                      _combo(holder, ["balanced", "legit", "rage", "seed"]))
            self._row(holder, 0, r * 8, "bone priority",
                      _combo(holder, ["crosshair", "head", "neck", "nearest"]))
            self._row(holder, 0, r * 9, "target tag",
                      _field(holder, "default_note"))
            self._row(holder, 0, r * 10, "auto scope",
                      Toggle(holder, 0, 0))

            self._row(holder, 1, r * 1, "activation key",
                      KeyBtn(holder, "Mouse4"))
            self._row(holder, 1, r * 2, "emergency key",
                      KeyBtn(holder, "F8"))
            self._row(holder, 1, r * 3, "profile name",
                      _field(holder, "profile_01"))
            self._row(holder, 1, r * 4, "aim zone",
                      _combo(holder, ["head", "chest", "pelvis", "random"]))
            self._row(holder, 1, r * 5, "preset slot",
                      _combo(holder, ["combat", "legit", "hvh"]))
            self._row(holder, 1, r * 6, "priority mode",
                      _combo(holder, ["crosshair", "distance", "health"]))
            self._row(holder, 1, r * 7, "aim keybind",
                      KeyBtn(holder, "MouseRight"))
            self._row(holder, 1, r * 8, "override key",
                      KeyBtn(holder, "LeftShift"))
            self._row(holder, 1, r * 9, "tap to lock",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 10, "auto save slot",
                      Toggle(holder, 0, 0))
        elif name == "visuals":
            self._head(holder, 0, 4, "RENDERING")
            self._head(holder, 1, 4, "FILTERS")
            r = 26
            self._row(holder, 0, r * 1, "box esp",
                      Toggle(holder, 0, 0, True))
            self._row(holder, 0, r * 2, "tracer",
                      Toggle(holder, 0, 0))
            self._row(holder, 0, r * 3, "skeleton",
                      Toggle(holder, 0, 0))
            sl, lb = _slider(holder, 0, 100, 60, "%")
            self._row(holder, 0, r * 4, "glow", sl, lb)
            sl, lb = _slider(holder, 10, 500, 120, " m")
            self._row(holder, 0, r * 5, "max distance", sl, lb)
            self._row(holder, 0, r * 6, "chams",
                      _combo(holder, ["off", "flat", "wireframe", "ghost"]))
            self._row(holder, 0, r * 7, "fps unlock",
                      Toggle(holder, 0, 0, True))
            self._row(holder, 1, r * 1, "show enemies",
                      Toggle(holder, 0, 0, True))
            self._row(holder, 1, r * 2, "show team",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 3, "show weapons",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 4, "visible only",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 5, "night mode",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 6, "brightness",
                      _combo(holder, ["normal", "bright", "dark"]))
        elif name == "misc":
            self._head(holder, 0, 4, "MOVEMENT")
            self._head(holder, 1, 4, "AUTOMATION")
            r = 26
            self._row(holder, 0, r * 1, "speed override",
                      Toggle(holder, 0, 0))
            sl, lb = _slider(holder, 16, 200, 34)
            self._row(holder, 0, r * 2, "walk speed", sl, lb)
            sl, lb = _slider(holder, 50, 300, 100, "%")
            self._row(holder, 0, r * 3, "jump power", sl, lb)
            self._row(holder, 0, r * 4, "fly",
                      Toggle(holder, 0, 0))
            self._row(holder, 0, r * 5, "no clip",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 1, "auto play",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 2, "auto ability",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 3, "anti afk",
                      Toggle(holder, 0, 0, True))
            self._row(holder, 1, r * 4, "spin bot",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 5, "key spam",
                      KeyBtn(holder, "G"))
        elif name == "config":
            self._head(holder, 0, 4, "PROFILE")
            self._head(holder, 1, 4, "SESSION")
            r = 26
            self._row(holder, 0, r * 1, "profile name",
                      _field(holder, "profile_01"))
            self._row(holder, 0, r * 2, "runtime tag",
                      _field(holder, "default_note"))
            self._row(holder, 0, r * 3, "slot",
                      _combo(holder, ["slot 1", "slot 2", "slot 3"]))
            self._row(holder, 0, r * 4, "cloud save",
                      Toggle(holder, 0, 0))
            self._row(holder, 0, r * 5, "auto load",
                      Toggle(holder, 0, 0, True))
            self._row(holder, 1, r * 1, "panic key",
                      KeyBtn(holder, "End"))
            self._row(holder, 1, r * 2, "menu key",
                      KeyBtn(holder, "Insert"))
            self._row(holder, 1, r * 3, "stealth mode",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 4, "logging",
                      Toggle(holder, 0, 0))
            self._row(holder, 1, r * 5, "theme",
                      _combo(holder, ["black&white", "wine", "mono"]))
        holder.hide()

    def _nav(self, name):
        self.page = name
        for n, h in self.rows.items():
            h.setVisible(n == name)
        for n, b in self.btns.items():
            b.setChecked(n == name)
        self.update()

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

        p.fillRect(0, 0, SB, H, QColor("#09090b"))
        p.setPen(QPen(QColor("#1d1d22"), 1))
        p.drawLine(SB, 0, SB, H)

        f = QFont(self.title_font)
        f.setPixelSize(17)
        p.setFont(f)
        p.setPen(QColor("#f0f0f4"))
        p.drawText(14, 40, "GOTHINC")
        p.setPen(QColor("#3a3a42"))
        p.setFont(QFont("Segoe UI", 7))
        p.drawText(14, 56, "v0.4")

        p.setPen(QColor("#fff"))
        p.setFont(QFont("Segoe UI Semibold", 13))
        p.drawText(SB + 16, 40, self.page)
        p.setPen(QPen(QColor("#1d1d22"), 1))
        p.drawLine(SB + 16, 52, W - 16, 52)

        p.end()

    def mousePressEvent(self, e):
        self._drag = e.globalPosition() - self.pos()

    def mouseMoveEvent(self, e):
        if self._drag is not None:
            self.move(e.globalPosition().toPoint() - self._drag.toPoint())

    def mouseReleaseEvent(self, e):
        self._drag = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Main()
    w.show()
    if "--shot" in sys.argv:
        QTimer.singleShot(300, lambda: w._nav("aimbot"))
        QTimer.singleShot(700, lambda:
            w.grab().toImage().save("shots/aimbot.png"))
        QTimer.singleShot(900, lambda: w._nav("welcome"))
        QTimer.singleShot(1400, lambda: (
            w.grab().toImage().save("shots/welcome.png"), app.quit()))
    app.exec()
