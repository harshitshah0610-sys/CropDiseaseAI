"""
KrishiRakshak AI — Local Training Script (PyTorch + EfficientNet)
Trains crop disease model on your local machine using CPU.
Run: python train_local.py
"""

import os, json, time, copy, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
from torch.optim.lr_scheduler import ReduceLROnPlateau
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.utils.class_weight import compute_class_weight
from PIL import Image

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
DATASET_PATH     = r"C:\Users\Hp\Desktop\Training_Images"
MODEL_SAVE_PATH  = r"C:\Users\Hp\Desktop\CropDiseaseAI\crop_disease_model.pth"
CLASS_NAMES_PATH = r"C:\Users\Hp\Desktop\CropDiseaseAI\class_names.json"
GRAPH_PATH       = r"C:\Users\Hp\Desktop\CropDiseaseAI\training_graph.png"

IMG_SIZE         = 224
BATCH_SIZE       = 16        # Batch size 16 for CPU efficiency
NUM_EPOCHS       = 12        # 12 epochs total for fast local completion
LEARNING_RATE    = 0.001
VAL_SPLIT        = 0.2
NUM_WORKERS      = 0
DEVICE           = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("=" * 60)
print("🌾  KrishiRakshak AI — Training Started")
print("=" * 60)
print(f"  Device  : {DEVICE}")
print(f"  Dataset : {DATASET_PATH}")
print(f"  Epochs  : {NUM_EPOCHS}")
print(f"  Batch   : {BATCH_SIZE}")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# CUSTOM DATASET THAT SKIPS EMPTY FOLDERS AND CORRUPT IMAGES
# ─────────────────────────────────────────────────────────────
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff')

class CropDiseaseDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []
        
        # Find non-empty class directories
        dir_names = sorted([d for d in os.listdir(root_dir)
                            if os.path.isdir(os.path.join(root_dir, d))])
        
        self.classes = []
        corrupt_count = 0
        
        for d in dir_names:
            folder_path = os.path.join(root_dir, d)
            valid_imgs_in_dir = 0
            
            for img_name in os.listdir(folder_path):
                if img_name.lower().endswith(VALID_EXTENSIONS):
                    img_path = os.path.join(folder_path, img_name)
                    # Verify file can be opened by PIL
                    try:
                        with Image.open(img_path) as img_test:
                            img_test.verify()
                        valid_imgs_in_dir += 1
                    except Exception:
                        corrupt_count += 1
            
            if valid_imgs_in_dir > 0:
                self.classes.append(d)
        
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        
        for cls_name in self.classes:
            folder_path = os.path.join(root_dir, cls_name)
            cls_idx = self.class_to_idx[cls_name]
            for img_name in os.listdir(folder_path):
                if img_name.lower().endswith(VALID_EXTENSIONS):
                    img_path = os.path.join(folder_path, img_name)
                    try:
                        with Image.open(img_path) as img_test:
                            img_test.verify()
                        self.samples.append((img_path, cls_idx))
                    except Exception:
                        pass
                    
        self.targets = [sample[1] for sample in self.samples]
        if corrupt_count > 0:
            print(f"  ⚠️ Skipped {corrupt_count} corrupt/invalid images.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, target = self.samples[idx]
        try:
            img = Image.open(path).convert('RGB')
        except Exception:
            # Fallback for transient errors
            img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), color='black')
        if self.transform is not None:
            img = self.transform(img)
        return img, target

# ─────────────────────────────────────────────────────────────
# DATA TRANSFORMS
# ─────────────────────────────────────────────────────────────
train_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

val_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# ─────────────────────────────────────────────────────────────
# LOAD DATASET
# ─────────────────────────────────────────────────────────────
print("\n📂 Loading dataset...")
full_dataset = CropDiseaseDataset(DATASET_PATH, transform=train_transforms)
class_names = full_dataset.classes
NUM_CLASSES = len(class_names)

# Save class names
with open(CLASS_NAMES_PATH, 'w', encoding='utf-8') as f:
    json.dump(class_names, f, ensure_ascii=False, indent=2)

print(f"  ✅ Valid images  : {len(full_dataset)}")
print(f"  ✅ Classes       : {NUM_CLASSES}")
print(f"  ✅ class_names.json saved ({NUM_CLASSES} non-empty disease classes)")

