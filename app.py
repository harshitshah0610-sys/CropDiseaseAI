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
import pydeck as pdk
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CUSTOM BRAND MARK (hand-built SVG, no stock photography)
# ─────────────────────────────────────────────────────────────
def logo_svg(size: int = 80) -> str:
    """A single sprout/leaf mark in a rounded badge — the app's own
    geometric mark rather than a generic photo or emoji."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="mkLogoGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#388E3C"/>
          <stop offset="100%" stop-color="#1B5E20"/>
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="96" height="96" rx="26" fill="url(#mkLogoGrad)"/>
      <path d="M50 80 C50 80 28 62 28 40 C28 24 41 14 60 15 C60 15 63 35 49 50 C40 59 50 80 50 80 Z"
            fill="#FFFFFF"/>
      <path d="M49 50 C49 50 38 41 37 29" stroke="#1B5E20" stroke-width="2.4"
            fill="none" stroke-linecap="round" opacity="0.45"/>
    </svg>"""

UPLOAD_ICON_SVG = """<svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="#558B2F" stroke-width="1.6">
  <path d="M4 16.5V18a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 3v12m0-12 4 4m-4-4-4 4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

SCAN_ICON_SVG = """<svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" stroke-width="1.6">
  <path d="M12 21c-4-3-7-6.5-7-10.5A7 7 0 0 1 12 4a7 7 0 0 1 7 6.5C19 14.5 16 18 12 21Z" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="12" cy="11" r="2.3"/>
</svg>"""

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG (FIGMA DASHBOARD LAYOUT)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MahaKrishi AI | महाकृषि",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# FIGMA-INSPIRED MODERN AGRI CSS STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif;
    }

    /* Main Header Figma Banner */
    .figma-header {
    background: linear-gradient(120deg, #1B5E20 0%, #2E7D32 45%, #388E3C 70%, #2E7D32 100%);
    background-size: 200% 200%;
    animation: headerShift 10s ease-in-out infinite;
    padding: 20px 28px;
    border-radius: 20px;
    margin-bottom: 24px;
    color: white;
    box-shadow: 0 14px 34px rgba(27, 94, 32, 0.32), inset 0 1px 0 rgba(255,255,255,0.12);
    border: 1px solid rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}
    @keyframes headerShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    .figma-header-title { font-size: 2.2rem; font-weight: 700; margin: 0; color: #FFFFFF; }
    .figma-header-sub { font-size: 1rem; color: #C8E6C9; margin-top: 6px; }

    /* Status dot — replaces the old colored emoji circles */
    .status-dot {
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        background: #A5D6A7; margin-right: 6px; vertical-align: middle;
        box-shadow: 0 0 0 rgba(165,214,167,0.7);
        animation: statusPulse 2s infinite;
    }
    @keyframes statusPulse {
        0%   { box-shadow: 0 0 0 0 rgba(165,214,167,0.6); }
        70%  { box-shadow: 0 0 0 7px rgba(165,214,167,0); }
        100% { box-shadow: 0 0 0 0 rgba(165,214,167,0); }
    }

  .figma-badge {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #E8F5E9;
    border: 1px solid rgba(255, 255, 255, 0.3);
    white-space: nowrap;
    flex-shrink: 0;
    align-self: flex-start;
}

    /* Cards */
    .figma-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: transform 0.35s cubic-bezier(0.2,0.8,0.2,1), box-shadow 0.35s ease;
        transform-style: preserve-3d;
        will-change: transform;
        animation: cardRiseIn 0.5s cubic-bezier(0.2,0.8,0.2,1) both;
    }
    .figma-card:hover {
        transform: perspective(800px) rotateX(1.5deg) translateY(-6px) scale(1.008);
        box-shadow: 0 18px 38px rgba(27,94,32,0.16);
    }

    @keyframes cardRiseIn {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Login Card */
    .login-card {
        background: linear-gradient(145deg, #FFFFFF, #F1F8E9);
        border-radius: 20px;
        padding: 36px 40px;
        border: 1px solid #C8E6C9;
        box-shadow: 0 8px 32px rgba(27, 94, 32, 0.12);
        max-width: 520px;
        margin: 0 auto;
    }

    /* Status Badges */
    .badge-emergency { background: #FFEBEE; color: #C62828; border: 1px solid #FFCDD2; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.82rem; }
    .badge-warning   { background: #FFF3E0; color: #EF6C00; border: 1px solid #FFE0B2; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.82rem; }
    .badge-success   { background: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.82rem; }
    .badge-low-conf  { background: #FFF9C4; color: #F57F17; border: 1px solid #FFF176; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.82rem; }

    /* Remedy Container */
    .remedy-chemical {
        background: #FFF8E1;
        border-left: 5px solid #FFA000;
        border-radius: 0 14px 14px 0;
        padding: 18px;
        margin: 12px 0;
    }
    .remedy-organic {
        background: #E8F5E9;
        border-left: 5px solid #4CAF50;
        border-radius: 0 14px 14px 0;
        padding: 18px;
        margin: 12px 0;
    }

    /* Chat Box */
    .chat-box {
        background: #F9FBE7;
        border-left: 5px solid #8BC34A;
        border-radius: 0 14px 14px 0;
        padding: 20px;
        margin: 12px 0;
        font-size: 1rem;
        line-height: 1.8;
    }

    /* Alert box */
    .alert-box {
        background: #FFF3E0;
        border: 2px solid #FF9800;
        border-radius: 14px;
        padding: 16px 20px;
        margin: 12px 0;
    }

    /* Audio section */
    .audio-section {
        background: #E3F2FD;
        border: 1px solid #90CAF9;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }

    /* Scheme Card */
    .scheme-card {
        background: #FFFFFF;
        border: 1px solid #C8E6C9;
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    }
    .scheme-card h4 { color: #1B5E20; margin-top: 0; }

    /* Contact Card */
    .contact-card {
        background: #FAFAFA;
        border: 1px solid #E0E0E0;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
    }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* ───────────── MOBILE RESPONSIVENESS ───────────── */
@media (max-width: 768px) {
  .figma-header { padding: 14px 16px; border-radius: 14px; flex-direction: column; align-items: flex-start; }
  .figma-header-title { font-size: 1.4rem; line-height: 1.2; }
  .figma-header-sub { font-size: 0.85rem; }
  .figma-badge { font-size: 0.72rem; padding: 6px 12px; }
  .figma-card { padding: 14px; border-radius: 12px; margin-bottom: 14px; }
  .login-card { padding: 22px 18px; max-width: 100%; border-radius: 16px; }
  .remedy-chemical, .remedy-organic, .chat-box, .alert-box, .audio-section, .scheme-card, .contact-card {
    padding: 12px; font-size: 0.92rem;
  }
  h1 { font-size: 1.5rem !important; }
  h2 { font-size: 1.25rem !important; }
  h3 { font-size: 1.1rem !important; }
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
  .stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; }

  /* Profile page mobile layout */
  .profile-avatar { width: 70px !important; height: 70px !important; font-size: 1.7rem !important; }
  .profile-name { font-size: 1.15rem !important; }
  .profile-meta { font-size: 0.82rem !important; }
  div[data-testid="stMetric"] { padding: 6px 2px !important; }
  div[data-testid="stMetricValue"] { font-size: 1.3rem !important; }
  div[data-testid="stMetricLabel"] { font-size: 0.72rem !important; }
}

@media (max-width: 380px) {
  .figma-header-title { font-size: 1.2rem; }
  img { max-width: 100%; height: auto; }
}

/* Profile icon button (top-right) */
div[data-testid="column"]:nth-of-type(2) button[kind="secondary"] {
    border-radius: 50% !important;
    width: 46px !important;
    height: 46px !important;
    padding: 0 !important;
    font-size: 1.3rem !important;
    background: linear-gradient(135deg, #2E7D32, #1B5E20) !important;
    color: white !important;
    border: 2px solid #A5D6A7 !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="column"]:nth-of-type(2) button[kind="secondary"]:hover {
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 8px 18px rgba(27,94,32,0.35) !important;
}
div[data-testid="column"]:nth-of-type(2) button[kind="secondary"]:active {
    transform: translateY(0) scale(0.96) !important;
}

/* Buttons — subtle 3D lift + press feedback across the whole app */
.stButton > button {
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(27,94,32,0.22) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* Tabs — animated underline instead of a flat highlight */
.stTabs [data-baseweb="tab-list"] button {
    transition: color 0.2s ease;
}
.stTabs [data-baseweb="tab-highlight"] {
    transition: left 0.3s cubic-bezier(0.4,0,0.2,1), width 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    background-color: #1B5E20 !important;
}

/* Page-level fade-in on load */
.main .block-container {
    animation: pageFadeIn 0.45s ease both;
}
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
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
EXCEL_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "detection_history.xlsx")

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
def append_signin_to_excel(name: str, phone: str, district: str, action: str):
    """Append a farmer sign-in/register entry to the shared Excel file."""
    new_row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name,
        "Phone": phone,
        "District": district,
        "Action": action
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
            return {"name": row.get("Name", ""), "district": row.get("District", "")}
    except Exception:
        pass
    return None


def append_detection_history(phone: str, name: str, district: str, category: str,
                              crop_or_pest_type: str, result_name: str, confidence: float):
    """Log every AI detection (disease or pest) for the logged-in farmer's profile history."""
    new_row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Phone": phone,
        "Name": name,
        "District": district,
        "Category": category,          # "Disease" or "Pest"
        "Crop_Type": crop_or_pest_type,
        "Result": result_name,
        "Confidence_Pct": round(confidence, 1)
    }
    if os.path.exists(EXCEL_HISTORY_FILE):
        try:
            existing = pd.read_excel(EXCEL_HISTORY_FILE, dtype=str)
            updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        except Exception:
            updated = pd.DataFrame([new_row])
    else:
        updated = pd.DataFrame([new_row])
    updated.to_excel(EXCEL_HISTORY_FILE, index=False)


