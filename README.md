# 3CX Dialer for macOS

A minimal macOS desktop app that embeds the 3CX web client in a native `.app` using Python + PyQt6.  
It supports automatic login, clipboard dialing, language switching, and start page selection.

## 🔧 Features

- ✅ Automatically logs into your 3CX web client using stored credentials  
- ✅ Language selection: English 🇬🇧 and German 🇩🇪  
- ✅ Start on specific 3CX subpages: Chat, Calls, Team, Contacts, Switchboard  
- ✅ Optional clipboard-to-dialer automation  
- ✅ Clean native macOS app experience (no browser needed)  
- ✅ Config reset and editing from the app menu  
- ✅ Packaged as a `.dmg` installer for easy deployment

## 📦 How to Install

1. Open the `.dmg` and drag **3CX Dialer** into your **Applications** folder.  
2. The first time you launch the app:
   - Right-click → **Open**
   - Confirm the Gatekeeper warning (required because the app is not notarized by Apple)

## 🧪 Usage

### 🛠 First Launch

You'll be prompted for:

- Your **3CX extension number**
- Your **password**
- The full **3CX web URL** (e.g. `https://pbx.company.com/webclient`)
- A **custom window title** (optional)
- Your **preferred language**
- Your **starting page** (Team, Chat, Call History, etc.)

All values are stored locally in `~/Documents/3cx_app/config.json`.

### 🚀 After Launch

- The app auto-fills your credentials and logs in after the web client loads.
- If clipboard automation is enabled, phone numbers copied to your clipboard will trigger a dial attempt.

> ⚠️ Gatekeeper warning is expected unless the app is notarized. Right-click → Open → Confirm the first time.

## 🌐 Supported Pages

You can configure the app to start on any of the following sections:

- Team
- Chat
- Call History
- Switchboard
- Contacts

## 🌍 Language Support

- English (`EN`)
- Deutsch (`DE`)

## 📁 Config & Reset

User data is stored here:

```bash
~/Documents/3cx_app/config.json
```

## 🛠 Built With

- Python 3.11+
- PyQt6
- PyQt6-WebEngine
- Briefcase by BeeWare
