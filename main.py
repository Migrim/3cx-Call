import webview

def enhance_performance_and_disable_audio():
    js_code = """
    (function() {
        // Mute audio and video elements
        let audioElements = document.querySelectorAll('audio, video');
        audioElements.forEach(el => el.muted = true);

        // Create a dummy AudioContext stub to prevent errors
        function createDummyAudioContext() {
            return new Proxy({}, {
                get: function(target, prop) {
                    // Return a no-op function for any property access.
                    return function() {
                        console.warn('Dummy AudioContext: method ' + prop + ' called');
                    };
                }
            });
        }

        // Override AudioContext and OfflineAudioContext with dummy stubs
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

        // Reduce animations and rendering load
        document.body.style.willChange = 'auto';
        document.body.style.transform = 'none';
    })();
    """
    webview.windows[0].evaluate_js(js_code)

def start_app():
    window = webview.create_window("Pega Mac 3cx Client 2025 Official", "https://pegasoft-gmbh.on3cx.de:5001/", resizable=False)
    webview.start(enhance_performance_and_disable_audio, window)

if __name__ == "__main__":
    start_app()