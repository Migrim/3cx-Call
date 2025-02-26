import webview
import json
import os

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

def load_window_state():
    if os.path.exists("window_state.json"):
        try:
            with open("window_state.json", "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_window_state(window):
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
    with open("window_state.json", "w") as f:
        json.dump(state, f)
    print("Window state saved:", state)

def start_app():
    state = load_window_state()
    x = state.get("x")
    y = state.get("y")
    width = state.get("width", 800)
    height = state.get("height", 600)
    window = webview.create_window("3CX - App Client", "https://pegasoft-gmbh.on3cx.de:5001/", x=x, y=y, width=width, height=height, resizable=True)
    window.events.closing += lambda: save_window_state(window)
    webview.start(enhance_performance_and_disable_audio, window, gui='edgechromium')

if __name__ == "__main__":
    start_app()
