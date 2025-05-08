import sys
import os
import json
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QInputDialog, QLineEdit, QMenuBar, QMenu, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QUrl, QRect, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

DOCS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "3cx_app")
os.makedirs(DOCS_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(DOCS_DIR, "config.json")
STATE_FILE = os.path.join(DOCS_DIR, "3cx_window_state.json")
last_bounds = None

LANGUAGES = {
    "en": {
        "title": "3CX Dialer",
        "username": "Extension:",
        "password": "Password:",
        "url": "Enter 3CX URL:",
        "app_title": "Window Title:",
        "automation": "Automation",
        "clipboard_dialer": "Clipboard → Dialer",
        "extras": "Extras",
        "change": "Change",
        "reset": "Reset Config",
        "reset_confirm": "Delete saved credentials and settings?",
        "reset_done": "Config has been deleted. Please restart the app.",
        "updated": "Updated",
        "change_success": "{} updated. Restart app for changes to apply.",
        "open_config": "Open Config Folder",
        "login": "Login",
        "lang_select": "Choose Language",
        "lang_prompt": "Select your language:",
        "lang_en": "English",
        "lang_de": "German",
        "start_page": "Starting Page",
        "start_page_prompt": "Choose where the app should start:",
        "start_team": "Team",
        "start_chat": "Chat",
        "start_calls": "Call History",
        "start_switch": "Switchboard",
        "start_contacts": "Contacts"
    },
    "de": {
        "title": "3CX Wählhilfe",
        "username": "Nebenstelle:",
        "password": "Passwort:",
        "url": "3cx URL eingeben:",
        "app_title": "Fenstertitel:",
        "automation": "Automatisierung",
        "clipboard_dialer": "Zwischenablage → Wählhilfe",
        "extras": "Extras",
        "change": "Ändern",
        "reset": "Zurücksetzen",
        "reset_confirm": "Gespeicherte Zugangsdaten und Einstellungen löschen?",
        "reset_done": "Konfiguration gelöscht. Bitte App neu starten.",
        "updated": "Aktualisiert",
        "change_success": "{} wurde aktualisiert. Bitte App neu starten.",
        "open_config": "Konfigurationsordner öffnen",
        "login": "Anmeldung",
        "lang_select": "Sprache wählen",
        "lang_prompt": "Bitte Sprache wählen:",
        "lang_en": "Englisch",
        "lang_de": "Deutsch",
        "start_page": "Startseite",
        "start_page_prompt": "Wählen Sie, wo die App starten soll:",
        "start_team": "Team",
        "start_chat": "Chat",
        "start_calls": "Anrufverlauf",
        "start_switch": "Zentrale",
        "start_contacts": "Kontakte"
    }
}

START_PAGE_OPTIONS = {
    "Team": "/#/people",
    "Chat": "/#/chat",
    "Call History": "/#/call_history",
    "Zentrale": "/#/switchboard",
    "Contacts": "/#/contacts",
    "Team_de": "/#/people",
    "Chat_de": "/#/chat",
    "Anrufverlauf": "/#/call_history",
    "Zentrale_de": "/#/switchboard",
    "Kontakte": "/#/contacts"
}

lang_code = "en"
tr = LANGUAGES[lang_code]

def select_language(cfg=None):
    global lang_code, tr
    items = [LANGUAGES["en"]["lang_en"], LANGUAGES["de"]["lang_de"]]
    current_lang = cfg.get("lang", "en") if cfg else "en"
    default_index = 1 if current_lang == "de" else 0
    item, ok = QInputDialog.getItem(None, LANGUAGES[current_lang]["lang_select"], LANGUAGES[current_lang]["lang_prompt"], items, default_index, False)
    if ok and item:
        lang_code = "de" if item == LANGUAGES["de"]["lang_de"] else "en"
        tr = LANGUAGES[lang_code]
        if cfg is not None:
            cfg["lang"] = lang_code
            save_config(cfg)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def ask_if_missing(parent, cfg, key, title, prompt, echo):
    if key in cfg and cfg[key]:
        return cfg[key]
    val, ok = QInputDialog.getText(parent, title, prompt, echo, cfg.get(key, ""))
    if not ok or not val:
        sys.exit()
    cfg[key] = val
    save_config(cfg)
    return val

def load_bounds():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"x": 100, "y": 100, "width": 900, "height": 700}

