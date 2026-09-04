import streamlit as st
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
from PIL import Image
import google.generativeai as genai
from gtts import gTTS
import tempfile
import json
import os
import base64
import re
import hashlib
import pydeck as pdk
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CUSTOM BRAND MARK — real MahaKrishi logo image
# ─────────────────────────────────────────────────────────────
_LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAIAAgADASIAAhEBAxEB/8QAHgABAAICAwEBAQAAAAAAAAAAAAcJBggEBQoDAgH/xABVEAABAwMCAwUEBQUMBgZF4hc538v3z+b3v831v5n1/c/80+g7v3/10/7/967lXo9yKquVVX5/01/wD611Xp/f/rR/513fX4uX/f3+9t9/b/T7f+r0+d2K7u0R3Kqu8P8AZb/m6ff/ALf+b5uNvd90irszwT/n/q/d7t1V3v8A85v9+34ff+08V2f3ifWXZF/5/wCt/wDz0/gK7e5/l/P/AMW4BwJ82/6X87e9y4E6bfq2/wBlf6b7fvXbfp8P1e7z4b953aKv+W6+O/2972+fwd+/e92n97/b5b9/j89/8r3f038fL++b/m1/b1e/z4/o+v8AL3fh9/t1/b4bf0/f/a/36/yfh4r3f8H3/X/wLfb4bf1+7+9v3bfHbfbf+d/n1/o+vvbfFvufwfLw+X+Xw+X9fvv/AJff236f0ff+/f5p9fbfp9vf+/6d16p8Nttv8d/n/wBxT/t/bf3t+f47/s6/0236eHT+79/6/wBv9/t8N/f5fD9L/H/X2+b0ffb+j/X+l+r+/bf6d912+b702V/vL02Tfb9X/b99+a/u238vT4f6/v7v6bfD9X5ff2+zfp9vh8/m3+7Xbf/Z"

def logo_svg(size: int = 80) -> str:
    """Return the MahaKrishi logo as an <img> tag sized to `size` px."""
    return (
        f'<img src="data:image/jpeg;base64,{_LOGO_B64}"'
        f' width="{size}" height="{size}"'
        f' style="border-radius:14px;object-fit:cover;display:block;"'
        f' alt="MahaKrishi Logo"/>' 
    )

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG (FIGMA DASHBOARD LAYOUT)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MahaKrishi AI | महाकृषि",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# FIGMA-INSPIRED MODERN AGRI CSS STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

    :root {
        --bg: #FAFAF8;
        --surface: #FFFFFF;
        --border: #E4E2DC;
        --text: #1F2320;
        --text-muted: #6B6F6A;
        --accent: #2F6B3E;
        --accent-dark: #1F4E2B;
        --accent-soft: #EEF3EC;
        --radius: 12px;
        --shadow-sm: 0 1px 2px rgba(20,20,15,0.05);
        --shadow-md: 0 4px 14px rgba(20,20,15,0.06);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans Devanagari', sans-serif;
        color: var(--text);
    }
    .stApp { background: var(--bg); }

    /* Header */
    .figma-header {
        background: var(--surface);
        padding: 22px 28px;
        border-radius: var(--radius);
        margin-bottom: 22px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }
    .figma-header-title { font-size: 1.7rem; font-weight: 700; margin: 0; color: var(--text); letter-spacing: -0.01em; }
    .figma-header-sub { font-size: 0.92rem; color: var(--text-muted); margin-top: 4px; }

    .figma-badge {
        background: var(--accent-soft);
        padding: 7px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--accent-dark);
        border: 1px solid #DCE8DD;
        white-space: nowrap;
        flex-shrink: 0;
    }

    /* Cards */
    .figma-card {
        background: var(--surface);
        border-radius: var(--radius);
        padding: 22px;
        margin-bottom: 18px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: cardRiseIn 0.4s ease both;
    }
    .figma-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }
    @keyframes cardRiseIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Login Card */
    .login-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 36px 40px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        max-width: 480px;
        margin: 0 auto;
    }

    /* Status Badges */
    .badge-emergency { background: #FBEBEA; color: #A23B34; border: 1px solid #F0D3D0; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
    .badge-warning   { background: #FBF1E4; color: #A0651A; border: 1px solid #F0E0C6; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
    .badge-success   { background: var(--accent-soft); color: var(--accent-dark); border: 1px solid #DCE8DD; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
    .badge-low-conf  { background: #FBF6E0; color: #8A6D14; border: 1px solid #EFE4B8; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }

    /* Profile Page */
    .profile-hero {
        background: var(--surface);
        border-radius: 16px; padding: 30px; margin-bottom: 22px;
        border: 1px solid var(--border); box-shadow: var(--shadow-sm);
        display: flex; align-items: center; gap: 22px;
    }
    .profile-avatar {
        width: 84px; height: 84px; background: var(--accent-soft);
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; font-size: 2.4rem; overflow: hidden;
        border: 1px solid var(--border); flex-shrink: 0;
    }
    .profile-avatar img { width: 100%; height: 100%; object-fit: cover; }
    .profile-stat-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 18px; text-align: center;
        box-shadow: var(--shadow-sm);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: cardRiseIn 0.4s ease both;
    }
    .profile-stat-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
    .profile-stat-num { font-size: 1.9rem; font-weight: 700; color: var(--text); margin: 0; }
    .profile-stat-label { color: var(--text-muted); font-size: 0.82rem; font-weight: 500; margin: 4px 0 0; }
    .history-row {
        background: var(--bg); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 14px 18px; margin-bottom: 10px;
        display: flex; align-items: center; gap: 14px;
    }
    .history-icon { font-size: 1.4rem; flex-shrink: 0; opacity: 0.8; }
    .history-badge { font-size: 0.76rem; font-weight: 600; padding: 3px 10px;
        border-radius: 20px; white-space: nowrap; }

    /* Remedy Container */
    .remedy-chemical {
        background: #FBF6EC;
        border-left: 3px solid #C08A2E;
        border-radius: 0 var(--radius) var(--radius) 0;
        padding: 18px;
        margin: 12px 0;
    }
    .remedy-organic {
        background: var(--accent-soft);
        border-left: 3px solid var(--accent);
        border-radius: 0 var(--radius) var(--radius) 0;
        padding: 18px;
        margin: 12px 0;
    }

    /* Chat Box */
    .chat-box {
        background: var(--bg);
        border-left: 3px solid var(--accent);
        border-radius: 0 var(--radius) var(--radius) 0;
        padding: 20px;
        margin: 12px 0;
        font-size: 1rem;
        line-height: 1.75;
        border-top: 1px solid var(--border); border-right: 1px solid var(--border); border-bottom: 1px solid var(--border);
    }

    /* Alert box */
    .alert-box {
        background: #FBF1E4;
        border: 1px solid #EAD3AC;
        border-radius: var(--radius);
        padding: 16px 20px;
        margin: 12px 0;
    }

    /* Audio section */
    .audio-section {
        background: #F0F4F8;
        border: 1px solid #D7E1E9;
        border-radius: var(--radius);
        padding: 16px;
        margin: 12px 0;
    }

    /* Scheme Card */
    .scheme-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 20px;
        height: 100%;
        box-shadow: var(--shadow-sm);
    }
    .scheme-card h4 { color: var(--text); margin-top: 0; }

    /* Contact Card */
    .contact-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Status dot */
    .status-dot {
        display: inline-block; width: 7px; height: 7px; border-radius: 50%;
        background: var(--accent); margin-right: 6px; vertical-align: middle;
        animation: statusPulse 2s infinite;
    }
    @keyframes statusPulse {
        0%   { box-shadow: 0 0 0 0 rgba(47,107,62,0.35); }
        70%  { box-shadow: 0 0 0 6px rgba(47,107,62,0); }
        100% { box-shadow: 0 0 0 0 rgba(47,107,62,0); }
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
        border-color: var(--accent) !important;
    }
    .stButton > button:active { transform: translateY(0) scale(0.98) !important; }

    .stTabs [data-baseweb="tab-highlight"] {
        transition: left 0.25s ease, width 0.25s ease !important;
        background-color: var(--accent) !important;
    }

    .main .block-container { animation: pageFadeIn 0.35s ease both; }
    @keyframes pageFadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Mobile */
    @media (max-width: 768px) {
        .figma-header { padding: 16px 18px; border-radius: 12px; }
        .figma-header-title { font-size: 1.3rem; line-height: 1.2; }
        .figma-header-sub { font-size: 0.82rem; }
        .figma-badge { font-size: 0.72rem; padding: 6px 12px; }
        .figma-card { padding: 16px; border-radius: 10px; margin-bottom: 14px; }
        .login-card { padding: 24px 20px; max-width: 100%; border-radius: 14px; }
        .remedy-chemical, .remedy-organic, .chat-box, .alert-box, .audio-section, .scheme-card, .contact-card {
            padding: 14px; font-size: 0.92rem;
        }
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.05rem !important; }
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
        .stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; }

        .profile-hero { flex-direction: column; align-items: flex-start; gap: 14px; padding: 20px; text-align: left; }
        .profile-hero > div:last-child { text-align: left !important; width: 100%; }
        .profile-avatar { width: 60px; height: 60px; font-size: 1.8rem; }
        .profile-stat-card { padding: 12px; }
        .profile-stat-num { font-size: 1.4rem; }
        .profile-stat-label { font-size: 0.7rem; }
        .history-row { padding: 10px 12px; gap: 10px; }
        .history-icon { font-size: 1.1rem; }
    }
    @media (max-width: 380px) {
        .figma-header-title { font-size: 1.15rem; }
        img { max-width: 100%; height: auto; }
    }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# TRANSLATIONS & CONFIG
# ─────────────────────────────────────────────────────────────
LANGUAGE_MAP   = {
    "मराठी (Marathi)": "mr",
    "हिंदी (Hindi)": "hi",
    "English": "en",
    "ગુજરાતી (Gujarati)": "gu",
    "ਪੰਜਾਬੀ (Punjabi)": "pa"
}
LANGUAGE_NAMES = {
    "mr": "Marathi",
    "hi": "Hindi",
    "en": "English",
    "gu": "Gujarati",
    "pa": "Punjabi"
}

