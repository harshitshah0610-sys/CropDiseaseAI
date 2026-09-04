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
_LOGO_B64 = "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"

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
    page_icon="",
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
        # Legacy accounts registered before password was added — let them in
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
    # remove any previous photo (different extension) for this farmer first
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
    """A plain gray silhouette on a light-gray circle — the same fallback
    style Instagram shows when no profile photo has been set."""
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
    """Return the farmer's uploaded photo as a data URI, or the default
    Instagram-style placeholder if they haven't uploaded one."""
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
    st.stop()   # Stop here — rest of app not shown until logged in

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

    # Back button
    if st.button("Back to Dashboard", key="back_from_profile"):
        st.session_state["show_profile"] = False
        st.rerun()

    # ── HERO CARD ──
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

    # ── CHANGE PROFILE PHOTO ──
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

    # ── STATS ROW ──
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

    # ── TWO COLUMN LAYOUT ──
    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        # Farmer Info Card
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

        # Quick Stats Mini Dashboard
        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### Activity Dashboard")
        if total_scans > 0:
            # Simple bar chart data
            import pandas as pd
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
        # Detection History
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
            for h in reversed(history[-10:]):  # Show last 10
                icon  = "" if h.get("type") == "disease" else ("" if h.get("type") == "pest" else "")
                badge_color = "#FFEBEE" if h.get("type") == "disease" else (
                              "#FFF3E0" if h.get("type") == "pest" else "#E8F5E9")
                badge_text_color = "#C62828" if h.get("type") == "disease" else (
                                   "#EF6C00" if h.get("type") == "pest" else "#2F6B39")
                label = "Disease" if h.get("type") == "disease" else (
                        "Pest" if h.get("type") == "pest" else "Healthy")
                st.markdown(f"""
                <div class='history-row'>
                    <div class='history-icon'>{icon}</div>
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

        # AI Model Info Card
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

    # ── SIGN OUT ──
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
    _sidebar_avatar_uri  = get_avatar_data_uri(st.session_state.get("farmer_phone", ""))

    # ── Sidebar top: profile avatar (Instagram-style) + name ──
    # Build pieces OUTSIDE the f-string so the large base64 logo_svg()
    # never gets printed as visible text in the Streamlit UI.
    _logo_html = logo_svg(44)
    _sidebar_html = (
        "<div style='text-align:center;padding:18px 16px 14px;"
        "background:linear-gradient(135deg,#E8F5E9,#C8E6C9);"
        "border-radius:14px;margin-bottom:15px;border:1px solid #A5D6A7'>"
        # App logo (small)
        "<div style='display:flex;justify-content:center;margin-bottom:10px'>"
        + _logo_html +
        "</div>"
        # Circular profile avatar
        "<div style='display:flex;justify-content:center;margin-bottom:10px'>"
        "<img src='" + _sidebar_avatar_uri + "'"
        " style='width:80px;height:80px;border-radius:50%;object-fit:cover;"
        "border:3px solid #FFFFFF;"
        "box-shadow:0 3px 12px rgba(31,78,43,0.30);"
        "background:#EEF3EC;'/>"
        "</div>"
        # Farmer name
        "<p style='color:#1F4E2B;font-weight:700;font-size:0.95rem;margin:0 0 2px;"
        "white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
        + farmer_name_display +
        "</p>"
        # District
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

    # Profile button inside sidebar
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
# FIGMA DYNAMIC HEADER (with Profile Icon embedded in header)
# ─────────────────────────────────────────────────────────────
farmer_name_header = st.session_state.get("farmer_name", "Farmer")
avatar_uri_header  = get_avatar_data_uri(st.session_state.get("farmer_phone", ""))

# Two columns: header bar | profile button column
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
    # Render the avatar as a plain <img> circle — no CSS selector games.
    # Below it, a real st.button (text hidden via CSS scoped to this column's
    # unique wrapper id) handles the Streamlit navigation.
    st.markdown(f"""
    <style>
    /* Scope all overrides strictly to this column wrapper */
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
    /* Make the st.button below invisible — clicking the img does the same job */
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
                 // Find the nearest Streamlit button and programmatically click it
                 var btns = document.querySelectorAll('#mk-profile-col button');
                 if(btns.length) {{ btns[0].style.pointerEvents='auto'; btns[0].click(); }}
             "/>
        <div class="mk-name-label">{farmer_name_header.split()[0]}</div>
    </div>
    """, unsafe_allow_html=True)

    # Real Streamlit button — invisible, activated by the img onclick above
    if st.button("↗", key="open_profile",
                 help=f"View Profile — {farmer_name_header}",
                 use_container_width=True):
        st.session_state["show_profile"] = True
        st.rerun()

# Spacer so header and tabs don't collapse together
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

                        # ── SAVE TO DETECTION HISTORY ──
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
                        # Avoid duplicate consecutive entries
                        if not st.session_state["detection_history"] or \
                           st.session_state["detection_history"][-1]["name"] != name:
                            st.session_state["detection_history"].append(history_entry)

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
                <h4 style='margin:8px 0 2px;color:#1F4E2B'>{ob['district']} — {ob['issue']}</h4>
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
                <span class='figma-badge' style='background:#1F4E2B;color:white'>{sc['cat']}</span>
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
