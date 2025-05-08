# 3CX Dialer for macOS

This is a minimal macOS desktop app that embeds the 3CX web client into a native `.app` using Python and PyQt6. It supports automatic login and opens the dialer interface directly.

## 🔧 Features

- ✅ Automatically logs into your 3CX web client using stored credentials  
- ✅ Opens the dial pad UI automatically  
- ✅ Packaged as a `.dmg` app for macOS  
- ✅ No browser needed — behaves like a native macOS app  

## 🗺 Roadmap

Planned features and improvements for future versions:

- [ ] 🔗 Support for handling `tel:` links from external apps and browsers
- [ ] 🔗 Custom Icon
- [ ] 🔗 Multi Language Support
      
## 📦 How to Install

1. Download the latest `.dmg` from the [Releases](https://github.com/Migrim/3cx-Dialer/releases) section.  
2. Open the `.dmg` and drag the app to your Applications folder.  
3. The first time you open it, right-click the app and select **"Open"**, then confirm the warning. This is required because it's not notarized by Apple.

## 🧪 Usage

1. On first launch, the app will prompt you for:
   - Your 3CX extension number
   - Your password
   - The full URL to your 3CX web app (e.g. `https://pbx.company.com/webclient`)
   - A custom window title (optional)

   These will be saved securely in your `~/Documents/3cx_app/config.json` file.

2. When the app opens:
   - It auto-fills your login credentials  
   - It opens the dialer panel automatically  

> ⚠️ Gatekeeper warning is expected unless the app is notarized. Your coworker should right-click → Open → Confirm once.

## 🛠 Built With

- Python 3.11+
- PyQt6
- PyQt6-WebEngine
- Briefcase by BeeWare

## 📁 Config Storage

User configuration is stored at:

~/Documents/3cx_app/config.json

You can delete this file to reset credentials and settings.
