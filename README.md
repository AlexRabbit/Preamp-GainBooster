<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows" alt="Windows"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Open%20Source-MIT-green?style=for-the-badge" alt="Open Source"/>
</p>

<h1 align="center">🎚️ Preamp GainBooster</h1>
<p align="center">
  <strong>Virtual microphone preamp for Windows</strong><br/>
  Boost your mic gain digitally • Use in Discord, Zoom, OBS & any app
</p>

<p align="center">
  <a href="#-what-is-this">What is this?</a> •
  <a href="#-features">Features</a> •
  <a href="#-how-it-works">How it works</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-troubleshooting">Troubleshooting</a>
</p>

---

## 🎯 What is this?

**Preamp GainBooster** is a small Windows app that acts as a **digital preamp** for your microphone.  
Your mic is too quiet in Discord, Zoom, or streaming? This app **raises the volume (gain)** before the sound reaches those apps—so you sound louder and clearer everywhere, **without buying hardware**.

```
🎤 Your mic  →  [ Preamp GainBooster ]  →  🔌 Virtual cable  →  Discord / Zoom / OBS
                    ↑ you set the dB
```

### 🤔 Why use it?

| Reason | Benefit |
|--------|--------|
| 🎤 **Quiet mic** | Boost level so others hear you clearly in calls and streams |
| 🎛️ **One place** | Control gain in one app; all other apps use the same “virtual mic” |
| 💾 **Presets** | Save “Streaming”, “Quiet room”, “Podcast” and switch in one click |
| 🆓 **Free & simple** | No extra hardware, minimal files (one `.bat` + one `.py`) |

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🎚️ **Gain control** | Adjust mic level from **-6 dB to +30 dB** with slider or number box |
| 🔌 **Virtual cable** | Sends boosted audio to **VB-Cable**; any app can use it as “CABLE Output” mic |
| 🎧 **Monitor** | Optional: hear yourself in your headphones (sidetone) |
| 💾 **Presets** | Save and load gain presets by name (e.g. “Streaming”, “Quiet room”) |
| 🌍 **8 languages** | Español, English, Français, Deutsch, Português, Italiano, Русский, 中文 |
| 🖥️ **System tray** | Minimize to tray; choose on close: **Quit** or **Minimize to tray** (and remember) |
| 🚀 **Run at startup** | One click to run when Windows starts |
| 🎨 **Dark UI** | Purple cyberpunk-style theme, easy on the eyes |
| 📦 **Minimal setup** | Only **2 files**: one `.bat`, one `.py` — no `requirements.txt` |

---

## 🔄 How it works

```mermaid
flowchart LR
    subgraph Input
        A[🎤 Real microphone]
    end
    subgraph App
        B[Preamp GainBooster]
        B --> C[Apply gain in dB]
    end
    subgraph Virtual
        D[CABLE Input]
        E[CABLE Output]
    end
    subgraph Apps
        F[Discord / Zoom / OBS]
    end
    A --> B
    C --> D
    D --> E
    E --> F
```

**In short:**

1. **Preamp GainBooster** captures audio from your **real microphone**.
2. It applies the **gain (dB)** you set and sends the result to **CABLE Input** (virtual playback device).
3. **CABLE Output** (virtual recording device) is what Windows and apps see as a “microphone”.
4. In **Discord, Zoom, OBS**, etc., you select **CABLE Output** as the input device → they get your mic **already boosted**.

### 🔌 CABLE Input vs CABLE Output (no confusion)

| Name in Windows | Where you see it | What it is |
|-----------------|------------------|------------|
| **CABLE Input** | **Playback** (speakers) list | The “speaker” the app *sends* audio to. **You select this in the app as “Output”.** |
| **CABLE Output** | **Recording** (microphone) list | The “microphone” that *receives* that audio. **You select this in Discord/Zoom as “Input”.** |