# Split into train / val
val_size   = int(len(full_dataset) * VAL_SPLIT)
train_size = len(full_dataset) - val_size
train_dataset, val_dataset = random_split(
    full_dataset, [train_size, val_size],
    generator=torch.Generator().manual_seed(42)
)

# Set val transforms
class SubsetWithTransform(Dataset):
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform
        self.targets = [subset.dataset.targets[i] for i in subset.indices]

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):
        path, target = self.subset.dataset.samples[self.subset.indices[idx]]
        try:
            img = Image.open(path).convert('RGB')
        except Exception:
            img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), color='black')
        if self.transform is not None:
            img = self.transform(img)
        return img, target

val_dataset_eval = SubsetWithTransform(val_dataset, val_transforms)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                          shuffle=True, num_workers=NUM_WORKERS, pin_memory=False)
val_loader   = DataLoader(val_dataset_eval, batch_size=BATCH_SIZE,
                          shuffle=False, num_workers=NUM_WORKERS, pin_memory=False)

print(f"  ✅ Train samples : {train_size}")
print(f"  ✅ Val samples   : {val_size}")

# ─────────────────────────────────────────────────────────────
# COMPUTE CLASS WEIGHTS
# ─────────────────────────────────────────────────────────────
all_train_labels = [train_dataset.dataset.targets[i] for i in train_dataset.indices]
class_weights = compute_class_weight('balanced',
                                     classes=np.arange(NUM_CLASSES),
                                     y=all_train_labels)
class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32).to(DEVICE)

# ─────────────────────────────────────────────────────────────
# BUILD MODEL — EfficientNet-B0
# ─────────────────────────────────────────────────────────────
print("\n🧠 Building EfficientNet-B0 model...")
model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)

# Freeze base layers for Phase 1
for param in model.parameters():
    param.requires_grad = False

# Replace classifier head
in_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(p=0.3, inplace=True),
    nn.Linear(in_features, 512),
    nn.ReLU(),
    nn.Dropout(p=0.2),
    nn.Linear(512, NUM_CLASSES)
)
model = model.to(DEVICE)

total_params     = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"  ✅ Total params    : {total_params:,}")
print(f"  ✅ Trainable params: {trainable_params:,}")

criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

# ─────────────────────────────────────────────────────────────
# TRAINING LOOPS
# ─────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    num_batches = len(loader)
    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
        
        if (batch_idx + 1) % 20 == 0 or (batch_idx + 1) == num_batches:
            print(f"    Batch {batch_idx+1}/{num_batches} | "
                  f"Loss: {running_loss/total:.4f} | "
                  f"Acc: {100.*correct/total:.1f}%", end='\r')
    print()
    return running_loss / total, correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
    return running_loss / total, correct / total


# ─────────────────────────────────────────────────────────────
# PHASE 1: Classification Head Only (6 epochs)
# ─────────────────────────────────────────────────────────────
PHASE1_EPOCHS = 6
print("\n" + "=" * 60)
print(f"🚀 PHASE 1: Training classification head ({PHASE1_EPOCHS} epochs)")
print("=" * 60)

optimizer1 = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()),
                        lr=LEARNING_RATE)
scheduler1 = ReduceLROnPlateau(optimizer1, mode='min', factor=0.5, patience=2)

history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
best_acc = 0.0

for epoch in range(PHASE1_EPOCHS):
    t0 = time.time()
    tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer1, criterion, DEVICE)
    vl_loss, vl_acc = evaluate(model, val_loader, criterion, DEVICE)
    scheduler1.step(vl_loss)

    history["train_loss"].append(tr_loss)
    history["val_loss"].append(vl_loss)
    history["train_acc"].append(tr_acc)
    history["val_acc"].append(vl_acc)

    elapsed = time.time() - t0
    print(f"  Epoch {epoch+1:02d}/{PHASE1_EPOCHS} | "
          f"Train Loss: {tr_loss:.4f} Acc: {tr_acc*100:.2f}% | "
          f"Val Loss: {vl_loss:.4f} Acc: {vl_acc*100:.2f}% | "
          f"Time: {elapsed:.0f}s")

    if vl_acc > best_acc:
        best_acc = vl_acc
        torch.save({"model_state": model.state_dict(),
                    "class_names": class_names,
                    "num_classes": NUM_CLASSES,
                    "img_size": IMG_SIZE}, MODEL_SAVE_PATH)
        print(f"  ✅ Saved best model! Val acc: {best_acc*100:.2f}%")

