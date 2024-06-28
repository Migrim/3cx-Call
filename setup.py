from setuptools import setup

APP = ['3cx.py']  # Replace with the name of your main Python file
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'includes': ['rumps', 'pyperclip', 'selenium', 'json', 'os', 'subprocess', 'time', 'threading'],  # Include all necessary modules
    'packages': ['rumps', 'selenium'],  # Ensure selenium and rumps packages are included
    'plist': {
        'CFBundleName': 'PhoneMenuBarApp',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
        'LSUIElement': True,  # Makes the app a background app (no dock icon)
    },
    'resources': ['config.json'],  # Include any other resources your app needs
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
