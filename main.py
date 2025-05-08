import webview
import json
import os
import tkinter as tk

BASE_DIR = os.path.join(os.path.expanduser("~"), "3cx_app_data")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_credentials(pos_x=None, pos_y=None):
    cred_file = os.path.join(BASE_DIR, "credentials.json")
    if os.path.exists(cred_file):
        try:
            with open(cred_file, "r") as f:
                creds = json.load(f)
            return creds.get("username"), creds.get("password")
        except Exception:
            pass
    root = tk.Tk()
    root.withdraw()
    popup = tk.Toplevel()
    popup.title("Anmeldedaten")
    if pos_x is not None and pos_y is not None:
        popup.geometry(f"300x150+{pos_x}+{pos_y}")
    else:
        popup.geometry("300x150+100+100")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    tk.Label(popup, text="Benutzername:").pack(pady=(10, 0))
    entry_user = tk.Entry(popup, width=30)
    entry_user.pack(pady=(0, 10))
    tk.Label(popup, text="Passwort:").pack()
    entry_pass = tk.Entry(popup, width=30, show="*")
    entry_pass.pack(pady=(0, 10))
    credentials = {}
    def submit():
        credentials["username"] = entry_user.get()
        credentials["password"] = entry_pass.get()
        popup.destroy()
    tk.Button(popup, text="Speichern", command=submit).pack(pady=(10, 0))
    popup.wait_window()
    root.destroy()
    with open(cred_file, "w") as f:
        json.dump(credentials, f)
    return credentials["username"], credentials["password"]

def enhance_performance_and_disable_audio(window):
    js_code = """
    (function() {
        let audioElements = document.querySelectorAll('audio, video');
        audioElements.forEach(el => el.muted = true);
        function createDummyAudioContext() {
            return new Proxy({}, {
                get: function(target, prop) {
                    return function() {
                        console.warn('Dummy AudioContext: method ' + prop + ' called');
                    };
                }
            });
        }
        if (window.AudioContext) {
            window.AudioContext = function() {
                console.warn('AudioContext disabled');
                return createDummyAudioContext();
            };
        }
        if (window.OfflineAudioContext) {
            window.OfflineAudioContext = function() {
                console.warn('OfflineAudioContext disabled');
                return createDummyAudioContext();
            };
        }
        document.body.style.overflow = 'hidden';
        document.body.style.willChange = 'auto';
        document.body.style.transform = 'none';
    })();
    """
    window.evaluate_js(js_code)

def auto_fill_credentials(window):
    try:
        pos = window.gui.get_position(window.uid)
        pos_x, pos_y = pos if pos and len(pos) >= 2 else (100, 100)
    except Exception:
        pos_x, pos_y = (100, 100)
    username, password = get_credentials(pos_x, pos_y)
    js_code = f"""
    (function() {{
        var userField = document.querySelector('#loginInput');
        var passField = document.querySelector('#passwordInput');
        if(userField && passField) {{
            userField.value = "{username}";
            passField.value = "{password}";
        }}
        setTimeout(function() {{
            var submitBtn = document.querySelector('#submitBtn');
            if(submitBtn) {{
                submitBtn.click();
            }}
        }}, 1000);
    }})();
    """
    window.evaluate_js(js_code)

def load_window_state():
    state_file = os.path.join(BASE_DIR, "window_state.json")
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_window_state(window):
    state_file = os.path.join(BASE_DIR, "window_state.json")
    try:
        pos = window.gui.get_position(window.uid)
        x, y = pos if pos and len(pos) >= 2 else (None, None)
    except Exception:
        x, y = None, None
    try:
        size = window.gui.get_size(window.uid)
        width, height = size if size and len(size) >= 2 else (800, 600)
    except Exception:
        width, height = 800, 600
    state = {"x": x, "y": y, "width": width, "height": height}
    with open(state_file, "w") as f:
        json.dump(state, f)
    print("Window state saved:", state)

def start_app():
    state = load_window_state()
    x = state.get("x")
    y = state.get("y")
    width = state.get("width", 800)
    height = state.get("height", 600)

                                   x=x, y=y, width=width, height=height, resizable=True)
    window.events.loaded += lambda: auto_fill_credentials(window)
    window.events.closing += lambda: save_window_state(window)
    webview.start(enhance_performance_and_disable_audio, window, gui='edgechromium')

if __name__ == "__main__":
    start_app()