UI_TEXT = {
    "en": {
        "title": "MahaKrishi AI",
        "subtitle": "Smart Crop Disease & Pest Detection",
        "signin_tab": "Sign In",
        "register_tab": "Register",
        "mobile": "Mobile Number",
        "name": "Full Name",
        "district": "District",
        "signin_btn": "Sign In",
        "register_btn": "Register & Sign In",
        "sel_lang": "Select Language",
        "tab_detect": "AI Detection",
        "tab_chat": "Treatment Chatbot",
        "tab_contacts": "Specialist Contacts",
        "tab_map": "Outbreak Map & Alerts",
        "tab_schemes": "Govt Schemes",
        "password": "Password",
        "signout": "Sign Out"
    },
    "mr": {
        "title": "महाकृषि AI",
        "subtitle": "स्मार्ट पीक रोग आणि कीड ओळख",
        "signin_tab": "लॉग इन",
        "register_tab": "नोंदणी",
        "mobile": "मोबाईल नंबर",
        "name": "पूर्ण नाव",
        "district": "जिल्हा",
        "signin_btn": "लॉग इन करा",
        "register_btn": "नोंदणी करा",
        "sel_lang": "भाषा निवडा",
        "tab_detect": "AI रोग निदान",
        "tab_chat": "कृषी चॅटबॉट",
        "tab_contacts": "विशेषज्ञ संपर्क",
        "tab_map": "रोग अलर्ट नकाशा",
        "tab_schemes": "शासकीय योजना",
        "password": "पासवर्ड",
        "signout": "लॉग आउट"
    },
     "hi": {
        "title": "महाकृषि AI",
        "subtitle": "स्मार्ट फसल रोग और कीट पहचान",
        "signin_tab": "साइन इन",
        "register_tab": "पंजीकरण",
        "mobile": "मोबाइल नंबर",
        "name": "पूरा नाम",
        "district": "जिला",
        "signin_btn": "साइन इन करें",
        "register_btn": "रजिस्टर करें",
        "sel_lang": "भाषा चुनें",
        "tab_detect": "AI रोग पहचान",
        "tab_chat": "कृषि चैटबॉट",
        "tab_contacts": "विशेषज्ञ संपर्क",
        "tab_map": "रोग अलर्ट मैप",
        "tab_schemes": "सरकारी योजनाएं",
        "password": "पासवर्ड",
        "signout": "लॉग आउट"
    },
    "gu": {
        "title": "મહાકૃષિ AI",
        "subtitle": "સ્માર્ટ પાક રોગ અને જીવાત શોધ",
        "signin_tab": "સાઇન ઇન",
        "register_tab": "નોંધણી",
        "mobile": "મોબાઇલ નંબર",
        "name": "પૂરું નામ",
        "district": "જિલ્લો",
        "signin_btn": "સાઇન ઇન કરો",
        "register_btn": "નોંધણી કરો",
        "sel_lang": "ભાષા પસંદ કરો",
        "tab_detect": "AI રોગ શોધ",
        "tab_chat": "કૃષિ ચેટબોટ",
        "tab_contacts": "નિષ્ણાત સંપર્ક",
        "tab_map": "રોગ એલર્ટ નકશો",
        "tab_schemes": "સરકારી યોજનાઓ",
        "password": "પાસવર્ડ",
        "signout": "લૉગ આઉટ"
    },
    "pa": {
        "title": "ਮਹਾਕ੍ਰਿਸ਼ੀ AI",
        "subtitle": "ਸਮਾਰਟ ਫਸਲ ਰੋਗ ਅਤੇ ਕੀਟ ਪਛਾਣ",
        "signin_tab": "ਸਾਈਨ ਇਨ",
        "register_tab": "ਰਜਿਸਟ੍ਰੇਸ਼ਨ",
        "mobile": "ਮੋਬਾਈਲ ਨੰਬਰ",
        "name": "ਪੂਰਾ ਨਾਮ",
        "district": "ਜ਼ਿਲ੍ਹਾ",
        "signin_btn": "ਸਾਈਨ ਇਨ ਕਰੋ",
        "register_btn": "ਰਜਿਸਟਰ ਕਰੋ",
        "sel_lang": "ਭਾਸ਼ਾ ਚੁਣੋ",
        "tab_detect": "AI ਰੋਗ ਪਛਾਣ",
        "tab_chat": "ਖੇਤੀ ਚੈਟਬੋਟ",
        "tab_contacts": "ਮਾਹਰ ਸੰਪਰਕ",
        "tab_map": "ਰੋਗ ਅਲਰਟ ਨਕਸ਼ਾ",
        "tab_schemes": "ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ",
        "password": "ਪਾਸਵਰਡ",
        "signout": "ਲੌਗ ਆਉਟ"
    }
}

def _t(key):
    lang = st.session_state.get("app_lang", "en")
    return UI_TEXT.get(lang, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))

# CONSTANTS & CONFIG
# ─────────────────────────────────────────────────────────────

IMG_SIZE = 224
DEVICE   = torch.device("cpu")

EXCEL_SIGNIN_FILE = os.path.join(os.path.dirname(__file__), "farmer_signins.xlsx")
EXCEL_ALERTS_FILE = os.path.join(os.path.dirname(__file__), "disease_alerts.xlsx")

CONF_THRESHOLD_LOW  = 45.0   # Below this show low-confidence warning
CONF_THRESHOLD_ALERT = 60.0  # Above this show "Alert Nearby Farmers" button

ALL_DISTRICTS = [
    "Pune", "Nashik", "Kolhapur", "Solapur", "Chhatrapati Sambhajinagar",
    "Nagpur", "Amravati", "Latur", "Satara", "Thane", "Ahmednagar",
    "Jalgaon", "Nanded", "Osmanabad", "Beed", "Buldhana", "Wardha",
    "Yavatmal", "Akola", "Washim", "Ratnagiri", "Sindhudurg", "Other"
]

# Get Gemini API key
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_KEY:
    try:
        GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        GEMINI_KEY = ""

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# EXCEL HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def append_signin_to_excel(name: str, phone: str, district: str, action: str, password_hash: str = ""):
    """Append a farmer sign-in/register entry to the shared Excel file."""
    new_row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name,
        "Phone": phone,
        "District": district,
        "Action": action,
        "Password_Hash": password_hash
    }
    if os.path.exists(EXCEL_SIGNIN_FILE):
        try:
            existing = pd.read_excel(EXCEL_SIGNIN_FILE, dtype=str)
            updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        except Exception:
            updated = pd.DataFrame([new_row])
    else:
        updated = pd.DataFrame([new_row])
    updated.to_excel(EXCEL_SIGNIN_FILE, index=False)


def append_alert_to_excel(reporter_name: str, reporter_phone: str, district: str,
                           crop: str, disease: str, confidence: float):
    """Append a disease/pest alert entry to the shared alerts Excel file."""
    new_row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Reporter_Name": reporter_name,
        "Reporter_Phone": reporter_phone,
        "District": district,
        "Crop_Disease": disease,
        "Crop_Type": crop,
        "Confidence_Pct": round(confidence, 1)
    }
    if os.path.exists(EXCEL_ALERTS_FILE):
        try:
            existing = pd.read_excel(EXCEL_ALERTS_FILE, dtype=str)
            updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        except Exception:
            updated = pd.DataFrame([new_row])
    else:
        updated = pd.DataFrame([new_row])
    updated.to_excel(EXCEL_ALERTS_FILE, index=False)


def get_registered_farmers_count(district: str) -> int:
    """Return count of registered farmers for a given district from Excel."""
    if not os.path.exists(EXCEL_SIGNIN_FILE):
        return 0
    try:
        df = pd.read_excel(EXCEL_SIGNIN_FILE, dtype=str)
        return int(df[df["District"].str.lower() == district.lower()].shape[0])
    except Exception:
        return 0


def phone_exists(phone: str) -> dict | None:
    """Check if phone number already registered. Returns farmer info dict or None."""
    if not os.path.exists(EXCEL_SIGNIN_FILE):
        return None
    try:
        df = pd.read_excel(EXCEL_SIGNIN_FILE, dtype=str)
        match = df[df["Phone"] == phone.strip()]
        if not match.empty:
            row = match.iloc[0]
            return {
                "name":          row.get("Name", ""),
                "district":      row.get("District", ""),
                "password_hash": row.get("Password_Hash", "")
            }
    except Exception:
        pass
    return None


def hash_password(password: str) -> str:
    """Return SHA-256 hex digest of the password."""
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def verify_password(entered: str, stored_hash: str) -> bool:
    """Return True if entered password matches the stored hash."""
    if not stored_hash:
        return True
    return hash_password(entered) == stored_hash


# ─────────────────────────────────────────────────────────────
# PROFILE PHOTO (uploaded photo, else Instagram-style default pfp)
# ─────────────────────────────────────────────────────────────
PROFILE_PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "profile_photos")
_PHOTO_EXTS = [".png", ".jpg", ".jpeg", ".webp"]

def _safe_phone_id(phone: str) -> str:
    return re.sub(r"\D", "", str(phone)) or "unknown"

def save_profile_photo(phone: str, uploaded_file) -> str:
    """Persist an uploaded profile photo to disk, keyed by phone number."""
    os.makedirs(PROFILE_PHOTOS_DIR, exist_ok=True)
    pid = _safe_phone_id(phone)
    for ext in _PHOTO_EXTS:
        old = os.path.join(PROFILE_PHOTOS_DIR, f"{pid}{ext}")
        if os.path.exists(old):
            os.remove(old)
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in _PHOTO_EXTS:
        ext = ".png"
    path = os.path.join(PROFILE_PHOTOS_DIR, f"{pid}{ext}")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def get_profile_photo_path(phone: str):
    """Return the saved photo path for this farmer, or None if never uploaded."""
    if not phone:
        return None
    pid = _safe_phone_id(phone)
    for ext in _PHOTO_EXTS:
        p = os.path.join(PROFILE_PHOTOS_DIR, f"{pid}{ext}")
        if os.path.exists(p):
            return p
    return None

def _default_avatar_data_uri() -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="50" fill="#DBDBDB"/>'
        '<circle cx="50" cy="40" r="18" fill="#FFFFFF"/>'
        '<path d="M50 60c-21 0-35 13-35 28v6h70v-6c0-15-14-28-35-28z" fill="#FFFFFF"/>'
        '</svg>'
    )
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

def get_avatar_data_uri(phone: str) -> str:
    path = get_profile_photo_path(phone)
    if path:
        try:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(path)[1].replace(".", "")
            mime = "jpeg" if ext == "jpg" else ext
            return f"data:image/{mime};base64,{b64}"
        except Exception:
            pass
    return _default_avatar_data_uri()


CHART_ICON_SVG = """<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#8BC34A" stroke-width="1.6">
  <path d="M4 20V10m6 10V4m6 16v-7" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M3 20h18" stroke-linecap="round"/>
</svg>"""

UPLOAD_ICON_SVG = """<svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="#558B2F" stroke-width="1.6">
  <path d="M4 16.5V18a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 3v12m0-12 4 4m-4-4-4 4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

SCAN_ICON_SVG = """<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#8BC34A" stroke-width="1.6">
  <path d="M12 21c-4-3-7-6.5-7-10.5A7 7 0 0 1 12 4a7 7 0 0 1 7 6.5C19 14.5 16 18 12 21Z" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="12" cy="11" r="2.3"/>
