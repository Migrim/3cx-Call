import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit
from PyQt6.QtCore import QUrl, QRect
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

DOCS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "3cx_app")
os.makedirs(DOCS_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(DOCS_DIR, "config.json")
STATE_FILE = os.path.join(DOCS_DIR, "3cx_window_state.json")
last_bounds = None

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
        json.dump(cfg, f)

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
    def __init__(self, username, password, url, title, state, tel_number=None):
        super().__init__()
        self.setWindowTitle(title)
        self.username = username
        self.password = password
        self.url = url
        self.tel_number = tel_number
        self.setGeometry(QRect(state["x"], state["y"], state["width"], state["height"]))
        profile = QWebEngineProfile("3cx_profile", self)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setCachePath(DOCS_DIR)
        profile.setPersistentStoragePath(DOCS_DIR)
        self.view = WebView(self)
        page = QWebEnginePage(profile, self.view)
        self.view.setPage(page)
        self.setCentralWidget(self.view)
        self.view.load(QUrl(self.url))
        self.view.loadFinished.connect(self.on_load_finished)

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
    tel_number = None
    if len(sys.argv) > 1 and sys.argv[1].startswith("tel:"):
        tel_number = sys.argv[1][4:]

    app = QApplication(sys.argv)
    cfg = load_config()
    username = ask_if_missing(None, cfg, "username", "Anmeldung", "Nebenstelle:", QLineEdit.EchoMode.Normal)
    password = ask_if_missing(None, cfg, "password", "Anmeldung", "Passwort:", QLineEdit.EchoMode.Password)
    url = ask_if_missing(None, cfg, "url", "3cx Web-App URL", "3cx URL eingeben:", QLineEdit.EchoMode.Normal)
    title = ask_if_missing(None, cfg, "title", "Fenstertitel", "Titel eingeben:", QLineEdit.EchoMode.Normal)
    state = load_bounds()
    win = MainWindow(username, password, url, title, state, tel_number=tel_number)
    win.show()
    sys.exit(app.exec())
