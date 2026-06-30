import sys, os, json, calendar
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QGridLayout, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame, QMessageBox, QMenu, QDialog, QLineEdit, QTextEdit,
    QComboBox, QDialogButtonBox, QFormLayout, QTimeEdit, QScrollArea, QToolButton,
    QGraphicsOpacityEffect, QSizePolicy)
from PySide6.QtGui import (QPixmap, QColor, QCursor, QPainter, QLinearGradient, QIcon, QAction,
    QDesktopServices, QFont, QRadialGradient, QConicalGradient, QPainterPath, QPen, QBrush,
    QFontMetrics)
from PySide6.QtCore import (Qt, QTimer, QTime, QUrl, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QSequentialAnimationGroup, QRect, QRectF, QPoint, QPointF,
    Property, QObject)

DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(DIR, "images")
DATA_FILE = os.path.join(DIR, "calendar_events.json")
IMG_NAMES = ["1january.jpg","2february.jpg","3march.jpg","4april.jpg","5may.jpg","6june.jpg",
             "7july.jpg","8august.jpg","9september.jpg","10october.jpg","11november.jpg","12december.jpg"]
GRADIENTS = [("#3a6186","#89253e"),("#1f4037","#99f2c8"),("#355c7d","#6c5b7b"),("#56ab2f","#a8e063"),
             ("#f7971e","#ffd200"),("#11998e","#38ef7d"),("#fc4a1a","#f7b733"),("#1488cc","#2b32b2"),
             ("#ff5f6d","#ffc371"),("#4b6cb7","#182848"),("#834d9b","#d04ed6"),("#0f2027","#2c5364")]
COLORS = {"Tomato":"#d50000","Flamingo":"#e67c73","Tangerine":"#f4511e","Banana":"#f6bf26",
          "Sage":"#33b679","Basil":"#0b8043","Peacock":"#039be5","Blueberry":"#3f51b5",
          "Lavender":"#7986cb","Grape":"#8e24aa","Graphite":"#616161"}
WD = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
WD_MINI = ["M","T","W","T","F","S","S"]

PALETTES = {
    "light": dict(bg="#ffffff", bg_alt="#f6f8fc", border="#dadce0", text="#202124",
                  text_dim="#5f6368", accent="#1a73e8", hover="#f1f3f4", weekend="#d93025"),
    "dark": dict(bg="#202124", bg_alt="#26272b", border="#3c4043", text="#e8eaed",
                 text_dim="#9aa0a6", accent="#8ab4f8", hover="#33343a", weekend="#f28b82"),
}

def system_theme():
    try:
        c = QApplication.palette().window().color()
        return "dark" if (0.299*c.red()+0.587*c.green()+0.114*c.blue()) < 128 else "light"
    except Exception:
        return "light"

def holidays(y):
    return {f"{y}-01-01":"New Year's Day", f"{y}-03-08":"Women's Day", f"{y}-03-23":"Pakistan Day",
            f"{y}-04-22":"Earth Day", f"{y}-05-01":"Labour Day", f"{y}-05-08":"Red Cross Day",
            f"{y}-06-05":"Environment Day", f"{y}-07-01":"Doctor's Day", f"{y}-08-14":"Independence Day",
            f"{y}-09-06":"Defence Day", f"{y}-10-02":"Gandhi's Birthday", f"{y}-11-09":"Iqbal Day",
            f"{y}-12-10":"Human Rights Day"}

def fmt_time(t):
    try: return datetime.strptime(t, "%H:%M").strftime("%I:%M %p").lstrip("0")
    except Exception: return t


# ─────────────────────────────────────────────────────────────────────────────
#  SPLASH SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class AnimatedOrb(QWidget):
    """Floating translucent orb for the splash background."""
    def __init__(self, parent, x, y, size, color1, color2, speed=3000):
        super().__init__(parent)
        self.setGeometry(x, y, size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._color1 = QColor(color1)
        self._color2 = QColor(color2)
        self._offset = 0.0
        self._size = size
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)
        self._t = 0
        self._speed = speed
        self._ox, self._oy = x, y
        self._amp = 18

    def _animate(self):
        import math
        self._t += 16
        dx = math.sin(self._t / self._speed * 2 * 3.14159) * self._amp
        dy = math.cos(self._t / self._speed * 2 * 3.14159) * self._amp * 0.6
        self.move(int(self._ox + dx), int(self._oy + dy))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QRadialGradient(self._size/2, self._size/2, self._size/2)
        c1 = QColor(self._color1); c1.setAlpha(90)
        c2 = QColor(self._color2); c2.setAlpha(0)
        grad.setColorAt(0, c1)
        grad.setColorAt(1, c2)
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, self._size, self._size)


