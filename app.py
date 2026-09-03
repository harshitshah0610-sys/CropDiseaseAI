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
    page_title="MahaKrishi AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# PROFESSIONAL GOVERNMENT-STYLE CSS STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans Devanagari', sans-serif;
        color: #212529;
    }

    /* Main Header Banner */
    .figma-header {
        background: linear-gradient(135deg, #113f15 0%, #1e5c23 100%);
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
    }
    .figma-header-title { font-size: 2rem; font-weight: 700; margin: 0; color: #FFFFFF; letter-spacing: -0.5px; }
    .figma-header-sub { font-size: 0.95rem; color: #daebd5; margin-top: 6px; font-weight: 400; }
    
    .figma-badge {
        background: rgba(255, 255, 255, 0.12);
        padding: 6px 14px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Professional Grid Cards */
    .figma-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #e3e8e3;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Status Badges */
    .badge-emergency { background: #fde8e8; color: #9b1c1c; border: 1px solid #f8b4b4; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }
    .badge-warning   { background: #fef08a; color: #713f12; border: 1px solid #fef08a; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }
    .badge-success   { background: #def7ec; color: #03543f; border: 1px solid #bcf0da; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }
    .badge-low-conf  { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }

    /* Profile Core Layouts */
    .profile-hero {
        background: #FFFFFF;
        border-radius: 12px; 
        padding: 32px; 
        margin-bottom: 24px;
        color: #113f15; 
        display: flex; 
        align-items: center; 
        gap: 24px;
        border: 1px solid #e3e8e3;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
    }
    .profile-avatar {
        width: 96px; 
        height: 96px; 
        background: #f3f4f6;
        border-radius: 50%; 
        display: flex; 
        align-items: center;
        justify-content: center; 
        border: 1px solid #e5e7eb; 
        flex-shrink: 0;
        overflow: hidden;
    }
    .profile-avatar img { width: 100%; height: 100%; object-fit: cover; }
    
    .profile-stat-card {
        background: #f8faf8; 
        border: 1px solid #e3e8e3;
        border-radius: 6px; 
        padding: 16px; 
        text-align: center;
    }
    .profile-stat-num { font-size: 1.75rem; font-weight: 700; color: #1e5c23; margin: 0; }
    .profile-stat-label { color: #4b5563; font-size: 0.85rem; font-weight: 500; margin: 4px 0 0; }
    
    .history-row {
        background: #ffffff; 
        border: 1px solid #e5e7eb;
        border-radius: 6px; 
        padding: 14px; 
        margin-bottom: 10px;
        display: flex; 
        align-items: center; 
        gap: 14px;
    }

    /* Structural design components */
    .remedy-chemical { background: #fffbeb; border-left: 4px solid #d97706; padding: 16px; margin: 12px 0; border-radius: 0 4px 4px 0; }
    .remedy-organic { background: #f0fdf4; border-left: 4px solid #16a34a; padding: 16px; margin: 12px 0; border-radius: 0 4px 4px 0; }
    .chat-box { background: #f9fafb; border: 1px solid #e5e7eb; padding: 20px; margin: 12px 0; border-radius: 6px; font-size: 0.95rem; line-height: 1.6; }
    .alert-box { background: #fffaf0; border: 1px solid #feebc8; border-radius: 6px; padding: 16px; margin: 12px 0; }
    .contact-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 16px; margin-bottom: 14px; }
    .scheme-card { background: #ffffff; border: 1px solid #e3e8e3; border-radius: 8px; padding: 20px; height: 100%; }

    /* Government Institutional Aesthetics / Logos Replacement Layout */
    .gov-logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .gov-logo-line {
        width: 2px;
        height: 36px;
        background-color: rgba(255, 255, 255, 0.3);
    }
    .gov-text-branding {
        font-size: 0.75rem;
        line-height: 1.3;
        color: #daebd5;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ───────────── MOBILE RESPONSIVENESS & REFINE PROFILE ───────────── */
    @media (max-width: 768px) {
        .figma-header { padding: 16px; border-radius: 8px; flex-direction: column; align-items: flex-start; gap: 12px; }
        .figma-header-title { font-size: 1.5rem; }
        .figma-header-sub { font-size: 0.85rem; }
        .profile-hero { flex-direction: column; text-align: center; padding: 20px; gap: 16px; }
        .profile-hero div { text-align: center !important; }
        .profile-avatar { width: 80px; height: 80px; margin: 0 auto; }
        .figma-card { padding: 16px; }
        .profile-stat-num { font-size: 1.5rem; }
        .history-row { flex-direction: column; align-items: flex-start; gap: 8px; }
        .history-row span { align-self: flex-start; }
        .block-container { padding: 1rem; }
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
        "subtitle": "Department of Agriculture • Government of Maharashtra",
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
        "subtitle": "कृषि विभाग • महाराष्ट्र शासन",
        "signin_tab": "लॉग इन",
        "register_tab": "नोंदणी",
        "mobile": "मोबाईल नंबर",
        "name": "पूर्ण नाव",
        "district": "जिल्हा",
        "signin_btn": "लॉग इन करा",
        "register_btn": "नोंदणी करा",
        "sel_lang": "भाषा निवडा",
        "tab_detect": "AI रोग निदान",
        "tab_chat": "कृषि चॅटबॉट",
        "tab_contacts": "विशेषज्ञ संपर्क",
        "tab_map": "रोग अलर्ट नकाशा",
        "tab_schemes": "शासकीय योजना",
        "signout": "लॉग आउट"
    }
}

def _t(key):
    lang = st.session_state.get("app_lang", "en")
    return UI_TEXT.get(lang, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))

IMG_SIZE = 224
DEVICE   = torch.device("cpu")

EXCEL_SIGNIN_FILE = os.path.join(os.path.dirname(__file__), "farmer_signins.xlsx")
EXCEL_ALERTS_FILE = os.path.join(os.path.dirname(__file__), "disease_alerts.xlsx")

CONF_THRESHOLD_LOW  = 45.0
CONF_THRESHOLD_ALERT = 60.0

ALL_DISTRICTS = [
    "Pune", "Nashik", "Kolhapur", "Solapur", "Chhatrapati Sambhajinagar",
    "Nagpur", "Amravati", "Latur", "Satara", "Thane", "Ahmednagar",
    "Jalgaon", "Nanded", "Osmanabad", "Beed", "Buldhana", "Wardha",
    "Yavatmal", "Akola", "Washim", "Ratnagiri", "Sindhudurg", "Other"
]

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
    new_row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name,
        "Phone": phone,
        "District": district,
        "Action": action
    }
    if os.path.exists(EXCEL_SIGNIN_FILE):
        try:
