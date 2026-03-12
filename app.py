# -*- coding: utf-8 -*-
"""
Preamp virtual para micrófono - Aplica ganancia en dB y envía al cable virtual.
Otras apps (Discord, Zoom, etc.) eligen "CABLE Output" como micrófono.
Opcional: activar "Monitor" para escucharte por los auriculares.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import numpy as np
import threading
import sys
import os
import json
import queue
import subprocess
import webbrowser

try:
    import pystray
    from PIL import Image
    _TRAY_AVAILABLE = True
except ImportError:
    _TRAY_AVAILABLE = False

VB_CABLE_DRIVER_URL = "https://vb-audio.com/Cable/"
GITHUB_URL = "https://github.com/AlexRabbit"

# Translations: natural, fluent strings per language
TRANSLATIONS = {
    "es": {
        "language": "Idioma",
        "window_title": "Micrófono",
        "refresh_devices": "Actualizar dispositivos",
        "input_label": "Entrada (micrófono)",
        "output_label": "Salida: CABLE Input",
        "output_hint": "Discord: CABLE Output como micrófono.",
        "monitor_device": "Monitor (auriculares)",
        "cable_warning": "Sin CABLE: instala driver VB-Cable (vb-audio.com/Cable).",
        "monitor_frame": "Monitor",
        "monitor_check": "Escucharte por auriculares",
        "gain_label": "Ganancia (dB)",
        "btn_start": "Iniciar preamp",
        "btn_stop": "Detener preamp",
        "tip": "Discord = CABLE Output. Windows: pestaña Micrófono (no Audífono), CABLE Output por defecto.",
        "btn_sound": "Abrir sonido Windows → Micrófono → CABLE Output por defecto",
        "status_stopped": "Detenido",
        "status_running": "Activo. Discord: CABLE Output.",
        "status_monitor_warn": "Monitor: elige auriculares, no CABLE.",
        "warn_select_devices": "Elige entrada y salida.",
        "error_start": "Error al iniciar audio",
        "error_monitor": "Error al iniciar monitor",
        "error_devices": "Error al listar dispositivos",
        "info_sound": "Sonido Windows → CABLE Output por defecto (micrófono).",
        "driver_link": "Driver VB-Cable",
        "run_at_startup": "Al iniciar Windows",
        "input_hint": "CABLE Output aparece aquí si está instalado.",
        "presets_frame": "Presets",
        "save_preset": "Guardar",
        "load_preset": "Cargar",
        "delete_preset": "Eliminar",
        "preset_name_prompt": "Nombre:",
        "preset_saved": "Guardado.",
        "github_link": "GitHub: AlexRabbit",
    },
    "en": {
        "language": "Language",
        "window_title": "Microphone",
        "refresh_devices": "Refresh devices",
        "input_label": "Input (mic)",
        "output_label": "Output: CABLE Input",
        "output_hint": "Discord: CABLE Output as mic.",
        "monitor_device": "Monitor (headphones)",
        "cable_warning": "No CABLE: install VB-Cable driver (vb-audio.com/Cable).",
        "monitor_frame": "Monitor",
        "monitor_check": "Hear yourself in headphones",
        "gain_label": "Gain (dB)",
        "btn_start": "Start preamp",
        "btn_stop": "Stop preamp",
        "tip": "Discord = CABLE Output. Windows: Microphone tab (not Speaker), set CABLE Output default.",
        "btn_sound": "Open Windows sound → Microphone → CABLE Output default",
        "status_stopped": "Stopped",
        "status_running": "Active. Discord: CABLE Output.",
        "status_monitor_warn": "Monitor: pick headphones, not CABLE.",
        "warn_select_devices": "Pick input and output.",
        "error_start": "Failed to start audio",
        "error_monitor": "Failed to start monitor",
        "error_devices": "Failed to list devices",
        "info_sound": "Windows sound → CABLE Output default (microphone).",
        "driver_link": "VB-Cable driver",
        "run_at_startup": "Run at Windows start",
        "input_hint": "CABLE Output shows here if installed.",
        "presets_frame": "Presets",
        "save_preset": "Save",
        "load_preset": "Load",
        "delete_preset": "Delete",
        "preset_name_prompt": "Name:",
        "preset_saved": "Saved.",
        "github_link": "GitHub: AlexRabbit",
    },
    "fr": {
        "language": "Langue",
        "window_title": "Préampli virtuel - Micro",
        "refresh_devices": "Actualiser",
        "input_label": "Entrée (micro)",
        "output_label": "Sortie (ici dans l’app) : sélectionne CABLE Input",
        "output_hint": "Dans Discord et autres apps tu DOIS choisir CABLE Output comme micro.",
        "monitor_device": "Monitor : sélectionne tes enceintes ou écouteurs corrects",
        "cable_warning": "CABLE absent : installe d’abord le pilote VB-Cable (https://vb-audio.com/Cable/). Sans lui, Discord ne peut pas utiliser le préampli en entrée.",
        "monitor_frame": "Écoute (s’entendre)",
        "monitor_check": "Activer le monitor : entendre le micro dans les écouteurs",
        "gain_label": "Gain (dB) :",
        "btn_start": "Démarrer le préampli",
        "btn_stop": "Arrêter le préampli",
        "tip": "Pour Discord et autres apps : choisis « CABLE Output » comme micro. Dans Windows, dans la zone micro (pas haut-parleurs), définis CABLE Output par défaut.",
        "btn_sound": "Ouvrir le son Windows : zone micro (pas haut-parleurs), CABLE Output par défaut",
        "status_stopped": "Arrêté",
        "status_running": "Préampli actif. Dans les autres apps, utilise « CABLE Output » comme micro.",
        "status_monitor_warn": "Préampli actif. Monitor : choisis les écouteurs, pas CABLE Input.",
        "warn_select_devices": "Sélectionne les périphériques d’entrée et de sortie.",
        "error_start": "Impossible de démarrer le flux audio",
        "error_monitor": "Impossible de démarrer le monitor",
        "error_devices": "Impossible de lister les périphériques",
        "info_sound": "Ouvre les paramètres son du système et choisis CABLE Output comme entrée par défaut.",
        "driver_link": "Pilote VB-Cable",
        "run_at_startup": "Démarrer avec Windows",
        "input_hint": "CABLE Output (pour Discord) apparaît ici en entrée si installé.",
        "presets_frame": "Préréglages de gain",
        "save_preset": "Enregistrer",
        "load_preset": "Charger",
        "delete_preset": "Supprimer",
        "preset_name_prompt": "Nom du préréglage :",
        "preset_saved": "Préréglage enregistré.",
        "github_link": "GitHub: AlexRabbit",
    },
    "de": {
        "language": "Sprache",
        "window_title": "Mikrofon",
        "refresh_devices": "Aktualisieren",
        "input_label": "Eingang (Mikro)",
        "output_label": "Ausgang: CABLE Input",
        "output_hint": "Discord: CABLE Output als Mikro.",
        "monitor_device": "Monitor (Kopfhörer)",
        "cable_warning": "Kein CABLE: VB-Cable-Treiber installieren (vb-audio.com/Cable).",
        "monitor_frame": "Monitor",
        "monitor_check": "Sich in Kopfhörern hören",
        "gain_label": "Verstärkung (dB)",
        "btn_start": "Starten",
        "btn_stop": "Stoppen",
        "tip": "Discord = CABLE Output. Windows: Mikrofon (nicht Lautsprecher), CABLE Output Standard.",
        "btn_sound": "Windows-Sound → Mikrofon → CABLE Output Standard",
        "status_stopped": "Gestoppt",
        "status_running": "Aktiv. Discord: CABLE Output.",
        "status_monitor_warn": "Monitor: Kopfhörer, nicht CABLE.",
        "warn_select_devices": "Eingabe und Ausgabe wählen.",
        "error_start": "Audio starten fehlgeschlagen",
        "error_monitor": "Monitor starten fehlgeschlagen",
        "error_devices": "Geräte auflisten fehlgeschlagen",
        "info_sound": "Windows-Sound → CABLE Output Standard (Mikrofon).",
        "driver_link": "VB-Cable-Treiber",
        "run_at_startup": "Mit Windows starten",
        "input_hint": "CABLE Output erscheint hier wenn installiert.",
        "presets_frame": "Presets",
        "save_preset": "Speichern",
        "load_preset": "Laden",
        "delete_preset": "Löschen",
        "preset_name_prompt": "Name:",
        "preset_saved": "Gespeichert.",
        "github_link": "GitHub: AlexRabbit",
    },
    "pt": {
        "language": "Idioma",
        "window_title": "Microfone",
        "refresh_devices": "Atualizar",
        "input_label": "Entrada (microfone)",
        "output_label": "Saída: CABLE Input",
        "output_hint": "Discord: CABLE Output como microfone.",
        "monitor_device": "Monitor (auscultadores)",
        "cable_warning": "Sem CABLE: instala driver VB-Cable (vb-audio.com/Cable).",
        "monitor_frame": "Monitor",
        "monitor_check": "Ouvir-te nos auscultadores",
        "gain_label": "Ganho (dB)",
        "btn_start": "Iniciar",
        "btn_stop": "Parar",
        "tip": "Discord = CABLE Output. Windows: Microfone (não Colunas), CABLE Output padrão.",
        "btn_sound": "Som Windows → Microfone → CABLE Output padrão",
        "status_stopped": "Parado",
        "status_running": "Ativo. Discord: CABLE Output.",
        "status_monitor_warn": "Monitor: auscultadores, não CABLE.",
        "warn_select_devices": "Escolhe entrada e saída.",
        "error_start": "Erro ao iniciar áudio",
        "error_monitor": "Erro ao iniciar monitor",
        "error_devices": "Erro ao listar dispositivos",
        "info_sound": "Som Windows → CABLE Output padrão (microfone).",
        "driver_link": "Driver VB-Cable",
        "run_at_startup": "Ao iniciar Windows",
        "input_hint": "CABLE Output aparece aqui se instalado.",
        "presets_frame": "Presets",
        "save_preset": "Guardar",
        "load_preset": "Carregar",
        "delete_preset": "Eliminar",
        "preset_name_prompt": "Nome:",
        "preset_saved": "Guardado.",
        "github_link": "GitHub: AlexRabbit",
    },
    "it": {
        "language": "Lingua",
        "window_title": "Microfono",
        "refresh_devices": "Aggiorna",
        "input_label": "Ingresso (microfono)",
        "output_label": "Uscita: CABLE Input",
        "output_hint": "Discord: CABLE Output come microfono.",
        "monitor_device": "Monitor (cuffie)",
        "cable_warning": "Nessun CABLE: installa driver VB-Cable (vb-audio.com/Cable).",
        "monitor_frame": "Monitor",
        "monitor_check": "Sentirti nelle cuffie",
        "gain_label": "Guadagno (dB)",
        "btn_start": "Avvia",
        "btn_stop": "Ferma",
        "tip": "Discord = CABLE Output. Windows: Microfono (non Altoparlanti), CABLE Output predefinito.",
        "btn_sound": "Audio Windows → Microfono → CABLE Output predefinito",
        "status_stopped": "Fermato",
        "status_running": "Attivo. Discord: CABLE Output.",
        "status_monitor_warn": "Monitor: cuffie, non CABLE.",
        "warn_select_devices": "Scegli ingresso e uscita.",
        "error_start": "Errore avvio audio",
        "error_monitor": "Errore avvio monitor",
        "error_devices": "Errore elenco dispositivi",
        "info_sound": "Audio Windows → CABLE Output predefinito (microfono).",
        "driver_link": "Driver VB-Cable",
        "run_at_startup": "All'avvio di Windows",
        "input_hint": "CABLE Output appare qui se installato.",
        "presets_frame": "Presets",
        "save_preset": "Salva",
        "load_preset": "Carica",
        "delete_preset": "Elimina",
        "preset_name_prompt": "Nome:",
        "preset_saved": "Salvato.",
        "github_link": "GitHub: AlexRabbit",
    },
    "ru": {
        "language": "Язык",
        "window_title": "Микрофон",
        "refresh_devices": "Обновить",
        "input_label": "Вход (микрофон)",
        "output_label": "Выход: CABLE Input",
        "output_hint": "Discord: CABLE Output как микрофон.",
        "monitor_device": "Монитор (наушники)",
        "cable_warning": "Нет CABLE: установите драйвер VB-Cable (vb-audio.com/Cable).",
        "monitor_frame": "Монитор",
        "monitor_check": "Слышать себя в наушниках",
        "gain_label": "Усиление (дБ)",
        "btn_start": "Запустить",
        "btn_stop": "Остановить",
        "tip": "Discord = CABLE Output. Windows: вкладка Микрофон (не Динамики), CABLE Output по умолчанию.",
        "btn_sound": "Звук Windows → Микрофон → CABLE Output по умолчанию",
        "status_stopped": "Остановлен",
        "status_running": "Активен. Discord: CABLE Output.",
        "status_monitor_warn": "Монитор: наушники, не CABLE.",
        "warn_select_devices": "Выберите вход и выход.",
        "error_start": "Ошибка запуска аудио",
        "error_monitor": "Ошибка запуска монитора",
        "error_devices": "Ошибка списка устройств",
        "info_sound": "Звук Windows → CABLE Output по умолчанию (микрофон).",
        "driver_link": "Драйвер VB-Cable",
        "run_at_startup": "При запуске Windows",
        "input_hint": "CABLE Output отображается здесь если установлен.",
        "presets_frame": "Пресеты",
        "save_preset": "Сохранить",
        "load_preset": "Загрузить",
        "delete_preset": "Удалить",
        "preset_name_prompt": "Имя:",
        "preset_saved": "Сохранено.",
        "github_link": "GitHub: AlexRabbit",
    },
    "zh": {
        "language": "语言",
        "window_title": "麦克风",
        "refresh_devices": "刷新",
        "input_label": "输入（麦克风）",
        "output_label": "输出：CABLE Input",
        "output_hint": "Discord：选 CABLE Output 为麦克风。",
        "monitor_device": "监听（耳机）",
        "cable_warning": "无 CABLE：安装 VB-Cable 驱动 (vb-audio.com/Cable)。",
        "monitor_frame": "监听",
        "monitor_check": "耳机中听自己",
        "gain_label": "增益（dB）",
        "btn_start": "启动",
        "btn_stop": "停止",
        "tip": "Discord = CABLE Output。Windows：麦克风（非扬声器），CABLE Output 默认。",
        "btn_sound": "Windows 声音 → 麦克风 → CABLE Output 默认",
        "status_stopped": "已停止",
        "status_running": "运行中。Discord：CABLE Output。",
        "status_monitor_warn": "监听：选耳机，勿选 CABLE。",
        "warn_select_devices": "请选输入和输出。",
        "error_start": "启动音频失败",
        "error_monitor": "启动监听失败",
        "error_devices": "列出设备失败",
        "info_sound": "Windows 声音 → CABLE Output 默认（麦克风）。",
        "driver_link": "VB-Cable 驱动",
        "run_at_startup": "开机时运行",
        "input_hint": "若已安装，CABLE Output 会显示在此。",
        "presets_frame": "预设",
        "save_preset": "保存",
        "load_preset": "加载",
        "delete_preset": "删除",
        "preset_name_prompt": "名称：",
        "preset_saved": "已保存。",
        "github_link": "GitHub: AlexRabbit",
    },
}
LANG_NAMES = {"es": "Español", "en": "English", "fr": "Français", "de": "Deutsch", "pt": "Português", "it": "Italiano", "ru": "Русский", "zh": "中文"}

# Maximum quality: 96 kHz, float32, no resampling (raw gain only)
SAMPLE_RATE = 96000
BLOCK_SIZE = 512
CHANNELS = 1
MONITOR_QUEUE_MAX = 8
# Monitor runs at 48 kHz for better compatibility with playback devices (avoids robotic sound)
MONITOR_RATE = 48000


def db_to_linear(db: float) -> float:
    """Convierte decibeles a factor lineal (ganancia)."""
    return float(10 ** (db / 20.0))


def get_device_list():
    """
    List unique input (recording) and output (playback) devices by name.
    One entry per device name so the list matches the actual number of devices (no duplicates).
    """
    devices = sd.query_devices()
    seen_in, seen_out = set(), set()
    inputs, outputs = [], []
    for i, d in enumerate(devices):
        name = (d.get("name") or "").strip()
        if not name:
            continue
        if d["max_input_channels"] > 0 and name not in seen_in:
            seen_in.add(name)
            inputs.append((i, name))
        if d["max_output_channels"] > 0 and name not in seen_out:
            seen_out.add(name)
            outputs.append((i, name))
    inputs.sort(key=lambda x: x[1].lower())
    outputs.sort(key=lambda x: x[1].lower())
    return inputs, outputs


# Dark purple cyberpunk theme (darker); borders darker than bg
THEME_BG = "#050208"
THEME_FG = "#a78bfa"
THEME_ACCENT = "#7c3aed"
THEME_FRAME = "#0f0618"
THEME_BUTTON_BG = "#1e0a2e"
THEME_ENTRY_BG = "#0a0312"
THEME_BORDER = "#030105"
APP_TITLE = "Preamp GainBooster"
# Cyberpunk-style font (Consolas = tech/mono on Windows)
FONT_FAMILY = "Consolas"
FONT_SIZE = 9
FONT_TITLE_SIZE = 16


class PreampApp:
    def __init__(self):
        self.root = tk.Tk()
        self._lang = "es"
        self.root.minsize(440, 420)
        self.root.resizable(True, True)
        self.root.configure(bg=THEME_BG)
        self._apply_theme()
        self._apply_combobox_dark()

        self.stream = None
        self.monitor_stream = None
        self._gain_db = 0.0
        self._gain_linear = 1.0
        self._running = False
        self._monitor_enabled = False
        self._lock = threading.Lock()
        self._monitor_queue = queue.Queue(maxsize=MONITOR_QUEUE_MAX)
        self._sample_rate = SAMPLE_RATE  # 96k preferred; fallback to 48k if needed
        self._monitor_last_block = None  # hold last block to avoid robotic dropouts
        self._tray_icon = None
        self._startup_bat_name = "PreampVirtual_Startup.bat"
        self._presets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gain_presets.json")
        self._config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preamp_config.json")
        self._presets = []  # list of {"name": str, "gain_db": float}

        self._build_ui()
        self._load_presets_file()
        self._refresh_presets_combo()
        self._refresh_devices()
        self.root.title(APP_TITLE + " - " + self._t("window_title"))
        self.combo_lang.set(LANG_NAMES[self._lang])

    def _apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.root.option_add("*HighlightBackground", THEME_BORDER)
        self.root.option_add("*HighlightColor", THEME_BORDER)
        self.root.option_add("*Background", THEME_FRAME)
        style.configure(".", background=THEME_FRAME, foreground=THEME_FG, fieldbackground=THEME_ENTRY_BG, font=(FONT_FAMILY, FONT_SIZE))
        style.configure("TFrame", background=THEME_FRAME)
        style.configure("TLabel", background=THEME_FRAME, foreground=THEME_FG, font=(FONT_FAMILY, FONT_SIZE))
        style.configure("TLabelframe", background=THEME_FRAME, foreground=THEME_ACCENT, bordercolor=THEME_BORDER)
        style.configure("TLabelframe.Label", background=THEME_FRAME, foreground=THEME_ACCENT, font=(FONT_FAMILY, FONT_SIZE, "bold"))
        style.configure("TButton", background=THEME_BUTTON_BG, foreground=THEME_FG, font=(FONT_FAMILY, FONT_SIZE), bordercolor=THEME_BORDER)
        style.map("TButton", background=[("active", THEME_ACCENT), ("pressed", THEME_ACCENT)], bordercolor=[("active", THEME_BORDER), ("pressed", THEME_BORDER)])
        style.configure("TCheckbutton", background=THEME_FRAME, foreground=THEME_FG, font=(FONT_FAMILY, FONT_SIZE))
        style.configure("TCombobox", fieldbackground=THEME_ENTRY_BG, background=THEME_FRAME, foreground=THEME_FG, arrowcolor=THEME_FG, bordercolor=THEME_BORDER, font=(FONT_FAMILY, FONT_SIZE))
        style.map("TCombobox", fieldbackground=[("readonly", THEME_ENTRY_BG)], background=[("readonly", THEME_FRAME)], foreground=[("readonly", THEME_FG)], bordercolor=[("readonly", THEME_BORDER)])
        style.configure("TSpinbox", fieldbackground=THEME_ENTRY_BG, background=THEME_FRAME, foreground=THEME_FG, bordercolor=THEME_BORDER, font=(FONT_FAMILY, FONT_SIZE))
        style.configure("TScale", background=THEME_FRAME)
        style.configure("Horizontal.TScale", background=THEME_FRAME, troughcolor=THEME_ENTRY_BG, bordercolor=THEME_BORDER)
        style.configure("TSeparator", background=THEME_ACCENT)

    def _apply_combobox_dark(self):
        """Dark dropdown list so text is readable (no white stripes)."""
        self.root.option_add("*Listbox*Background", THEME_ENTRY_BG)
        self.root.option_add("*Listbox*Foreground", THEME_FG)
        self.root.option_add("*Listbox*selectBackground", THEME_ACCENT)
        self.root.option_add("*Listbox*selectForeground", THEME_FG)

    def _t(self, key):
        return TRANSLATIONS.get(self._lang, TRANSLATIONS["es"]).get(key, key)

    def _on_language_change(self):
        try:
            name = self.combo_lang.get()
            for code, n in LANG_NAMES.items():
                if n == name:
                    self._lang = code
                    break
        except (tk.TclError, KeyError):
            return
        self.root.title(APP_TITLE + " - " + self._t("window_title"))
        self.btn_refresh["text"] = self._t("refresh_devices")
        self.label_input["text"] = self._t("input_label")
        self.label_output["text"] = self._t("output_label")
        if hasattr(self, "label_output_hint"):
            self.label_output_hint["text"] = self._t("output_hint")
        if hasattr(self, "label_monitor_dev"):
            self.label_monitor_dev["text"] = self._t("monitor_device")
        self.monitor_frame["text"] = self._t("monitor_frame")
        self.check_monitor["text"] = self._t("monitor_check")
        self.label_monitor_dev["text"] = self._t("monitor_device")
        self.label_gain["text"] = self._t("gain_label")
        self.btn_toggle["text"] = self._t("btn_stop") if self._running else self._t("btn_start")
        self.tip_label["text"] = self._t("tip")
        self.btn_sound["text"] = self._t("btn_sound")
        self.status["text"] = self._t("status_running") if self._running else self._t("status_stopped")
        if hasattr(self, "label_cable_warning") and self.label_cable_warning["text"]:
            self.label_cable_warning["text"] = self._t("cable_warning")
        if hasattr(self, "check_startup"):
            self.check_startup["text"] = self._t("run_at_startup")
        if hasattr(self, "link_driver"):
            self.link_driver["text"] = self._t("driver_link")
        if hasattr(self, "label_input_hint"):
            self.label_input_hint["text"] = self._t("input_hint")
        if hasattr(self, "preset_frame"):
            self.preset_frame["text"] = self._t("presets_frame")
        if hasattr(self, "link_github"):
            self.link_github["text"] = self._t("github_link")

    def _on_device_change(self):
        if not self._running:
            return
        self._stop_stream()
        self._start_stream()
        if self._monitor_enabled:
            self._start_monitor_stream()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # App title at very top
        title_label = ttk.Label(main, text=APP_TITLE, font=(FONT_FAMILY, FONT_TITLE_SIZE, "bold"), foreground=THEME_ACCENT)
        title_label.pack(anchor=tk.CENTER, pady=(0, 12))

        # Language selector
        lang_frame = ttk.Frame(main)
        lang_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(lang_frame, text=self._t("language") + ":").pack(side=tk.LEFT, padx=(0, 6))
        self.combo_lang = ttk.Combobox(lang_frame, state="readonly", width=14, values=list(LANG_NAMES.values()))
        self.combo_lang.pack(side=tk.LEFT)
        self.combo_lang.bind("<<ComboboxSelected>>", lambda e: self._on_language_change())

        self.btn_refresh = ttk.Button(main, text=self._t("refresh_devices"), command=self._refresh_devices)
        self.btn_refresh.pack(anchor=tk.W, pady=(0, 8))

        self.label_input = ttk.Label(main, text=self._t("input_label"))
        self.label_input.pack(anchor=tk.W)
        self.combo_input = ttk.Combobox(main, state="readonly", width=52)
        self.combo_input.pack(fill=tk.X, pady=(0, 2))
        self.label_input_hint = ttk.Label(main, text=self._t("input_hint"), font=(FONT_FAMILY, FONT_SIZE - 1), foreground=THEME_FG, wraplength=420)
        self.label_input_hint.pack(anchor=tk.W, pady=(0, 4))
        self.combo_input.bind("<<ComboboxSelected>>", lambda e: self._on_device_change())

        self.label_output = ttk.Label(main, text=self._t("output_label"))
        self.label_output.pack(anchor=tk.W)
        self.combo_output = ttk.Combobox(main, state="readonly", width=52)
        self.combo_output.pack(fill=tk.X, pady=(0, 2))
        self.label_output_hint = ttk.Label(main, text=self._t("output_hint"), font=(FONT_FAMILY, FONT_SIZE - 1), foreground=THEME_FG, wraplength=420)
        self.label_output_hint.pack(anchor=tk.W, pady=(0, 4))
        self.combo_output.bind("<<ComboboxSelected>>", lambda e: self._on_device_change())
        self.label_cable_warning = ttk.Label(main, text="", font=(FONT_FAMILY, FONT_SIZE - 1), foreground="#f87171", wraplength=420)
        self.label_cable_warning.pack(anchor=tk.W, pady=(0, 8))

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Monitor
        self.monitor_frame = ttk.LabelFrame(main, text=self._t("monitor_frame"), padding=6)
        self.monitor_frame.pack(fill=tk.X, pady=(0, 8))
        self.var_monitor = tk.BooleanVar(value=False)
        self.check_monitor = ttk.Checkbutton(
            self.monitor_frame, text=self._t("monitor_check"),
            variable=self.var_monitor, command=self._on_monitor_toggle
        )
        self.check_monitor.pack(anchor=tk.W)
        self.label_monitor_dev = ttk.Label(self.monitor_frame, text=self._t("monitor_device"))
        self.label_monitor_dev.pack(anchor=tk.W)
        self.combo_monitor = ttk.Combobox(self.monitor_frame, state="readonly", width=50)
        self.combo_monitor.pack(fill=tk.X, pady=(2, 0))
        self.combo_monitor.bind("<<ComboboxSelected>>", lambda e: self._on_device_change())

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        self.label_gain = ttk.Label(main, text=self._t("gain_label"))
        self.label_gain.pack(anchor=tk.W)
        gain_frame = ttk.Frame(main)
        gain_frame.pack(fill=tk.X, pady=(0, 4))
        self.label_db = ttk.Label(gain_frame, text="0.0 dB", width=8)
        self.label_db.pack(side=tk.RIGHT, padx=(8, 0))
        self.spin_db = ttk.Spinbox(main, from_=-6, to=30, width=8, command=self._on_spin)
        self.spin_db.insert(0, "0")
        self.spin_db.bind("<Return>", lambda e: self._on_spin())
        self.spin_db.bind("<FocusOut>", lambda e: self._on_spin())
        self.spin_db.pack(anchor=tk.W, pady=(0, 4))
        self.slider = ttk.Scale(gain_frame, from_=-6, to=30, orient=tk.HORIZONTAL, length=280, command=self._on_slider)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.slider.set(0)

        # Gain presets
        self.preset_frame = ttk.LabelFrame(main, text=self._t("presets_frame"), padding=6)
        self.preset_frame.pack(fill=tk.X, pady=(8, 4))
        preset_row = ttk.Frame(self.preset_frame)
        preset_row.pack(fill=tk.X)
        self.combo_presets = ttk.Combobox(preset_row, state="readonly", width=28)
        self.combo_presets.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(preset_row, text=self._t("save_preset"), command=self._save_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_row, text=self._t("load_preset"), command=self._load_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_row, text=self._t("delete_preset"), command=self._delete_preset).pack(side=tk.LEFT, padx=2)
        self._refresh_presets_combo()

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        btn_center = ttk.Frame(main)
        btn_center.pack(fill=tk.X, pady=(0, 6))
        self.btn_toggle = ttk.Button(btn_center, text=self._t("btn_start"), command=self._toggle_stream)
        self.btn_toggle.pack(anchor=tk.CENTER)

        self.tip_label = ttk.Label(main, text=self._t("tip"), font=(FONT_FAMILY, FONT_SIZE - 1), foreground=THEME_FG, wraplength=400)
        self.tip_label.pack(anchor=tk.W)
        self.btn_sound = ttk.Button(main, text=self._t("btn_sound"), command=self._open_sound_settings)
        self.btn_sound.pack(anchor=tk.W, pady=(6, 4))
        self.status = ttk.Label(main, text=self._t("status_stopped"), foreground=THEME_FG)
        self.status.pack(anchor=tk.W, pady=(8, 0))

        # Bottom row: GitHub (left), Run at startup, Driver link (right)
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=(12, 0))
        self.link_github = ttk.Label(bottom, text=self._t("github_link"), foreground=THEME_ACCENT, cursor="hand2")
        self.link_github.pack(side=tk.LEFT)
        self.link_github.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))
        self.var_run_at_startup = tk.BooleanVar(value=self._get_run_at_startup())
        self.check_startup = ttk.Checkbutton(
            bottom, text=self._t("run_at_startup"),
            variable=self.var_run_at_startup, command=self._on_run_at_startup_toggle
        )
        self.check_startup.pack(side=tk.LEFT, padx=(20, 0))
        self.link_driver = ttk.Label(bottom, text=self._t("driver_link"), foreground=THEME_ACCENT, cursor="hand2")
        self.link_driver.pack(side=tk.RIGHT)
        self.link_driver.bind("<Button-1>", lambda e: webbrowser.open(VB_CABLE_DRIVER_URL))

    def _get_run_at_startup(self):
        startup = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
        bat_path = os.path.join(startup, self._startup_bat_name)
        return os.path.isfile(bat_path)

    def _on_run_at_startup_toggle(self):
        startup = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
        bat_path = os.path.join(startup, self._startup_bat_name)
        app_dir = os.path.dirname(os.path.abspath(__file__))
        if self.var_run_at_startup.get():
            try:
                with open(bat_path, "w") as f:
                    f.write("@echo off\r\ncd /d \"%s\"\r\npythonw \"%s\"\r\n" % (app_dir, os.path.join(app_dir, "app.py")))
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
                self.var_run_at_startup.set(False)
        else:
            try:
                if os.path.isfile(bat_path):
                    os.remove(bat_path)
            except Exception:
                pass

    def _load_presets_file(self):
        try:
            if os.path.isfile(self._presets_file):
                with open(self._presets_file, "r", encoding="utf-8") as f:
                    self._presets = json.load(f)
                if not isinstance(self._presets, list):
                    self._presets = []
            else:
                self._presets = []
        except Exception:
            self._presets = []

    def _save_presets_file(self):
        try:
            with open(self._presets_file, "w", encoding="utf-8") as f:
                json.dump(self._presets, f, indent=2)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _refresh_presets_combo(self):
        names = [p["name"] for p in self._presets]
        self.combo_presets["values"] = names
        if names:
            self.combo_presets.current(0)
        else:
            self.combo_presets.set("")

    def _save_preset(self):
        from tkinter import simpledialog
        name = simpledialog.askstring(self._t("save_preset"), self._t("preset_name_prompt"), parent=self.root)
        if not (name and name.strip()):
            return
        name = name.strip()
        gain = round(self._gain_db, 1)
        for p in self._presets:
            if p["name"] == name:
                p["gain_db"] = gain
                self._save_presets_file()
                self._refresh_presets_combo()
                messagebox.showinfo("", self._t("preset_saved"))
                return
        self._presets.append({"name": name, "gain_db": gain})
        self._save_presets_file()
        self._refresh_presets_combo()
        messagebox.showinfo("", self._t("preset_saved"))

    def _load_preset(self):
        sel = self.combo_presets.current()
        if sel < 0 or sel >= len(self._presets):
            return
        p = self._presets[sel]
        db = max(-6, min(30, float(p["gain_db"])))
        self._gain_db = db
        with self._lock:
            self._gain_linear = db_to_linear(db)
        if hasattr(self, "slider"):
            self.slider.set(db)
        if hasattr(self, "spin_db"):
            self.spin_db.delete(0, tk.END)
            self.spin_db.insert(0, str(db))
        if hasattr(self, "label_db"):
            self.label_db["text"] = f"{db} dB"

    def _delete_preset(self):
        sel = self.combo_presets.current()
        if sel < 0 or sel >= len(self._presets):
            return
        del self._presets[sel]
        self._save_presets_file()
        self._refresh_presets_combo()

    def _open_sound_settings(self):
        """Abre la configuración de sonido de Windows para poner CABLE Output como micrófono por defecto."""
        try:
            if sys.platform == "win32":
                subprocess.Popen("mmsys.cpl", shell=True)
            else:
                messagebox.showinfo("Info", self._t("info_sound"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_devices(self):
        try:
            inputs, outputs = get_device_list()
            self._input_devices = inputs
            self._output_devices = outputs
            self.combo_input["values"] = [d[1] for d in inputs]
            self.combo_output["values"] = [d[1] for d in outputs]
            self.combo_monitor["values"] = [d[1] for d in outputs]
            if inputs:
                self.combo_input.current(0)
            if outputs:
                self.combo_output.current(0)
                self.combo_monitor.current(0)
            # Avisar si no hay ningún "CABLE" (driver del cable virtual no instalado)
            has_cable = any("CABLE" in d[1].upper() for d in outputs)
            if not has_cable:
                self.label_cable_warning["text"] = self._t("cable_warning")
            else:
                self.label_cable_warning["text"] = ""
        except Exception as e:
            messagebox.showerror("Error", f"{self._t('error_devices')}:\n{e}")

    def _on_monitor_toggle(self):
        self._monitor_enabled = self.var_monitor.get()
        if not self._running:
            return
        if self._monitor_enabled:
            self._start_monitor_stream()
        else:
            self._stop_monitor_stream()

    def _on_slider(self, value):
        try:
            db = round(float(value), 1)
            self._gain_db = db
            with self._lock:
                self._gain_linear = db_to_linear(db)
            if hasattr(self, "label_db"):
                self.label_db["text"] = f"{db} dB"
            if hasattr(self, "spin_db"):
                self.spin_db.delete(0, tk.END)
                self.spin_db.insert(0, str(db))
        except ValueError:
            pass

    def _on_spin(self):
        try:
            db = float(self.spin_db.get())
            db = max(-6, min(30, db))
            self._gain_db = db
            with self._lock:
                self._gain_linear = db_to_linear(db)
            if hasattr(self, "slider"):
                self.slider.set(db)
            if hasattr(self, "label_db"):
                self.label_db["text"] = f"{db} dB"
        except (ValueError, tk.TclError):
            pass

    def _audio_callback(self, indata, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        with self._lock:
            g = self._gain_linear
        # Raw gain only, no filters; float32 for max quality
        block = (indata * g).astype(np.float32)
        np.clip(block, -1.0, 1.0, out=block)
        outdata[:] = block
        if self._monitor_enabled and self.monitor_stream is not None:
            to_put = block
            if self._sample_rate == 96000:
                to_put = block[::2].astype(np.float32)  # downsample 96k -> 48k for monitor
            try:
                self._monitor_queue.put_nowait(to_put.copy())
            except queue.Full:
                try:
                    self._monitor_queue.get_nowait()
                    self._monitor_queue.put_nowait(to_put.copy())
                except (queue.Empty, queue.Full):
                    pass

    def _monitor_callback(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        try:
            block = self._monitor_queue.get_nowait()
            self._monitor_last_block = block
            outdata[:] = block
        except queue.Empty:
            if self._monitor_last_block is not None and len(self._monitor_last_block) >= frames:
                outdata[:] = self._monitor_last_block[:frames]
            else:
                outdata.fill(0)

    def _toggle_stream(self):
        if self._running:
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self):
        if not self._input_devices or not self._output_devices:
            messagebox.showwarning("Aviso", self._t("warn_select_devices"))
            return
        try:
            in_idx = self._input_devices[self.combo_input.current()][0]
            out_idx = self._output_devices[self.combo_output.current()][0]
        except (IndexError, tk.TclError):
            messagebox.showwarning("Aviso", self._t("warn_select_devices"))
            return

        for rate in (SAMPLE_RATE, 48000):
            try:
                self._sample_rate = rate
                self.stream = sd.Stream(
                    device=(in_idx, out_idx),
                    samplerate=rate,
                    blocksize=BLOCK_SIZE,
                    channels=(CHANNELS, CHANNELS),
                    callback=self._audio_callback,
                    dtype=np.float32,
                )
                self.stream.start()
                self._running = True
                if self._monitor_enabled:
                    self._start_monitor_stream()
                self.btn_toggle["text"] = self._t("btn_stop")
                self.status["text"] = self._t("status_running")
                self.status["foreground"] = "green"
                break
            except Exception as e:
                if rate == 48000:
                    messagebox.showerror("Error", f"{self._t('error_start')}:\n{e}")
                continue

    def _start_monitor_stream(self):
        if not self._output_devices or not self._running:
            return
        try:
            mon_idx = self._output_devices[self.combo_monitor.current()][0]
            out_idx = self._output_devices[self.combo_output.current()][0]
            if mon_idx == out_idx:
                self.status["text"] = self._t("status_monitor_warn")
                return
        except (IndexError, tk.TclError):
            return
        try:
            while not self._monitor_queue.empty():
                try:
                    self._monitor_queue.get_nowait()
                except queue.Empty:
                    break
            self._monitor_last_block = None
            monitor_blocksize = BLOCK_SIZE // 2 if self._sample_rate == 96000 else BLOCK_SIZE
            self.monitor_stream = sd.OutputStream(
                device=mon_idx,
                samplerate=MONITOR_RATE,
                blocksize=monitor_blocksize,
                channels=CHANNELS,
                callback=self._monitor_callback,
                dtype=np.float32,
            )
            self.monitor_stream.start()
        except Exception as e:
            self.var_monitor.set(False)
            self._monitor_enabled = False
            messagebox.showerror("Error", f"{self._t('error_monitor')}:\n{e}")

    def _stop_monitor_stream(self):
        if self.monitor_stream:
            try:
                self.monitor_stream.stop()
                self.monitor_stream.close()
            except Exception:
                pass
            self.monitor_stream = None
        while not self._monitor_queue.empty():
            try:
                self._monitor_queue.get_nowait()
            except queue.Empty:
                break

    def _stop_stream(self):
        self._running = False
        self._stop_monitor_stream()
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        self.btn_toggle["text"] = self._t("btn_start")
        self.status["text"] = self._t("status_stopped")
        self.status["foreground"] = THEME_FG

    def _create_tray_icon(self):
        if not _TRAY_AVAILABLE:
            return
        img = Image.new("RGBA", (64, 64), (70, 130, 180, 255))
        try:
            self._tray_icon = pystray.Icon("preamp", img, self._t("window_title"), self._tray_menu())
            threading.Thread(target=self._tray_icon.run, daemon=True).start()
        except Exception:
            pass

    def _tray_menu(self):
        def show(icon, item):
            self.root.after(0, self._show_from_tray)
        def run_at_startup(icon, item):
            self.var_run_at_startup.set(not self.var_run_at_startup.get())
            self.root.after(0, self._on_run_at_startup_toggle)
        def quit_app(icon, item):
            self.root.after(0, self._quit_from_tray)
        return pystray.Menu(
            pystray.MenuItem(self._t("window_title"), show, default=True),
            pystray.MenuItem(self._t("run_at_startup"), run_at_startup, checked=lambda item: self.var_run_at_startup.get()),
            pystray.MenuItem("Exit", quit_app),
        )

    def _show_from_tray(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _quit_from_tray(self):
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
        self._stop_stream()
        self.root.quit()
        self.root.destroy()

    def _get_on_close_preference(self):
        """Return 'quit', 'tray', or None if no saved preference."""
        try:
            if os.path.isfile(self._config_file):
                with open(self._config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                v = cfg.get("on_close")
                if v in ("quit", "tray"):
                    return v
        except Exception:
            pass
        return None

    def _save_on_close_preference(self, choice):
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump({"on_close": choice}, f)
        except Exception:
            pass

    def _ask_close_or_tray(self):
        """Show dialog: Quit or Minimize to tray? Optional Remember."""
        d = tk.Toplevel(self.root)
        d.title(APP_TITLE)
        d.transient(self.root)
        d.grab_set()
        d.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 80))
        d.configure(bg=THEME_FRAME)
        frame = ttk.Frame(d, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="On close: quit the app or minimize to tray?", font=(FONT_FAMILY, FONT_SIZE)).pack(pady=(0, 12))
        var_remember = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Remember my choice", variable=var_remember).pack(anchor=tk.W, pady=(0, 12))
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        result = [None]

        def do_quit():
            if var_remember.get():
                self._save_on_close_preference("quit")
            result[0] = "quit"
            d.destroy()

        def do_tray():
            if var_remember.get():
                self._save_on_close_preference("tray")
            result[0] = "tray"
            d.destroy()

        ttk.Button(btn_frame, text="Quit", command=do_quit).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Minimize to tray", command=do_tray).pack(side=tk.LEFT, padx=4)
        d.wait_window()
        return result[0]

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        if _TRAY_AVAILABLE:
            self._create_tray_icon()
        self.root.mainloop()

    def _on_close(self):
        pref = self._get_on_close_preference()
        if pref == "quit":
            self._stop_stream()
            self.root.destroy()
            return
        if pref == "tray" and _TRAY_AVAILABLE and self._tray_icon:
            self.root.withdraw()
            return
        # No saved preference: ask user (or quit if no tray)
        if _TRAY_AVAILABLE and self._tray_icon:
            choice = self._ask_close_or_tray()
            if choice == "quit":
                self._stop_stream()
                self.root.destroy()
            elif choice == "tray":
                self.root.withdraw()
        else:
            self._stop_stream()
            self.root.destroy()


if __name__ == "__main__":
    PreampApp().run()
