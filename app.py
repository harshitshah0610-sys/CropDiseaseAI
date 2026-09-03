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
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif;
    }

    /* Main Header Figma Banner */
    .figma-header {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
    padding: 20px 28px;
    border-radius: 20px;
    margin-bottom: 24px;
    color: white;
    box-shadow: 0 10px 30px rgba(27, 94, 32, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}
    .figma-header-title { font-size: 2.2rem; font-weight: 700; margin: 0; color: #FFFFFF; }
    .figma-header-sub { font-size: 1rem; color: #C8E6C9; margin-top: 6px; }
    
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
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .figma-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 26px rgba(46,125,50,0.12);
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

# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# TRANSLATIONS & CONFIG
# ─────────────────────────────────────────────────────────────
LANGUAGE_MAP   = {
    "🌾 मराठी (Marathi)": "mr",
    "🇮🇳 हिंदी (Hindi)": "hi",
    "🌍 English": "en",
    "🌻 ગુજરાતી (Gujarati)": "gu",
    "🌟 ਪੰਜਾਬੀ (Punjabi)": "pa"
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
        "signin_tab": "🔑 Sign In",
        "register_tab": "📝 Register",
        "mobile": "📱 Mobile Number",
        "name": "👤 Full Name",
        "district": "📍 District",
        "signin_btn": "✅ Sign In",
        "register_btn": "📝 Register & Sign In",
        "sel_lang": "🌐 Select Language",
        "tab_detect": "🔍 AI Detection",
        "tab_chat": "🤖 Treatment Chatbot",
        "tab_contacts": "📞 Specialist Contacts",
        "tab_map": "🗺️ Outbreak Map & Alerts",
        "tab_schemes": "🏛️ Govt Schemes",
        "signout": "🚪 Sign Out"
    },
    "mr": {
        "title": "महाकृषि AI",
        "subtitle": "स्मार्ट पीक रोग आणि कीड ओळख",
        "signin_tab": "🔑 लॉग इन",
        "register_tab": "📝 नोंदणी",
        "mobile": "📱 मोबाईल नंबर",
        "name": "👤 पूर्ण नाव",
        "district": "📍 जिल्हा",
        "signin_btn": "✅ लॉग इन करा",
        "register_btn": "📝 नोंदणी करा",
        "sel_lang": "🌐 भाषा निवडा",
        "tab_detect": "🔍 AI रोग निदान",
        "tab_chat": "🤖 कृषी चॅटबॉट",
        "tab_contacts": "📞 विशेषज्ञ संपर्क",
        "tab_map": "🗺️ रोग अलर्ट नकाशा",
        "tab_schemes": "🏛️ शासकीय योजना",
        "signout": "🚪 लॉग आउट"
    },
     "hi": {
        "title": "महाकृषि AI",
        "subtitle": "स्मार्ट फसल रोग और कीट पहचान",
        "signin_tab": "🔑 साइन इन",
        "register_tab": "📝 पंजीकरण",
        "mobile": "📱 मोबाइल नंबर",
        "name": "👤 पूरा नाम",
        "district": "📍 जिला",
        "signin_btn": "✅ साइन इन करें",
        "register_btn": "📝 रजिस्टर करें",
        "sel_lang": "🌐 भाषा चुनें",
        "tab_detect": "🔍 AI रोग पहचान",
        "tab_chat": "🤖 कृषि चैटबॉट",
        "tab_contacts": "📞 विशेषज्ञ संपर्क",
        "tab_map": "🗺️ रोग अलर्ट मैप",
        "tab_schemes": "🏛️ सरकारी योजनाएं",
        "signout": "🚪 लॉग आउट"
    },
    "gu": {
        "title": "મહાકૃષિ AI",
        "subtitle": "સ્માર્ટ પાક રોગ અને જીવાત શોધ",
        "signin_tab": "🔑 સાઇન ઇન",
        "register_tab": "📝 નોંધણી",
        "mobile": "📱 મોબાઇલ નંબર",
        "name": "👤 પૂરું નામ",
        "district": "📍 જિલ્લો",
        "signin_btn": "✅ સાઇન ઇન કરો",
        "register_btn": "📝 નોંધણી કરો",
        "sel_lang": "🌐 ભાષા પસંદ કરો",
        "tab_detect": "🔍 AI રોગ શોધ",
        "tab_chat": "🤖 કૃષિ ચેટબોટ",
        "tab_contacts": "📞 નિષ્ણાત સંપર્ક",
        "tab_map": "🗺️ રોગ એલર્ટ નકશો",
        "tab_schemes": "🏛️ સરકારી યોજનાઓ",
        "signout": "🚪 લૉગ આઉટ"
    },
    "pa": {
        "title": "ਮਹਾਕ੍ਰਿਸ਼ੀ AI",
        "subtitle": "ਸਮਾਰਟ ਫਸਲ ਰੋਗ ਅਤੇ ਕੀਟ ਪਛਾਣ",
        "signin_tab": "🔑 ਸਾਈਨ ਇਨ",
        "register_tab": "📝 ਰਜਿਸਟ੍ਰੇਸ਼ਨ",
        "mobile": "📱 ਮੋਬਾਈਲ ਨੰਬਰ",
        "name": "👤 ਪੂਰਾ ਨਾਮ",
        "district": "📍 ਜ਼ਿਲ੍ਹਾ",
        "signin_btn": "✅ ਸਾਈਨ ਇਨ ਕਰੋ",
        "register_btn": "📝 ਰਜਿਸਟਰ ਕਰੋ",
        "sel_lang": "🌐 ਭਾਸ਼ਾ ਚੁਣੋ",
        "tab_detect": "🔍 AI ਰੋਗ ਪਛਾਣ",
        "tab_chat": "🤖 ਖੇਤੀ ਚੈਟਬੋਟ",
        "tab_contacts": "📞 ਮਾਹਰ ਸੰਪਰਕ",
        "tab_map": "🗺️ ਰੋਗ ਅਲਰਟ ਨਕਸ਼ਾ",
        "tab_schemes": "🏛️ ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ",
        "signout": "🚪 ਲੌਗ ਆਉਟ"
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

CONF_THRESHOLD_LOW  = 45.0   # Below this → show low-confidence warning
CONF_THRESHOLD_ALERT = 60.0  # Above this → show "Alert Nearby Farmers" button

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


# ─────────────────────────────────────────────────────────────
# LOGIN / REGISTER GATE
# ─────────────────────────────────────────────────────────────

def show_login_page():
    st.markdown("""
    <div style='text-align:center;padding:30px 0 10px'>
        <img src='data:image/jpeg;base64,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' width='140' style='border-radius:15px; margin-bottom:10px; box-shadow: 0px 4px 12px rgba(0,0,0,0.2)'/>
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
            st.session_state["sel_lang_display"] = "🌾 मराठी (Marathi)"
        
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
        🌾 <b>MahaKrishi AI</b> | Powered by PyTorch + Google Gemini AI<br>
        Maharashtra Government Agri-Tech Initiative
    </div>
    """, unsafe_allow_html=True)


# ── SESSION GUARD ──
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_login_page()
    st.stop()   # Stop here — rest of app not shown until logged in


# ─────────────────────────────────────────────────────────────
# LOAD PyTorch MODELS (Disease & Pest)
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_disease_model():
    model_path = os.path.join(os.path.dirname(__file__), "crop_disease_model.pth")
    if not os.path.exists(model_path):
        return None, None, "❌ Model file 'crop_disease_model.pth' not found."
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
        return None, None, f"❌ Error loading disease model: {e}"


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
        return None, None, f"❌ Error loading pest model: {e}"


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
            "⚠️ **Image too dark for accurate detection!**\n\n"
            "Please retake the photo in bright daylight or good lighting. "
            "Dark images cause the AI to give wrong predictions."
        )

    # Blur check: Laplacian variance (low = blurry)
    laplacian_var = np.var(np.gradient(img_array.astype(float)))
    if laplacian_var < 50:
        return False, (
            "⚠️ **Image appears blurry or out of focus!**\n\n"
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
    clean = re.sub(r'[🔴🤒🦠💊🌿🛡️☎️✅❌🌾🔊👀💧🥇🥈🥉🎉📁📐🐛🏛️🗺️🚨]', '', clean)
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

        1. 🙏 **नमस्कार व कृषी मित्राचे मनोगत (GREETING & EMPATHETIC INTRODUCTION)**
           - Respectful warm greeting to the farmer.

        2. 🦠 **पिकावर होणारा विघातक परिणाम (HOW THE DISEASE/PEST AFFECTS THE PLANT)**
           - Detail plant physiological damage: leaf chlorosis, sap-sucking damage, photosynthesis blockage, stem vascular clogging, fruit/boll boring, root rot, or severe yield reduction.

        3. 🌧️ **कीड / रोग येण्याची मुख्य कारणे (WHY THE PEST/DISEASE OCCURS)**
           - Explain triggers: high atmospheric humidity (>80%), cloudy monsoon weather, excessive nitrogen/urea fertilizer use, stubble residue, temperature fluctuations, and lack of natural beneficial insects.

        4. 📊 **रोगाचे / कीडीचे ३ मुख्य टप्पे (STAGES OF DISEASE / PEST INFESTATION)**
           - Describe Early Stage (🌱 प्राथमिक टप्पा - 1-5% infestation, mild leaf spotting, easily controlled by Neem Oil).
           - Describe Moderate Stage (🌿 मध्यम टप्पा - 10-30% infestation, active lesions & caterpillars, target chemical spray needed within 48 hours).
           - Describe Critical/Severe Stage (🥀 गंभीर / तीव्र टप्पा - 50%+ foliage damage, wilt/rot/boring, emergency systemic spray & burning infected plants required).

        5. 💊 **टप्पा १: प्रभावी रसायनिक फवारणी (STEP 1: CHEMICAL SPRAY SOLUTION WITH DOSAGES)**
           - Recommend specific chemical pesticides/fungicides (e.g., Profenofos 50% EC, Emamectin Benzoate 5% SG, Hexaconazole 5% EC, Chlorantraniliprole 18.5% SC).
           - Provide EXACT dosage per Liter of water AND per Acre (e.g., 2 ml/Liter or 400 ml/Acre in 200 Liters water).
           - Specify best spraying time (evening/early morning) and safety gear (mask, gloves).

        6. 🌿 **टप्पा २: सेंद्रिय व जैविक घरगुती उपाय (STEP 2: ORGANIC & BIOLOGICAL SOLUTIONS)**
           - Detailed recipe for 5% Neem Oil (कडुनिंब तेल - 5 ml/L), Jeevamrut (जीवामृत), or Dashparni Ark (दशपर्णी अर्क - 5 ml/L).
           - Bio-control agents (Trichoderma viride @ 5g/L for soil diseases or Beauveria bassiana for insect pests).
           - Mechanical traps: Yellow and blue sticky traps (10-15 traps/Acre) or Pheromone traps (5 traps/Acre for bollworm/borer).

        7. 🛡️ **टप्पा ३: दीर्घकालीन शेत स्वच्छता व सुपीकता (STEP 3: LONG-TERM PREVENTION & FIELD HYGIENE)**
           - Cultural practices: Removing & burning infected plant parts.
           - Soil health management, crop rotation, and subsoil drainage.

        8. ☎️ **मोफत कृषी हेल्पलाइन (HELPLINE SUPPORT)**
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
            return "🙏 **रामराम शेतकरी दादा!** 🌾\n\n✅ तुमचे पीक पूर्णपणे निरोगी आहे!..."
        elif lang_name == "Hindi":
            return "🙏 **नमस्कार किसान भाई!** 🌾\n\n✅ आपकी फसल पूरी तरह स्वस्थ है!..."
        elif lang_name == "Gujarati":
            return "🙏 **નમસ્કાર ખેડૂત ભાઈ/બહેન!** 🌾\n\n✅ તમારો પાક સંપૂર્ણ સ્વસ્થ અને લીલોછમ છે!\n\n💧 **કૃષિ મિત્રની સલાહ:**\n૧. જમીનની જરૂરિયાત મુજબ સિંચાઈ કરો.\n૨. દરરોજ સવારે પાકનું નિરીક્ષણ કરો.\n૩. જીવામૃતનો ઉપયોગ કરી જમીન સુધારો."
        elif lang_name == "Punjabi":
            return "🙏 **ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਭਰਾ/ਭੈਣ!** 🌾\n\n✅ ਤੁਹਾਡੀ ਫਸਲ ਬਿਲਕੁਲ ਸਿਹਤਮੰਦ ਅਤੇ ਹਰੀਭਰੀ ਹੈ!\n\n💧 **ਕ੍ਰਿਸ਼ੀ ਮਿੱਤਰ ਦੀ ਸਲਾਹ:**\n੧. ਜ਼ਮੀਨ ਦੀ ਲੋੜ ਅਨੁਸਾਰ ਸਿੰਚਾਈ ਕਰੋ.\n੨. ਹਰ ਰੋਜ਼ ਸਵੇਰੇ ਫਸਲ ਦੀ ਜਾਂਚ ਕਰੋ.\n੩. ਜੀਵਾਮ੍ਰਿਤ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਮਿੱਟੀ ਸੁਧਾਰੋ."
        else:
            return "🙏 **Greetings Dear Farmer!** 🌾\n\n✅ Your crop is completely healthy and growing strong!\n\n💧 **Krishi Mitra Advice:**\n1. Maintain timely irrigation.\n2. Inspect fields every morning.\n3. Apply Jeevamrut to boost soil health."
    else:
        if lang_name == "Marathi":
            return f"""🙏 **रामराम शेतकरी दादा!** 🌾

🔴 **आढळलेला विकार / कीड:** **{issue_name}**

🦠 **पिकावर होणारा विघातक परिणाम (How it Affects Plant):**
• हा विकार किंवा कीड पानांमधील रस शोषून घेते, ज्यामुळे पानातील हरितद्रव्य (Photosynthesis) नष्ट होते.
• झाडाची वाढ खुंटते, पाने पिवळी पडून वाळतात आणि उत्पादनात ३०% ते ५०% पर्यंत घट येऊ शकते.

🌧️ **प्रादुर्भावाची मुख्य कारणे (Why it Attacks):**
• हवेतील वाढलेला दमटपणा, सततचे ढगाळ हवामान आणि युरियाचा (नत्र) अतिवापर यांमुळे कीड व रोगाचा प्रसार वेगाने होतो.

📊 **रोगाचे / कीडीचे ३ मुख्य टप्पे (Stages of Disease / Infestation):**
• **🌱 १. प्राथमिक टप्पा (Early Stage):** पानांवर बारीक डाग (१-५% प्रादुर्भाव). ५% कडुनिंब तेल व चिकट सापळ्यांनी सहज नियंत्रण शक्य.
• **🌿 २. मध्यम टप्पा (Moderate Stage):** १०-३०% पानांवर डाग किंवा कीड. ४८ तासांत रसायनिक फवारणी (प्रोफेनोफॉस/इमॅमेक्टिन/हेक्झाकोनॅझोल) आवश्यक.
• **🥀 ३. गंभीर / तीव्र टप्पा (Critical Stage):** ५०% पेक्षा जास्त पीक बाधित, पाने वाळणे, खोड सडणे. तातडीची सिस्टेमिक औषध फवारणी व बाधित भाग जाळणे आवश्यक.

💊 **टप्पा १: रसायनिक फवारणी उपाय (Chemical Treatment):**
• **औषध:** प्रोफेनोफॉस ५०% EC (२ मिली प्रति लिटर पाणी) किंवा इमॅमेक्टिन बेन्झोएट ५% SG (०.५ ग्रॅम प्रति लिटर पाणी).
• **प्रमाण:** एका एकरासाठी २०० लिटर पाण्यात ४०० मिली औषध मिसळून फवारणी करा.
• **सुरक्षा:** फवारणी नेहमी संध्याकाळी व तोंडाला मास्क लावूनच करा.

🌿 **टप्पा २: सेंद्रिय व जैविक घरगुती उपाय (Organic Treatment):**
• **कडुनिंब तेल (Neem Oil):** ५ मिली कडुनिंब तेल (1500 PPM) + १ मिली डिटर्जंट लिक्विड प्रति लिटर पाण्यात मिसळून फवारा.
• **दशपर्णी अर्क:** ५ मिली दशपर्णी अर्क प्रति लिटर पाण्यात मिसळून फवारल्यास कीड पळून जाते.
• **चिकट सापळे:** कीडींच्या नियंत्रणासाठी शेतात एकरी १०-१२ पिवळे व निळे चिकट सापळे (Sticky Traps) लावा.

🛡️ **टप्पा ३: दीर्घकालीन शेत स्वच्छता व बचाव:**
• बाधित पाने व झाडांचे अवशेष तात्काळ गोळा करून नष्ट करा.
• पिकांची आलटून-पालटून (Crop Rotation) लागवड करा.

☎️ **मोफत कृषी हेल्पलाइन:** 1800-180-1551 (कृषी सल्ला केंद्र)"""
        elif lang_name == "Hindi":
            return f"""🙏 **नमस्कार किसान भाई!** 🌾

🔴 **पहचाना गया रोग / कीट:** **{issue_name}**

🦠 **फसल पर प्रभाव (How it Affects Plant):**
• यह कीट या रोग पत्तियों का रस चूसता है, जिससे प्रकाश संश्लेषण (Photosynthesis) बाधित होता है और पत्तियां पीली पड़कर सूख जाती हैं।

🌧️ **प्रकोप का कारण (Why it Attacks):**
• मौसम में अत्यधिक नमी, बादल छाए रहना और नाइट्रोजन (यूरिया) का अत्यधिक उपयोग कीटों के पनपने का मुख्य कारण है।

📊 **बीमारी / कीट प्रकोप के 3 चरण (Stages of Disease / Infestation):**
• **🌱 1. प्रारंभिक चरण (Early Stage):** पत्तियों पर छोटे धब्बे (1-5% प्रभाव)। 5% नीम तेल एवं स्टिकी ट्रैप से नियंत्रण संभव।
• **🌿 2. मध्यम चरण (Moderate Stage):** 10-30% प्रभाव। 48 घंटे के भीतर रसायनिक छिड़काव आवश्यक।
• **🥀 3. गंभीर चरण (Critical Stage):** 50%+ फसल प्रभावित, पत्तियां सूखना व सड़ना। तुरंत आपातकालीन सिस्टमिक स्प्रे व रोगग्रस्त पौधों को जलाना आवश्यक.

💊 **चरण 1: रासायनिक छिड़काव (Chemical Treatment):**
• **दवा:** प्रोफेनोफॉस 50% EC (2 मिली प्रति लीटर पानी) या इमामेक्टिन बेंजोएट (0.5 ग्राम/लीटर)।
• **मात्रा:** 1 एकड़ के लिए 200 लीटर पानी में 400 मिली दवा मिलाकर छिड़काव करें।
• **सावधानी:** शाम के समय सुरक्षा मास्क पहनकर छिड़काव करें।

🌿 **चरण 2: जैविक एवं देसी उपाय (Organic Treatment):**
• **नीम तेल (Neem Oil):** 5 मिली नीम तेल प्रति लीटर पानी में मिलाकर स्प्रे करें।
• **दशपर्णी अर्क:** 5 मिली दशपर्णी अर्क का स्प्रे करें।
• **स्टिकी ट्रैप:** खेत में प्रति एकड़ 10-12 पीले व नीले स्टिकी ट्रैप लगाएं।

🛡️ **चरण 3: दीर्घकालिक बचाव:**
• प्रभावित पत्तियों को खेत से बाहर नष्ट करें।

☎️ **हेल्पलाइन:** 1800-180-1551"""
              elif lang_name == "Gujarati":        # ← ADD FROM HERE
            return f"""🙏 **નમસ્કાર ખેડૂત ભાઈ/બહેન!** 🌾

🔴 **શોધાયેલ રોગ / જીવાત:** **{issue_name}**

🦠 **પાક પર અસર:**
- આ રોગ અથવા જીવાત પાંદડાનો રસ ચૂસે છે, જેથી પ્રકાશ-સંશ્લેષણ અટકે છે અને ઉત્પાદન ૩૦-૫૦% ઘટે છે.

🌧️ **ઉત્પત્તિનાં કારણો:**
- ભેજ, વાદળછાયું હવામાન અને વધુ પડતા નાઇટ્રોજનનો ઉપયોગ.

💊 **રાસાયણિક સ્પ્રે:**
- પ્રોફેનોફોસ ૫૦% EC (૨ ml/લિટર) અથવા ઇમામેક્ટિન (૦.૫ ગ્રામ/લિટર).
- સાંજે માસ્ક પહેરીને છંટકાવ કરો.

🌿 **જૈવિક ઉપાય:**
- લીમડાનું તેલ ૫ ml/લિટર અથવા દશપર્ણી અર્ક ૫ ml/લિટર.
- ચીકણા પીળા-વાદળી ટ્રેપ એકર દીઠ ૧૦-૧૨ લગાવો.

☎️ **હેલ્પલાઇન:** 1800-180-1551"""

        elif lang_name == "Punjabi":
            return f"""🙏 **ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਭਰਾ/ਭੈਣ!** 🌾

🔴 **ਪਛਾਣਿਆ ਗਿਆ ਰੋਗ / ਕੀਟ:** **{issue_name}**

🦠 **ਫਸਲ ਉੱਤੇ ਅਸਰ:**
- ਇਹ ਰੋਗ ਪੱਤਿਆਂ ਦਾ ਰਸ ਚੂਸਦਾ ਹੈ, ਜਿਸ ਨਾਲ ਝਾੜ ੩੦-੫੦% ਘੱਟਦਾ ਹੈ.

🌧️ **ਕਾਰਨ:**
- ਵੱਧ ਨਮੀ, ਬੱਦਲਵਾਈ ਮੌਸਮ ਅਤੇ ਜ਼ਿਆਦਾ ਯੂਰੀਆ ਦੀ ਵਰਤੋਂ.

💊 **ਰਸਾਇਣਕ ਸਪ੍ਰੇ:**
- ਪ੍ਰੋਫੇਨੋਫੋਸ ੫੦% EC (੨ ml/ਲਿਟਰ) ਜਾਂ ਇਮਾਮੇਕਟਿਨ (੦.੫ ਗ੍ਰਾਮ/ਲਿਟਰ).
- ਸ਼ਾਮ ਨੂੰ ਮਾਸਕ ਪਾ ਕੇ ਸਪ੍ਰੇ ਕਰੋ.

🌿 **ਜੈਵਿਕ ਉਪਾਅ:**
- ਨਿੰਮ ਤੇਲ ੫ ml/ਲਿਟਰ ਜਾਂ ਦਸ਼ਪਰਣੀ ਅਰਕ ੫ ml/ਲਿਟਰ.
- ਪੀਲੇ-ਨੀਲੇ ਸਟਿੱਕੀ ਟਰੈਪ ਏਕੜ ਪਿੱਛੇ ੧੦-੧੨ ਲਗਾਓ.

☎️ **ਹੈਲਪਲਾਈਨ:** 1800-180-1551"""
            
        else:
            return f"""🙏 **Hello Dear Farmer!** 🌾

🔴 **Detected Issue:** **{issue_name}**

🦠 **How it Affects the Crop:**
• This pest/disease disrupts photosynthesis, causes chlorosis, saps leaf nutrients, and clogs stem vascular tissues, leading to potential 30-50% yield loss.

🌧️ **Why it Occurs (Triggers):**
• High relative atmospheric humidity (>80%), prolonged cloudy weather, and excessive nitrogenous fertilizer application create favorable conditions for pest outbreaks.

📊 **3 Stages of Disease / Infestation:**
• **🌱 1. Early Stage (1-5% Damage):** Mild leaf spotting or initial egg clusters. Easily controlled with 5% Neem Oil spray & sticky traps.
• **🌿 2. Moderate Stage (10-30% Damage):** Active lesions & caterpillar feeding. Requires targeted chemical spray (Profenofos / Emamectin) within 48 hours.
• **🥀 3. Critical Stage (50%+ Damage):** Severe defoliation, stem rot, or boll boring. Requires emergency systemic sprays and destruction of infected plant debris.

💊 **Step 1: Chemical Spray Treatment:**
• **Recommended Pesticide:** Spray Profenofos 50% EC (2 ml / Liter of water) or Emamectin Benzoate 5% SG (0.5g / Liter).
• **Dosage:** 400 ml in 200 Liters of water per Acre.
• **Safety:** Always spray in the late afternoon wearing protective gloves and face mask.

🌿 **Step 2: Organic & Biological Control:**
• **Neem Oil Spray:** Mix 5 ml Neem Oil (1500 PPM) + 1 ml liquid soap per Liter of water and spray thoroughly.
• **Dashparni Ark:** Spray 5 ml Dashparni Ark per Liter of water.
• **Traps:** Install 10-12 Yellow and Blue Sticky Traps per Acre.

🛡️ **Step 3: Field Management & Prevention:**
• Collect and burn infected crop residues to eliminate spore inoculum.

☎️ **Toll-Free Kisan Helpline:** 1800-180-1551"""


# ─────────────────────────────────────────────────────────────
# SIDEBAR  (shown only after login)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    farmer_name_display = st.session_state.get("farmer_name", "Farmer")
    farmer_dist_display = st.session_state.get("farmer_district", "")

    st.markdown(f"""
    <div style='text-align:center;padding:16px;background:linear-gradient(135deg,#E8F5E9,#C8E6C9);
                border-radius:14px;margin-bottom:15px;border:1px solid #A5D6A7'>
        <img src='data:image/jpeg;base64,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' width='80' style='border-radius:10px; margin-bottom:5px;'/><h2 style='color:#1B5E20;margin:0;font-weight:700'>महाकृषि</h2>
        <p style='color:#2E7D32;font-size:0.88rem;margin:3px 0 0;font-weight:600'>MahaKrishi AI</p>
        <span class='figma-badge' style='background:#1B5E20;color:white;margin-top:6px;display:inline-block'>
            Govt. Agri-Tech Initiative
        </span>
    </div>
    <div style='background:#F1F8E9;border-radius:10px;padding:10px 14px;margin-bottom:12px;border:1px solid #C8E6C9'>
        <small>👤 <b>{farmer_name_display}</b><br>📍 {farmer_dist_display}</small>
    </div>
    """, unsafe_allow_html=True)

    lang_code = st.session_state.get("app_lang", "mr")
    lang_name = st.session_state.get("lang_name", "Marathi")

    enable_voice = st.toggle("🔊 Voice Output / आवाज उत्तर", value=True)

    st.markdown("---")
    st.markdown("### 📊 AI Model Directory")
    st.markdown("""
    <div class='contact-card'><small>
    🌾 <b>Crop Diseases:</b> 39 Classes (Rice, Sugarcane, Cotton, Wheat, Tomato, Potato)<br>
    🐛 <b>Crop Pests:</b> 14 Classes (Bollworm, Stem Borer, Aphids, Whitefly, Armyworm, etc.)<br>
    🤖 <b>AI Advisory:</b> Gemini AI + gTTS Voice Output<br>
    🎯 <b>Accuracy:</b> Test-Time Augmentation (TTA ×4)
    </small></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#FFF3E0;border-left:4px solid #FF9800;padding:10px;border-radius:6px'>
    <small><b>🚨 Emergency Agri Helpline:</b><br>
    📞 Kisan Call Center: <b>1800-180-1551</b> (Toll-Free)</small>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button(_t("signout"), use_container_width=True):
        for key in ["logged_in", "farmer_name", "farmer_phone", "farmer_district"]:
            st.session_state.pop(key, None)
        st.rerun()


# ─────────────────────────────────────────────────────────────
# FIGMA DYNAMIC HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='figma-header'>
    <div style='flex: 1; min-width: 0;'>
        <h1 class='figma-header-title'>🌾 MahaKrishi AI | महाकृषि</h1>
        <p class='figma-header-sub'>
            AI Crop Disease &amp; Pest Detection | Chemical &amp; Organic Remedies | Specialist Helplines &amp; Govt Schemes
        </p>
    </div>
    <div style='flex-shrink: 0;'>
        <span class='figma-badge'>🟢 System Active | महाराष्ट्र शासन</span>
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
            "🎯 Select AI Target Mode / काय ओळखायचे आहे?",
            ["🌾 Crop Disease Detection (पिकांचे रोग)", "🐛 Pest Identification (कीड ओळख)"],
            horizontal=True
        )

    col_img, col_res = st.columns([1, 1.3], gap="large")

    with col_img:
        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### 📷 Upload Crop / Pest Photo")
        uploaded = st.file_uploader("Choose leaf or pest photo...", type=["jpg","jpeg","png","bmp","webp"],
                                    label_visibility="collapsed")

        if uploaded:
            pil_image = Image.open(uploaded).convert("RGB")
            st.image(pil_image, caption="📸 Uploaded Image", use_container_width=True)
            analyze_btn = st.button("🔍 Analyze with AI | निदान करा", type="primary", use_container_width=True)
        else:
            st.markdown("""
            <div style='background:#F9FBE7;border:2px dashed #8BC34A;border-radius:14px;
                        padding:40px;text-align:center'>
                <div style='font-size:3rem'>📸</div>
                <p style='color:#33691E;font-weight:600;margin:10px 0 2px'>Upload a photo of crop leaf or pest</p>
                <small style='color:#558B2F'>Supports JPG, PNG, WEBP</small>
            </div>""", unsafe_allow_html=True)
            analyze_btn = False
        st.markdown("</div>", unsafe_allow_html=True)

    with col_res:
        st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
        st.markdown("### 🧠 AI Diagnosis & Advisory")

        if not uploaded:
            st.markdown("""
            <div style='background:#E8F5E9;border-radius:12px;padding:30px;text-align:center'>
                <div style='font-size:2.5rem'>🌱</div>
                <h4 style='color:#1B5E20;margin:8px 0 4px'>Ready for Instant AI Diagnosis</h4>
                <p style='color:#2E7D32;font-size:0.9rem'>Upload an image on the left and click 'Analyze with AI'</p>
            </div>""", unsafe_allow_html=True)

        elif analyze_btn:
            is_pest_mode = "Pest" in model_mode

            # ── IMAGE QUALITY CHECK FIRST ──
            with st.spinner("🔎 Checking image quality..."):
                quality_ok, quality_msg = check_image_quality(pil_image)

            if not quality_ok:
                st.warning(quality_msg)
                st.info("💡 **Tip:** Take photo in bright natural light, hold camera steady, and ensure the leaf fills most of the frame.")
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
                            <span class='badge-low-conf'>⚠️ Low Confidence Detection</span>
                            <h4 style='color:#E65100;margin:10px 0 4px'>Best Match: {name}</h4>
                            <p style='margin:0;color:#BF360C'>AI Confidence: <b>{conf:.1f}%</b> — This is below the reliable threshold (45%)</p>
                            <p style='margin:6px 0 0;font-size:0.88rem;color:#6D4C41'>
                            📌 <b>Suggestions:</b> Retake the photo in bright natural light, ensure leaf fills the frame, 
                            avoid shadows, and make sure the image is sharp/in-focus.
                            </p>
                        </div>""", unsafe_allow_html=True)
                    else:
                        badge_cls = "badge-success" if healthy else ("badge-warning" if is_pest_mode else "badge-emergency")
                        status_txt = "Healthy Crop! 🎉" if healthy else ("Pest Detected! 🐛" if is_pest_mode else "Disease Detected! 🔴")

                        st.markdown(f"""
                        <div style='background:#FAFAFA;border-radius:12px;padding:16px;margin-bottom:12px;border:1px solid #E0E0E0'>
                            <span class='{badge_cls}'>{status_txt}</span>
                            <h3 style='color:#1B5E20;margin:10px 0 4px'>{name}</h3>
                            <p style='color:#558B2F;font-size:0.88rem;margin:0'>AI Confidence (TTA avg): <b>{conf:.1f}%</b></p>
                        </div>""", unsafe_allow_html=True)
                        st.progress(conf / 100)

                        with st.expander("📊 Probable AI Top 3 Matches"):
                            for i, r in enumerate(results):
                                st.markdown(f"{'🥇🥈🥉'[i]} **{r['name']}** — `{r['confidence']:.1f}%`")
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
                                <b>🚨 {name} detected in {farmer_district} district!</b><br>
                                <small>There are <b>{nearby_count}</b> registered farmers in your district 
                                who could be at risk. Alert them instantly.</small>
                            </div>""", unsafe_allow_html=True)

                            alert_key = f"alerted_{name}_{uploaded.name}"
                            if alert_key not in st.session_state:
                                st.session_state[alert_key] = False

                            if not st.session_state[alert_key]:
                                if st.button(
                                    f"🚨 Alert {nearby_count} Farmers in {farmer_district} | शेतकऱ्यांना अलर्ट पाठवा",
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
                                    f"✅ Alert successfully sent to **{nearby_count}** registered farmers "
                                    f"in **{farmer_district}** district! "
                                    f"Disease alert for **{name}** recorded in system."
                                )

                        # Generate AI Advisory
                        with st.spinner(f"💬 Generating {lang_name} advisory & remedies..."):
                            ai_resp = get_ai_advisory(name, is_pest_mode, lang_name, conf)

                            audio_bytes = None
                            if enable_voice:
                                try:
                                    audio_bytes = text_to_speech(ai_resp, lang_code)
                                except Exception:
                                    audio_bytes = None

                            st.markdown(f"<div class='chat-box'>{ai_resp.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

                            if enable_voice and audio_bytes:
                                st.markdown("#### 🔊 Marathi/Hindi Voice Advisory (आवाज उत्तर)")
                                st.audio(audio_bytes, format="audio/mp3")

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 2: TREATMENT AI CHATBOT (CHEMICAL & ORGANIC)
# ─────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### 🤖 Krishi AI Specialist Chatbot / कृषी उपचार चॅटबॉट")
    st.markdown(" Ask any crop disease, pest issue, or treatment query. Get **Chemical (रसायनिक)** and **Organic (जैविक)** solutions instantly!")

    # Preset quick chips (Dynamic Language)
    st.markdown("#### 💡 Quick Questions / जलद प्रश्न / शीघ्र प्रश्न:")
    c1, c2, c3, c4 = st.columns(4)
    quick_q = None
    if c1.button("🌾 Rice Stem Borer Spray?", use_container_width=True):
        if lang_name == "English":
            quick_q = "What is the chemical and organic treatment for Rice Stem Borer?"
        elif lang_name == "Hindi":
            quick_q = "धान की फसल के खोड कीट (Stem Borer) के लिए रासायनिक एवं जैविक उपाय बताएं।"
        else:
            quick_q = "धान्य / तांदूळ पिकावरील खोड कीडीसाठी रसायनिक आणि सेंद्रिय उपाय सांगा."

    if c2.button("🌿 Organic Control for Aphids?", use_container_width=True):
        if lang_name == "English":
            quick_q = "How to prepare organic pesticide and Neem oil for Aphids control?"
        elif lang_name == "Hindi":
            quick_q = "माहू (Aphids) के लिए जैविक एवं नीम तेल दवा कैसे तैयार करें?"
        else:
            quick_q = "मावा (Aphids) साठी जैविक आणि सेंद्रिय औषध कसे तयार करावे?"

    if c3.button("🎋 Sugarcane Red Rot Remedy?", use_container_width=True):
        if lang_name == "English":
            quick_q = "What chemical spray and organic remedy is recommended for Sugarcane Red Rot?"
        elif lang_name == "Hindi":
            quick_q = "गन्ने के लाल सड़न (Red Rot) रोग के लिए कौन सी दवा का छिड़काव करें?"
        else:
            quick_q = "उसावरील तांबेरा व तांबड्या रोगासाठी कोणते औषध फवारावे?"

    if c4.button("🌸 Cotton Pink Bollworm Spray?", use_container_width=True):
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
            1. 🌾 Crop Disease & Pest Diagnosis (पिकांचे रोग व कीड निदान)
            2. 💊 Chemical Spray & 🌿 Organic Remedies (फवारणी व सेंद्रिय घरगुती उपाय)
            3. 🏛️ Government Schemes & Helplines (शासकीय योजना व हेल्पलाइन)

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
               🔴 ओळख व कारण / Identified Issue & Cause: [Simple human explanation]
               💊 रसायनिक फवारणी (Chemical Spray): [Recommended spray name, exact dosage per Liter/Acre, best spraying time & safety mask]
               🌿 सेंद्रिय व जैविक उपचार (Organic Remedy): [Neem oil / Jeevamrut / Dashparni Ark / Sticky traps recipe & dosage]
               🛡️ शेतकरी मित्रासाठी विशेष सल्ला (Expert Human Advice): [Field management & encouragement]
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
                        bot_ans = "🙏 **मला आपला संदेश स्पष्टपणे समजला नाही.**\n\nकृपया आपले पीक, रोग किंवा शेतीविषयीचा प्रश्न औपचारिक व स्पष्टपणे सांगावा ही नम्र विनंती. उदा. *'उसावरील तांबेरा रोगासाठी उपाय काय?'*"
                    elif lang_name == "Hindi":
                        bot_ans = "🙏 **मुझे आपका संदेश स्पष्ट रूप से समझ नहीं आया।**\n\nकृपया अपनी फसल, बीमारी या खेती से जुड़ा प्रश्न स्पष्ट रूप से लिखें। जैसे: *'धान के खोड कीट का उपचार क्या है?'*"
                    else:
                        bot_ans = "🙏 **I could not understand your message.**\n\nCould you please state your crop, disease, or farming question more clearly in a formal manner?"
                elif is_greeting:
                    if lang_name == "Marathi":
                        bot_ans = "🙏 **नमस्कार! मी महाकृषि AI सहाय्यक आहे.** 🌾\n\nमी तुम्हाला शेतीविषयक खालील बाबतीत मदत करू शकतो:\n\n• 🌾 **पिकांचे रोग व कीड ओळख** (Crop Disease & Pest Diagnosis)\n• 💊 **रसायनिक फवारणी व 🌿 सेंद्रिय उपाय** (Chemical & Organic Spray Remedies)\n• 🏛️ **शासकीय कृषी योजना व तज्ज्ञ हेल्पलाइन** (Govt Schemes & Helplines)\n\nतुमच्या पिकाची समस्या किंवा प्रश्न खाली विचारा!"
                    elif lang_name == "Hindi":
                        bot_ans = "🙏 **नमस्ते! मैं महाकृषि AI सहायक हूँ।** 🌾\n\nमैं आपकी खेती में निम्नलिखित सहायता कर सकता हूँ:\n\n• 🌾 **फसलों के रोग एवं कीट पहचान**\n• 💊 **रासायनिक छिड़काव एवं 🌿 जैविक उपचार**\n• 🏛️ **सरकारी कृषि योजनाएं एवं हेल्पलाइन**\n\nकृपया अपनी फसल का प्रश्न नीचे लिखें!"
                    else:
                        bot_ans = "🙏 **Hello! I am MahaKrishi AI Assistant.** 🌾\n\nI can assist you with:\n\n• 🌾 **Crop Disease & Pest Diagnosis**\n• 💊 **Chemical Spray & 🌿 Organic Remedies**\n• 🏛️ **Government Schemes & Helplines**\n\nPlease ask any crop question or problem below!"
                elif not is_agri_related:
                    if lang_name == "Marathi":
                        bot_ans = "❓ **कृपया तुमचे पीक, रोग किंवा कीड कोणती आहे ते सांगू शकाल का?**"
                    elif lang_name == "Hindi":
                        bot_ans = "❓ **क्या आप कृपया बता सकते हैं कि आपकी फसल का रोग या कीट कौन सा है?**"
                    else:
                        bot_ans = "❓ **Can you please tell what is your crop disease or pest?**"
                else:
                    if lang_name == "Marathi":
                        bot_ans = f"""🔴 कृषी सल्ला (प्रश्न: {active_query})

💊 रसायनिक उपचार (Chemical Treatment):
• कीड/रोगासाठी योग्य कीटकनाशकाची (उदा. क्लोरपायरीफॉस २ मिली/लिटर किंवा इमॅमेक्टिन ०.५ ग्रॅम/लिटर) फवारणी करा.
• संध्याकाळी फवारणी करणे अधिक प्रभावी ठरते.

🌿 सेंद्रिय व जैविक उपचार (Organic Treatment):
• ५% कडुनिंब तेल (Neem Oil) किंवा दशपर्णी अर्क (५ मिली/लिटर) चा वापर करा.
• शेतात पिवळे व निळे चिकट सापळे (Sticky Traps) लावा.

🛡️ बचाव व सुरक्षा:
• मास्क आणि हातमोजे वापरूनच फवारणी करा.
☎️ अधिक मदतीसाठी हेल्पलाइन: 1800-180-1551"""
                    elif lang_name == "Hindi":
                        bot_ans = f"""🔴 कृषि सलाह (प्रश्न: {active_query})

💊 रासायनिक उपचार (Chemical Treatment):
• उपयुक्त कीटनाशक (जैसे इमामेक्टिन 0.5 ग्राम/लीटर) का छिड़काव करें।

🌿 जैविक उपचार (Organic Treatment):
• 5% नीम तेल या दशपर्णी अर्क (5 मिली/लीटर) का स्प्रे करें।

🛡️ बचाव:
• सुरक्षा मास्क पहनकर छिड़काव करें।
☎️ हेल्पलाइन: 1800-180-1551"""
                    else:
                        bot_ans = f"""🔴 Agronomic Advisory (Query: {active_query})

💊 Chemical Treatment:
• Spray recommended pesticide with protective mask.

🌿 Organic Treatment:
• Spray 5% Neem Oil or Dashparni Ark (5 ml / Liter).

☎️ Kisan Helpline: 1800-180-1551"""
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
    st.markdown("### 📞 Verified Agricultural Specialist Directory & Emergency Helplines")
    st.markdown("Connect directly with Maharashtra Krishi Vigyan Kendras (KVK), ICAR Scientists, and Govt Officers.")

    # Emergency Call Bar
    st.markdown("""
    <div style='background:#FFEBEE;border:2px solid #FFCDD2;border-radius:12px;padding:16px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center'>
        <div>
            <h4 style='color:#C62828;margin:0'>🚨 Toll-Free Kisan Call Center (राष्ट्रीय कृषी हेल्पलाइन)</h4>
            <p style='color:#B71C1C;margin:2px 0 0;font-size:0.9rem'>Call for free instant expert advice in Marathi, Hindi & English (6 AM - 10 PM)</p>
        </div>
        <a href='tel:18001801551' style='background:#C62828;color:white;padding:10px 20px;border-radius:30px;text-decoration:none;font-weight:bold'>📞 1800-180-1551</a>
    </div>""", unsafe_allow_html=True)

    r1, r2, r3, r4 = st.tabs(["🏛️ State & National", "🌾 Western MH & Pune", "🎋 Marathwada & Nashik", "🌿 Vidarbha & Cotton"])

    with r1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>🇮🇳 Kisan Call Center (KCC)</h4>
                <p><b>Number:</b> 1800-180-1551 (Toll-Free)<br>
                <b>Languages:</b> Marathi, Hindi, English<br>
                <b>Timings:</b> 6:00 AM - 10:00 PM (Daily)</p>
                <a href='tel:18001801551'>📞 Call KCC Now</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>🌾 Maharashtra Agriculture Dept (कृषी आयुक्तालय)</h4>
                <p><b>Helpline:</b> 1800-233-4000 / 14447<br>
                <b>Location:</b> Shivajinagar, Pune<br>
                <b>Services:</b> Crop advice, Subsidies, Disease alerts</p>
                <a href='tel:18002334000'>📞 Call State Agri Helpline</a>
            </div>""", unsafe_allow_html=True)

    with r2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>📍 KVK Baramati (Pune District)</h4>
                <p><b>Phone:</b> 02112-255227 / 255327<br>
                <b>Speciality:</b> Sugarcane, Fruits, Pest Control<br>
                <b>WhatsApp Support:</b> <a href='https://wa.me/919422000000' target='_blank'>💬 Chat on WhatsApp</a></p>
                <a href='tel:02112255227'>📞 Call KVK Baramati</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>🏛️ Vasantdada Sugar Institute (VSI Pune)</h4>
                <p><b>Phone:</b> 020-26902100 / 26902200<br>
                <b>Speciality:</b> Sugarcane Red Rot, Pokkah Boeng, Pest Advisory</p>
                <a href='tel:02026902100'>📞 Call VSI Experts</a>
            </div>""", unsafe_allow_html=True)

    with r3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>📍 KVK Yashwantrao Chavan (Nashik)</h4>
                <p><b>Phone:</b> 0253-2415121 / 2415321<br>
                <b>Speciality:</b> Grapes, Onion, Vegetables, Leaf Blight Advisory</p>
                <a href='tel:02532415121'>📞 Call KVK Nashik</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>🌾 MPKV Rahuri Agri University</h4>
                <p><b>Phone:</b> 02426-243208 / 243311<br>
                <b>Speciality:</b> Pulses, Rice Blast, Crop Pathology Research</p>
                <a href='tel:02426243208'>📞 Call MPKV Rahuri</a>
            </div>""", unsafe_allow_html=True)

    with r4:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='contact-card'>
                <h4>🔬 ICAR - CICR Cotton Experts (Nagpur)</h4>
                <p><b>Phone:</b> 07103-275536 / 275538<br>
                <b>Speciality:</b> Pink Bollworm, Cotton Leaf Curl, Whitefly Control</p>
                <a href='tel:07103275536'>📞 Call CICR Cotton Helpline</a>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='contact-card'>
                <h4>📍 Dr. PDKV Agri University (Akola)</h4>
                <p><b>Phone:</b> 0724-2258419<br>
                <b>Speciality:</b> Soybean, Cotton, Grain Crop Protection</p>
                <a href='tel:07242258419'>📞 Call PDKV Akola</a>
            </div>""", unsafe_allow_html=True)

    # Specialist Form
    st.markdown("---")
    st.markdown("#### 📝 Request Direct Specialist Callback / तज्ज्ञ कॉल विनंती")
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
        submit_form = st.form_submit_button("📩 Submit Request / विनंती पाठवा", type="primary")

        if submit_form:
            st.success(f"✅ धन्यवाद {farmer_name}! तुमची विनंती नोंदवली गेली आहे. कृषी तज्ज्ञ २४ तासांत {farmer_phone} वर संपर्क साधतील.")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 4: NEARBY FARMER OUTBREAK MAP & ALERT SYSTEM
# ─────────────────────────────────────────────────────────────
with tab_map:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### 🗺️ Nearby Farmer Disease & Pest Outbreak Alert Map")
    st.markdown("Real-time outbreak mapping across Maharashtra. Color-coded severity pins notify nearby farmers within **10 km - 50 km** radius.")

    # Show real alert history from Excel if available
    if os.path.exists(EXCEL_ALERTS_FILE):
        try:
            alerts_df = pd.read_excel(EXCEL_ALERTS_FILE, dtype=str)
            if not alerts_df.empty:
                st.markdown("#### 📋 Recent AI-Detected Alerts (from Registered Farmers):")
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
        {"district": "Nashik", "lat": 20.0059, "lon": 73.7898, "issue": "Fall Armyworm (लष्करी अळी)", "crop": "Maize / मका", "severity": "🔴 Emergency Outbreak", "radius": 15000, "color": [211, 47, 47, 180]},
        {"district": "Kolhapur", "lat": 16.7050, "lon": 74.2433, "issue": "Sugarcane Red Rot (ऊस तांबेरा)", "crop": "Sugarcane / ऊस", "severity": "🟠 Warning", "radius": 20000, "color": [245, 124, 0, 180]},
        {"district": "Pune (Baramati)", "lat": 18.1519, "lon": 74.5768, "issue": "Early Shoot Borer (खोड कीड)", "crop": "Sugarcane / ऊस", "severity": "🔴 Emergency Outbreak", "radius": 12000, "color": [211, 47, 47, 180]},
        {"district": "Nagpur", "lat": 21.1458, "lon": 79.0882, "issue": "Pink Bollworm (गुलाबी बोंडअळी)", "crop": "Cotton / कापूस", "severity": "🔴 Emergency Outbreak", "radius": 25000, "color": [211, 47, 47, 180]},
        {"district": "Sambhajinagar", "lat": 19.8762, "lon": 75.3433, "issue": "Whitefly Pest (पांढरी माशी)", "crop": "Cotton / कापूस", "severity": "🟡 Advisory Watch", "radius": 18000, "color": [251, 192, 45, 180]},
        {"district": "Solapur", "lat": 17.6599, "lon": 75.9064, "issue": "Aphids Damage (मावा)", "crop": "Vegetables / भाजीपाला", "severity": "🟠 Warning", "radius": 10000, "color": [245, 124, 0, 180]}
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
    st.markdown("#### 🚨 Active Regional Outbreak Alerts:")
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
                <h4 style='margin:8px 0 2px;color:#1B5E20'>📍 {ob['district']} — {ob['issue']}</h4>
                <p style='margin:0;font-size:0.88rem;color:#558B2F'>
                <b>Affected Crop:</b> {ob['crop']} | <b>Impact Radius:</b> {ob['radius']//1000} km{reg_info}
                </p>
            </div>""", unsafe_allow_html=True)

    # Broadcast Alert Form
    st.markdown("---")
    st.markdown("#### 📢 Broadcast New Disease/Pest Alert to Nearby Farmers")
    with st.form("alert_broadcast"):
        ac1, ac2, ac3 = st.columns(3)
        b_dist  = ac1.selectbox("जिल्हा / District", ALL_DISTRICTS)
        b_crop  = ac2.text_input("पीक / Crop Name", "Sugarcane / कापूस / धान")
        b_issue = ac3.selectbox("रोग / कीड / Issue Type", ["Pink Bollworm", "Fall Armyworm", "Red Rot", "Rice Blast", "Aphids", "Whitefly"])
        b_desc  = st.text_area("अलर्ट माहिती / Detailed Outbreak Description")
        broadcast_btn = st.form_submit_button("🚨 Broadcast SMS & Map Alert | अलर्ट जारी करा", type="primary")

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
                f"🚨 अलर्ट यशस्वीपणे पाठवला! "
                f"**{b_dist}** परिसरातील **{reach}** नोंदणीकृत शेतकऱ्यांना "
                f"**{b_issue}** बद्दल अलर्ट पाठवण्यात आला आहे."
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 5: GOVERNMENT SCHEMES & SUBSIDIES PORTAL
# ─────────────────────────────────────────────────────────────
with tab_schemes:
    st.markdown("<div class='figma-card'>", unsafe_allow_html=True)
    st.markdown("### 🏛️ Official Government Agricultural Schemes & Subsidies Portal")
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
                <p><b>🎁 Benefit:</b> {sc['benefit']}<br>
                <b>👥 Eligibility:</b> {sc['eligibility']}<br>
                <b>📄 Required Docs:</b> {sc['docs']}</p>
            </div>""", unsafe_allow_html=True)
            st.link_button(f"🔗 Apply Now / अधिकृत संकेतस्थळ ({sc['name'].split()[0]})", sc['link'], use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:20px;color:#558B2F;font-size:0.85rem;border-top:1px solid #DCEDC8;margin-top:40px'>
🌾 <b>MahaKrishi AI</b> | महाकृषि | Maharashtra Government Hackathon Initiative<br>
Powered by PyTorch EfficientNet-B0 + Google Gemini AI + gTTS Voice Advisory + PyDeck Outbreak Maps
</div>
""", unsafe_allow_html=True)
