# ============================================================
# 🌾 KRISHIRAKSHAK AI — CROP DISEASE MODEL TRAINING
# Run this on Google Colab (Free GPU)
# ============================================================
# HOW TO USE:
# 1. Open Google Colab: https://colab.research.google.com
# 2. Upload your Training_Images folder to Google Drive
# 3. Click Runtime → Change runtime type → GPU → Save
# 4. Upload this file and run each cell step by step
# ============================================================

# ─────────────────────────────────────────────────────────────
# CELL 1: Install required packages
# ─────────────────────────────────────────────────────────────
# Run this cell first!

# pip install tensorflow pillow matplotlib scikit-learn


# ─────────────────────────────────────────────────────────────
# CELL 2: Mount Google Drive and Import Libraries
# ─────────────────────────────────────────────────────────────

from google.colab import drive
drive.mount('/content/drive')

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard
)
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("✅ TensorFlow version:", tf.__version__)
print("✅ GPU available:", tf.config.list_physical_devices('GPU'))


# ─────────────────────────────────────────────────────────────
# CELL 3: Configuration — UPDATE THIS PATH!
# ─────────────────────────────────────────────────────────────

# ⚠️ IMPORTANT: Update this path to where you uploaded Training_Images in Google Drive
DATASET_PATH = "/content/drive/MyDrive/Training_Images"   # ← Change if needed
MODEL_SAVE_PATH = "/content/drive/MyDrive/crop_disease_model.h5"
CLASS_NAMES_PATH = "/content/drive/MyDrive/class_names.json"

# Training settings
IMG_SIZE = (224, 224)
BATCH_SIZE = 16          # Use 16 for small dataset, 32 if you have more RAM
EPOCHS = 40
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2   # 20% images for validation

# Verify dataset path
if not os.path.exists(DATASET_PATH):
    print(f"❌ Dataset not found at: {DATASET_PATH}")
    print("Please update DATASET_PATH to correct Google Drive location!")
else:
    classes = sorted(os.listdir(DATASET_PATH))
    classes = [c for c in classes if os.path.isdir(os.path.join(DATASET_PATH, c))]
    NUM_CLASSES = len(classes)
    print(f"✅ Dataset found! Total classes: {NUM_CLASSES}")
    print(f"📁 Classes: {classes}")
    
    # Count images per class
    total_images = 0
    for cls in classes:
        cls_path = os.path.join(DATASET_PATH, cls)
        img_count = len([f for f in os.listdir(cls_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        total_images += img_count
        print(f"   {cls}: {img_count} images")
    print(f"\n📊 Total images: {total_images}")


# ─────────────────────────────────────────────────────────────
# CELL 4: Save Class Names to JSON
# ─────────────────────────────────────────────────────────────

classes = sorted([c for c in os.listdir(DATASET_PATH) 
                  if os.path.isdir(os.path.join(DATASET_PATH, c))])

with open(CLASS_NAMES_PATH, 'w', encoding='utf-8') as f:
    json.dump(classes, f, ensure_ascii=False, indent=2)

print(f"✅ Saved {len(classes)} class names to: {CLASS_NAMES_PATH}")
print("Classes:", classes)


# ─────────────────────────────────────────────────────────────
# CELL 5: Data Augmentation and Loading
# ─────────────────────────────────────────────────────────────
# Data augmentation helps when we have fewer images (~100 per class)
# It creates variations of existing images so the model learns better

train_datagen = ImageDataGenerator(
    rescale=1.0/255,                # Normalize pixels 0-1
    validation_split=VALIDATION_SPLIT,
    rotation_range=30,              # Randomly rotate images
    width_shift_range=0.2,          # Shift horizontally
    height_shift_range=0.2,         # Shift vertically
    horizontal_flip=True,           # Flip left-right
    vertical_flip=False,
    zoom_range=0.25,                # Random zoom
    brightness_range=[0.7, 1.3],    # Random brightness
    shear_range=0.2,
    fill_mode='nearest'
)

# Validation data — only rescale, no augmentation
val_datagen = ImageDataGenerator(
    rescale=1.0/255,
    validation_split=VALIDATION_SPLIT
)

print("📂 Loading training data...")
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True,
    seed=42
)

print("📂 Loading validation data...")
val_generator = val_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False,
    seed=42
)

NUM_CLASSES = train_generator.num_classes
print(f"\n✅ Training samples: {train_generator.samples}")
print(f"✅ Validation samples: {val_generator.samples}")
print(f"✅ Number of classes: {NUM_CLASSES}")

# Save class indices mapping
class_indices = train_generator.class_indices
class_names_ordered = [None] * NUM_CLASSES
for class_name, index in class_indices.items():
    class_names_ordered[index] = class_name

with open(CLASS_NAMES_PATH, 'w', encoding='utf-8') as f:
    json.dump(class_names_ordered, f, ensure_ascii=False, indent=2)

print(f"✅ Updated class_names.json with correct order")


# ─────────────────────────────────────────────────────────────
# CELL 6: Compute Class Weights (handles imbalanced data)
# ─────────────────────────────────────────────────────────────

labels = train_generator.classes
class_weights_array = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(labels),
    y=labels
)
class_weight_dict = {i: w for i, w in enumerate(class_weights_array)}
print("✅ Class weights computed (handles imbalanced classes)")
print("Sample weights:", {k: round(v, 2) for k, v in list(class_weight_dict.items())[:5]})