class CalendarIconWidget(QWidget):
    """Animated mini calendar icon with a glowing ring."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 110)
        self._angle = 0
        self._t = QTimer(self)
        self._t.timeout.connect(self._spin)
        self._t.start(16)
        self._rot = 0

    def _spin(self):
        self._rot = (self._rot + 0.5) % 360
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy, r = 55, 55, 46

        # Spinning gradient ring
        grad = QConicalGradient(cx, cy, self._rot)
        grad.setColorAt(0.0, QColor("#1a73e8"))
        grad.setColorAt(0.3, QColor("#4285f4"))
        grad.setColorAt(0.6, QColor("#8ab4f8"))
        grad.setColorAt(1.0, QColor("#1a73e8"))
        pen = QPen(QBrush(grad), 4)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Soft halo behind the card
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(26, 115, 232, 18))
        p.drawEllipse(cx - r + 6, cy - r + 6, (r - 6) * 2, (r - 6) * 2)

        # Calendar emoji-style icon
        inner = r - 10
        rect = QRectF(cx - inner, cy - inner, inner * 2, inner * 2)
        p.setBrush(QColor(255, 255, 255))
        p.setPen(QPen(QColor(218, 220, 224), 1.5))
        p.drawRoundedRect(rect, 6, 6)

        # Calendar header bar
        header = QRectF(cx - inner, cy - inner, inner * 2, inner * 0.55)
        p.setBrush(QColor(26, 115, 232, 230))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(header, 6, 6)
        p.drawRect(QRectF(cx - inner, cy - inner + header.height() - 6, inner * 2, 6))

        # Day number in center
        now = datetime.now()
        p.setPen(QColor(32, 33, 36))
        f = QFont("Segoe UI", 14, QFont.Bold)
        p.setFont(f)
        p.drawText(QRectF(cx - inner, cy - inner + inner * 0.6, inner * 2, inner * 1.2),
                   Qt.AlignHCenter | Qt.AlignTop, str(now.day))


class SplashScreen(QWidget):
    """Full-screen animated splash / launch screen."""

    def __init__(self, on_enter):
        super().__init__()
        self._on_enter = on_enter
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setFixedSize(1000, 640)

        # Background
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: #ffffff;")

        # Decorative orbs
        AnimatedOrb(self, -60, -60, 340, "#1a73e8", "#8ab4f8", 5000)
        AnimatedOrb(self, 700, 400, 280, "#4285f4", "#aecbfa", 7000)
        AnimatedOrb(self, 300, 500, 200, "#669df6", "#c2e7ff", 4000)
        AnimatedOrb(self, 820, -40, 220, "#8ab4f8", "#d2e3fc", 6000)

        # Main layout
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Top spacer
        lay.addStretch(2)

        # Icon + wordmark row
        center = QHBoxLayout()
        center.addStretch()

        v_center = QVBoxLayout()
        v_center.setSpacing(0)
        v_center.setAlignment(Qt.AlignHCenter)

        # Calendar icon
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        self._icon = CalendarIconWidget(self)
        icon_row.addWidget(self._icon)
        icon_row.addStretch()
        v_center.addLayout(icon_row)

        v_center.addSpacing(22)

        # App name
        self._name_label = QLabel("Pro Calendar")
        self._name_label.setAlignment(Qt.AlignCenter)
        font = QFont("Segoe UI", 48, QFont.Light)
        font.setLetterSpacing(QFont.AbsoluteSpacing, -1.5)
        self._name_label.setFont(font)
        self._name_label.setStyleSheet("color: #202124;")
        v_center.addWidget(self._name_label)

        v_center.addSpacing(8)

        # Tagline
        self._tag_label = QLabel("Your year, beautifully organized.")
        self._tag_label.setAlignment(Qt.AlignCenter)
        tag_font = QFont("Segoe UI", 13)
        tag_font.setLetterSpacing(QFont.AbsoluteSpacing, 2.5)
        self._tag_label.setFont(tag_font)
        self._tag_label.setStyleSheet("color: rgba(26,115,232,0.85);")
        v_center.addWidget(self._tag_label)

        v_center.addSpacing(48)

        # Enter button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._enter_btn = QPushButton("  Open Calendar  →")
        self._enter_btn.setFixedSize(220, 52)
        self._enter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._enter_btn.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self._enter_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1a73e8, stop:1 #4285f4);
                color: white;
                border: none;
                border-radius: 26px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1765cc, stop:1 #3367d6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #135cb0, stop:1 #2a56b8);
            }
        """)
        self._enter_btn.clicked.connect(self._launch)
        btn_row.addWidget(self._enter_btn)
        btn_row.addStretch()
        v_center.addLayout(btn_row)

        center.addLayout(v_center)
        center.addStretch()
        lay.addLayout(center)

        lay.addStretch(2)

        # Bottom strip
        bottom = QHBoxLayout()
        bottom.setContentsMargins(40, 0, 40, 28)
        now = datetime.now()
        month_names = ["January","February","March","April","May","June",
                       "July","August","September","October","November","December"]
        self._date_label = QLabel(
            f"{month_names[now.month-1].upper()}  ·  {now.year}"
        )
        self._date_label.setFont(QFont("Segoe UI", 9))
        self._date_label.setStyleSheet("color: rgba(32,33,36,0.35); letter-spacing: 3px;")

        self._ver_label = QLabel("v 2026")
        self._ver_label.setFont(QFont("Segoe UI", 9))
        self._ver_label.setStyleSheet("color: rgba(32,33,36,0.35); letter-spacing: 2px;")
        bottom.addWidget(self._date_label)
        bottom.addStretch()
        bottom.addWidget(self._ver_label)
        lay.addLayout(bottom)

        # Fade-in effect
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0)
        self._fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setDuration(800)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)
        QTimer.singleShot(80, self._fade_in.start)

    def _launch(self):
        self._fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setDuration(400)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)
        self._fade_out.finished.connect(self._finish)
        self._fade_out.start()

    def _finish(self):
        self.hide()
        self._on_enter()
        self.deleteLater()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._launch()
        super().keyPressEvent(e)


