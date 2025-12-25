# Yüz Şekli Sınıflandırma - ML Model Eğitimi

Bu klasör, CNN tabanlı yüz şekli sınıflandırma modelinin eğitimi için gerekli dosyaları içerir.

## Veri Seti

Kaggle'dan "Face Shape Dataset" kullanılmaktadır:
- **URL:** https://www.kaggle.com/datasets/niten19/face-shape-dataset
- **Sınıflar:** Heart, Oblong, Oval, Round, Square
- **Toplam Görüntü:** ~5000

## Kurulum

### 1. Veri Setini İndir

1. Kaggle hesabı oluşturun (yoksa)
2. https://www.kaggle.com/datasets/niten19/face-shape-dataset adresine gidin
3. "Download" butonuna tıklayın
4. ZIP dosyasını `backend/ml/data/` klasörüne çıkartın

Klasör yapısı şöyle olmalı:
```
backend/ml/data/
└── Face Shape Dataset/
    ├── training_set/
    │   ├── Heart/
    │   ├── Oblong/
    │   ├── Oval/
    │   ├── Round/
    │   └── Square/
    └── testing_set/
        ├── Heart/
        ├── Oblong/
        ├── Oval/
        ├── Round/
        └── Square/
```

### 2. Gerekli Kütüphaneleri Yükle

```bash
pip install tensorflow scikit-learn matplotlib
```

### 3. Modeli Eğit

```bash
cd backend/ml
python train_face_shape_model.py
```

## Eğitim Sonuçları

Eğitim tamamlandığında şu dosyalar oluşturulur:

- `models/face_shape_model.keras` - Keras model dosyası
- `models/face_shape_model.tflite` - TensorFlow Lite versiyonu (mobil için)
- `models/model_metadata.json` - Model metadata ve metrikler
- `models/training_history.png` - Eğitim grafikleri

## Model Mimarisi

```
Input (128x128x3)
    ↓
Conv2D(32) → BatchNorm → Conv2D(32) → MaxPool → Dropout(0.25)
    ↓
Conv2D(64) → BatchNorm → Conv2D(64) → MaxPool → Dropout(0.25)
    ↓
Conv2D(128) → BatchNorm → Conv2D(128) → MaxPool → Dropout(0.25)
    ↓
Conv2D(256) → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Flatten → Dense(512) → BatchNorm → Dropout(0.5)
    ↓
Dense(256) → Dropout(0.5)
    ↓
Dense(5, softmax) → Output
```

## Hiperparametreler

| Parametre | Değer |
|-----------|-------|
| Görüntü Boyutu | 128x128 |
| Batch Size | 32 |
| Epochs | 50 (Early Stopping) |
| Optimizer | Adam (lr=0.001) |
| Loss | Categorical Crossentropy |

## Data Augmentation

- Rotation: ±20°
- Width/Height Shift: 20%
- Shear: 20%
- Zoom: 20%
- Horizontal Flip: True

## Beklenen Performans

Kaggle veri seti ile eğitildiğinde:
- **Eğitim Doğruluğu:** ~90-95%
- **Test Doğruluğu:** ~75-85%