print(f"\n✅ Phase 1 complete! Best val accuracy: {best_acc*100:.2f}%")

# ─────────────────────────────────────────────────────────────
# PHASE 2: Fine-Tuning Top Layers (6 epochs)
# ─────────────────────────────────────────────────────────────
PHASE2_EPOCHS = 6
print("\n" + "=" * 60)
print(f"🔧 PHASE 2: Fine-tuning top layers ({PHASE2_EPOCHS} epochs)")
print("=" * 60)

# Unfreeze top feature blocks
for i, layer in enumerate(model.features):
    if i >= 6:
        for param in layer.parameters():
            param.requires_grad = True

trainable_now = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"  Trainable params now: {trainable_now:,}")

optimizer2 = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()),
                        lr=LEARNING_RATE / 5)
scheduler2 = ReduceLROnPlateau(optimizer2, mode='min', factor=0.5, patience=2)

for epoch in range(PHASE2_EPOCHS):
    t0 = time.time()
    tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer2, criterion, DEVICE)
    vl_loss, vl_acc = evaluate(model, val_loader, criterion, DEVICE)
    scheduler2.step(vl_loss)

    history["train_loss"].append(tr_loss)
    history["val_loss"].append(vl_loss)
    history["train_acc"].append(tr_acc)
    history["val_acc"].append(vl_acc)

    elapsed = time.time() - t0
    print(f"  Epoch {epoch+1:02d}/{PHASE2_EPOCHS} | "
          f"Train Loss: {tr_loss:.4f} Acc: {tr_acc*100:.2f}% | "
          f"Val Loss: {vl_loss:.4f} Acc: {vl_acc*100:.2f}% | "
          f"Time: {elapsed:.0f}s")

    if vl_acc > best_acc:
        best_acc = vl_acc
        torch.save({"model_state": model.state_dict(),
                    "class_names": class_names,
                    "num_classes": NUM_CLASSES,
                    "img_size": IMG_SIZE}, MODEL_SAVE_PATH)
        print(f"  ✅ Saved best model! Val acc: {best_acc*100:.2f}%")

# ─────────────────────────────────────────────────────────────
# PLOT RESULTS
# ─────────────────────────────────────────────────────────────
epochs_range = range(1, len(history["train_acc"]) + 1)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("🌾 KrishiRakshak AI — Training Results", fontsize=14, fontweight='bold')

ax1.plot(epochs_range, [a * 100 for a in history["train_acc"]], label='Train Acc', color='#2E7D32')
ax1.plot(epochs_range, [a * 100 for a in history["val_acc"]],   label='Val Acc',   color='#FF6F00')
ax1.axvline(x=PHASE1_EPOCHS, color='red', linestyle='--', alpha=0.7, label='Fine-tune start')
ax1.set_title('Accuracy (%)'); ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy %'); ax1.legend(); ax1.grid(alpha=0.3)

ax2.plot(epochs_range, history["train_loss"], label='Train Loss', color='#2E7D32')
ax2.plot(epochs_range, history["val_loss"],   label='Val Loss',   color='#FF6F00')
ax2.axvline(x=PHASE1_EPOCHS, color='red', linestyle='--', alpha=0.7, label='Fine-tune start')
ax2.set_title('Loss'); ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss'); ax2.legend(); ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(GRAPH_PATH, dpi=150, bbox_inches='tight')
print(f"\n✅ Training graph saved: {GRAPH_PATH}")

# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("🎉  TRAINING COMPLETE!")
print("=" * 60)
print(f"  ✅ Best Validation Accuracy : {best_acc * 100:.2f}%")
print(f"  ✅ Model saved              : {MODEL_SAVE_PATH}")
print(f"  ✅ Class names saved        : {CLASS_NAMES_PATH}")
print(f"  ✅ Training graph           : {GRAPH_PATH}")
print("=" * 60)