# ─────────────────────────────────────────────────────────────────────────────
#  ORIGINAL CALENDAR CODE (unchanged logic)
# ─────────────────────────────────────────────────────────────────────────────

class Event:
    def __init__(self, title, time="", color="Peacock", notes="", link=""):
        self.title, self.time, self.color, self.notes, self.link = title, time, color, notes, link
    def to_dict(self): return self.__dict__
    @staticmethod
    def from_dict(d): return Event(d.get("title",""), d.get("time",""), d.get("color","Peacock"), d.get("notes",""), d.get("link",""))


class EventDialog(QDialog):
    def __init__(self, parent, date_str, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Event"); self.setMinimumWidth(380)
        self.result_event, self.delete_requested = None, False
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d, %Y")))

        form = QFormLayout()
        self.title_edit = QLineEdit(existing.title if existing else "")
        self.title_edit.setPlaceholderText("Add title (e.g. Birthday: Sara)")
        form.addRow("Title", self.title_edit)

        row = QHBoxLayout()
        self.all_day = QComboBox(); self.all_day.addItems(["All day", "At a time"])
        self.time_edit = QTimeEdit(); self.time_edit.setDisplayFormat("hh:mm AP")
        if existing and existing.time:
            self.all_day.setCurrentIndex(1)
            h, m = map(int, existing.time.split(":")); self.time_edit.setTime(QTime(h, m))
        else:
            self.time_edit.setTime(QTime(9, 0)); self.time_edit.setEnabled(False)
        self.all_day.currentIndexChanged.connect(lambda i: self.time_edit.setEnabled(i == 1))
        row.addWidget(self.all_day); row.addWidget(self.time_edit)
        form.addRow("When", row)

        self.color_combo = QComboBox()
        for name, hexcode in COLORS.items():
            self.color_combo.addItem(name)
            pix = QPixmap(14, 14); pix.fill(QColor(hexcode))
            self.color_combo.setItemIcon(self.color_combo.count()-1, QIcon(pix))
        if existing:
            i = self.color_combo.findText(existing.color)
            if i >= 0: self.color_combo.setCurrentIndex(i)
        form.addRow("Color", self.color_combo)

        self.notes_edit = QTextEdit(existing.notes if existing else "")
        self.notes_edit.setFixedHeight(70)
        form.addRow("Notes", self.notes_edit)

        self.link_edit = QLineEdit(existing.link if existing else "")
        self.link_edit.setPlaceholderText("https://... (Zoom, registration page, etc.)")
        form.addRow("Link", self.link_edit)
        lay.addLayout(form)

        btns = QHBoxLayout()
        if existing:
            del_btn = QPushButton("Delete event"); del_btn.clicked.connect(self._delete)
            btns.addWidget(del_btn)
        btns.addStretch()
        box = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        box.accepted.connect(self._save); box.rejected.connect(self.reject)
        btns.addWidget(box); lay.addLayout(btns)

    def _save(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Missing title", "Please give the event a title.")
            return
        t = self.time_edit.time().toString("HH:mm") if self.all_day.currentIndex() == 1 else ""
        link = self.link_edit.text().strip()
        if link and not link.lower().startswith(("http://", "https://")):
            link = "https://" + link
        self.result_event = Event(title, t, self.color_combo.currentText(), self.notes_edit.toPlainText().strip(), link)
        self.accept()

    def _delete(self):
        self.delete_requested = True
        self.accept()


class DayCell(QFrame):
    MAX_CHIPS = 3
    def __init__(self, owner):
        super().__init__()
        self.owner, self.date_key = owner, None
        self.setMinimumSize(90, 78); self.setCursor(QCursor(Qt.PointingHandCursor))
        v = QVBoxLayout(self); v.setContentsMargins(6, 4, 6, 4); v.setSpacing(2)
        top = QHBoxLayout()
        self.num = QLabel(""); self.num.setFixedSize(26, 26); self.num.setAlignment(Qt.AlignCenter)
        top.addWidget(self.num); top.addStretch()
        v.addLayout(top)
        self.chips = QVBoxLayout(); self.chips.setSpacing(2)
        v.addLayout(self.chips); v.addStretch()
        self.p = PALETTES["light"]

    def _clear_chips(self):
        while self.chips.count():
            w = self.chips.takeAt(0).widget()
            if w: w.deleteLater()

    def _chip(self, text, color):
        l = QLabel(text)
        l.setStyleSheet(f"background:{color}; color:white; border-radius:4px; font-size:10px; padding:2px 6px;")
        l.setMaximumWidth(160)
        return l

    def set_empty(self, p):
        self.p = p; self.date_key = None; self.num.setText(""); self.num.setStyleSheet("")
        self._clear_chips(); self.setEnabled(False)
        self.setStyleSheet(f"background:{p['bg_alt']}; border:1px solid {p['border']};")

    def set_day(self, day, evs, holiday, is_today, is_weekend, date_key, p):
        self.p, self.date_key = p, date_key
        self.setEnabled(True); self.num.setText(str(day))
        if is_today:
            self.num.setStyleSheet(f"background:{p['accent']}; color:white; border-radius:13px; font-weight:700;")
        else:
            self.num.setStyleSheet(f"color:{p['weekend'] if is_weekend else p['text']}; font-weight:600;")
        self.setStyleSheet(f"background:{p['bg']}; border:1px solid {p['border']};")
        self._clear_chips()
        if holiday and not evs:
            self.chips.addWidget(self._chip(holiday, "#0b8043"))
        else:
            shown = evs[:self.MAX_CHIPS]
            for ev in shown:
                label = ev.title if not ev.time else f"{fmt_time(ev.time)}  {ev.title}"
                self.chips.addWidget(self._chip(label, COLORS.get(ev.color, p['accent'])))
            if len(evs) > len(shown):
                more = QLabel(f"+{len(evs)-len(shown)} more")
                more.setStyleSheet(f"color:{p['text_dim']}; font-size:10px;")
                self.chips.addWidget(more)
        self.setToolTip("\n".join(e.title for e in evs) if evs else (holiday or ""))

    def mousePressEvent(self, e):
        if self.date_key: self.owner.open_event_dialog(self.date_key)
        super().mousePressEvent(e)


class ProCalendar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro Calendar 2026")
        self.setGeometry(100, 100, 1240, 820); self.setMinimumSize(1080, 700)
        now = datetime.now()
        self.current_year, self.current_month = now.year, now.month
        self.events = {}
        self.theme_mode = "light"
        self.load_events()
        self._build_ui()
        self._apply_theme()
        self.refresh()
        self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(1000); self._tick()

    def _build_ui(self):
        root = QHBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(self._sidebar())
        root.addWidget(self._main_panel(), 1)

    def _sidebar(self):
        side = QFrame(); side.setFixedWidth(280)
        lay = QVBoxLayout(side); lay.setContentsMargins(18, 22, 18, 18); lay.setSpacing(14)

        self.create_btn = QPushButton("＋  Create event"); self.create_btn.setFixedHeight(46)
        self.create_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.create_btn.clicked.connect(self._create_today)
        lay.addWidget(self.create_btn)

        nav = QHBoxLayout()
        self.mini_label = QLabel()
        prev, nxt = QToolButton(text="‹"), QToolButton(text="›")
        prev.clicked.connect(self.prev_month); nxt.clicked.connect(self.next_month)
        for b in (prev, nxt): b.setCursor(QCursor(Qt.PointingHandCursor)); b.setFixedSize(26, 26)
        nav.addWidget(self.mini_label, 1); nav.addWidget(prev); nav.addWidget(nxt)
        lay.addLayout(nav)

        self.mini_grid = QGridLayout(); self.mini_grid.setSpacing(4)
        lay.addLayout(self.mini_grid)
        self.mini_labels = []
        for col, d in enumerate(WD_MINI):
            l = QLabel(d); l.setAlignment(Qt.AlignCenter)
            self.mini_grid.addWidget(l, 0, col)
        for r in range(1, 7):
            row = []
            for c in range(7):
                l = QLabel(""); l.setAlignment(Qt.AlignCenter); l.setFixedSize(30, 26)
                l.setCursor(QCursor(Qt.PointingHandCursor))
                l.mousePressEvent = lambda e, rr=r, cc=c: self._mini_clicked(rr, cc)
                self.mini_grid.addWidget(l, r, c); row.append(l)
            self.mini_labels.append(row)

        lay.addSpacing(10)
        lay.addWidget(QLabel("Upcoming"))
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        scroll.setMaximumHeight(190)
        holder = QWidget(); self.upcoming_layout = QVBoxLayout(holder)
        self.upcoming_layout.setContentsMargins(0, 0, 0, 0); self.upcoming_layout.setSpacing(6)
        self.upcoming_layout.addStretch()
        scroll.setWidget(holder); lay.addWidget(scroll)

        lay.addSpacing(6)
        sep1 = QFrame(); sep1.setFixedHeight(1); sep1.setObjectName("sep")
        lay.addWidget(sep1)
        lay.addSpacing(6)

        lay.addWidget(QLabel("My Calendars"))
        legend = QGridLayout(); legend.setHorizontalSpacing(8); legend.setVerticalSpacing(4)
        legend_names = list(COLORS.items())
        for i, (name, hexcode) in enumerate(legend_names):
            dot = QLabel(); dot.setFixedSize(9, 9); dot.setStyleSheet(f"background:{hexcode}; border-radius:4px;")
            lbl = QLabel(name); lbl.setStyleSheet("font-size:11px;")
            r, c = divmod(i, 2)
            box = QHBoxLayout(); box.setSpacing(6); box.addWidget(dot); box.addWidget(lbl); box.addStretch()
            wrap = QWidget(); wrap.setLayout(box)
            legend.addWidget(wrap, r, c)
        lay.addLayout(legend)

        lay.addSpacing(6)
        sep2 = QFrame(); sep2.setFixedHeight(1); sep2.setObjectName("sep")
        lay.addWidget(sep2)
        lay.addSpacing(6)

        lay.addWidget(QLabel("This Month"))
        self.stats_label = QLabel("")
        self.stats_label.setWordWrap(True)
        lay.addWidget(self.stats_label)
        lay.addStretch()
        return side

    def _main_panel(self):
        panel = QWidget(); right = QVBoxLayout(panel)
        right.setContentsMargins(0, 0, 0, 0); right.setSpacing(0)

        self.header = QFrame(); self.header.setFixedHeight(190)
        self.bg_label = QLabel(self.header); self.bg_label.lower()
        hl = QVBoxLayout(self.header); hl.setContentsMargins(28, 16, 28, 16)
        top = QHBoxLayout()
        self.title_label = QLabel("Pro Calendar")
        self.clock_label = QLabel()
        self.settings_btn = QPushButton("⚙"); self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.settings_btn.clicked.connect(self._settings_menu)
        top.addWidget(self.title_label); top.addStretch(); top.addWidget(self.clock_label)
        top.addSpacing(10); top.addWidget(self.settings_btn)
        hl.addLayout(top); hl.addStretch()
        bottom = QHBoxLayout()
        self.month_year_label = QLabel(); bottom.addWidget(self.month_year_label); bottom.addStretch()
        hl.addLayout(bottom)
        right.addWidget(self.header)

        body = QFrame(); bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 18, 24, 24); bl.setSpacing(14)
        toolbar = QHBoxLayout()
        self.today_btn = QPushButton("Today"); self.today_btn.setFixedHeight(40)
        self.today_btn.clicked.connect(self.go_to_today)
        prev, nxt = QToolButton(text="‹"), QToolButton(text="›")
        prev.clicked.connect(self.prev_month); nxt.clicked.connect(self.next_month)
        for b in (prev, nxt): b.setFixedSize(36, 36); b.setCursor(QCursor(Qt.PointingHandCursor))
        self.toolbar_label = QLabel()
        toolbar.addWidget(self.today_btn); toolbar.addWidget(prev); toolbar.addWidget(nxt)
        toolbar.addWidget(self.toolbar_label); toolbar.addStretch()
        bl.addLayout(toolbar)

        self.grid_widget = QWidget(); self.grid = QGridLayout(self.grid_widget); self.grid.setSpacing(1)
        for c in range(7): self.grid.setColumnStretch(c, 1)
        for r in range(1, 7): self.grid.setRowStretch(r, 1)
        for col, day in enumerate(WD):
            l = QLabel(day); l.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(l, 0, col)
        self.day_cells = []
        for r in range(1, 7):
            row = []
            for c in range(7):
                cell = DayCell(self); self.grid.addWidget(cell, r, c); row.append(cell)
            self.day_cells.append(row)
        bl.addWidget(self.grid_widget, 1)
        right.addWidget(body, 1)
        return panel

    def refresh(self):
        p = self._palette
        self.month_year_label.setText(f"{calendar.month_name[self.current_month]} {self.current_year}")
        self.toolbar_label.setText(f"{calendar.month_name[self.current_month]} {self.current_year}")
        self._fill_main_grid(p)
        self._fill_mini_grid()
        self._fill_upcoming()
        self._load_background(self.current_month)

    def _fill_main_grid(self, p):
        days = list(calendar.Calendar(firstweekday=0).itermonthdays(self.current_year, self.current_month))
        today = datetime.now(); hd = holidays(self.current_year); it = iter(days)
        for week in range(6):
            for col in range(7):
                cell = self.day_cells[week][col]
                d = next(it, 0)
                if d == 0:
                    cell.set_empty(p); continue
                key = f"{self.current_year}-{self.current_month:02d}-{d:02d}"
                evs = self.events.get(key, [])
                is_today = today.year == self.current_year and today.month == self.current_month and today.day == d
                cell.set_day(d, evs, hd.get(key), is_today, col >= 5, key, p)

    def _fill_mini_grid(self):
        self.mini_label.setText(f"{calendar.month_name[self.current_month]} {self.current_year}")
        days = list(calendar.Calendar(firstweekday=0).itermonthdays(self.current_year, self.current_month))
        today = datetime.now(); it = iter(days)
        for week in range(6):
            for col in range(7):
                l = self.mini_labels[week][col]
                d = next(it, 0)
                if d == 0:
                    l.setText(""); l.setStyleSheet(""); continue
                key = f"{self.current_year}-{self.current_month:02d}-{d:02d}"
                is_today = today.year == self.current_year and today.month == self.current_month and today.day == d
                l.setText(str(d))
                p = self._palette
                style = f"color:{p['text']}; border-radius:13px;"
                if is_today: style = f"background:{p['accent']}; color:white; font-weight:700; border-radius:13px;"
                elif self.events.get(key): style += " font-weight:700; text-decoration:underline;"
                l.setStyleSheet(style)

    def _fill_upcoming(self):
        while self.upcoming_layout.count():
            w = self.upcoming_layout.takeAt(0).widget()
            if w: w.deleteLater()
        today = datetime.now().date(); flat = []
        for key, evs in self.events.items():
            try: d = datetime.strptime(key, "%Y-%m-%d").date()
            except ValueError: continue
            if d >= today:
                for ev in evs: flat.append((d, ev))
        flat.sort(key=lambda x: (x[0], x[1].time or "99:99"))
        flat = flat[:8]
        if not flat:
            l = QLabel("No upcoming events"); l.setStyleSheet(f"color:{self._palette['text_dim']}; font-size:12px;")
            self.upcoming_layout.addWidget(l)
        else:
            for d, ev in flat:
                row = QFrame(); h = QHBoxLayout(row); h.setContentsMargins(8, 6, 8, 6); h.setSpacing(8)
                dot = QLabel(); dot.setFixedSize(10, 10)
                dot.setStyleSheet(f"background:{COLORS.get(ev.color,'#1a73e8')}; border-radius:5px;")
                txt = QLabel(f"{ev.title}\n{d.strftime('%b %d')}" + (f" · {fmt_time(ev.time)}" if ev.time else ""))
                h.addWidget(dot); h.addWidget(txt, 1)
                row.setStyleSheet(f"background:{self._palette['bg_alt']}; border-radius:8px;")
                self.upcoming_layout.addWidget(row)
        self.upcoming_layout.addStretch()

    def open_event_dialog(self, date_key):
        existing_list = self.events.get(date_key, [])
        existing = existing_list[0] if existing_list else None
        dlg = EventDialog(self, date_key, existing)
        if dlg.exec() == QDialog.Accepted:
            if dlg.delete_requested:
                if existing_list:
                    existing_list.pop(0)
                    if not existing_list: self.events.pop(date_key, None)
            elif dlg.result_event:
                lst = self.events.setdefault(date_key, [])
                if existing: lst[0] = dlg.result_event
                else: lst.append(dlg.result_event)
            self.save_events(); self.refresh()

    def _create_today(self):
        now = datetime.now()
        if now.month != self.current_month or now.year != self.current_year:
            self.current_year, self.current_month = now.year, now.month
            self.refresh()
        self.open_event_dialog(now.strftime("%Y-%m-%d"))

    def _mini_clicked(self, row, col):
        l = self.mini_labels[row][col]
        if l.text().isdigit():
            day = int(l.text())
            self.open_event_dialog(f"{self.current_year}-{self.current_month:02d}-{day:02d}")

    def _settings_menu(self):
        menu = QMenu(self)
        for label, mode in (("☀  Light theme", "light"), ("🌙  Dark theme", "dark"), ("🖥  Match system", "system")):
            act = QAction(label, self); act.setCheckable(True); act.setChecked(self.theme_mode == mode)
            act.triggered.connect(lambda _, m=mode: self._set_theme(m))
            menu.addAction(act)
        menu.exec(self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomLeft()))

    def _set_theme(self, mode):
        self.theme_mode = mode
        self._apply_theme()
        self.refresh()

    def _apply_theme(self):
        mode = system_theme() if self.theme_mode == "system" else self.theme_mode
        p = PALETTES[mode]; self._palette = p
        self.setStyleSheet(f"""
            QWidget {{ font-family:'Segoe UI',Arial,sans-serif; color:{p['text']}; }}
            ProCalendar {{ background:{p['bg']}; }}
            QPushButton {{ background:{p['bg_alt']}; border:1px solid {p['border']}; border-radius:18px; padding:0 16px; }}
            QPushButton:hover {{ background:{p['hover']}; }}
            QToolButton {{ background:transparent; border:none; font-size:16px; border-radius:13px; }}
            QToolButton:hover {{ background:{p['hover']}; }}
            QLabel {{ color:{p['text']}; }}
            DayCell {{ background:{p['bg']}; border:1px solid {p['border']}; }}
            DayCell:hover {{ background:{p['hover']}; }}
        """)
        self.title_label.setStyleSheet("font-size:20px; font-weight:600; color:white;")
        self.clock_label.setStyleSheet("font-size:16px; font-family:Consolas; color:white;")
        self.month_year_label.setStyleSheet("font-size:30px; font-weight:700; color:white;")
        self.settings_btn.setStyleSheet("background:rgba(255,255,255,40); border:none; border-radius:20px; color:white;")
        self.create_btn.setStyleSheet(f"background:{p['accent']}; color:white; border:none; border-radius:23px; font-weight:600; text-align:left; padding-left:18px;")
        self.toolbar_label.setStyleSheet("font-size:20px; font-weight:600; margin-left:8px;")
        self._load_background(self.current_month)

    def _tick(self):
        self.clock_label.setText(datetime.now().strftime("%I:%M:%S %p").lstrip("0"))

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1: self.current_month, self.current_year = 12, self.current_year - 1
        self.refresh()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12: self.current_month, self.current_year = 1, self.current_year + 1
        self.refresh()

    def go_to_today(self):
        now = datetime.now(); self.current_year, self.current_month = now.year, now.month
        self.refresh()

    def load_events(self):
        self.events = {}
        if not os.path.exists(DATA_FILE): return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for key, val in raw.items():
                if isinstance(val, list): self.events[key] = [Event.from_dict(v) for v in val]
                elif isinstance(val, dict): self.events[key] = [Event.from_dict(val)]
                elif isinstance(val, str): self.events[key] = [Event(val)]
        except (json.JSONDecodeError, OSError):
            self.events = {}

    def save_events(self):
        try:
            data = {k: [e.to_dict() for e in v] for k, v in self.events.items() if v}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as exc:
            QMessageBox.warning(self, "Save failed", f"Could not save events:\n{exc}")

    def _load_background(self, month):
        w, h = max(self.header.width(), 900), self.header.height()
        pix = None
        try:
            path = os.path.join(IMG_DIR, IMG_NAMES[month - 1])
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                cand = QPixmap(path)
                if not cand.isNull(): pix = cand
        except Exception:
            pix = None
        if pix is None:
            pix = self._gradient(w, h, month)
        else:
            pix = pix.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            if pix.width() > w or pix.height() > h:
                x, y = max(0, (pix.width()-w)//2), max(0, (pix.height()-h)//2)
                pix = pix.copy(x, y, w, h)
            d = QPixmap(pix); pt = QPainter(d); pt.fillRect(d.rect(), QColor(0, 0, 0, 70)); pt.end()
            pix = d
        self.bg_label.setPixmap(pix); self.bg_label.setGeometry(0, 0, w, h); self.bg_label.lower()

    @staticmethod
    def _gradient(w, h, month):
        c1, c2 = GRADIENTS[month - 1]
        pix = QPixmap(max(w, 1), max(h, 1)); pt = QPainter(pix)
        g = QLinearGradient(0, 0, w, h); g.setColorAt(0, QColor(c1)); g.setColorAt(1, QColor(c2))
        pt.fillRect(pix.rect(), g); pt.end()
        return pix

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._load_background(self.current_month)


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    cal_win = None

    def open_calendar():
        nonlocal cal_win
        cal_win = ProCalendar()
        # Fade the calendar in
        effect = QGraphicsOpacityEffect(cal_win)
        cal_win.setGraphicsEffect(effect)
        effect.setOpacity(0)
        cal_win.show()
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(500)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        # keep reference so it isn't GC'd
        cal_win._fade_anim = anim

    splash = SplashScreen(open_calendar)
    # Center on screen
    screen = app.primaryScreen().geometry()
    splash.move((screen.width() - splash.width()) // 2,
                (screen.height() - splash.height()) // 2)
    splash.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()