So: **app → CABLE Input** … cable connects them … **CABLE Output → Discord/Zoom**. Both appear after you install [VB-Cable](https://vb-audio.com/Cable/).

### 📊 User journey (high level)

```mermaid
flowchart TD
    A[Install VB-Cable driver] --> B[Run install_and_run.bat]
    B --> C[Select mic + CABLE Input + set gain]
    C --> D[Start preamp]
    D --> E[Set CABLE Output as mic in Discord/Zoom]
    E --> F[You sound louder everywhere]
```

---

## 📋 Requirements

| Requirement | Notes |
|-------------|--------|
| 🪟 **Windows** | Tested on Windows 10/11 |
| 🐍 **Python 3.8+** | Installed automatically by the `.bat` via winget if missing |
| 🔌 **VB-Cable driver** | You must install it once from [vb-audio.com/Cable](https://vb-audio.com/Cable/) |

---

## 🚀 Quick Start

### 1️⃣ Install the virtual cable driver (one-time)

You need **VB-Cable** so that “CABLE Input” and “CABLE Output” exist in Windows.

- Download: **[VB-Cable from vb-audio.com](https://vb-audio.com/Cable/)**
- Run **VBCABLE_Setup_x64.exe** (or x86) **as Administrator**.
- Reboot if the installer asks.

### 2️⃣ Run the app

- **Double-click** `install_and_run.bat`.  
- It will install Python (via winget) if needed, install dependencies, and start the app—**no `requirements.txt`**, everything is in the batch file.

That’s it. 🎉

---

## 📖 Usage

### In the app

| Step | What to do |
|------|------------|
| 1 | **Input:** Select your **real microphone** (the one you speak into). |
| 2 | **Output:** Select **CABLE Input** (the virtual device the app sends audio to). |
| 3 | **Gain:** Set the dB you want (e.g. +6, +12, +18). Use the slider or the number box. |
| 4 | **Monitor** (optional): Enable if you want to hear yourself in your headphones; choose your **speakers/headphones** as the monitor device. |
| 5 | Click **Start preamp**. |
| 6 | In **Discord / Zoom / OBS**: set the **microphone** to **CABLE Output** (or set CABLE Output as the default **Recording** device in Windows). |

### Windows sound (microphone tab)

- Use the in-app button: **“Open Windows sound → Microphone → CABLE Output default”**.
- In **Sound settings**, open the **Microphone** (Recording) tab—**not** the Speaker tab—and set **CABLE Output** as the default device so all apps use it.

### Presets

- Set your desired gain, then click **Save** and give the preset a name.
- Later: select the preset and click **Load** to apply it.

### Closing the app (X)

- First time: you’ll be asked **Quit** or **Minimize to tray**.
- Check **“Remember my choice”** to skip the question next time.

---

## 📁 Project structure (minimal)

```
mic-preamp/
├── app.py              # Main application (all logic + UI)
├── install_and_run.bat # Install Python/deps + run app (no requirements.txt)
├── gain_presets.json   # Your saved presets (created at runtime)
└── preamp_config.json  # Close behavior: quit / tray (created at runtime)
```

**Dependencies** (installed by the `.bat`): `sounddevice`, `numpy`, `pystray`, `Pillow`.

---

## 🛠️ Troubleshooting

| Problem | What to do |
|--------|------------|
| **CABLE doesn’t appear** | Install [VB-Cable](https://vb-audio.com/Cable/) and run the installer as Administrator. Reboot if asked. |
| **No sound in Discord/Zoom** | In the app, output must be **CABLE Input**. In Discord/Zoom, **input** must be **CABLE Output**. In Windows, set **CABLE Output** as default **Recording** device (Microphone tab). |
| **Monitor sounds bad / robotic** | Monitor runs at 48 kHz for compatibility. Make sure the monitor device is your **headphones/speakers**, not CABLE Input. |
| **Python not found** | Run `install_and_run.bat`; it will try to install Python via **winget**. Or install [Python](https://www.python.org/downloads/) manually and tick “Add Python to PATH”. |

---

## 🖼️ Screenshot

> 📷 *Add a screenshot of the app here for your repo (e.g. `docs/screenshot.png`) to show the dark purple UI, device dropdowns, gain slider, and presets.*

| What you’ll see |
|-----------------|
| Dark purple “cyberpunk” theme |
| Title: **Preamp GainBooster** |
| Device lists: Input (mic), Output (CABLE Input), Monitor (headphones) |
| Gain slider + dB value + presets (Save/Load/Delete) |
| Start/Stop preamp, language selector, tray & startup options |

---

## 📜 License

Open source — use and modify as you like.

---

## 👤 Author

**AlexRabbit**  
🔗 [GitHub](https://github.com/AlexRabbit)

---

<p align="center">
  <strong>Made with 🎚️ for streamers, podcasters, and everyone who needs a bit more mic level.</strong><br/>
  <sub>If this helped you, consider starring the repo ⭐</sub>
</p>