# ─────────────────────────────────────────────────────────────
# CELL 7: Build the Model (EfficientNetB0 + Transfer Learning)
# ─────────────────────────────────────────────────────────────
# EfficientNetB0 was trained on 1.2 million ImageNet images
# We use its knowledge and add our crop disease layers on top

def build_model(num_classes, learning_rate=0.001):
    # Load pre-trained EfficientNetB0 (without top classification layer)
    base_model = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_shape=(*IMG_SIZE, 3)
    )
    
    # Phase 1: Freeze base model — only train our new layers first
    base_model.trainable = False
    
    # Build full model
    inputs = keras.Input(shape=(*IMG_SIZE, 3))
    
    # Data augmentation inside model (works on GPU)
    x = layers.RandomFlip("horizontal")(inputs)
    x = layers.RandomRotation(0.1)(x)
    
    # Base model features
    x = base_model(x, training=False)
    
    # Global average pooling
    x = layers.GlobalAveragePooling2D()(x)
    
    # Classification head
    x = layers.BatchNormalization()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = keras.Model(inputs, outputs)
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top3_accuracy')]
    )
    
    return model, base_model

model, base_model = build_model(NUM_CLASSES, LEARNING_RATE)
model.summary()
print(f"\n✅ Model built! Total parameters: {model.count_params():,}")


# ─────────────────────────────────────────────────────────────
# CELL 8: Training Callbacks (Auto-save best model)
# ─────────────────────────────────────────────────────────────

callbacks = [
    # Save best model automatically
    ModelCheckpoint(
        MODEL_SAVE_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    # Stop training if no improvement for 10 epochs
    EarlyStopping(
        monitor='val_accuracy',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    # Reduce learning rate when stuck
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.3,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]

print("✅ Callbacks ready!")


# ─────────────────────────────────────────────────────────────
# CELL 9: Phase 1 Training — Train Classification Head Only
# ─────────────────────────────────────────────────────────────
# First, train only our new layers (base model is frozen)
# This is faster and prevents destroying pre-trained features

print("=" * 60)
print("🚀 PHASE 1: Training classification head...")
print("=" * 60)

history_phase1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=20,
    callbacks=callbacks,
    class_weight=class_weight_dict,
    verbose=1
)

print(f"\n✅ Phase 1 complete!")
print(f"Best validation accuracy: {max(history_phase1.history['val_accuracy']):.4f}")


# ─────────────────────────────────────────────────────────────
# CELL 10: Phase 2 — Fine-Tuning (Unfreeze top layers)
# ─────────────────────────────────────────────────────────────
# Now unfreeze top 30 layers of EfficientNet for fine-tuning

print("\n" + "=" * 60)
print("🔧 PHASE 2: Fine-tuning top layers...")
print("=" * 60)

# Unfreeze top 30 layers
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

# Recompile with lower learning rate for fine-tuning
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 10),
    loss='categorical_crossentropy',
    metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top3_accuracy')]
)

history_phase2 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=20,
    callbacks=callbacks,
    class_weight=class_weight_dict,
    verbose=1
)

print(f"\n✅ Phase 2 complete!")
print(f"Best validation accuracy: {max(history_phase2.history['val_accuracy']):.4f}")


# ─────────────────────────────────────────────────────────────
# CELL 11: Plot Training Results
# ─────────────────────────────────────────────────────────────

