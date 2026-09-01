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

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KrishiRakshak AI | कृषि रक्षक",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B5E20, #2E7D32, #388E3C);
        padding: 22px 30px; border-radius: 16px; margin-bottom: 25px;
        text-align: center; color: white;
        box-shadow: 0 4px 18px rgba(46,125,50,0.45);
    }
    .main-header h1 { color: white; font-size: 2.1rem; margin: 0; }
    .main-header p  { color: #C8E6C9; font-size: 0.97rem; margin: 5px 0 0; }

    .disease-card {
        border-radius: 13px; padding: 18px; margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.09);
    }
    .chat-box {
        background: #F9FBE7; border-left: 5px solid #8BC34A;
        border-radius: 0 12px 12px 0; padding: 20px;
        margin: 10px 0; font-size: 1rem; line-height: 1.85;
    }
    .info-box {
        background: #E8F5E9; border: 1px solid #A5D6A7;
        border-radius: 8px; padding: 14px; margin: 7px 0;
    }
    .audio-section {
        background: #E3F2FD; border: 1px solid #90CAF9;
        border-radius: 10px; padding: 15px; margin: 10px 0;
    }
    .footer {
        text-align: center; padding: 14px; color: #558B2F;
        font-size: 0.84rem; border-top: 1px solid #DCEDC8; margin-top: 30px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
LANGUAGE_MAP   = {"🇮🇳 हिंदी (Hindi)": "hi",
                  "🌾 मराठी (Marathi)": "mr",
                  "🌍 English": "en"}
LANGUAGE_NAMES = {"🇮🇳 हिंदी (Hindi)": "Hindi",
                  "🌾 मराठी (Marathi)": "Marathi",
                  "🌍 English": "English"}
IMG_SIZE = 224
DEVICE   = torch.device("cpu")

# ─────────────────────────────────────────────────────────────
# LOAD MODEL (PyTorch EfficientNet-B0)
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_disease_model():
    model_path = "crop_disease_model.pth"
    if not os.path.exists(model_path):
        return None, None, "❌ Model not found! Run train_local.py first."
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
        return None, None, f"❌ Error loading model: {e}"


@st.cache_data(show_spinner=False)
def load_class_names_json():
    if os.path.exists("class_names.json"):
        with open("class_names.json", encoding="utf-8") as f:
            return json.load(f), None
    return None, "❌ class_names.json not found"


# ─────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────────────────────
_val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def predict_disease(model, class_names, pil_image):
    tensor = _val_transform(pil_image.convert("RGB")).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = model(tensor)[0]
        probs  = torch.softmax(logits, dim=0).cpu().numpy()
    top3_idx = np.argsort(probs)[::-1][:3]
    return [
        {"disease":  class_names[i].replace("_", " ").replace("  ", " "),
         "raw_name": class_names[i],
         "confidence": float(probs[i]) * 100}
        for i in top3_idx
    ]


def get_gemini_response(model, disease_name, lang_name, confidence):
    is_healthy = "healthy" in disease_name.lower()
    if is_healthy:
        prompt = f"""
        You are KrishiRakshak, an agricultural assistant for Maharashtra farmers.
        The crop looks HEALTHY (confidence {confidence:.1f}%).
        Respond in {lang_name} with simple words a village farmer understands.
        Give: ✅ Good news, 💧 Tips to keep crop healthy, 👀 What to watch for.
        Use emojis. Max 150 words.
        """
    else:
        prompt = f"""
        You are KrishiRakshak, an agricultural expert for Maharashtra farmers.
        Detected disease: **{disease_name}** (Confidence: {confidence:.1f}%)

        Respond ONLY in {lang_name}. Use very simple language for village farmers.

        Format:
        🔴 रोग / Disease: [simple name]
        🤒 लक्षण / Symptoms: [2-3 bullet points — what farmer sees on plant]
        🦠 कारण / Cause: [1-2 simple sentences]
        💊 तुरंत करें / Do Now: [3-4 numbered steps]
        🌿 दवाई / Medicine: [specific product name + dosage available in local market]
        🛡️ बचाव / Prevention: [2-3 tips]
        ☎️ सलाह: [when to call agri officer]

        End with an encouraging line for the farmer. Max 300 words. Full {lang_name} script.
        """
    try:
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"AI error: {e}\nCheck your Gemini API key."


def text_to_speech(text, lang_code):
    clean = text
    for ch in ['*', '#', '`', '🔴', '🤒', '🦠', '💊', '🌿', '🛡️', '☎️',
               '✅', '❌', '🌾', '🔊', '👀', '💧']:
        clean = clean.replace(ch, '')
    clean = ' '.join(clean.split())
    tts = gTTS(text=clean, lang=lang_code, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name); path = f.name
    with open(path, 'rb') as f:
        audio = f.read()
    os.unlink(path)
    return audio


def audio_html(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    return (f'<audio controls autoplay style="width:100%;border-radius:8px;">'
            f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>')


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:12px;background:#E8F5E9;
                border-radius:10px;margin-bottom:15px'>
        <h2 style='color:#1B5E20;margin:0'>🌾 कृषि रक्षक</h2>
        <p style='color:#388E3C;font-size:0.85rem;margin:2px 0'>KrishiRakshak AI</p>
        <p style='color:#558B2F;font-size:0.75rem;margin:0'>Maharashtra Government</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Settings")

    sel_lang  = st.selectbox("🗣️ भाषा / Language", list(LANGUAGE_MAP.keys()))
    lang_code = LANGUAGE_MAP[sel_lang]
    lang_name = LANGUAGE_NAMES[sel_lang]

    st.markdown("### 🔑 API Key")
    _secret = ""
    try:
        _secret = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass

    if _secret:
        api_key = _secret
        st.success("✅ API Key loaded!")
    else:
        api_key = st.text_input("Gemini API Key", type="password",
                                placeholder="AIzaSy...",
                                help="aistudio.google.com/app/apikey")
        if not api_key:
            st.warning("⚠️ Enter API key for AI advice & voice")
            st.markdown("[🔗 Get Free Key](https://aistudio.google.com/app/apikey)")
        else:
            st.success("✅ API Key set!")

    enable_voice = st.toggle("🔊 Voice Output", value=True)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    <div class='info-box'><small>
    <b>Detects 39 crop diseases:</b><br>
    🌾 Rice — 20+ diseases<br>
    🎋 Sugarcane — 9 diseases<br>
    🍅 Tomato — 3 diseases<br>
    🥔 Potato — 1 disease<br>
    🌿 Cotton — 4 diseases<br>
    🌾 Wheat — 1 disease<br>
    ✅ Healthy — 2 classes
    </small></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <small style='color:#558B2F'>
    🏆 Maharashtra Govt Hackathon<br>
    Early Crop Disease Detection<br>
    AI + ML Solution
    </small>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <h1>🌾 KrishiRakshak AI | कृषि रक्षक</h1>
    <p>Early Crop Disease Detection | फसल रोग पहचान | Maharashtra Government Initiative</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────────────────────
with st.spinner("⏳ Loading AI model..."):
    model, class_names, model_err = load_disease_model()

if model_err:
    st.error(model_err)
    st.info("**Steps:** Run `python train_local.py` in terminal, then restart the app.")
    st.stop()

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────
col_img, col_res = st.columns([1, 1.4], gap="large")

# ── LEFT: Upload ─────────────────────────────────────────────
with col_img:
    st.markdown("### 📷 Upload Crop Photo")
    st.markdown("<small style='color:#558B2F'>अपनी फसल की फोटो डालें</small>",
                unsafe_allow_html=True)

    uploaded = st.file_uploader("Choose image...", type=["jpg","jpeg","png","bmp","webp"],
                                label_visibility="collapsed")

    if uploaded:
        pil_image = Image.open(uploaded).convert("RGB")
        st.image(pil_image, caption="📸 Uploaded Image", use_container_width=True)
        st.markdown(f"""
        <div class='info-box'><small>
        📁 {uploaded.name} &nbsp;|&nbsp;
        📐 {pil_image.size[0]}×{pil_image.size[1]}px
        </small></div>""", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Detect Disease | रोग पहचानें",
                                type="primary", use_container_width=True)
    else:
        st.markdown("""
        <div style='background:#F9FBE7;border:2px dashed #AED581;border-radius:12px;
                    padding:45px;text-align:center;margin-top:10px'>
            <div style='font-size:3rem'>📷</div>
            <p style='color:#558B2F;font-weight:bold'>Upload a crop photo</p>
            <p style='color:#7CB342;font-size:0.9rem'>JPG / PNG / JPEG</p>
        </div>""", unsafe_allow_html=True)
        analyze_btn = False

# ── RIGHT: Results ────────────────────────────────────────────
with col_res:
    st.markdown("### 🧠 AI Analysis")

    if not uploaded:
        st.markdown("""
        <div style='background:#F9FBE7;border:1px solid #DCEDC8;border-radius:12px;
                    padding:35px;text-align:center'>
            <div style='font-size:2.5rem'>🌱</div>
            <p style='color:#558B2F;font-weight:bold'>Ready to detect diseases!</p>
            <p style='color:#7CB342;font-size:0.9rem'>Upload a crop photo to start</p>
        </div>""", unsafe_allow_html=True)

    elif analyze_btn:
        # ── Predict ──
        with st.spinner("🔍 Detecting disease..."):
            results = predict_disease(model, class_names, pil_image)

        top     = results[0]
        name    = top["disease"]
        conf    = top["confidence"]
        healthy = "healthy" in name.lower()

        bg  = "#E8F5E9" if healthy else "#FFF8E1"
        bdr = "#4CAF50" if healthy else "#FF9800"
        em  = "✅"      if healthy else "🔴"
        lbl = "Healthy Crop! 🎉" if healthy else "Disease Detected!"

        st.markdown(f"""
        <div style='background:{bg};border:2px solid {bdr};
                    border-radius:12px;padding:18px;margin-bottom:12px'>
            <h3 style='margin:0;color:#1B5E20'>{em} {lbl}</h3>
            <h4 style='color:#388E3C;margin:8px 0 3px'>{name}</h4>
            <p style='color:#558B2F;font-size:0.85rem;margin:0'>
                Confidence: <b>{conf:.1f}%</b></p>
        </div>""", unsafe_allow_html=True)
        st.progress(conf / 100)

        with st.expander("📊 Top 3 Predictions"):
            for i, r in enumerate(results):
                st.markdown(f"{'🥇🥈🥉'[i]} **{r['disease']}** — `{r['confidence']:.1f}%`")
                st.progress(r["confidence"] / 100)

        # ── Gemini AI ──
        if api_key:
            with st.spinner(f"💬 Generating {lang_name} advice..."):
                gemini = genai.GenerativeModel("gemini-1.5-flash")
                genai.configure(api_key=api_key)
                ai_resp = get_gemini_response(gemini, name, lang_name, conf)
                st.session_state.chat_history.append({
                    "disease": name, "confidence": conf,
                    "response": ai_resp,
                    "lang_name": lang_name, "lang_code": lang_code
                })
        else:
            st.warning("⚠️ Add Gemini API key in sidebar for AI advice")


# ─────────────────────────────────────────────────────────────
# CHAT + VOICE OUTPUT
# ─────────────────────────────────────────────────────────────
if st.session_state.chat_history:
    latest = st.session_state.chat_history[-1]
    st.markdown("---")
    st.markdown(f"### 💬 AI Advice | {lang_name} में सलाह")

    st.markdown(
        f"<div class='chat-box'>{latest['response'].replace(chr(10),'<br>')}</div>",
        unsafe_allow_html=True
    )

    if enable_voice and api_key:
        st.markdown("### 🔊 Voice Output | आवाज़ में सुनें")
        v1, v2 = st.columns([1, 3])
        with v1:
            play_btn = st.button("▶️ Play Audio", use_container_width=True)
        with v2:
            if play_btn:
                with st.spinner("🎵 Generating voice..."):
                    try:
                        audio = text_to_speech(latest["response"], latest["lang_code"])
                        st.markdown(
                            f"<div class='audio-section'>{audio_html(audio)}</div>",
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.error(f"Voice error: {e}")

    # Previous chats
    if len(st.session_state.chat_history) > 1:
        with st.expander(f"📜 Previous ({len(st.session_state.chat_history)-1})", False):
            for chat in reversed(st.session_state.chat_history[:-1]):
                st.markdown(f"**{chat['disease']}** — {chat['confidence']:.1f}% ({chat['lang_name']})")
                st.markdown(
                    f"<div class='chat-box' style='font-size:.85rem'>"
                    f"{chat['response'][:400]}...</div>", unsafe_allow_html=True)
                st.markdown("---")

    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


# ─────────────────────────────────────────────────────────────
# DISEASE REFERENCE TABLE
# ─────────────────────────────────────────────────────────────
with st.expander("📚 All 39 Disease Classes", expanded=False):
    t1, t2, t3 = st.tabs(["🌾 Rice/धान", "🎋 Sugarcane/ऊस", "🍅 Others"])
    with t1:
        for n in class_names:
            if "Rice" in n or "rice" in n.lower(): st.markdown(f"• {n.replace('_',' ')}")
    with t2:
        for n in class_names:
            if "Sugarcane" in n: st.markdown(f"• {n.replace('_',' ')}")
    with t3:
        for n in class_names:
            if "Rice" not in n and "Sugarcane" not in n: st.markdown(f"• {n.replace('_',' ')}")


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='footer'>
🌾 <b>KrishiRakshak AI</b> | कृषि रक्षक | Maharashtra Government Hackathon |
Early Crop Disease Detection<br>
<small>Powered by EfficientNet-B0 (PyTorch) + Google Gemini AI + gTTS | 39 Disease Classes</small>
</div>
""", unsafe_allow_html=True)