</svg>"""


# ─────────────────────────────────────────────────────────────
# LOGIN / REGISTER GATE
# ─────────────────────────────────────────────────────────────

def show_login_page():
    st.markdown("""
    <div style='text-align:center;padding:30px 0 10px'>
        <div style="display:flex;justify-content:center;margin-bottom:10px">""" + logo_svg(96) + """</div>
        <h1 style='color:#1F4E2B;font-size:2rem;margin:0'>""" + _t('title') + """</h1>
        <p style='color:#2F6B39;font-size:1rem;margin:4px 0 0'>""" + _t('subtitle') + """</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if "app_lang" not in st.session_state:
            st.session_state["app_lang"] = "mr"
        if "lang_name" not in st.session_state:
            st.session_state["lang_name"] = "Marathi"
        if "sel_lang_display" not in st.session_state:
            st.session_state["sel_lang_display"] = "मराठी (Marathi)"
        
        def on_lang_change():
            chosen = st.session_state["lang_selector"]
            st.session_state["app_lang"] = LANGUAGE_MAP[chosen]
            st.session_state["lang_name"] = LANGUAGE_NAMES[LANGUAGE_MAP[chosen]]
            st.session_state["sel_lang_display"] = chosen
        
        lang_options = list(LANGUAGE_MAP.keys())
        current_index = lang_options.index(st.session_state["sel_lang_display"]) \
            if st.session_state["sel_lang_display"] in lang_options else 0
        
        st.selectbox(
            _t('sel_lang'),
            lang_options,
            index=current_index,
            key="lang_selector",
            on_change=on_lang_change
        )
        tab_signin, tab_register = st.tabs([_t('signin_tab'), _t('register_tab')])

        with tab_signin:
            si_phone    = st.text_input(_t('mobile'), key="si_phone")
            si_password = st.text_input(_t('password'), type="password", key="si_password")
            if st.button(_t('signin_btn'), type="primary", use_container_width=True, key="btn_signin"):
                phone_clean = si_phone.strip()
                lang        = st.session_state["app_lang"]
                if not phone_clean or len(phone_clean) < 10:
                    st.error("Invalid number" if lang == "en" else "अवैध नंबर")
                elif not si_password.strip():
                    st.error("Please enter your password." if lang == "en" else "कृपया पासवर्ड टाका.")
                else:
                    farmer_info = phone_exists(phone_clean)
                    if farmer_info:
                        if verify_password(si_password, farmer_info.get("password_hash", "")):
                            append_signin_to_excel(farmer_info["name"], phone_clean, farmer_info["district"], "Sign-In")
                            st.session_state["logged_in"] = True
                            st.session_state["farmer_name"] = farmer_info["name"]
                            st.session_state["farmer_phone"] = phone_clean
                            st.session_state["farmer_district"] = farmer_info["district"]
                            st.rerun()
                        else:
                            st.error("❌ Incorrect password. Please try again." if lang == "en" else "❌ चुकीचा पासवर्ड. पुन्हा प्रयत्न करा.")
                    else:
                        st.error("Not found. Please register." if lang == "en" else "नंबर आढळला नाही. कृपया नोंदणी करा.")

        with tab_register:
            rg_name     = st.text_input(_t('name'), key="rg_name")
            rg_phone    = st.text_input(_t('mobile') + " ", key="rg_phone")
            rg_district = st.selectbox(_t('district'), ALL_DISTRICTS, key="rg_district")
            rg_password  = st.text_input(_t('password'), type="password", key="rg_password",
                                         help="Min 6 characters" if st.session_state.get("app_lang","mr")=="en" else "किमान 6 अक्षरे")
            rg_confirm   = st.text_input(
                ("Confirm Password" if st.session_state.get("app_lang","mr")=="en" else "पासवर्ड पुन्हा टाका"),
                type="password", key="rg_confirm"
            )

            if st.button(_t('register_btn'), type="primary", use_container_width=True, key="btn_register"):
                name_clean, phone_clean = rg_name.strip(), rg_phone.strip()
                pwd_clean = rg_password.strip()
                lang = st.session_state.get("app_lang", "mr")
                if not name_clean or not phone_clean or len(phone_clean) < 10:
                    st.error("Invalid details" if lang=="en" else "अवैध माहिती")
                elif len(pwd_clean) < 6:
                    st.error("Password must be at least 6 characters." if lang=="en" else "पासवर्ड किमान 6 अक्षरांचा असावा.")
                elif pwd_clean != rg_confirm.strip():
                    st.error("Passwords do not match." if lang=="en" else "पासवर्ड जुळत नाही.")
                else:
                    if phone_exists(phone_clean):
                        st.warning("Already registered" if lang=="en" else "हा नंबर आधीच नोंदणीकृत आहे.")
                    else:
                        append_signin_to_excel(name_clean, phone_clean, rg_district, "Register",
                                               password_hash=hash_password(pwd_clean))
                        st.session_state["logged_in"] = True
                        st.session_state["farmer_name"] = name_clean
                        st.session_state["farmer_phone"] = phone_clean
                        st.session_state["farmer_district"] = rg_district
                        st.rerun()

    st.markdown("""
    <div style='text-align:center;padding:30px;color:#558B2F;font-size:0.82rem;margin-top:20px'>
        <b>MahaKrishi AI</b> | Powered by PyTorch + Google Gemini AI<br>
        Maharashtra Government Agri-Tech Initiative
    </div>
    """, unsafe_allow_html=True)


# ── SESSION GUARD ──
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_login_page()
    st.stop()

# ── PROFILE PAGE SESSION STATE ──
if "show_profile" not in st.session_state:
    st.session_state["show_profile"] = False
if "detection_history" not in st.session_state:
    st.session_state["detection_history"] = []