def get_user_history(phone: str) -> pd.DataFrame:
    """Return this farmer's past detections, most recent first."""
    if not os.path.exists(EXCEL_HISTORY_FILE):
        return pd.DataFrame()
    try:
        df = pd.read_excel(EXCEL_HISTORY_FILE, dtype=str)
        df = df[df["Phone"] == phone.strip()]
        return df.sort_values("Timestamp", ascending=False)
    except Exception:
        return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# LOGIN / REGISTER GATE
# ─────────────────────────────────────────────────────────────

def show_login_page():
    st.markdown("""
    <div style='text-align:center;padding:30px 0 10px'>
        <div style="display:flex;justify-content:center;margin-bottom:10px">""" + logo_svg(96) + """</div>
        <h1 style='color:#1B5E20;font-size:2rem;margin:0'>""" + _t('title') + """</h1>
        <p style='color:#2E7D32;font-size:1rem;margin:4px 0 0'>""" + _t('subtitle') + """</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
                    # Initialize language in session state only ONCE
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
            si_phone = st.text_input(_t('mobile'), key="si_phone")
            if st.button(_t('signin_btn'), type="primary", use_container_width=True, key="btn_signin"):
                phone_clean = si_phone.strip()
                if not phone_clean or len(phone_clean) < 10:
                    st.error("Invalid number" if st.session_state["app_lang"]=="en" else "अवैध नंबर")
                else:
                    farmer_info = phone_exists(phone_clean)
                    if farmer_info:
                        append_signin_to_excel(farmer_info["name"], phone_clean, farmer_info["district"], "Sign-In")
                        st.session_state["logged_in"] = True
                        st.session_state["farmer_name"] = farmer_info["name"]
                        st.session_state["farmer_phone"] = phone_clean
                        st.session_state["farmer_district"] = farmer_info["district"]
                        st.rerun()
                    else:
                        st.error("Not found. Please register." if st.session_state["app_lang"]=="en" else "नंबर आढळला नाही. कृपया नोंदणी करा.")

        with tab_register:
            rg_name = st.text_input(_t('name'), key="rg_name")
            rg_phone = st.text_input(_t('mobile') + " ", key="rg_phone")
            rg_district = st.selectbox(_t('district'), ALL_DISTRICTS, key="rg_district")

            if st.button(_t('register_btn'), type="primary", use_container_width=True, key="btn_register"):
                name_clean, phone_clean = rg_name.strip(), rg_phone.strip()
                if not name_clean or not phone_clean or len(phone_clean) < 10:
                    st.error("Invalid details")
                else:
                    if phone_exists(phone_clean):
                        st.warning("Already registered")
                    else:
                        append_signin_to_excel(name_clean, phone_clean, rg_district, "Register")
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
    st.stop()   # Stop here — rest of app not shown until logged in

if "page" not in st.session_state:
    st.session_state["page"] = "main"


def show_profile_page():
    """Farmer profile & detection-history dashboard. Built mobile-first —
    single-column stack that widens gracefully on larger screens."""
    back_l, _ = st.columns([1, 3])
    with back_l:
        if st.button("Back", use_container_width=True):
            st.session_state["page"] = "main"
            st.rerun()

    name = st.session_state.get("farmer_name", "Farmer")
    phone = st.session_state.get("farmer_phone", "")
    district = st.session_state.get("farmer_district", "")

    st.markdown(f"""
    <div class='login-card' style='text-align:center;'>
        <div class='profile-avatar' style='width:90px;height:90px;border-radius:50%;
             background:linear-gradient(135deg,#2E7D32,#1B5E20);
             display:flex;align-items:center;justify-content:center;
             margin:0 auto 14px;font-size:2.2rem;color:white;'></div>
        <h2 class='profile-name' style='color:#1B5E20;margin:0;word-wrap:break-word;'>{name}</h2>
        <p class='profile-meta' style='color:#558B2F;margin:6px 0 0;font-size:0.95rem;'>
            {phone}<br>{district}
        </p>
    </div>
    """, unsafe_allow_html=True)

    history_df = get_user_history(phone)
    total = len(history_df)
    disease_count = int((history_df["Category"] == "Disease").sum()) if total else 0
    pest_count = int((history_df["Category"] == "Pest").sum()) if total else 0

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Your Activity")
    # 3 equal columns — Streamlit stacks these to full-width rows on narrow
    # screens automatically, and stMetric font sizes shrink via the CSS
    # media query above, so this stays readable on a phone.
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Scans", total)
    c2.metric("Diseases", disease_count)
    c3.metric("Pests", pest_count)

    st.markdown("### Detection History")
    if history_df.empty:
        st.info("No detections yet. Run a scan from the AI Detection tab to see your history here.")
    else:
        # On mobile, a wide dataframe forces horizontal scroll — so instead
        # of st.dataframe (bad on small screens), render each entry as a
        # stacked card that reads top-to-bottom naturally on a phone.
        for _, row in history_df.iterrows():
            badge_cls = "badge-warning" if row["Category"] == "Pest" else "badge-emergency"
            st.markdown(f"""
            <div class='contact-card'>
                <span class='{badge_cls}'>{row['Category']}</span>
                <span style='float:right;color:#888;font-size:0.8rem'>{row['Timestamp']}</span>
                <h4 style='margin:8px 0 2px;color:#1B5E20;word-wrap:break-word;'>{row['Result']}</h4>
                <p style='margin:0;font-size:0.88rem;color:#558B2F;word-wrap:break-word;'>
                    <b>Mode:</b> {row['Crop_Type']} &nbsp;|&nbsp; <b>Confidence:</b> {row['Confidence_Pct']}%
                </p>
            </div>""", unsafe_allow_html=True)


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

# Standard inference transform — 256 resize then 224 center-crop (EfficientNet-B0 best practice)
_val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# TTA augmentation variants
_tta_transforms = [
    # Original
    transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    # Horizontal flip
    transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.RandomHorizontalFlip(p=1.0),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    # Vertical flip
    transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.RandomVerticalFlip(p=1.0),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    # Slight crop variation (top-left corner crop)
    transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
]


def check_image_quality(pil_image: Image.Image) -> tuple[bool, str]:
    """
    Check if image is good enough for accurate inference.
    Returns (is_ok, warning_message).
    """
    img_array = np.array(pil_image.convert("L"))  # Grayscale

    # Darkness check: mean pixel brightness
    brightness = img_array.mean()
    if brightness < 40:
        return False, (
            "**Image too dark for accurate detection!**\n\n"
            "Please retake the photo in bright daylight or good lighting. "
            "Dark images cause the AI to give wrong predictions."
        )

    # Blur check: Laplacian variance (low = blurry)
    laplacian_var = np.var(np.gradient(img_array.astype(float)))
    if laplacian_var < 50:
        return False, (
            "**Image appears blurry or out of focus!**\n\n"
            "Please hold the camera steady and retake the photo closer to the leaf/plant. "
            "Blurry images significantly reduce detection accuracy."
        )

    return True, ""


def predict_crop_issue(model, class_names, pil_image: Image.Image):
    """
    Predict with Test-Time Augmentation (TTA):
    Run inference on 4 augmented versions and average softmax probabilities
    for more stable and accurate predictions.
    """
    rgb_image = pil_image.convert("RGB")
    all_probs = []

    with torch.no_grad():
        for tfm in _tta_transforms:
            tensor = tfm(rgb_image).unsqueeze(0).to(DEVICE)
            logits = model(tensor)[0]
            probs  = torch.softmax(logits, dim=0).cpu().numpy()
            all_probs.append(probs)

    # Average across TTA variants
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
# AUDIO & TEXT HELPERS
# ─────────────────────────────────────────────────────────────
def clean_text_for_speech(text):
    """Regex-based text cleaner for gTTS to produce clean Marathi/Hindi speech."""
    clean = re.sub(r'[*#`_~]', '', text)
    clean = re.sub(r'[]', '', clean)
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
    tts = gTTS(text=clean, lang=lang_code, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        path = f.name
    with open(path, 'rb') as f:
        audio_bytes = f.read()
    os.unlink(path)
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
           - Respectful warm greeting to the farmer.

        2. **पिकावर होणारा विघातक परिणाम (HOW THE DISEASE/PEST AFFECTS THE PLANT)**
           - Detail plant physiological damage: leaf chlorosis, sap-sucking damage, photosynthesis blockage, stem vascular clogging, fruit/boll boring, root rot, or severe yield reduction.

        3. **कीड / रोग येण्याची मुख्य कारणे (WHY THE PEST/DISEASE OCCURS)**
           - Explain triggers: high atmospheric humidity (>80%), cloudy monsoon weather, excessive nitrogen/urea fertilizer use, stubble residue, temperature fluctuations, and lack of natural beneficial insects.

        4. **रोगाचे / कीडीचे ३ मुख्य टप्पे (STAGES OF DISEASE / PEST INFESTATION)**
           - Describe Early Stage (प्राथमिक टप्पा - 1-5% infestation, mild leaf spotting, easily controlled by Neem Oil).
           - Describe Moderate Stage (मध्यम टप्पा - 10-30% infestation, active lesions & caterpillars, target chemical spray needed within 48 hours).
           - Describe Critical/Severe Stage (गंभीर / तीव्र टप्पा - 50%+ foliage damage, wilt/rot/boring, emergency systemic spray & burning infected plants required).

        5. **टप्पा १: प्रभावी रसायनिक फवारणी (STEP 1: CHEMICAL SPRAY SOLUTION WITH DOSAGES)**
           - Recommend specific chemical pesticides/fungicides (e.g., Profenofos 50% EC, Emamectin Benzoate 5% SG, Hexaconazole 5% EC, Chlorantraniliprole 18.5% SC).
           - Provide EXACT dosage per Liter of water AND per Acre (e.g., 2 ml/Liter or 400 ml/Acre in 200 Liters water).
           - Specify best spraying time (evening/early morning) and safety gear (mask, gloves).

        6. **टप्पा २: सेंद्रिय व जैविक घरगुती उपाय (STEP 2: ORGANIC & BIOLOGICAL SOLUTIONS)**
           - Detailed recipe for 5% Neem Oil (कडुनिंब तेल - 5 ml/L), Jeevamrut (जीवामृत), or Dashparni Ark (दशपर्णी अर्क - 5 ml/L).
           - Bio-control agents (Trichoderma viride @ 5g/L for soil diseases or Beauveria bassiana for insect pests).
           - Mechanical traps: Yellow and blue sticky traps (10-15 traps/Acre) or Pheromone traps (5 traps/Acre for bollworm/borer).

        7. **टप्पा ३: दीर्घकालीन शेत स्वच्छता व सुपीकता (STEP 3: LONG-TERM PREVENTION & FIELD HYGIENE)**
           - Cultural practices: Removing & burning infected plant parts.
           - Soil health management, crop rotation, and subsoil drainage.

        8. **मोफत कृषी हेल्पलाइन (HELPLINE SUPPORT)**
           - Toll-Free Kisan Call Center: 1800-180-1551.
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
                 return "**रामराम शेतकरी दादा!** \n\nतुमचे पीक पूर्णपणे निरोगी आहे!..."
             elif lang_name == "Hindi":
                  return "**नमस्कार किसान भाई!** \n\nआपकी फसल पूरी तरह स्वस्थ है!..."
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

**बीमारी / कीट प्रकोप के 3 चरण (Stages of Disease / Infestation):**
• **1. प्रारंभिक चरण (Early Stage):** पत्तियों पर छोटे धब्बे (1-5% प्रभाव)। 5% नीम तेल एवं स्टिकी ट्रैप से नियंत्रण संभव।
• **2. मध्यम चरण (Moderate Stage):** 10-30% प्रभाव। 48 घंटे के भीतर रसायनिक छिड़काव आवश्यक।
• **3. गंभीर चरण (Critical Stage):** 50%+ फसल प्रभावित, पत्तियां सूखना व सड़ना। तुरंत आपातकालीन सिस्टमिक स्प्रे व रोगग्रस्त पौधों को जलाना आवश्यक.

**चरण 1: रासायनिक छिड़काव (Chemical Treatment):**
• **दवा:** प्रोफेनोफॉस 50% EC (2 मिली प्रति लीटर पानी) या इमामेक्टिन बेंजोएट (0.5 ग्राम/लीटर)।
• **मात्रा:** 1 एकड़ के लिए 200 लीटर पानी में 400 मिली दवा मिलाकर छिड़काव करें।
• **सावधानी:** शाम के समय सुरक्षा मास्क पहनकर छिड़काव करें।

**चरण 2: जैविक एवं देसी उपाय (Organic Treatment):**
• **नीम तेल (Neem Oil):** 5 मिली नीम तेल प्रति लीटर पानी में मिलाकर स्प्रे करें।
• **दशपर्णी अर्क:** 5 मिली दशपर्णी अर्क का स्प्रे करें।
• **स्टिकी ट्रैप:** खेत में प्रति एकड़ 10-12 पीले व नीले स्टिकी ट्रैप लगाएं।

**चरण 3: दीर्घकालिक बचाव:**
• प्रभावित पत्तियों को खेत से बाहर नष्ट करें।

**हेल्पलाइन:** 1800-180-1551"""
        elif lang_name == "Gujarati":        # ADD FROM HERE
            return f"""**નમસ્કાર ખેડૂત ભાઈ/બહેન!** 
**શોધાયેલ રોગ / જીવાત:** **{issue_name}**

**પાક પર અસર:**
- આ રોગ અથવા જીવાત પાંદડાનો રસ ચૂસે છે, જેથી પ્રકાશ-સંશ્લેષણ અટકે છે અને ઉત્પાદન ૩૦-૫૦% ઘટે છે.

**ઉત્પત્તિનાં કારણો:**
- ભેજ, વાદળછાયું હવામાન અને વધુ પડતા નાઇટ્રોજનનો ઉપયોગ.

**રાસાયણિક સ્પ્રે:**
- પ્રોફેનોફોસ ૫૦% EC (૨ ml/લિટર) અથવા ઇમામેક્ટિન (૦.૫ ગ્રામ/લિટર).
- સાંજે માસ્ક પહેરીને છંટકાવ કરો.

**જૈવિક ઉપાય:**
- લીમડાનું તેલ ૫ ml/લિટર અથવા દશપર્ણી અર્ક ૫ ml/લિટર.
- ચીકણા પીળા-વાદળી ટ્રેપ એકર દીઠ ૧૦-૧૨ લગાવો.

**હેલ્પલાઇન:** 1800-180-1551"""

        elif lang_name == "Punjabi":
            return f"""**ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਭਰਾ/ਭੈਣ!** 
**ਪਛਾਣਿਆ ਗਿਆ ਰੋਗ / ਕੀਟ:** **{issue_name}**

**ਫਸਲ ਉੱਤੇ ਅਸਰ:**
- ਇਹ ਰੋਗ ਪੱਤਿਆਂ ਦਾ ਰਸ ਚੂਸਦਾ ਹੈ, ਜਿਸ ਨਾਲ ਝਾੜ ੩੦-੫੦% ਘੱਟਦਾ ਹੈ.

**ਕਾਰਨ:**
- ਵੱਧ ਨਮੀ, ਬੱਦਲਵਾਈ ਮੌਸਮ ਅਤੇ ਜ਼ਿਆਦਾ ਯੂਰੀਆ ਦੀ ਵਰਤੋਂ.

**ਰਸਾਇਣਕ ਸਪ੍ਰੇ:**
- ਪ੍ਰੋਫੇਨੋਫੋਸ ੫੦% EC (੨ ml/ਲਿਟਰ) ਜਾਂ ਇਮਾਮੇਕਟਿਨ (੦.੫ ਗ੍ਰਾਮ/ਲਿਟਰ).
- ਸ਼ਾਮ ਨੂੰ ਮਾਸਕ ਪਾ ਕੇ ਸਪ੍ਰੇ ਕਰੋ.

**ਜੈਵਿਕ ਉਪਾਅ:**
- ਨਿੰਮ ਤੇਲ ੫ ml/ਲਿਟਰ ਜਾਂ ਦਸ਼ਪਰਣੀ ਅਰਕ ੫ ml/ਲਿਟਰ.
- ਪੀਲੇ-ਨੀਲੇ ਸਟਿੱਕੀ ਟਰੈਪ ਏਕੜ ਪਿੱਛੇ ੧੦-੧੨ ਲਗਾਓ.

**ਹੈਲਪਲਾਈਨ:** 1800-180-1551"""
            
        else:
            return f"""**Hello Dear Farmer!** 
**Detected Issue:** **{issue_name}**

**How it Affects the Crop:**
• This pest/disease disrupts photosynthesis, causes chlorosis, saps leaf nutrients, and clogs stem vascular tissues, leading to potential 30-50% yield loss.

**Why it Occurs (Triggers):**
• High relative atmospheric humidity (>80%), prolonged cloudy weather, and excessive nitrogenous fertilizer application create favorable conditions for pest outbreaks.

**3 Stages of Disease / Infestation:**
• **1. Early Stage (1-5% Damage):** Mild leaf spotting or initial egg clusters. Easily controlled with 5% Neem Oil spray & sticky traps.
• **2. Moderate Stage (10-30% Damage):** Active lesions & caterpillar feeding. Requires targeted chemical spray (Profenofos / Emamectin) within 48 hours.
• **3. Critical Stage (50%+ Damage):** Severe defoliation, stem rot, or boll boring. Requires emergency systemic sprays and destruction of infected plant debris.

**Step 1: Chemical Spray Treatment:**
• **Recommended Pesticide:** Spray Profenofos 50% EC (2 ml / Liter of water) or Emamectin Benzoate 5% SG (0.5g / Liter).
• **Dosage:** 400 ml in 200 Liters of water per Acre.
• **Safety:** Always spray in the late afternoon wearing protective gloves and face mask.

**Step 2: Organic & Biological Control:**
• **Neem Oil Spray:** Mix 5 ml Neem Oil (1500 PPM) + 1 ml liquid soap per Liter of water and spray thoroughly.
• **Dashparni Ark:** Spray 5 ml Dashparni Ark per Liter of water.
• **Traps:** Install 10-12 Yellow and Blue Sticky Traps per Acre.

**Step 3: Field Management & Prevention:**
• Collect and burn infected crop residues to eliminate spore inoculum.

**Toll-Free Kisan Helpline:** 1800-180-1551"""


# ─────────────────────────────────────────────────────────────
# SIDEBAR  (shown only after login)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    farmer_name_display = st.session_state.get("farmer_name", "Farmer")
    farmer_dist_display = st.session_state.get("farmer_district", "")

    st.markdown(f"""
    <div style='text-align:center;padding:16px;background:linear-gradient(135deg,#E8F5E9,#C8E6C9);
                border-radius:14px;margin-bottom:15px;border:1px solid #A5D6A7'>
        <div style="display:flex;justify-content:center;margin-bottom:5px">""" + logo_svg(64) + f"""</div><h2 style='color:#1B5E20;margin:0;font-weight:700'>महाकृषि</h2>
        <p style='color:#2E7D32;font-size:0.88rem;margin:3px 0 0;font-weight:600'>MahaKrishi AI</p>
        <span class='figma-badge' style='background:#1B5E20;color:white;margin-top:6px;display:inline-block'>
            Govt. Agri-Tech Initiative
        </span>
    </div>
    <div style='background:#F1F8E9;border-radius:10px;padding:10px 14px;margin-bottom:12px;border:1px solid #C8E6C9'>
        <small><b>{farmer_name_display}</b><br>{farmer_dist_display}</small>
    </div>
    """, unsafe_allow_html=True)

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
if st.session_state["page"] == "profile":
    show_profile_page()
    st.stop()

# Profile icon (top-right corner). Column ratio [6,1] keeps the icon
# reachable with a thumb on narrow phone widths instead of being pushed
# too far into the corner.
top_l, top_r = st.columns([6, 1])
with top_r:
    if st.button("", key="profile_icon_btn", help="My Profile"):
        st.session_state["page"] = "profile"
        st.rerun()

# ─────────────────────────────────────────────────────────────
# FIGMA DYNAMIC HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='figma-header'>
    <div style='flex: 1; min-width: 0;'>
        <h1 class='figma-header-title'>MahaKrishi AI | महाकृषि</h1>
        <p class='figma-header-sub'>
            AI Crop Disease &amp; Pest Detection | Chemical &amp; Organic Remedies | Specialist Helplines &amp; Govt Schemes
        </p>
    </div>
    <div style='flex-shrink: 0;'>
        <span class='figma-badge'><span class='status-dot'></span>System Active | महाराष्ट्र शासन</span>
    </div>
</div>
""", unsafe_allow_html=True)

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
                <div style="display:flex;justify-content:center">""" + UPLOAD_ICON_SVG + """</div>
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
                <div style="display:flex;justify-content:center">""" + SCAN_ICON_SVG + """</div>
                <h4 style='color:#1B5E20;margin:8px 0 4px'>Ready for Instant AI Diagnosis</h4>
                <p style='color:#2E7D32;font-size:0.9rem'>Upload an image on the left and click 'Analyze with AI'</p>
            </div>""", unsafe_allow_html=True)

        elif analyze_btn:
            is_pest_mode = "Pest" in model_mode

            # ── IMAGE QUALITY CHECK FIRST ──
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

                    append_detection_history(
                        st.session_state.get("farmer_phone", ""),
                        st.session_state.get("farmer_name", ""),
                        st.session_state.get("farmer_district", ""),
                        "Pest" if is_pest_mode else "Disease",
                        model_mode,
                        name,
                        conf
                    )

                    # ── LOW CONFIDENCE WARNING ──
                    if conf < CONF_THRESHOLD_LOW:
                        st.markdown(f"""
                        <div class='alert-box'>
                            <span class='badge-low-conf'>Low Confidence Detection</span>
                            <h4 style='color:#E65100;margin:10px 0 4px'>Best Match: {name}</h4>
                            <p style='margin:0;color:#BF360C'>AI Confidence: <b>{conf:.1f}%</b> — This is below the reliable threshold (45%)</p>
                            <p style='margin:6px 0 0;font-size:0.88rem;color:#6D4C41'>
                            <b>Suggestions:</b> Retake the photo in bright natural light, ensure leaf fills the frame, 
                            avoid shadows, and make sure the image is sharp/in-focus.
                            </p>
                        </div>""", unsafe_allow_html=True)
                    else:
                        badge_cls = "badge-success" if healthy else ("badge-warning" if is_pest_mode else "badge-emergency")
                        status_txt = "Healthy Crop! " if healthy else ("Pest Detected! " if is_pest_mode else "Disease Detected! ")

                        st.markdown(f"""
                        <div style='background:#FAFAFA;border-radius:12px;padding:16px;margin-bottom:12px;border:1px solid #E0E0E0'>
                            <span class='{badge_cls}'>{status_txt}</span>
                            <h3 style='color:#1B5E20;margin:10px 0 4px'>{name}</h3>
                            <p style='color:#558B2F;font-size:0.88rem;margin:0'>AI Confidence (TTA avg): <b>{conf:.1f}%</b></p>
                        </div>""", unsafe_allow_html=True)
                        st.progress(conf / 100)

                        with st.expander("Probable AI Top 3 Matches"):
                            for i, r in enumerate(results):
                                st.markdown(f"{''[i]} **{r['name']}** — `{r['confidence']:.1f}%`")
                                st.progress(r["confidence"] / 100)

                        # ── ALERT NEARBY FARMERS (only for disease/pest, conf >= threshold) ──
                        if not healthy and conf >= CONF_THRESHOLD_ALERT:
                            farmer_district = st.session_state.get("farmer_district", "")
                            farmer_name_s   = st.session_state.get("farmer_name", "")
                            farmer_phone_s  = st.session_state.get("farmer_phone", "")

                            nearby_count = get_registered_farmers_count(farmer_district)
                            nearby_count = max(nearby_count, 1)  # At least 1 (self)

                            st.markdown(f"""
                            <div class='alert-box'>
                                <b>{name} detected in {farmer_district} district!</b><br>
                                <small>There are <b>{nearby_count}</b> registered farmers in your district 
                                who could be at risk. Alert them instantly.</small>
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
                                    f"Alert successfully sent to **{nearby_count}** registered farmers "
                                    f"in **{farmer_district}** district! "
                                    f"Disease alert for **{name}** recorded in system."
                                )

                        # Generate AI Advisory
                        with st.spinner(f"Generating {lang_name} advisory & remedies..."):
                            ai_resp = get_ai_advisory(name, is_pest_mode, lang_name, conf)

                            audio_bytes = None
                            if enable_voice:
                                try:
                                    audio_bytes = text_to_speech(ai_resp, lang_code)
                                except Exception:
                                    audio_bytes = None

                            st.markdown(f"<div class='chat-box'>{ai_resp.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

                            if enable_voice and audio_bytes:
                                st.markdown("#### Marathi/Hindi Voice Advisory (आवाज उत्तर)")
                                st.audio(audio_bytes, format="audio/mp3")

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 2: TREATMENT AI CHATBOT (CHEMICAL & ORGANIC)
# ─────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### Krishi AI Specialist Chatbot / कृषी उपचार चॅटबॉट")
    st.markdown(" Ask any crop disease, pest issue, or treatment query. Get **Chemical (रसायनिक)** and **Organic (जैविक)** solutions instantly!")

    # Preset quick chips (Dynamic Language)
    st.markdown("#### Quick Questions / जलद प्रश्न / शीघ्र प्रश्न:")
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

    # Input chat
    user_input = st.chat_input("उदा. उसावरील कीडीसाठी सेंद्रिय उपाय सांगा... Ask crop remedy...")
    active_query = user_input or quick_q

    if active_query:
        st.session_state.bot_history.append({"role": "user", "content": active_query})

        # Smart query classification: Gibberish vs Greeting vs Agri-Related vs Unrelated
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
            Reply in a warm, polite human formal tone:
            - Gently explain that you could not understand their message.
            - Ask them politely to state their crop name, disease, pest issue, or farming question clearly.
            Keep it formal and compassionate (max 60 words).
            """
        elif is_greeting:
            prompt_chat = f"""
            You are Krishi Mitra (कृषी मित्र), a caring, expert human agricultural scientist advising a farmer in Maharashtra.
            User Query: {active_query}
            STRICT LANGUAGE INSTRUCTION: Respond ONLY in {lang_name} native script ({lang_name}). Do NOT mix languages.

            Greet the farmer warmly with respect (e.g. 'रामराम शेतकरी दादा / ताई!' in Marathi, 'नमस्कार किसान भाई!' in Hindi, 'Greetings dear farmer!' in English).
            Introduce yourself as Krishi Mitra (कृषी मित्र) and state in 3 simple points how you can guide them:
            1. Crop Disease & Pest Diagnosis (पिकांचे रोग व कीड निदान)
            2. Chemical Spray & Organic Remedies (फवारणी व सेंद्रिय घरगुती उपाय)
            3. Government Schemes & Helplines (शासकीय योजना व हेल्पलाइन)

            Invite them warmly to ask any crop or farming query! Max 100 words.
            """
        elif not is_agri_related:
            prompt_chat = f"""
            You are Krishi Mitra (कृषी मित्र), an expert agricultural assistant in Maharashtra.
            User Input: "{active_query}"
            STRICT LANGUAGE INSTRUCTION: Respond ONLY in {lang_name} native script ({lang_name}).

            The user input is NOT related to any crop, plant disease, pest infestation, or farming topic.
            Respond ONLY with this exact question asking what crop disease or pest they have:
            - English: "Can you please tell what is your crop disease or pest?"
            - Marathi: "कृपया तुमचे पीक, रोग किंवा कीड कोणती आहे ते सांगू शकाल का?"
            - Hindi: "क्या आप कृपया बता सकते हैं कि आपकी फसल का रोग या कीट कौन सा है?"
            Do NOT provide any information on unrelated non-farming topics.
            """
        else:
            prompt_chat = f"""
            You are Krishi Mitra (कृषी मित्र), an expert human agricultural scientist advising a farmer in Maharashtra.
            User Query: {active_query}
            STRICT LANGUAGE INSTRUCTION: Write your complete response ONLY in {lang_name} native script ({lang_name}). Do NOT mix languages.

            HUMAN PERSONA & ADVISORY GUIDELINES:
            1. Speak like a caring, experienced human agricultural expert (empathetic, respectful, practical).
            2. TYPO AUTO-CORRECTION: If there are typos in crop or pest names (e.g. 'sugrcan', 'pnik bolworm', 'tomto'), auto-correct them naturally and answer for the intended crop.
            3. CROP ADVISORY: For disease or pest questions, provide structured solutions:
               ओळख व कारण / Identified Issue & Cause: [Simple human explanation]
               रसायनिक फवारणी (Chemical Spray): [Recommended spray name, exact dosage per Liter/Acre, best spraying time & safety mask]
               सेंद्रिय व जैविक उपचार (Organic Remedy): [Neem oil / Jeevamrut / Dashparni Ark / Sticky traps recipe & dosage]
               शेतकरी मित्रासाठी विशेष सल्ला (Expert Human Advice): [Field management & encouragement]
            Keep simple, practical, and compassionate. Max 250 words.
            """

        try:
            if GEMINI_KEY:
                genai.configure(api_key=GEMINI_KEY)
                gmodel = genai.GenerativeModel("gemini-1.5-flash")
                bot_ans = gmodel.generate_content(prompt_chat).text
            else:
                if is_gibberish:
                    if lang_name == "Marathi":
                        bot_ans = "**मला आपला संदेश स्पष्टपणे समजला नाही.**\n\nकृपया आपले पीक, रोग किंवा शेतीविषयीचा प्रश्न औपचारिक व स्पष्टपणे सांगावा ही नम्र विनंती. उदा. *'उसावरील तांबेरा रोगासाठी उपाय काय?'*"
                    elif lang_name == "Hindi":
                        bot_ans = "**मुझे आपका संदेश स्पष्ट रूप से समझ नहीं आया।**\n\nकृपया अपनी फसल, बीमारी या खेती से जुड़ा प्रश्न स्पष्ट रूप से लिखें। जैसे: *'धान के खोड कीट का उपचार क्या है?'*"
                    else:
                        bot_ans = "**I could not understand your message.**\n\nCould you please state your crop, disease, or farming question more clearly in a formal manner?"
                elif is_greeting:
                    if lang_name == "Marathi":
                        bot_ans = "**नमस्कार! मी महाकृषि AI सहाय्यक आहे.** \n\nमी तुम्हाला शेतीविषयक खालील बाबतीत मदत करू शकतो:\n\n• **पिकांचे रोग व कीड ओळख** (Crop Disease & Pest Diagnosis)\n• **रसायनिक फवारणी व सेंद्रिय उपाय** (Chemical & Organic Spray Remedies)\n• **शासकीय कृषी योजना व तज्ज्ञ हेल्पलाइन** (Govt Schemes & Helplines)\n\nतुमच्या पिकाची समस्या किंवा प्रश्न खाली विचारा!"
                    elif lang_name == "Hindi":
                        bot_ans = "**नमस्ते! मैं महाकृषि AI सहायक हूँ।** \n\nमैं आपकी खेती में निम्नलिखित सहायता कर सकता हूँ:\n\n• **फसलों के रोग एवं कीट पहचान**\n• **रासायनिक छिड़काव एवं जैविक उपचार**\n• **सरकारी कृषि योजनाएं एवं हेल्पलाइन**\n\nकृपया अपनी फसल का प्रश्न नीचे लिखें!"
                    else:
                        bot_ans = "**Hello! I am MahaKrishi AI Assistant.** \n\nI can assist you with:\n\n• **Crop Disease & Pest Diagnosis**\n• **Chemical Spray & Organic Remedies**\n• **Government Schemes & Helplines**\n\nPlease ask any crop question or problem below!"
                elif not is_agri_related:
                    if lang_name == "Marathi":
                        bot_ans = "**कृपया तुमचे पीक, रोग किंवा कीड कोणती आहे ते सांगू शकाल का?**"
                    elif lang_name == "Hindi":
                        bot_ans = "**क्या आप कृपया बता सकते हैं कि आपकी फसल का रोग या कीट कौन सा है?**"
                    else:
                        bot_ans = "**Can you please tell what is your crop disease or pest?**"
                else:
                    if lang_name == "Marathi":
                        bot_ans = f"""कृषी सल्ला (प्रश्न: {active_query})

रसायनिक उपचार (Chemical Treatment):
• कीड/रोगासाठी योग्य कीटकनाशकाची (उदा. क्लोरपायरीफॉस २ मिली/लिटर किंवा इमॅमेक्टिन ०.५ ग्रॅम/लिटर) फवारणी करा.
• संध्याकाळी फवारणी करणे अधिक प्रभावी ठरते.

सेंद्रिय व जैविक उपचार (Organic Treatment):
• ५% कडुनिंब तेल (Neem Oil) किंवा दशपर्णी अर्क (५ मिली/लिटर) चा वापर करा.
• शेतात पिवळे व निळे चिकट सापळे (Sticky Traps) लावा.

बचाव व सुरक्षा:
• मास्क आणि हातमोजे वापरूनच फवारणी करा.
अधिक मदतीसाठी हेल्पलाइन: 1800-180-1551"""
                    elif lang_name == "Hindi":
                        bot_ans = f"""कृषि सलाह (प्रश्न: {active_query})

रासायनिक उपचार (Chemical Treatment):
• उपयुक्त कीटनाशक (जैसे इमामेक्टिन 0.5 ग्राम/लीटर) का छिड़काव करें।

जैविक उपचार (Organic Treatment):
• 5% नीम तेल या दशपर्णी अर्क (5 मिली/लीटर) का स्प्रे करें।

बचाव:
• सुरक्षा मास्क पहनकर छिड़काव करें।
हेल्पलाइन: 1800-180-1551"""
                    else:
                        bot_ans = f"""Agronomic Advisory (Query: {active_query})

Chemical Treatment:
• Spray recommended pesticide with protective mask.

Organic Treatment:
• Spray 5% Neem Oil or Dashparni Ark (5 ml / Liter).

Kisan Helpline: 1800-180-1551"""
        except Exception:
            bot_ans = "कृपया कृषी हेल्पलाइन 1800-180-1551 वर संपर्क साधा."

        st.session_state.bot_history.append({"role": "assistant", "content": bot_ans})

    # Render History
    for msg in st.session_state.bot_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 3: SPECIALIST HELPLINE & EXPERT DIRECTORY
# ─────────────────────────────────────────────────────────────
with tab_contacts:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### Verified Agricultural Specialist Directory & Emergency Helplines")
    st.markdown("Connect directly with Maharashtra Krishi Vigyan Kendras (KVK), ICAR Scientists, and Govt Officers.")

    # Emergency Call Bar
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
                <b>Speciality:</b> Sugarcane, Fruits, Pest Control<br>
                <b>WhatsApp Support:</b> <a href='https://wa.me/919422000000' target='_blank'>Chat on WhatsApp</a></p>
                <a href='tel:02112255227'>Call KVK Baramati</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>Vasantdada Sugar Institute (VSI Pune)</h4>
                <p><b>Phone:</b> 020-26902100 / 26902200<br>
                <b>Speciality:</b> Sugarcane Red Rot, Pokkah Boeng, Pest Advisory</p>
                <a href='tel:02026902100'>Call VSI Experts</a>
            </div>""", unsafe_allow_html=True)

    with r3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>KVK Yashwantrao Chavan (Nashik)</h4>
                <p><b>Phone:</b> 0253-2415121 / 2415321<br>
                <b>Speciality:</b> Grapes, Onion, Vegetables, Leaf Blight Advisory</p>
                <a href='tel:02532415121'>Call KVK Nashik</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>MPKV Rahuri Agri University</h4>
                <p><b>Phone:</b> 02426-243208 / 243311<br>
                <b>Speciality:</b> Pulses, Rice Blast, Crop Pathology Research</p>
                <a href='tel:02426243208'>Call MPKV Rahuri</a>
            </div>""", unsafe_allow_html=True)

    with r4:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>ICAR - CICR Cotton Experts (Nagpur)</h4>
                <p><b>Phone:</b> 07103-275536 / 275538<br>
                <b>Speciality:</b> Pink Bollworm, Cotton Leaf Curl, Whitefly Control</p>
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

    # Specialist Form
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
    st.markdown("Real-time outbreak mapping across Maharashtra. Color-coded severity pins notify nearby farmers within **10 km - 50 km** radius.")

    # Show real alert history from Excel if available
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

    # Outbreak Data Points in Maharashtra
    outbreaks = [
        {"district": "Nashik", "lat": 20.0059, "lon": 73.7898, "issue": "Fall Armyworm (लष्करी अळी)", "crop": "Maize / मका", "severity": "Emergency Outbreak", "radius": 15000, "color": [211, 47, 47, 180]},
        {"district": "Kolhapur", "lat": 16.7050, "lon": 74.2433, "issue": "Sugarcane Red Rot (ऊस तांबेरा)", "crop": "Sugarcane / ऊस", "severity": "Warning", "radius": 20000, "color": [245, 124, 0, 180]},
        {"district": "Pune (Baramati)", "lat": 18.1519, "lon": 74.5768, "issue": "Early Shoot Borer (खोड कीड)", "crop": "Sugarcane / ऊस", "severity": "Emergency Outbreak", "radius": 12000, "color": [211, 47, 47, 180]},
        {"district": "Nagpur", "lat": 21.1458, "lon": 79.0882, "issue": "Pink Bollworm (गुलाबी बोंडअळी)", "crop": "Cotton / कापूस", "severity": "Emergency Outbreak", "radius": 25000, "color": [211, 47, 47, 180]},
        {"district": "Sambhajinagar", "lat": 19.8762, "lon": 75.3433, "issue": "Whitefly Pest (पांढरी माशी)", "crop": "Cotton / कापूस", "severity": "Advisory Watch", "radius": 18000, "color": [251, 192, 45, 180]},
        {"district": "Solapur", "lat": 17.6599, "lon": 75.9064, "issue": "Aphids Damage (मावा)", "crop": "Vegetables / भाजीपाला", "severity": "Warning", "radius": 10000, "color": [245, 124, 0, 180]}
    ]

    # PyDeck Map
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

    # Active Alert List
    st.markdown("#### Active Regional Outbreak Alerts:")
    m1, m2 = st.columns(2)
    for idx, ob in enumerate(outbreaks):
        target_col = m1 if idx % 2 == 0 else m2
        with target_col:
            badge_type = "badge-emergency" if "Emergency" in ob["severity"] else ("badge-warning" if "Warning" in ob["severity"] else "badge-success")
            # Show real registered farmer count for district
            reg_count = get_registered_farmers_count(ob["district"].split(" ")[0])
            reg_info  = f" | <b>Registered Farmers:</b> {reg_count}" if reg_count > 0 else ""
            st.markdown(f"""
            <div class='contact-card'>
                <span class='{badge_type}'>{ob['severity']}</span>
                <h4 style='margin:8px 0 2px;color:#1B5E20'>{ob['district']} — {ob['issue']}</h4>
                <p style='margin:0;font-size:0.88rem;color:#558B2F'>
                <b>Affected Crop:</b> {ob['crop']} | <b>Impact Radius:</b> {ob['radius']//1000} km{reg_info}
                </p>
            </div>""", unsafe_allow_html=True)

    # Broadcast Alert Form
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
            # Log broadcast alert
            append_alert_to_excel(
                reporter_name=st.session_state.get("farmer_name", "Unknown"),
                reporter_phone=st.session_state.get("farmer_phone", ""),
                district=b_dist,
                crop=b_crop,
                disease=b_issue,
                confidence=100.0
            )
            st.success(
                f"अलर्ट यशस्वीपणे पाठवला! "
                f"**{b_dist}** परिसरातील **{reach}** नोंदणीकृत शेतकऱ्यांना "
                f"**{b_issue}** बद्दल अलर्ट पाठवण्यात आला आहे."
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 5: GOVERNMENT SCHEMES & SUBSIDIES PORTAL
# ─────────────────────────────────────────────────────────────
with tab_schemes:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### Official Government Agricultural Schemes & Subsidies Portal")
    st.markdown("Direct access to Central & Maharashtra Govt schemes, eligibility criteria, subsidy rates, and official portals.")

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
            "benefit": "Crop loans up to ₹3 Lakh at 4% interest rate (with 3% prompt repayment incentive)",
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
                <span class='figma-badge' style='background:#1B5E20;color:white'>{sc['cat']}</span>
                <h4 style='margin-top:10px'>{sc['name']}</h4>
                <p><b>Benefit:</b> {sc['benefit']}<br>
                <b>Eligibility:</b> {sc['eligibility']}<br>
                <b>Required Docs:</b> {sc['docs']}</p>
            </div>""", unsafe_allow_html=True)
            st.link_button(f"Apply Now / अधिकृत संकेतस्थळ ({sc['name'].split()[0]})", sc['link'], use_container_width=True)
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