def save_bounds():
    if last_bounds:
        x, y, w, h = last_bounds
        with open(STATE_FILE, "w") as f:
            json.dump({"x": x, "y": y, "width": w, "height": h}, f)

class WebView(QWebEngineView):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS[{level}] {message} (Line {lineNumber}) @ {sourceID}")

class MainWindow(QMainWindow):
    def __init__(self, cfg, tel_number=None):
        super().__init__()
        self.cfg = cfg
        self.username = cfg["username"]
        self.password = cfg["password"]
        self.url = cfg["url"]
        self.setWindowTitle(cfg["title"])
        self.tel_number = tel_number
        state = load_bounds()
        self.setGeometry(QRect(state["x"], state["y"], state["width"], state["height"]))

        profile = QWebEngineProfile("3cx_profile", self)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setCachePath(DOCS_DIR)
        profile.setPersistentStoragePath(DOCS_DIR)

        self.view = WebView(self)
        page = QWebEnginePage(profile, self.view)
        self.view.setPage(page)
        self.setCentralWidget(self.view)

        full_url = self.url
        if self.cfg.get("start_page"):
            full_url += self.cfg["start_page"]
        self.view.load(QUrl(full_url))
        self.view.loadFinished.connect(self.on_load_finished)

        self.clipboard = QApplication.clipboard()
        self.last_clipboard = ""
        self.clip_timer = QTimer(self)
        self.clip_timer.timeout.connect(self.check_clipboard)

        if self.cfg.get("clipboard_dialer_enabled", False):
            self.clip_timer.start(3000)

        self.setup_menu()

    def setup_menu(self):
        menubar = self.menuBar()

        automation_menu = menubar.addMenu(tr["automation"])
        self.clip_toggle_action = QAction(tr["clipboard_dialer"], self)
        self.clip_toggle_action.setCheckable(True)
        self.clip_toggle_action.setChecked(self.cfg.get("clipboard_dialer_enabled", False))
        self.clip_toggle_action.triggered.connect(self.toggle_clipboard_listener)
        automation_menu.addAction(self.clip_toggle_action)

        startpage_action = QAction(tr["start_page"], self)
        startpage_action.triggered.connect(self.set_start_page)
        automation_menu.addAction(startpage_action)

        extras_menu = menubar.addMenu(tr["extras"])
        for key in ["username", "password", "url", "title"]:
            act = QAction(f"{tr['change']} {key.capitalize()}", self)
            act.triggered.connect(lambda _, k=key: self.change_config(k))
            extras_menu.addAction(act)

        reset_action = QAction(tr["reset"], self)
        reset_action.triggered.connect(self.reset_config)
        extras_menu.addAction(reset_action)

        open_dir_action = QAction(tr["open_config"], self)
        open_dir_action.triggered.connect(lambda: os.system(f"open '{DOCS_DIR}'"))
        extras_menu.addAction(open_dir_action)

        language_menu = menubar.addMenu(tr["lang_select"])
        lang_en_action = QAction(tr["lang_en"], self)
        lang_en_action.triggered.connect(lambda: self.set_language("en"))
        language_menu.addAction(lang_en_action)

        lang_de_action = QAction(tr["lang_de"], self)
        lang_de_action.triggered.connect(lambda: self.set_language("de"))
        language_menu.addAction(lang_de_action)

    def set_start_page(self):
        options = [
            tr["start_team"],
            tr["start_chat"],
            tr["start_calls"],
            tr["start_switch"],
            tr["start_contacts"]
        ]
        item, ok = QInputDialog.getItem(self, tr["start_page"], tr["start_page_prompt"], options, 0, False)
        if ok and item:
            key = item if lang_code == "en" else item + "_de"
            self.cfg["start_page"] = START_PAGE_OPTIONS.get(key, "")
            save_config(self.cfg)

    def change_config(self, key):
        val, ok = QInputDialog.getText(self, f"{tr['change']} {key.capitalize()}", f"{tr['change']} {key}:", QLineEdit.EchoMode.Password if key == "password" else QLineEdit.EchoMode.Normal)
        if ok and val:
            self.cfg[key] = val
            save_config(self.cfg)
            QMessageBox.information(self, tr["updated"], tr["change_success"].format(key.capitalize()))

    def toggle_clipboard_listener(self, checked):
        self.cfg["clipboard_dialer_enabled"] = checked
        save_config(self.cfg)
        if checked:
            self.clip_timer.start(3000)
        else:
            self.clip_timer.stop()

    def reset_config(self):
        reply = QMessageBox.question(self, tr["reset"], tr["reset_confirm"],
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            QMessageBox.information(self, tr["reset"], tr["reset_done"])
            self.close()

    def set_language(self, code):
        global lang_code, tr
        lang_code = code
        tr = LANGUAGES[lang_code]
        self.cfg["lang"] = lang_code
        save_config(self.cfg)

        msg = QMessageBox(self)
        msg.setWindowTitle(tr["updated"])
        msg.setText(tr["change_success"].format("Language"))
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowIcon(QIcon()) 
        msg.exec()

        self.close()

    def check_clipboard(self):
        raw = self.clipboard.text().strip()
        cleaned = re.sub(r"[^\d+]", "", raw)
        if cleaned.startswith('+'):
            cleaned = '+' + re.sub(r"[^\d]", "", cleaned[1:])
        else:
            cleaned = re.sub(r"[^\d]", "", cleaned)

        if raw != self.last_clipboard and 5 <= len(cleaned) <= 20:
            self.last_clipboard = raw
            js = (
                "var dialer = document.querySelector('#menuDialer');"
                "var dialerContainer = document.querySelector('toaster-container');"
                "if (dialer && dialerContainer && getComputedStyle(dialerContainer).display === 'none') {"
                "  dialer.click();"
                "  setTimeout(function() {"
                "    var input = document.querySelector('#dialpad-input');"
                f"    if (input) input.value = {json.dumps(cleaned)};"
                "  }, 1000);"
                "} else {"
                "  var input = document.querySelector('#dialpad-input');"
                f"  if (input) input.value = {json.dumps(cleaned)};"
                "}"
            )
            self.view.page().runJavaScript(js)

    def on_load_finished(self, ok):
        if not ok:
            return
        login_js = (
            "(function(){"
            "var u=" + json.dumps(self.username) + ";"
            "var p=" + json.dumps(self.password) + ";"
            "var f=document.querySelector('#loginInput');"
            "var g=document.querySelector('#passwordInput');"
            "if(f&&g){f.value=u;g.value=p;}"
            "setTimeout(function(){"
            "var b=document.querySelector('#submitBtn');"
            "if(b){b.click();}"
            "},1000);"
            "})();"
        )
        self.view.page().runJavaScript(login_js)

        if self.tel_number:
            inject_js = (
                "setTimeout(function() {"
                "  var dialer = document.querySelector('#menuDialer');"
                "  if (dialer) {"
                "    dialer.click();"
                "    setTimeout(function() {"
                "      var input = document.querySelector('#dialpad-input');"
                f"      if (input) input.value = {json.dumps(self.tel_number)};"
                "    }, 1000);"
                "  }"
                "}, 3000);"
            )
            self.view.page().runJavaScript(inject_js)

    def moveEvent(self, event):
        global last_bounds
        g = self.geometry()
        last_bounds = (g.x(), g.y(), g.width(), g.height())
        super().moveEvent(event)

    def resizeEvent(self, event):
        global last_bounds
        g = self.geometry()
        last_bounds = (g.x(), g.y(), g.width(), g.height())
        super().resizeEvent(event)

    def closeEvent(self, event):
        save_bounds()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cfg = load_config()
    if "lang" in cfg:
        lang_code = cfg["lang"]
        tr = LANGUAGES.get(lang_code, LANGUAGES["en"])
    else:
        select_language(cfg)

    username = ask_if_missing(None, cfg, "username", tr["login"], tr["username"], QLineEdit.EchoMode.Normal)
    password = ask_if_missing(None, cfg, "password", tr["login"], tr["password"], QLineEdit.EchoMode.Password)
    url = ask_if_missing(None, cfg, "url", tr["title"], tr["url"], QLineEdit.EchoMode.Normal)
    title = ask_if_missing(None, cfg, "title", tr["title"], tr["app_title"], QLineEdit.EchoMode.Normal)

    cfg.update({
        "username": username,
        "password": password,
        "url": url,
        "title": title
    })
    save_config(cfg)

    tel_number = None
    if len(sys.argv) > 1 and sys.argv[1].startswith("tel:"):
        tel_number = sys.argv[1][4:]

    win = MainWindow(cfg, tel_number=tel_number)
    win.show()
    sys.exit(app.exec())