# ─────────────────────────────────────────────────────────────
# PROFILE PAGE FUNCTION
# ─────────────────────────────────────────────────────────────
def show_profile_page():
    farmer_name    = st.session_state.get("farmer_name", "Farmer")
    farmer_phone   = st.session_state.get("farmer_phone", "—")
    farmer_district= st.session_state.get("farmer_district", "—")
    reg_number     = f"MK-{abs(hash(farmer_phone)) % 900000 + 100000}"
    history        = st.session_state.get("detection_history", [])

    if st.button("Back to Dashboard", key="back_from_profile"):
        st.session_state["show_profile"] = False
        st.rerun()

    avatar_uri = get_avatar_data_uri(farmer_phone)
    st.markdown(f"""
    <div class='profile-hero'>
        <div class='profile-avatar'><img src='{avatar_uri}'/></div>
        <div style='flex:1'>
            <h2 style='margin:0 0 4px;font-size:1.6rem;color:var(--text,#1F2320)'>{farmer_name}</h2>
            <p style='margin:0;color:var(--text-muted,#6B6F6A);font-size:0.95rem'>{farmer_phone}</p>
            <p style='margin:4px 0 0;color:var(--text-muted,#6B6F6A);font-size:0.88rem'>{farmer_district} District, Maharashtra</p>
            <p style='margin:8px 0 0;'>
                <span style='background:var(--accent-soft,#EEF3EC);color:var(--accent-dark,#1F4E2B);border-radius:20px;
                             padding:4px 14px;font-size:0.8rem;font-weight:600;border:1px solid #DCE8DD'>
                    Reg. No: {reg_number}
                </span>
            </p>
        </div>
        <div style='text-align:right'>
            <p style='margin:0;font-size:0.78rem;color:var(--text-muted,#6B6F6A)'>Member Since</p>
            <p style='margin:0;font-weight:700;font-size:1.05rem;color:var(--text,#1F2320)'>{datetime.now().strftime("%b %Y")}</p>
            <span style='background:var(--accent-soft,#EEF3EC);color:var(--accent-dark,#1F4E2B);border-radius:20px;
                         padding:3px 12px;font-size:0.76rem;font-weight:600;border:1px solid #DCE8DD'>Verified Farmer</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Change Profile Photo"):
        new_photo = st.file_uploader(
            "Upload a photo (JPG, PNG, or WEBP)",
            type=["png", "jpg", "jpeg", "webp"],
            key="profile_photo_uploader"
        )
        if new_photo is not None:
            if st.button("Save Photo", key="save_profile_photo_btn"):
                save_profile_photo(farmer_phone, new_photo)
                st.success("Profile photo updated.")
                st.rerun()
        if get_profile_photo_path(farmer_phone):
            st.caption("You currently have a photo uploaded. Upload a new one above to replace it.")
        else:
            st.caption("No photo uploaded yet — showing the default avatar.")

    disease_count = sum(1 for h in history if h.get("type") == "disease")
    pest_count    = sum(1 for h in history if h.get("type") == "pest")
    healthy_count = sum(1 for h in history if h.get("healthy"))
    total_scans   = len(history)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class='profile-stat-card'>
            <p class='profile-stat-num'>{total_scans}</p>
            <p class='profile-stat-label'>Total AI Scans</p>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class='profile-stat-card'>
            <p class='profile-stat-num'>{disease_count}</p>
            <p class='profile-stat-label'>Diseases Detected</p>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class='profile-stat-card'>
            <p class='profile-stat-num'>{pest_count}</p>
            <p class='profile-stat-label'>Pests Identified</p>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class='profile-stat-card'>
            <p class='profile-stat-num'>{healthy_count}</p>
            <p class='profile-stat-label'>Healthy Crops</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### Farmer Information")
        st.markdown(f"""
        <table style='width:100%;border-collapse:collapse;font-size:0.92rem'>
            <tr style='border-bottom:1px solid #E8F5E9'>
                <td style='padding:10px 0;color:#558B2F;font-weight:600'>Full Name</td>
                <td style='padding:10px 0;color:#1F4E2B;font-weight:700'>{farmer_name}</td>
            </tr>
            <tr style='border-bottom:1px solid #E8F5E9'>
                <td style='padding:10px 0;color:#558B2F;font-weight:600'>Mobile Number</td>
                <td style='padding:10px 0;color:#1F4E2B'>{farmer_phone}</td>
            </tr>
            <tr style='border-bottom:1px solid #E8F5E9'>
                <td style='padding:10px 0;color:#558B2F;font-weight:600'>District</td>
                <td style='padding:10px 0;color:#1F4E2B'>{farmer_district}</td>
            </tr>
            <tr style='border-bottom:1px solid #E8F5E9'>
                <td style='padding:10px 0;color:#558B2F;font-weight:600'>State</td>
                <td style='padding:10px 0;color:#1F4E2B'>Maharashtra</td>
            </tr>
            <tr style='border-bottom:1px solid #E8F5E9'>
                <td style='padding:10px 0;color:#558B2F;font-weight:600'>Registration No.</td>
                <td style='padding:10px 0'>
                    <span style='background:#E8F5E9;color:#1F4E2B;font-weight:700;
                                 padding:3px 10px;border-radius:10px'>{reg_number}</span>
                </td>
            </tr>
            <tr>
                <td style='padding:10px 0;color:#558B2F;font-weight:600'>Account Status</td>
                <td style='padding:10px 0'>
                    <span style='background:#C8E6C9;color:#1F4E2B;font-weight:700;
                                 padding:3px 10px;border-radius:10px'>Active</span>
                </td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### Activity Dashboard")
        if total_scans > 0:
            chart_data = {
                "Category": ["Disease", "Pest", "Healthy"],
                "Count": [disease_count, pest_count, healthy_count]
            }
            df_chart = pd.DataFrame(chart_data)
            st.bar_chart(df_chart.set_index("Category"), color="#2F6B39", use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align:center;padding:30px;background:#F9FBE7;border-radius:12px'>
                <div style='display:flex;justify-content:center'>""" + CHART_ICON_SVG + """</div>
                <p style='color:#558B2F;margin:8px 0 0'>No scan data yet.<br>
                   <small>Start detecting crop diseases to see your activity chart here.</small></p>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### Detection History")

        if not history:
            st.markdown("""
            <div style='text-align:center;padding:30px;background:#F9FBE7;border-radius:12px'>
                <div style='display:flex;justify-content:center'>""" + SCAN_ICON_SVG + """</div>
                <p style='color:#558B2F;margin:8px 0 0'>No detections yet.<br>
                   <small>Upload a crop photo on the AI Detection tab to get started.</small></p>
            </div>""", unsafe_allow_html=True)
        else:
            for h in reversed(history[-10:]):
                badge_color = "#FFEBEE" if h.get("type") == "disease" else (
                              "#FFF3E0" if h.get("type") == "pest" else "#E8F5E9")
                badge_text_color = "#C62828" if h.get("type") == "disease" else (
                                   "#EF6C00" if h.get("type") == "pest" else "#2F6B39")
                label = "Disease" if h.get("type") == "disease" else (
                        "Pest" if h.get("type") == "pest" else "Healthy")
                st.markdown(f"""
                <div class='history-row'>
                    <div style='flex:1;min-width:0'>
                        <p style='margin:0;font-weight:600;color:#1F4E2B;
                                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>
                            {h.get("name","Unknown")}
                        </p>
                        <p style='margin:2px 0 0;font-size:0.78rem;color:#558B2F'>
                            {h.get("time","—")} &nbsp;|&nbsp; {h.get("conf",0):.1f}% confidence
                        </p>
                    </div>
                    <span class='history-badge'
                          style='background:{badge_color};color:{badge_text_color}'>{label}</span>
                </div>""", unsafe_allow_html=True)

            if st.button("Clear History", key="clear_hist"):
                st.session_state["detection_history"] = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### AI Models Used")
        st.markdown("""
        <div style='display:flex;flex-direction:column;gap:10px'>
            <div style='background:#E8F5E9;border-radius:10px;padding:12px'>
                <b style='color:#1F4E2B'>Crop Disease Model</b>
                <p style='margin:4px 0 0;font-size:0.82rem;color:#33691E'>
                    EfficientNet-B0 · 39 Classes · TTA ×4<br>
                    Rice, Sugarcane, Cotton, Wheat, Tomato, Potato
                </p>
            </div>
            <div style='background:#FFF3E0;border-radius:10px;padding:12px'>
                <b style='color:#E65100'>Pest Detection Model</b>
                <p style='margin:4px 0 0;font-size:0.82rem;color:#BF360C'>
                    EfficientNet-B0 · 14 Classes · TTA ×4<br>
                    Bollworm, Aphids, Stem Borer, Whitefly, Armyworm
                </p>
            </div>
            <div style='background:#E3F2FD;border-radius:10px;padding:12px'>
                <b style='color:#1565C0'>AI Advisory Engine</b>
                <p style='margin:4px 0 0;font-size:0.82rem;color:#0D47A1'>
                    Google Gemini 1.5 Flash + gTTS Voice<br>
                    Supports: Marathi, Hindi, English, Gujarati, Punjabi
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sign Out", type="secondary", use_container_width=False, key="profile_signout"):
        for key in ["logged_in", "farmer_name", "farmer_phone", "farmer_district",
                    "show_profile", "detection_history"]:
            st.session_state.pop(key, None)
        st.rerun()


# ─────────────────────────────────────────────────────────────
# LOAD PyTorch MODELS (Disease & Pest)
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_disease_model():
    model_path = os.path.join(os.path.dirname(__file__), "crop_disease_model.pth")
    if not os.path.exists(model_path):
        return None, None, "Model file 'crop_disease_model.pth' not found."
    try:
        checkpoint  = torch.load(model_path, map_location=DEVICE)
        class_names = checkpoint["class_names"]
        num_classes = checkpoint["num_classes"]

        base = models.efficientnet_b0(weights=None)
        in_f = base.classifier[1].in_features
        base.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_f, 512),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(512, num_classes)
        )
        base.load_state_dict(checkpoint["model_state"])
        base.eval().to(DEVICE)
        return base, class_names, None
    except Exception as e:
        return None, None, f"Error loading disease model: {e}"


@st.cache_resource(show_spinner=False)
def load_pest_model():
    model_path = os.path.join(os.path.dirname(__file__), "pest_model.pth")
    if not os.path.exists(model_path):
        return None, None, "⏳ Pest model checkpoint is being prepared..."
    try:
        checkpoint  = torch.load(model_path, map_location=DEVICE)
        class_names = checkpoint["class_names"]
        num_classes = checkpoint["num_classes"]

        base = models.efficientnet_b0(weights=None)
        in_f = base.classifier[1].in_features
        base.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_f, 256),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(256, num_classes)
        )
        base.load_state_dict(checkpoint["model_state"])
        base.eval().to(DEVICE)
        return base, class_names, None
    except Exception as e:
        return None, None, f"Error loading pest model: {e}"


# ─────────────────────────────────────────────────────────────
# CORE INFERENCE WITH TEST-TIME AUGMENTATION (TTA)
# ─────────────────────────────────────────────────────────────

_val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

_tta_transforms = [
    transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.RandomHorizontalFlip(p=1.0),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.RandomVerticalFlip(p=1.0),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
]


def check_image_quality(pil_image: Image.Image) -> tuple[bool, str]:
    img_array = np.array(pil_image.convert("L"))

    brightness = img_array.mean()
    if brightness < 40:
        return False, (
            "**Image too dark for accurate detection!**\n\n"
            "Please retake the photo in bright daylight or good lighting. "
            "Dark images cause the AI to give wrong predictions."
        )

    laplacian_var = np.var(np.gradient(img_array.astype(float)))
    if laplacian_var < 50:
        return False, (
            "**Image appears blurry or out of focus!**\n\n"
            "Please hold the camera steady and retake the photo closer to the leaf/plant. "
            "Blurry images significantly reduce detection accuracy."
        )

    return True, ""


def predict_crop_issue(model, class_names, pil_image: Image.Image):
    rgb_image = pil_image.convert("RGB")
    all_probs = []

    with torch.no_grad():
        for tfm in _tta_transforms:
            tensor = tfm(rgb_image).unsqueeze(0).to(DEVICE)
            logits = model(tensor)[0]
            probs  = torch.softmax(logits, dim=0).cpu().numpy()
            all_probs.append(probs)

    avg_probs = np.mean(all_probs, axis=0)
    top3_idx  = np.argsort(avg_probs)[::-1][:3]

    return [
        {
            "name":       class_names[i].replace("_", " ").replace("  ", " "),
            "raw_name":   class_names[i],
            "confidence": float(avg_probs[i]) * 100
        }
        for i in top3_idx
    ]


# ─────────────────────────────────────────────────────────────
# AUDIO & TEXT HELPERS (FIXED REGEX BUG FOR gTTS)
# ─────────────────────────────────────────────────────────────
def clean_text_for_speech(text):
    """Regex-based text cleaner for gTTS to produce clean Marathi/Hindi speech."""
    clean = re.sub(r'[*#`_~]', '', text)
    clean = re.sub(r'[\[\]()]', '', clean)  # FIXED REGEX CHAR SET
    clean = re.sub(r'https?://\S+', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean if clean else "पिकाचे विश्लेषण पूर्ण झाले आहे."


def is_gibberish_query(query):
    q = query.strip()
    if not q:
        return True
    if re.search(r'[\u0900-\u097F]', q):
        return False
    words = q.split()
    for w in words:
        c = re.sub(r'[^a-zA-Z]', '', w.lower())
        if len(c) >= 5:
            vowels = sum(1 for char in c if char in 'aeiouy')
            if vowels == 0:
                return True
            if any(p in c for p in ['asdf', 'qwerty', 'zxcv', 'dfgh', 'fghj', 'ghjk', 'hjkl', 'jklj', 'klj', 'jkl', 'lklj']):
                return True
    return False


AGRI_KEYWORDS = {
    'rice', 'sugarcane', 'cotton', 'potato', 'tomato', 'wheat', 'maize', 'corn', 'grain', 'crop', 'crops',
    'धान', 'तांदूळ', 'भात', 'ऊस', 'गन्ना', 'कापूस', 'कपाशी', 'कपास', 'बटाटा', 'आलू',
    'टोमॅटो', 'टमाटर', 'गहू', 'गेहूं', 'मका', 'मक्का', 'बाजरी', 'ज्वारी', 'सोयाबीन', 'चना',
    'blight', 'rot', 'smut', 'wilt', 'rust', 'mosaic', 'spot', 'mildew', 'blast', 'canker',
    'तांबेरा', 'करपा', 'सड', 'मर', 'मोझॅक', 'काणी', 'टिक्का', 'डाग',
    'aphids', 'aphid', 'planthopper', 'borer', 'armyworm', 'leafhopper', 'bollworm', 'moth',
    'fly', 'termites', 'termite', 'whitefly', 'hopper', 'pest', 'pests', 'insect', 'worm', 'caterpillar',
    'मावा', 'तुडतुडे', 'खोड कीड', 'अळी', 'बोंडअळी', 'पतंग', 'वाळवी', 'माशी', 'पांढरी माशी', 'कीड', 'कीटक',
    'plant', 'plants', 'leaf', 'leaves', 'farm', 'farmer', 'farming', 'agriculture',
    'field', 'disease', 'diseases', 'spray', 'spraying', 'pesticide', 'fungicide', 'insecticide',
    'fertilizer', 'organic', 'chemical', 'neem', 'jeevamrut', 'dashparni', 'treatment', 'remedy', 'remedies',
    'पीक', 'पिके', 'शेती', 'शेतकरी', 'शेत', 'झाड', 'झाडे', 'पान', 'पाने', 'रोग', 'उपचार', 'औषध',
    'फवारणी', 'सेंद्रिय', 'रसायनिक', 'खत', 'खते', 'जीवामृत', 'दशपर्णी', 'कडुनिंब', 'पाणी', 'सिंचन',
    'फसल', 'किसान', 'खेती', 'बीमारी', 'दवा', 'छिड़काव', 'जैविक', 'रासायनिक'
}


def is_agri_related_query(query):
    q_lower = query.lower().strip()
    for kw in AGRI_KEYWORDS:
        if kw in q_lower:
            return True
    return False


def text_to_speech(text, lang_code):
    clean = clean_text_for_speech(text)
    if len(clean) > 1000:
        clean = clean[:1000]
    tts = gTTS(text=clean, lang=lang_code, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        path = f.name
    with open(path, 'rb') as f:
        audio_bytes = f.read()
    try:
        os.unlink(path)
    except Exception:
        pass
    return audio_bytes


def audio_html(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    return f'<audio controls autoplay style="width:100%;border-radius:8px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'


# ─────────────────────────────────────────────────────────────
# GEMINI ADVISORY GENERATOR (WITH SMART OFFLINE FALLBACK)
# ─────────────────────────────────────────────────────────────
def get_ai_advisory(issue_name, is_pest, lang_name, confidence):
    is_healthy = "healthy" in issue_name.lower() or "निरोगी" in issue_name.lower()
    
    if is_healthy:
        prompt = f"""
        You are Krishi Mitra (कृषी मित्र), a caring, expert human agricultural scientist from Maharashtra, India speaking directly to a farmer.
        Crop/plant condition: HEALTHY (Confidence: {confidence:.1f}%).
        Name: {issue_name}

        STRICT LANGUAGE INSTRUCTION:
        Write your complete response ONLY in {lang_name} native script ({lang_name}). Do NOT use English or other languages unless explicitly requested.

        HUMAN PERSONA & DETAILED GUIDE:
        - Greet the farmer warmly (e.g. 'रामराम शेतकरी दादा / ताई!' in Marathi, 'नमस्कार किसान भाई!' in Hindi, 'Greetings dear farmer!' in English).
        - Congratulate and encourage the farmer on maintaining a healthy field.
        - Give 4 practical human tips for irrigation, soil health, balanced fertigation, and organic care.
        - List 3 early symptoms to watch out for to prevent sudden pest attacks.
        """
    else:
        type_str = "कीड (Pest Attack)" if is_pest else "रोग (Disease Outbreak)"
        prompt = f"""
        You are Krishi Mitra (कृषी मित्र), a senior human agricultural scientist and expert crop pathologist from Maharashtra advising a farmer.
        Detected {type_str}: **{issue_name}** (Confidence: {confidence:.1f}%)

        STRICT LANGUAGE INSTRUCTION:
        Write your complete response ONLY in {lang_name} native script ({lang_name}). Do NOT mix other languages. Use standard native terms.

        CRITICAL REQUIREMENT — COMPREHENSIVE, ELABORATIVE & STEP-BY-STEP ADVISORY:
        Provide a detailed, thorough, highly elaborative advisory covering all of the following sections:

        1. **नमस्कार व कृषी मित्राचे मनोगत (GREETING & EMPATHETIC INTRODUCTION)**
        2. **पिकावर होणारा विघातक परिणाम (HOW THE DISEASE/PEST AFFECTS THE PLANT)**
        3. **कीड / रोग येण्याची मुख्य कारणे (WHY THE PEST/DISEASE OCCURS)**
        4. **रोगाचे / कीडीचे ३ मुख्य टप्पे (STAGES OF DISEASE / PEST INFESTATION)**
        5. **टप्पा १: प्रभावी रसायनिक फवारणी (STEP 1: CHEMICAL SPRAY SOLUTION WITH DOSAGES)**
        6. **टप्पा २: सेंद्रिय व जैविक घरगुती उपाय (STEP 2: ORGANIC & BIOLOGICAL SOLUTIONS)**
        7. **टप्पा ३: दीर्घकालीन शेत स्वच्छता व सुपीकता (STEP 3: LONG-TERM PREVENTION & FIELD HYGIENE)**
        8. **मोफत कृषी हेल्पलाइन (HELPLINE SUPPORT)**
        """
    try:
        if GEMINI_KEY:
            genai.configure(api_key=GEMINI_KEY)
            gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            resp = gemini_model.generate_content(prompt)
            return resp.text
    except Exception:
        pass

    # Elaborative Fallback Response
    if is_healthy:
        if lang_name == "Marathi":
            return "**रामराम शेतकरी दादा!** \n\nतुमचे पीक पूर्णपणे निरोगी आहे!\n\n**कृषी मित्राची सल्ला:**\n१. जमिनीच्या गरजेनुसार वेळेवर सिंचन करा.\n२. रोज सकाळी पिकाचे निरीक्षण करा.\n३. जीवामृताचा वापर करून जमिनीची सुपीकता वाढवा."
        elif lang_name == "Hindi":
            return "**नमस्कार किसान भाई!** \n\nआपकी फसल पूरी तरह स्वस्थ है!\n\n**कृषि मित्र की सलाह:**\n1. आवश्यकतानुसार सिंचाई करें।\n2. नियमित रूप से फसल की जांच करें।\n3. जैविक खाद एवं जीवामृत का उपयोग करें।"
        elif lang_name == "Gujarati":
            return "**નમસ્કાર ખેડૂત ભાઈ/બહેન!** \n\nતમારો પાક સંપૂર્ણ સ્વસ્થ અને લીલોછમ છે!\n\n**કૃષિ મિત્રની સલાહ:**\n૧. જમીનની જરૂરિયાત મુજબ સિંચાઈ કરો.\n૨. દરરોજ સવારે પાકનું નિરીક્ષણ કરો.\n૩. જીવામૃતનો ઉપયોગ કરી જમીન સુધારો."
        elif lang_name == "Punjabi":
            return "**ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਭਰਾ/ਭੈਣ!** \n\nਤੁਹਾਡੀ ਫਸਲ ਬਿਲਕੁਲ ਸਿਹਤਮੰਦ ਅਤੇ ਹਰੀਭਰੀ ਹੈ!\n\n**ਕ੍ਰਿਸ਼ੀ ਮਿੱਤਰ ਦੀ ਸਲਾਹ:**\n੧. ਜ਼ਮੀਨ ਦੀ ਲੋੜ ਅਨੁਸਾਰ ਸਿੰਚਾਈ ਕਰੋ.\n੨. ਹਰ ਰੋਜ਼ ਸਵੇਰੇ ਫਸਲ ਦੀ ਜਾਂਚ ਕਰੋ.\n੩. ਜੀਵਾਮ੍ਰਿਤ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਮਿੱਟੀ ਸੁਧਾਰੋ."
        else:
            return "**Greetings Dear Farmer!** \n\nYour crop is completely healthy and growing strong!\n\n**Krishi Mitra Advice:**\n1. Maintain timely irrigation.\n2. Inspect fields every morning.\n3. Apply Jeevamrut to boost soil health."
    else:
        if lang_name == "Marathi":
            return f"""**रामराम शेतकरी दादा!** 
**आढळलेला विकार / कीड:** **{issue_name}**

**पिकावर होणारा विघातक परिणाम (How it Affects Plant):**
• हा विकार किंवा कीड पानांमधील रस शोषून घेते, ज्यामुळे पानातील हरितद्रव्य (Photosynthesis) नष्ट होते.
• झाडाची वाढ खुंटते, पाने पिवळी पडून वाळतात आणि उत्पादनात ३०% ते ५०% पर्यंत घट येऊ शकते.

**प्रादुर्भावाची मुख्य कारणे (Why it Attacks):**
• हवेतील वाढलेला दमटपणा, सततचे ढगाळ हवामान आणि युरियाचा (नत्र) अतिवापर यांमुळे कीड व रोगाचा प्रसार वेगाने होतो.

**रोगाचे / कीडीचे ३ मुख्य टप्पे (Stages of Disease / Infestation):**
• **१. प्राथमिक टप्पा (Early Stage):** पानांवर बारीक डाग (१-५% प्रादुर्भाव). ५% कडुनिंब तेल व चिकट सापळ्यांनी सहज नियंत्रण शक्य.
• **२. मध्यम टप्पा (Moderate Stage):** १०-३०% पानांवर डाग किंवा कीड. ४८ तासांत रसायनिक फवारणी (प्रोफेनोफॉस/इमॅमेक्टिन/हेक्झाकोनॅझोल) आवश्यक.
• **३. गंभीर / तीव्र टप्पा (Critical Stage):** ५०% पेक्षा जास्त पीक बाधित, पाने वाळणे, खोड सडणे. तातडीची सिस्टेमिक औषध फवारणी व बाधित भाग जाळणे आवश्यक.

**टप्पा १: रसायनिक फवारणी उपाय (Chemical Treatment):**
• **औषध:** प्रोफेनोफॉस ५०% EC (२ मिली प्रति लिटर पाणी) किंवा इमॅमेक्टिन बेन्झोएट ५% SG (०.५ ग्रॅम प्रति लिटर पाणी).
• **प्रमाण:** एका एकरासाठी २०० लिटर पाण्यात ४०० मिली औषध मिसळून फवारणी करा.
• **सुरक्षा:** फवारणी नेहमी संध्याकाळी व तोंडाला मास्क लावूनच करा.

**टप्पा २: सेंद्रिय व जैविक घरगुती उपाय (Organic Treatment):**
• **कडुनिंब तेल (Neem Oil):** ५ मिली कडुनिंब तेल (1500 PPM) + १ मिली डिटर्जंट लिक्विड प्रति लिटर पाण्यात मिसळून फवारा.
• **दशपर्णी अर्क:** ५ मिली दशपर्णी अर्क प्रति लिटर पाण्यात मिसळून फवारल्यास कीड पळून जाते.
• **चिकट सापळे:** कीडींच्या नियंत्रणासाठी शेतात एकरी १०-१२ पिवळे व निळे चिकट सापळे (Sticky Traps) लावा.

**टप्पा ३: दीर्घकालीन शेत स्वच्छता व बचाव:**
• बाधित पाने व झाडांचे अवशेष तात्काळ गोळा करून नष्ट करा.
• पिकांची आलटून-पालटून (Crop Rotation) लागवड करा.

**मोफत कृषी हेल्पलाइन:** 1800-180-1551 (कृषी सल्ला केंद्र)"""
        elif lang_name == "Hindi":
            return f"""**नमस्कार किसान भाई!** 
**पहचाना गया रोग / कीट:** **{issue_name}**

**फसल पर प्रभाव (How it Affects Plant):**
• यह कीट या रोग पत्तियों का रस चूसता है, जिससे प्रकाश संश्लेषण (Photosynthesis) बाधित होता है और पत्तियां पीली पड़कर सूख जाती हैं।

**प्रकोप का कारण (Why it Attacks):**
• मौसम में अत्यधिक नमी, बादल छाए रहना और नाइट्रोजन (यूरिया) का अत्यधिक उपयोग कीटों के पनपने का मुख्य कारण है।

**चरण 1: रासायनिक छिड़काव (Chemical Treatment):**
• **दवा:** प्रोफेनोफॉस 50% EC (2 मिली प्रति लीटर पानी) या इमामेक्टिन बेंजोएट (0.5 ग्राम/लीटर)।
• **मात्रा:** 1 एकड़ के लिए 200 लीटर पानी में 400 मिली दवा मिलाकर छिड़काव करें।

**चरण 2: जैविक एवं देसी उपाय (Organic Treatment):**
• **नीम तेल (Neem Oil):** 5 मिली नीम तेल प्रति लीटर पानी में मिलाकर स्प्रे करें।
• **दशपर्णी अर्क:** 5 मिली दशपर्णी अर्क का स्प्रे करें।
• **स्टिकी ट्रैप:** खेत में प्रति एकड़ 10-12 पीले व नीले स्टिकी ट्रैप लगाएं।

**हेल्पलाइन:** 1800-180-1551"""
        elif lang_name == "Gujarati":
            return f"""**નમસ્કાર ખેડૂત ભાઈ/બહેન!** 
**શોધાયેલ રોગ / જીવાત:** **{issue_name}**

**પાક પર અસર:**
- આ રોગ અથવા જીવાત પાંદડાનો રસ ચૂસે છે, જેથી પ્રકાશ-સંશ્લેષણ અટકે છે અને ઉત્પાદન ૩૦-૫૦% ઘટે છે.

**રાસાયણિક સ્પ્રે:**
- પ્રોફેનોફોસ ૫૦% EC (૨ ml/લિટર) અથવા ઇમામેક્ટિન (૦.૫ ગ્રામ/લિટર).

**જૈવિક ઉપાય:**
- લીમડાનું તેલ ૫ ml/લિટર અથવા દશપર્ણી અર્ક ૫ ml/લિટર.
- ચીકણા પીળા-વાદળી ટ્રેપ એકર દીઠ ૧૦-૧૨ લગાવો.

**હેલ્પલાઇન:** 1800-180-1551"""
        elif lang_name == "Punjabi":
            return f"""**ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਭਰਾ/ਭੈਣ!** 
**ਪਛਾਣਿਆ ਗਿਆ ਰੋਗ / ਕੀਟ:** **{issue_name}**

**ਫਸਲ ਉੱਤੇ ਅਸਰ:**
- ਇਹ ਰੋਗ ਪੱਤਿਆਂ ਦਾ ਰਸ ਚੂਸਦਾ ਹੈ, ਜਿਸ ਨਾਲ ਝਾੜ ੩੦-੫੦% ਘੱਟਦਾ ਹੈ.

**ਰਸਾਇਣਕ ਸਪ੍ਰੇ:**
- ਪ੍ਰੋਫੇਨੋਫੋਸ ੫੦% EC (੨ ml/ਲਿਟਰ) ਜਾਂ ਇਮਾਮੇਕਟਿਨ (੦.੫ ਗ੍ਰਾਮ/ਲਿਟਰ).

**ਜੈਵਿਕ ਉਪਾਅ:**
- ਨਿੰਮ ਤੇਲ ੫ ml/ਲਿਟਰ ਜਾਂ ਦਸ਼ਪਰਣੀ ਅਰਕ ੫ ml/ਲਿਟਰ.
- ਪੀਲੇ-ਨੀਲੇ ਸਟਿੱਕੀ ਟਰੈਪ ਏਕੜ ਪਿੱਛੇ ੧੦-੧੨ ਲਗਾਓ.

**ਹੈਲਪਲਾਈਨ:** 1800-180-1551"""
        else:
            return f"""**Hello Dear Farmer!** 
**Detected Issue:** **{issue_name}**

**How it Affects the Crop:**
• Disrupts photosynthesis, saps leaf nutrients, and clogs stem vascular tissues leading to potential yield loss.

**Step 1: Chemical Spray Treatment:**
• **Recommended Pesticide:** Spray Profenofos 50% EC (2 ml / Liter of water) or Emamectin Benzoate 5% SG (0.5g / Liter).

**Step 2: Organic & Biological Control:**
• **Neem Oil Spray:** Mix 5 ml Neem Oil (1500 PPM) + 1 ml liquid soap per Liter of water.
• **Traps:** Install 10-12 Yellow and Blue Sticky Traps per Acre.

**Toll-Free Kisan Helpline:** 1800-180-1551"""


# ─────────────────────────────────────────────────────────────
# SIDEBAR  (shown only after login)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    farmer_name_display = st.session_state.get("farmer_name", "Farmer")
    farmer_dist_display = st.session_state.get("farmer_district", "")
    _sidebar_avatar_uri  = get_avatar_data_uri(st.session_state.get("farmer_phone", ""))

    _logo_html = logo_svg(44)
    _sidebar_html = (
        "<div style='text-align:center;padding:18px 16px 14px;"
        "background:linear-gradient(135deg,#E8F5E9,#C8E6C9);"
        "border-radius:14px;margin-bottom:15px;border:1px solid #A5D6A7'>"
        "<div style='display:flex;justify-content:center;margin-bottom:10px'>"
        + _logo_html +
        "</div>"
        "<div style='display:flex;justify-content:center;margin-bottom:10px'>"
        "<img src='" + _sidebar_avatar_uri + "'"
        " style='width:80px;height:80px;border-radius:50%;object-fit:cover;"
        "border:3px solid #FFFFFF;"
        "box-shadow:0 3px 12px rgba(31,78,43,0.30);"
        "background:#EEF3EC;'/>"
        "</div>"
        "<p style='color:#1F4E2B;font-weight:700;font-size:0.95rem;margin:0 0 2px;"
        "white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
        + farmer_name_display +
        "</p>"
        "<p style='color:#558B2F;font-size:0.78rem;margin:0 0 8px'>"
        + farmer_dist_display +
        "</p>"
        "<span class='figma-badge'"
        " style='background:#1F4E2B;color:white;margin-top:2px;display:inline-block;font-size:0.72rem'>"
        "Govt. Agri-Tech Initiative"
        "</span>"
        "</div>"
    )
    st.markdown(_sidebar_html, unsafe_allow_html=True)

    if st.button("👤 View My Profile", use_container_width=True, key="sidebar_profile_btn"):
        st.session_state["show_profile"] = True
        st.rerun()

    lang_code = st.session_state.get("app_lang", "mr")
    lang_name = st.session_state.get("lang_name", "Marathi")

    enable_voice = st.toggle("Voice Output / आवाज उत्तर", value=True)

    st.markdown("---")
    st.markdown("### AI Model Directory")
    st.markdown("""
    <div class='contact-card'><small>
    <b>Crop Diseases:</b> 39 Classes (Rice, Sugarcane, Cotton, Wheat, Tomato, Potato)<br>
    <b>Crop Pests:</b> 14 Classes (Bollworm, Stem Borer, Aphids, Whitefly, Armyworm, etc.)<br>
    <b>AI Advisory:</b> Gemini AI + gTTS Voice Output<br>
    <b>Accuracy:</b> Test-Time Augmentation (TTA ×4)
    </small></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#FFF3E0;border-left:4px solid #FF9800;padding:10px;border-radius:6px'>
    <small><b>Emergency Agri Helpline:</b><br>
    Kisan Call Center: <b>1800-180-1551</b> (Toll-Free)</small>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button(_t("signout"), use_container_width=True):
        for key in ["logged_in", "farmer_name", "farmer_phone", "farmer_district"]:
            st.session_state.pop(key, None)
        st.rerun()


# ─────────────────────────────────────────────────────────────
# PROFILE PAGE ROUTING
# ─────────────────────────────────────────────────────────────
if st.session_state.get("show_profile", False):
    show_profile_page()
    st.stop()

# ─────────────────────────────────────────────────────────────
# FIGMA DYNAMIC HEADER
# ─────────────────────────────────────────────────────────────
farmer_name_header = st.session_state.get("farmer_name", "Farmer")
avatar_uri_header  = get_avatar_data_uri(st.session_state.get("farmer_phone", ""))

header_col, profile_col = st.columns([11, 1])

with header_col:
    st.markdown(f"""
    <div class='figma-header' style='margin-bottom:0'>
        <div style='flex:1;min-width:0'>
            <h1 class='figma-header-title'>MahaKrishi AI | महाकृषि</h1>
            <p class='figma-header-sub'>
                AI Crop Disease &amp; Pest Detection | Chemical &amp; Organic Remedies |
                Specialist Helplines &amp; Govt Schemes
            </p>
        </div>
        <div style='flex-shrink:0'>
            <span class='figma-badge'>
                <span class='status-dot'></span>System Active | महाराष्ट्र शासन
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with profile_col:
    st.markdown(f"""
    <style>
    #mk-profile-col {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 6px;
    }}
    #mk-profile-col img.mk-avatar {{
        width: 52px;
        height: 52px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #A5D6A7;
        box-shadow: 0 2px 10px rgba(31,78,43,0.22);
        background: #EEF3EC;
        display: block;
        cursor: pointer;
        transition: border-color 0.2s, box-shadow 0.2s, transform 0.18s;
        margin-bottom: 3px;
    }}
    #mk-profile-col img.mk-avatar:hover {{
        border-color: #2F6B3E;
        box-shadow: 0 4px 16px rgba(47,107,62,0.35);
        transform: scale(1.07);
    }}
    #mk-profile-col .mk-name-label {{
        font-size: 0.6rem;
        color: #2F6B39;
        font-weight: 600;
        text-align: center;
        max-width: 60px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-bottom: 2px;
    }}
    #mk-profile-col button {{
        opacity: 0 !important;
        height: 1px !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        pointer-events: none !important;
        position: absolute !important;
    }}
    </style>
    <div id="mk-profile-col">
        <img class="mk-avatar"
             src="{avatar_uri_header}"
             alt="Profile"
             title="View Profile — {farmer_name_header}"
             onclick="
                 var btns = document.querySelectorAll('#mk-profile-col button');
                 if(btns.length) {{ btns[0].style.pointerEvents='auto'; btns[0].click(); }}
             "/>
        <div class="mk-name-label">{farmer_name_header.split()[0]}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↗", key="open_profile",
                 help=f"View Profile — {farmer_name_header}",
                 use_container_width=True):
        st.session_state["show_profile"] = True
        st.rerun()

