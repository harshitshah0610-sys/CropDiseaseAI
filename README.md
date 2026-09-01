# 🌾 KrishiRakshak AI — कृषि रक्षक
### Early Crop Disease Detection System | Maharashtra Government Hackathon

---

## 🚀 Quick Start

### Step 1: Train the Model (Google Colab)
1. Go to [Google Colab](https://colab.research.google.com)
2. Upload your `Training_Images` folder to Google Drive
3. Upload `train_model_colab.py` to Colab
4. Set **Runtime → T4 GPU**
5. Run all cells — training takes ~30-60 minutes
6. Download `crop_disease_model.h5` and `class_names.json` from Google Drive
7. Place both files in this `CropDiseaseAI` folder

### Step 2: Get Free Gemini API Key
1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key (starts with `AIzaSy...`)

### Step 3: Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Step 4: Deploy Online (Streamlit Cloud — FREE)
1. Create a [GitHub](https://github.com) account
2. Create a new repository (e.g., `KrishiRakshakAI`)
3. Upload all files:
   - `app.py`
   - `requirements.txt`
   - `class_names.json`
   - `crop_disease_model.h5`  ← (download from Colab after training)
   - `.streamlit/config.toml`
4. Go to [share.streamlit.io](https://share.streamlit.io)
5. Sign in with GitHub
6. Click **New app** → Select your repository → `app.py`
7. Click **Deploy** — done! Your app is online in ~5 minutes! 🎉

---

## 📁 Project Structure

```
CropDiseaseAI/
│
├── app.py                     # 🌐 Main web application
├── train_model_colab.py       # 🧠 Google Colab training script
├── requirements.txt           # 📦 Python dependencies
├── class_names.json           # 🏷️  39 disease class labels
├── crop_disease_model.h5      # 🤖 Trained model (add after training)
├── .streamlit/
│   └── config.toml            # 🎨 App theme settings
└── README.md                  # 📖 This file
```

---

## 🧠 How It Works

```
Farmer uploads photo
        ↓
EfficientNetB0 AI Model
(trained on 39 disease classes)
        ↓
Disease Name + Confidence %
        ↓
Gemini AI generates advice
(in Hindi / Marathi / English)
        ↓
gTTS converts to voice audio
        ↓
Farmer sees + hears the result!
```

---

## 🌿 Supported Diseases (39 Classes)

### 🌾 Rice Diseases (20 classes)
| Disease | Scientific Cause |
|---------|-----------------|
| Rice Blast | Magnaporthe oryzae (fungus) |
| Brown Spot | Helminthosporium oryzae |
| Bacterial Leaf Blight | Xanthomonas oryzae |
| Sheath Blight | Rhizoctonia solani |
| Sheath Rot | Sarocladium oryzae |
| False Smut | Ustilaginoidea virens |
| Stem Rot | Sclerotium oryzae |
| Tungro | Rice tungro virus |
| Bakanae / Foot Rot | Fusarium moniliforme |
| Khaira | Zinc deficiency |
| + 10 more... | |

### 🎋 Sugarcane Diseases (9 classes)
| Disease | Cause |
|---------|-------|
| Red Rot | Colletotrichum falcatum |
| Mosaic | Sugarcane mosaic virus |
| Wilt | Fusarium sacchari |
| Whip Smut | Sporisorium scitamineum |
| Pokkah Boeng | Fusarium moniliforme |
| Yellow Leaf | Polerovirus |
| + 3 more... | |

### 🍅 Tomato, 🥔 Potato, 🌿 Cotton, 🌾 Wheat
- Tomato Early/Late Blight, Leaf Curl
- Potato Early Blight
- Cotton Grey Mildew, Downy Mildew, Leaf Curl, Boll Rot
- Wheat Yellow Rust

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Disease Detection | TensorFlow + EfficientNetB0 | Image classification |
| AI Chat | Google Gemini 1.5 Flash | Farmer advice generation |
| Voice Output | gTTS | Text-to-speech in Hindi/Marathi |
| Web Interface | Streamlit | User interface |
| Deployment | Streamlit Cloud | Online hosting (free) |

---

## 📊 Model Details

- **Architecture**: EfficientNetB0 (Transfer Learning)
- **Input Size**: 224 × 224 pixels
- **Classes**: 39 crop disease categories
- **Training**: 2-Phase (frozen base → fine-tuning)
- **Augmentation**: Rotation, flip, zoom, brightness variation
- **Expected Accuracy**: 85–92%

---

## 🏆 Hackathon Info

- **Problem Statement**: Early Crop Disease Detection
- **By**: Government of Maharashtra
- **Dataset**: 39 crop diseases, ~100 images each
- **Solution**: AI model + Chat + Voice for farmers

---

## 📞 Common Issues

**Q: Model file is too large for GitHub (>100MB)?**  
A: Use Git LFS or host model on Hugging Face Hub and load from URL.

**Q: gTTS not working / slow?**  
A: Requires internet connection. Works well on Streamlit Cloud.

**Q: Gemini API quota exceeded?**  
A: Free tier allows 15 requests/minute. Wait a moment and retry.

**Q: Low accuracy on custom images?**  
A: Ensure clear, close-up photos of affected plant parts in good lighting.

---

*Made with ❤️ for the farmers of Maharashtra | शेतकऱ्यांसाठी बनवलेले*