def plot_history(h1, h2):
    acc = h1.history['accuracy'] + h2.history['accuracy']
    val_acc = h1.history['val_accuracy'] + h2.history['val_accuracy']
    loss = h1.history['loss'] + h2.history['loss']
    val_loss = h1.history['val_loss'] + h2.history['val_loss']
    
    epochs_range = range(len(acc))
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    axes[0].plot(epochs_range, acc, label='Training Accuracy', color='#2E7D32')
    axes[0].plot(epochs_range, val_acc, label='Validation Accuracy', color='#FF6F00')
    axes[0].axvline(x=20, color='red', linestyle='--', label='Fine-tuning Start')
    axes[0].set_title('Model Accuracy', fontsize=14)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(epochs_range, loss, label='Training Loss', color='#2E7D32')
    axes[1].plot(epochs_range, val_loss, label='Validation Loss', color='#FF6F00')
    axes[1].axvline(x=20, color='red', linestyle='--', label='Fine-tuning Start')
    axes[1].set_title('Model Loss', fontsize=14)
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/content/drive/MyDrive/training_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✅ Training graph saved!")

plot_history(history_phase1, history_phase2)


# ─────────────────────────────────────────────────────────────
# CELL 12: Evaluate Model on Validation Set
# ─────────────────────────────────────────────────────────────

print("\n📊 Evaluating model...")
best_model = tf.keras.models.load_model(MODEL_SAVE_PATH)
val_loss, val_acc, val_top3 = best_model.evaluate(val_generator, verbose=1)

print(f"\n{'='*50}")
print(f"✅ FINAL RESULTS:")
print(f"   Validation Accuracy  : {val_acc*100:.2f}%")
print(f"   Top-3 Accuracy       : {val_top3*100:.2f}%")
print(f"   Validation Loss      : {val_loss:.4f}")
print(f"{'='*50}")

# Detailed classification report
val_generator.reset()
y_pred = best_model.predict(val_generator, verbose=1)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true = val_generator.classes[:len(y_pred_classes)]

print("\n📋 Per-class accuracy:")
report = classification_report(y_true, y_pred_classes, 
                                target_names=class_names_ordered,
                                output_dict=True)
for cls, metrics in report.items():
    if isinstance(metrics, dict) and cls in class_names_ordered:
        print(f"   {cls[:30]:30s} : {metrics['precision']:.2f} precision, {metrics['recall']:.2f} recall")


# ─────────────────────────────────────────────────────────────
# CELL 13: Test with a Single Image
# ─────────────────────────────────────────────────────────────

from tensorflow.keras.preprocessing import image as keras_image

def predict_single_image(img_path, model, class_names, top_k=3):
    """Test the model on a single image"""
    img = keras_image.load_img(img_path, target_size=IMG_SIZE)
    img_array = keras_image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    predictions = model.predict(img_array, verbose=0)[0]
    top_indices = np.argsort(predictions)[::-1][:top_k]
    
    print(f"\n🔍 Predictions for: {os.path.basename(img_path)}")
    for i, idx in enumerate(top_indices):
        confidence = predictions[idx] * 100
        print(f"  {i+1}. {class_names[idx]:40s} — {confidence:.1f}%")
    
    return class_names[top_indices[0]], predictions[top_indices[0]]

# Example: Test on the first image from any class
test_class = class_names_ordered[0]
test_dir = os.path.join(DATASET_PATH, test_class)
test_imgs = [f for f in os.listdir(test_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
if test_imgs:
    test_img_path = os.path.join(test_dir, test_imgs[0])
    disease, confidence = predict_single_image(test_img_path, best_model, class_names_ordered)
    print(f"\n✅ Test passed! Detected: {disease} ({confidence*100:.1f}%)")


# ─────────────────────────────────────────────────────────────
# CELL 14: DONE! Download the model file
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("🎉 TRAINING COMPLETE!")
print("="*60)
print(f"✅ Model saved to Google Drive: {MODEL_SAVE_PATH}")
print(f"✅ Class names saved to: {CLASS_NAMES_PATH}")
print(f"✅ Training graph saved to Google Drive")
print()
print("📥 NEXT STEPS:")
print("  1. Download 'crop_disease_model.h5' from Google Drive")
print("  2. Download 'class_names.json' from Google Drive")
print("  3. Place both files in your CropDiseaseAI folder")
print("  4. Run: streamlit run app.py")
print("="*60)

# Optional: Download model directly from Colab
from google.colab import files
print("\n💾 Downloading model file to your computer...")
# Uncomment below line to download directly:
# files.download(MODEL_SAVE_PATH)
# files.download(CLASS_NAMES_PATH)