st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB NAVIGATION (FIGMA DASHBOARD SYSTEM)
# ─────────────────────────────────────────────────────────────
tab_detect, tab_chat, tab_contacts, tab_map, tab_schemes = st.tabs([
    _t("tab_detect"),
    _t("tab_chat"),
    _t("tab_contacts"),
    _t("tab_map"),
    _t("tab_schemes")
])

# ─────────────────────────────────────────────────────────────
# TAB 1: AI DISEASE & PEST DETECTION
# ─────────────────────────────────────────────────────────────
with tab_detect:
    col_mode, _ = st.columns([2, 1])
    with col_mode:
        model_mode = st.radio(
            "Select AI Target Mode / काय ओळखायचे आहे?",
            ["Crop Disease Detection (पिकांचे रोग)", "Pest Identification (कीड ओळख)"],
            horizontal=True
        )

    col_img, col_res = st.columns([1, 1.3], gap="large")

    with col_img:
        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### Upload Crop / Pest Photo")
        uploaded = st.file_uploader("Choose leaf or pest photo...", type=["jpg","jpeg","png","bmp","webp"],
                                    label_visibility="collapsed")

        if uploaded:
            pil_image = Image.open(uploaded).convert("RGB")
            st.image(pil_image, caption="Uploaded Image", use_container_width=True)
            analyze_btn = st.button("Analyze with AI | निदान करा", type="primary", use_container_width=True)
        else:
            st.markdown("""
            <div style='background:#F9FBE7;border:2px dashed #8BC34A;border-radius:14px;
                        padding:40px;text-align:center'>
                <div style='display:flex;justify-content:center'>""" + UPLOAD_ICON_SVG + """</div>
                <p style='color:#33691E;font-weight:600;margin:10px 0 2px'>Upload a photo of crop leaf or pest</p>
                <small style='color:#558B2F'>Supports JPG, PNG, WEBP</small>
            </div>""", unsafe_allow_html=True)
            analyze_btn = False
        st.markdown("</div>", unsafe_allow_html=True)

    with col_res:
        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### AI Diagnosis & Advisory")

        if not uploaded:
            st.markdown("""
            <div style='background:#E8F5E9;border-radius:12px;padding:30px;text-align:center'>
                <div style='display:flex;justify-content:center'>""" + SCAN_ICON_SVG + """</div>
                <h4 style='color:#1F4E2B;margin:8px 0 4px'>Ready for Instant AI Diagnosis</h4>
                <p style='color:#2F6B39;font-size:0.9rem'>Upload an image on the left and click 'Analyze with AI'</p>
            </div>""", unsafe_allow_html=True)

        elif analyze_btn:
            is_pest_mode = "Pest" in model_mode

            with st.spinner("Checking image quality..."):
                quality_ok, quality_msg = check_image_quality(pil_image)

            if not quality_ok:
                st.warning(quality_msg)
                st.info("**Tip:** Take photo in bright natural light, hold camera steady, and ensure the leaf fills most of the frame.")
            else:
                with st.spinner("⏳ Loading AI model & analyzing features (TTA ×4)..."):
                    if is_pest_mode:
                        model, class_names, err = load_pest_model()
                    else:
                        model, class_names, err = load_disease_model()

                if err:
                    st.error(err)
                else:
                    results = predict_crop_issue(model, class_names, pil_image)
                    top = results[0]
                    name = top["name"]
                    conf = top["confidence"]
                    healthy = "healthy" in name.lower() or "निरोगी" in name.lower()

                    if conf < CONF_THRESHOLD_LOW:
                        st.markdown(f"""
                        <div class='alert-box'>
                            <span class='badge-low-conf'>Low Confidence Detection</span>
                            <h4 style='color:#E65100;margin:10px 0 4px'>Best Match: {name}</h4>
                            <p style='margin:0;color:#BF360C'>AI Confidence: <b>{conf:.1f}%</b> — This is below the reliable threshold (45%)</p>
                        </div>""", unsafe_allow_html=True)
                    else:
                        badge_cls = "badge-success" if healthy else ("badge-warning" if is_pest_mode else "badge-emergency")
                        status_txt = "Healthy Crop! " if healthy else ("Pest Detected! " if is_pest_mode else "Disease Detected! ")

                        st.markdown(f"""
                        <div style='background:#FAFAFA;border-radius:12px;padding:16px;margin-bottom:12px;border:1px solid #E0E0E0'>
                            <span class='{badge_cls}'>{status_txt}</span>
                            <h3 style='color:#1F4E2B;margin:10px 0 4px'>{name}</h3>
                            <p style='color:#558B2F;font-size:0.88rem;margin:0'>AI Confidence (TTA avg): <b>{conf:.1f}%</b></p>
                        </div>""", unsafe_allow_html=True)
                        st.progress(conf / 100)

                        with st.expander("Probable AI Top 3 Matches"):
                            rank_icons = ["🥇", "🥈", "🥉"]
                            for i, r in enumerate(results):
                                icon = rank_icons[i] if i < len(rank_icons) else "•"
                                st.markdown(f"{icon} **{r['name']}** — `{r['confidence']:.1f}%`")
                                st.progress(r["confidence"] / 100)

                        if not healthy and conf >= CONF_THRESHOLD_ALERT:
                            farmer_district = st.session_state.get("farmer_district", "")
                            farmer_name_s   = st.session_state.get("farmer_name", "")
                            farmer_phone_s  = st.session_state.get("farmer_phone", "")

                            nearby_count = get_registered_farmers_count(farmer_district)
                            nearby_count = max(nearby_count, 1)

                            st.markdown(f"""
                            <div class='alert-box'>
                                <b>{name} detected in {farmer_district} district!</b><br>
                                <small>There are <b>{nearby_count}</b> registered farmers in your district who could be at risk. Alert them instantly.</small>
                            </div>""", unsafe_allow_html=True)

                            alert_key = f"alerted_{name}_{uploaded.name}"
                            if alert_key not in st.session_state:
                                st.session_state[alert_key] = False

                            if not st.session_state[alert_key]:
                                if st.button(
                                    f"Alert {nearby_count} Farmers in {farmer_district} | शेतकऱ्यांना अलर्ट पाठवा",
                                    type="primary",
                                    use_container_width=True,
                                    key=f"btn_alert_{alert_key}"
                                ):
                                    crop_hint = "Pest" if is_pest_mode else "Disease"
                                    append_alert_to_excel(
                                        reporter_name=farmer_name_s,
                                        reporter_phone=farmer_phone_s,
                                        district=farmer_district,
                                        crop=crop_hint,
                                        disease=name,
                                        confidence=conf
                                    )
                                    st.session_state[alert_key] = True
                                    st.rerun()
                            else:
                                st.success(
                                    f"Alert successfully sent to **{nearby_count}** registered farmers in **{farmer_district}** district!"
                                )

                        history_entry = {
                            "name":    name,
                            "type":    "pest" if is_pest_mode else "disease",
                            "healthy": healthy,
                            "conf":    conf,
                            "time":    datetime.now().strftime("%d %b %Y, %I:%M %p"),
                            "district": st.session_state.get("farmer_district", "")
                        }
                        if "detection_history" not in st.session_state:
                            st.session_state["detection_history"] = []
                        if not st.session_state["detection_history"] or \
                           st.session_state["detection_history"][-1]["name"] != name:
                            st.session_state["detection_history"].append(history_entry)

                        # Generate AI Advisory & Voice Output
                        with st.spinner(f"Generating {lang_name} advisory & remedies..."):
                            ai_resp = get_ai_advisory(name, is_pest_mode, lang_name, conf)

                            audio_bytes = None
                            if enable_voice:
                                try:
                                    audio_bytes = text_to_speech(ai_resp, lang_code)
                                except Exception:
                                    audio_bytes = None

                            st.markdown(f"<div class='chat-box'>{ai_resp.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

                            # RENDER VOICE PLAYER (Autoplay HTML + standard audio widget)
                            if enable_voice and audio_bytes:
                                st.markdown("#### 🔊 Voice Advisory / आवाज उत्तर")
                                st.markdown(audio_html(audio_bytes), unsafe_allow_html=True)
                                st.audio(audio_bytes, format="audio/mp3")

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 2: TREATMENT AI CHATBOT (CHEMICAL & ORGANIC)
# ─────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### Krishi AI Specialist Chatbot / कृषी उपचार चॅटबॉट")
    st.markdown("Ask any crop disease, pest issue, or treatment query. Get **Chemical (रसायनिक)** and **Organic (जैविक)** solutions instantly!")

    st.markdown("#### Quick Questions / जलद प्रश्न:")
    c1, c2, c3, c4 = st.columns(4)
    quick_q = None
    if c1.button("Rice Stem Borer Spray?", use_container_width=True):
        if lang_name == "English":
            quick_q = "What is the chemical and organic treatment for Rice Stem Borer?"
        elif lang_name == "Hindi":
            quick_q = "धान की फसल के खोड कीट (Stem Borer) के लिए रासायनिक एवं जैविक उपाय बताएं।"
        else:
            quick_q = "धान्य / तांदूळ पिकावरील खोड कीडीसाठी रसायनिक आणि सेंद्रिय उपाय सांगा."

    if c2.button("Organic Control for Aphids?", use_container_width=True):
        if lang_name == "English":
            quick_q = "How to prepare organic pesticide and Neem oil for Aphids control?"
        elif lang_name == "Hindi":
            quick_q = "माहू (Aphids) के लिए जैविक एवं नीम तेल दवा कैसे तैयार करें?"
        else:
            quick_q = "मावा (Aphids) साठी जैविक आणि सेंद्रिय औषध कसे तयार करावे?"

    if c3.button("Sugarcane Red Rot Remedy?", use_container_width=True):
        if lang_name == "English":
            quick_q = "What chemical spray and organic remedy is recommended for Sugarcane Red Rot?"
        elif lang_name == "Hindi":
            quick_q = "गन्ने के लाल सड़न (Red Rot) रोग के लिए कौन सी दवा का छिड़काव करें?"
        else:
            quick_q = "उसावरील तांबेरा व तांबड्या रोगासाठी कोणते औषध फवारावे?"

    if c4.button("Cotton Pink Bollworm Spray?", use_container_width=True):
        if lang_name == "English":
            quick_q = "Tell effective chemical and bio-control remedies for Cotton Pink Bollworm."
        elif lang_name == "Hindi":
            quick_q = "कपास की गुलाबी सुंडी (Pink Bollworm) के लिए प्रभावी उपचार बताएं।"
        else:
            quick_q = "कपाशीवरील गुलाबी बोंडअळीसाठी प्रभावी उपाय सांगा."

    if "bot_history" not in st.session_state:
        st.session_state.bot_history = []

    user_input = st.chat_input("उदा. उसावरील कीडीसाठी सेंद्रिय उपाय सांगा... Ask crop remedy...")
    active_query = user_input or quick_q

    if active_query:
        st.session_state.bot_history.append({"role": "user", "content": active_query})

        q_lower = active_query.lower().strip()
        is_gibberish = is_gibberish_query(active_query)

        greeting_keywords = [
            "hello", "hi", "hey", "namaste", "namaskar", "नमस्कार", "नमस्ते", "हॅलो", "हाय", "हाय्",
            "who are you", "who r u", "tu kon ahes", "तुम्ही कोण आहात", "कोण आहात", "who made you",
            "how are you", "kasa ahes", "कसे आहात", "help", "मदत करा", "धन्यवाद", "thank you", "thanks"
        ]
        is_greeting = any(k in q_lower for k in greeting_keywords) and len(active_query.split()) <= 5
        is_agri_related = is_agri_related_query(active_query)

        if is_gibberish:
            prompt_chat = f"""
            You are Krishi Mitra (कृषी मित्र), a polite human agricultural expert in Maharashtra.
            User Input: "{active_query}"
            STRICT LANGUAGE INSTRUCTION: Respond ONLY in {lang_name} native script ({lang_name}). Do NOT use English or other languages.

            The user input appears to be random characters or keyboard mashing.
            Reply in a warm, polite human formal tone explaining you could not understand their message.
            """
        elif is_greeting:
            prompt_chat = f"""
            You are Krishi Mitra (कृषी मित्र), a caring, expert human agricultural scientist advising a farmer in Maharashtra.
            User Query: {active_query}
            STRICT LANGUAGE INSTRUCTION: Respond ONLY in {lang_name} native script ({lang_name}).

            Greet the farmer warmly with respect and introduce yourself.
            """
        elif not is_agri_related:
            prompt_chat = f"""
            You are Krishi Mitra (कृषी मित्र), an expert agricultural assistant in Maharashtra.
            User Input: "{active_query}"
            STRICT LANGUAGE INSTRUCTION: Respond ONLY in {lang_name} native script ({lang_name}).

            Ask them politely to specify their crop disease or pest issue.
            """
        else:
            prompt_chat = f"""
            You are Krishi Mitra (कृषी मित्र), an expert human agricultural scientist advising a farmer in Maharashtra.
            User Query: {active_query}
            STRICT LANGUAGE INSTRUCTION: Write your complete response ONLY in {lang_name} native script ({lang_name}).

            Provide detailed Chemical Spray & Organic Remedies with exact dosages.
            """

        try:
            if GEMINI_KEY:
                genai.configure(api_key=GEMINI_KEY)
                gmodel = genai.GenerativeModel("gemini-1.5-flash")
                bot_ans = gmodel.generate_content(prompt_chat).text
            else:
                if is_gibberish:
                    bot_ans = "**मला आपला संदेश स्पष्टपणे समजला नाही.** कृपया आपले पीक, रोग किंवा शेतीविषयीचा प्रश्न विचारा."
                elif is_greeting:
                    bot_ans = "**नमस्कार! मी महाकृषि AI सहाय्यक आहे.** मी तुम्हाला पिकांचे रोग, कीड व उपचारांमध्ये मदत करू शकतो."
                elif not is_agri_related:
                    bot_ans = "**कृपया तुमचे पीक, रोग किंवा कीड कोणती आहे ते सांगू शकाल का?**"
                else:
                    bot_ans = f"**कृषी सल्ला (प्रश्न: {active_query}):**\n\n• **रसायनिक फवारणी:** इमॅमेक्टिन ०.५ ग्रॅम/लिटर फवारा.\n• **सेंद्रिय उपाय:** ५% कडुनिंब तेल (Neem Oil) ५ मिली/लिटर फवारा.\n• **हेल्पलाइन:** 1800-180-1551"
        except Exception:
            bot_ans = "कृपया कृषी हेल्पलाइन 1800-180-1551 वर संपर्क साधा."

        st.session_state.bot_history.append({"role": "assistant", "content": bot_ans})

        # VOICE GENERATION FOR CHATBOT
        if enable_voice:
            try:
                chat_audio = text_to_speech(bot_ans, lang_code)
                st.session_state["last_chat_audio"] = chat_audio
            except Exception:
                pass

    for msg in st.session_state.bot_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])

    # Play latest chatbot audio response
    if enable_voice and st.session_state.get("last_chat_audio"):
        st.markdown("#### 🔊 Voice Response / आवाज उत्तर")
        st.markdown(audio_html(st.session_state["last_chat_audio"]), unsafe_allow_html=True)
        st.audio(st.session_state["last_chat_audio"], format="audio/mp3")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 3: SPECIALIST HELPLINE & EXPERT DIRECTORY
# ─────────────────────────────────────────────────────────────
with tab_contacts:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### Verified Agricultural Specialist Directory & Emergency Helplines")

    st.markdown("""
    <div style='background:#FFEBEE;border:2px solid #FFCDD2;border-radius:12px;padding:16px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center'>
        <div>
            <h4 style='color:#C62828;margin:0'>Toll-Free Kisan Call Center (राष्ट्रीय कृषी हेल्पलाइन)</h4>
            <p style='color:#B71C1C;margin:2px 0 0;font-size:0.9rem'>Call for free instant expert advice in Marathi, Hindi & English (6 AM - 10 PM)</p>
        </div>
        <a href='tel:18001801551' style='background:#C62828;color:white;padding:10px 20px;border-radius:30px;text-decoration:none;font-weight:bold'>1800-180-1551</a>
    </div>""", unsafe_allow_html=True)

    r1, r2, r3, r4 = st.tabs(["State & National", "Western MH & Pune", "Marathwada & Nashik", "Vidarbha & Cotton"])

    with r1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>Kisan Call Center (KCC)</h4>
                <p><b>Number:</b> 1800-180-1551 (Toll-Free)<br>
                <b>Languages:</b> Marathi, Hindi, English<br>
                <b>Timings:</b> 6:00 AM - 10:00 PM (Daily)</p>
                <a href='tel:18001801551'>Call KCC Now</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>Maharashtra Agriculture Dept (कृषी आयुक्तालय)</h4>
                <p><b>Helpline:</b> 1800-233-4000 / 14447<br>
                <b>Location:</b> Shivajinagar, Pune<br>
                <b>Services:</b> Crop advice, Subsidies, Disease alerts</p>
                <a href='tel:18002334000'>Call State Agri Helpline</a>
            </div>""", unsafe_allow_html=True)

    with r2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>KVK Baramati (Pune District)</h4>
                <p><b>Phone:</b> 02112-255227 / 255327<br>
                <b>Speciality:</b> Sugarcane, Fruits, Pest Control</p>
                <a href='tel:02112255227'>Call KVK Baramati</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>Vasantdada Sugar Institute (VSI Pune)</h4>
                <p><b>Phone:</b> 020-26902100 / 26902200<br>
                <b>Speciality:</b> Sugarcane Red Rot, Pokkah Boeng</p>
                <a href='tel:02026902100'>Call VSI Experts</a>
            </div>""", unsafe_allow_html=True)

    with r3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>KVK Yashwantrao Chavan (Nashik)</h4>
                <p><b>Phone:</b> 0253-2415121 / 2415321<br>
                <b>Speciality:</b> Grapes, Onion, Vegetables</p>
                <a href='tel:02532415121'>Call KVK Nashik</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>MPKV Rahuri Agri University</h4>
                <p><b>Phone:</b> 02426-243208 / 243311<br>
                <b>Speciality:</b> Pulses, Rice Blast, Crop Pathology</p>
                <a href='tel:02426243208'>Call MPKV Rahuri</a>
            </div>""", unsafe_allow_html=True)

    with r4:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>ICAR - CICR Cotton Experts (Nagpur)</h4>
                <p><b>Phone:</b> 07103-275536 / 275538<br>
                <b>Speciality:</b> Pink Bollworm, Cotton Leaf Curl</p>
                <a href='tel:07103275536'>Call CICR Cotton Helpline</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>Dr. PDKV Agri University (Akola)</h4>
                <p><b>Phone:</b> 0724-2258419<br>
                <b>Speciality:</b> Soybean, Cotton, Grain Crop Protection</p>
                <a href='tel:07242258419'>Call PDKV Akola</a>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Request Direct Specialist Callback / तज्ज्ञ कॉल विनंती")
    with st.form("specialist_form"):
        fc1, fc2, fc3 = st.columns(3)
        farmer_name = fc1.text_input("शेतकऱ्याचे नाव / Farmer Name",
                                     value=st.session_state.get("farmer_name", ""))
        farmer_phone = fc2.text_input("मोबाईल नंबर / Mobile Number",
                                      value=st.session_state.get("farmer_phone", ""))
        farmer_dist = fc3.selectbox(
            "जिल्हा / District",
            ALL_DISTRICTS,
            index=ALL_DISTRICTS.index(st.session_state.get("farmer_district", "Pune"))
                  if st.session_state.get("farmer_district", "Pune") in ALL_DISTRICTS else 0
        )
        crop_query = st.text_area("पिकाची समस्या सांगा / Describe Crop Problem")
        submit_form = st.form_submit_button("Submit Request / विनंती पाठवा", type="primary")

        if submit_form:
            st.success(f"धन्यवाद {farmer_name}! तुमची विनंती नोंदवली गेली आहे. कृषी तज्ज्ञ २४ तासांत {farmer_phone} वर संपर्क साधतील.")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 4: NEARBY FARMER OUTBREAK MAP & ALERT SYSTEM
# ─────────────────────────────────────────────────────────────
with tab_map:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### Nearby Farmer Disease & Pest Outbreak Alert Map")

    if os.path.exists(EXCEL_ALERTS_FILE):
        try:
            alerts_df = pd.read_excel(EXCEL_ALERTS_FILE, dtype=str)
            if not alerts_df.empty:
                st.markdown("#### Recent AI-Detected Alerts (from Registered Farmers):")
                st.dataframe(
                    alerts_df[["Timestamp", "Reporter_Name", "District", "Crop_Disease", "Confidence_Pct"]]
                    .tail(10)
                    .rename(columns={
                        "Timestamp": "Date/Time",
                        "Reporter_Name": "Reported By",
                        "District": "District",
                        "Crop_Disease": "Disease/Pest",
                        "Confidence_Pct": "AI Confidence (%)"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        except Exception:
            pass

    outbreaks = [
        {"district": "Nashik", "lat": 20.0059, "lon": 73.7898, "issue": "Fall Armyworm (लष्करी अळी)", "crop": "Maize / मका", "severity": "Emergency Outbreak", "radius": 15000, "color": [211, 47, 47, 180]},
        {"district": "Kolhapur", "lat": 16.7050, "lon": 74.2433, "issue": "Sugarcane Red Rot (ऊस तांबेरा)", "crop": "Sugarcane / ऊस", "severity": "Warning", "radius": 20000, "color": [245, 124, 0, 180]},
        {"district": "Pune (Baramati)", "lat": 18.1519, "lon": 74.5768, "issue": "Early Shoot Borer (खोड कीड)", "crop": "Sugarcane / ऊस", "severity": "Emergency Outbreak", "radius": 12000, "color": [211, 47, 47, 180]},
        {"district": "Nagpur", "lat": 21.1458, "lon": 79.0882, "issue": "Pink Bollworm (गुलाबी बोंडअळी)", "crop": "Cotton / कापूस", "severity": "Emergency Outbreak", "radius": 25000, "color": [211, 47, 47, 180]},
        {"district": "Sambhajinagar", "lat": 19.8762, "lon": 75.3433, "issue": "Whitefly Pest (पांढरी माशी)", "crop": "Cotton / कापूस", "severity": "Advisory Watch", "radius": 18000, "color": [251, 192, 45, 180]},
        {"district": "Solapur", "lat": 17.6599, "lon": 75.9064, "issue": "Aphids Damage (मावा)", "crop": "Vegetables / भाजीपाला", "severity": "Warning", "radius": 10000, "color": [245, 124, 0, 180]}
    ]

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=outbreaks,
        get_position="[lon, lat]",
        get_color="color",
        get_radius="radius",
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_min_pixels=10,
        radius_max_pixels=40
    )

    view_state = pdk.ViewState(
        latitude=19.5,
        longitude=76.0,
        zoom=6.2,
        pitch=30
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"html": "<b>{district}</b><br><b>Issue:</b> {issue}<br><b>Crop:</b> {crop}<br><b>Status:</b> {severity}"}
    )

    st.pydeck_chart(r)

    st.markdown("#### Active Regional Outbreak Alerts:")
    m1, m2 = st.columns(2)
    for idx, ob in enumerate(outbreaks):
        target_col = m1 if idx % 2 == 0 else m2
        with target_col:
            badge_type = "badge-emergency" if "Emergency" in ob["severity"] else ("badge-warning" if "Warning" in ob["severity"] else "badge-success")
            reg_count = get_registered_farmers_count(ob["district"].split(" ")[0])
            reg_info  = f" | <b>Registered Farmers:</b> {reg_count}" if reg_count > 0 else ""
            st.markdown(f"""
            <div class='contact-card'>
                <span class='{badge_type}'>{ob['severity']}</span>
                <h4 style='margin:8px 0 2px;color:#1F4E2B'>{ob['district']} — {ob['issue']}</h4>
                <p style='margin:0;font-size:0.88rem;color:#558B2F'>
                <b>Affected Crop:</b> {ob['crop']} | <b>Impact Radius:</b> {ob['radius']//1000} km{reg_info}
                </p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Broadcast New Disease/Pest Alert to Nearby Farmers")
    with st.form("alert_broadcast"):
        ac1, ac2, ac3 = st.columns(3)
        b_dist  = ac1.selectbox("जिल्हा / District", ALL_DISTRICTS)
        b_crop  = ac2.text_input("पीक / Crop Name", "Sugarcane / कापूस / धान")
        b_issue = ac3.selectbox("रोग / कीड / Issue Type", ["Pink Bollworm", "Fall Armyworm", "Red Rot", "Rice Blast", "Aphids", "Whitefly"])
        b_desc  = st.text_area("अलर्ट माहिती / Detailed Outbreak Description")
        broadcast_btn = st.form_submit_button("Broadcast SMS & Map Alert | अलर्ट जारी करा", type="primary")

        if broadcast_btn:
            reg_in_dist = get_registered_farmers_count(b_dist)
            reach = max(reg_in_dist, 1)
            append_alert_to_excel(
                reporter_name=st.session_state.get("farmer_name", "Unknown"),
                reporter_phone=st.session_state.get("farmer_phone", ""),
                district=b_dist,
                crop=b_crop,
                disease=b_issue,
                confidence=100.0
            )
            st.success(
                f"अलर्ट यशस्वीपणे पाठवला! **{b_dist}** परिसरातील **{reach}** नोंदणीकृत शेतकऱ्यांना **{b_issue}** बद्दल अलर्ट पाठवण्यात आला आहे."
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 5: GOVERNMENT SCHEMES & SUBSIDIES PORTAL
# ─────────────────────────────────────────────────────────────
with tab_schemes:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### Official Government Agricultural Schemes & Subsidies Portal")

    schemes = [
        {
            "name": "PM-KISAN (प्रधानमंत्री किसान सन्मान निधी)",
            "cat": "Cash Benefit",
            "benefit": "₹6,000 / Year (3 equal installments of ₹2,000 direct bank transfer)",
            "eligibility": "Small & Marginal Farmers owning cultivable land",
            "link": "https://pmkisan.gov.in/",
            "docs": "7/12 Extract, Aadhaar Card, Bank Passbook"
        },
        {
            "name": "PM Fasal Bima Yojana (पीक विमा योजना)",
            "cat": "Insurance",
            "benefit": "Comprehensive crop loss coverage against drought, flood & pest attacks for ₹1 premium",
            "eligibility": "All farmers growing notified crops in MH",
            "link": "https://pmfby.gov.in/",
            "docs": "Sowing Certificate, 7/12, Aadhaar, Bank Details"
        },
        {
            "name": "MahaDBT Farmer Portal (महाडीबीटी कृषी योजना)",
            "cat": "Subsidy",
            "benefit": "50% - 80% subsidy on Tractors, Rotavators, Seeds, Drip Irrigation & Implements",
            "eligibility": "Maharashtra farmers with valid 7/12 & 8A",
            "link": "https://mahadbt.maharashtra.gov.in/",
            "docs": "Aadhaar, 7/12, 8A, Caste Certificate (if applicable)"
        },
        {
            "name": "PoCRA (नानाजी देशमुख कृषी संजीवनी प्रकल्प)",
            "cat": "Climate Action",
            "benefit": "100% financial assistance for Shade Net, Polyhouse, Farm Ponds & Drip Irrigation",
            "eligibility": "Drought-prone villages across Marathwada & Vidarbha",
            "link": "https://pocra.mahagov.in/",
            "docs": "7/12, Aadhaar, Bank Passbook"
        },
        {
            "name": "Magel Tyala Solar Pump (मागेल त्याला सोलर पंप)",
            "cat": "Solar & Irrigation",
            "benefit": "90% - 95% subsidy for 3 HP, 5 HP & 7.5 HP Off-Grid Solar Agriculture Pumps",
            "eligibility": "Farmers with water source but no regular electricity connection",
            "link": "https://www.mahadiscom.in/solar-mpskvy/",
            "docs": "7/12, Water Availability Certificate, Aadhaar"
        },
        {
            "name": "Kisan Credit Card (KCC - किसान क्रेडिट कार्ड)",
            "cat": "Loan",
            "benefit": "Crop loans up to ₹3 Lakh at 4% interest rate",
            "eligibility": "Landowners, tenant farmers & self-help groups",
            "link": "https://www.myscheme.gov.in/",
            "docs": "7/12, Land Record, KYC Documents"
        },
        {
            "name": "PMKSY Drip & Micro Irrigation (ठिबक सिंचन अनुदान)",
            "cat": "Irrigation",
            "benefit": "80% subsidy for small/marginal farmers and 75% for other farmers for drip/sprinkler",
            "eligibility": "Farmers with permanent water source",
            "link": "https://pmksy.gov.in/",
            "docs": "Water Source Certificate, 7/12, Quotation"
        },
        {
            "name": "Paramparagat Krishi Vikas Yojana (PKVY - सेंद्रिय शेती)",
            "cat": "Organic Farming",
            "benefit": "₹50,000 per hectare support for organic inputs, certification & marketing",
            "eligibility": "Farmer clusters forming organic farming groups",
            "link": "https://pgsindia-ncof.gov.in/",
            "docs": "Group Registration, Land Details"
        }
    ]

    sc1, sc2 = st.columns(2)
    for idx, sc in enumerate(schemes):
        target_col = sc1 if idx % 2 == 0 else sc2
        with target_col:
            st.markdown(f"""
            <div class='scheme-card' style='margin-bottom:16px'>
                <span class='figma-badge' style='background:#1F4E2B;color:white'>{sc['cat']}</span>
                <h4 style='margin-top:10px'>{sc['name']}</h4>
                <p><b>Benefit:</b> {sc['benefit']}<br>
                <b>Eligibility:</b> {sc['eligibility']}<br>
                <b>Required Docs:</b> {sc['docs']}</p>
            </div>""", unsafe_allow_html=True)
            st.link_button(f"Apply Now ({sc['name'].split()[0]})", sc['link'], use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:20px;color:#558B2F;font-size:0.85rem;border-top:1px solid #DCEDC8;margin-top:40px'>
<b>MahaKrishi AI</b> | महाकृषि | Maharashtra Government Hackathon Initiative<br>
Powered by PyTorch EfficientNet-B0 + Google Gemini AI + gTTS Voice Advisory + PyDeck Outbreak Maps
</div>
""", unsafe_allow_html=True)

