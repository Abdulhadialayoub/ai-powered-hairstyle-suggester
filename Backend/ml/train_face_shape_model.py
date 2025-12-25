"""
Yüz Şekli Sınıflandırma - CNN Model Eğitimi

Kaggle Face Shape Dataset kullanılarak eğitilmiş bir CNN modeli.
Dataset: https://www.kaggle.com/datasets/niten19/face-shape-dataset

Kullanım:
1. Kaggle'dan veri setini indir
2. backend/ml/data/ klasörüne çıkart
3. Bu scripti çalıştır: python train_face_shape_model.py
"""

import os
import sys
import numpy as np
from PIL import ImageFile

# Bozuk/kesik görüntüleri tolere et
ImageFile.LOAD_TRUNCATED_IMAGES = True

# TensorFlow import
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# TF ve Keras import
import tensorflow as tf
from tensorflow import keras
layers = keras.layers
Sequential = keras.Sequential
ImageDataGenerator = keras.preprocessing.image.ImageDataGenerator
EarlyStopping = keras.callbacks.EarlyStopping
ModelCheckpoint = keras.callbacks.ModelCheckpoint
Adam = keras.optimizers.Adam
print(f"TensorFlow version: {tf.__version__}")

import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışması için
import matplotlib.pyplot as plt
import json
from datetime import datetime

# Ayarlar
IMG_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 50
NUM_CLASSES = 5  # Heart, Oblong, Oval, Round, Square

# Veri seti yolu
DATA_DIR = os.path.join(os.path.dirname(__file__), 'FaceShape Dataset')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

# Klasör oluştur
os.makedirs(MODEL_DIR, exist_ok=True)


def create_cnn_model():
    """CNN modeli oluştur"""
    model = Sequential([
        # Input layer
        layers.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 3)),
        
        # Conv Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Conv Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Conv Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Conv Block 4
        layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Fully Connected
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        
        # Output
        layers.Dense(NUM_CLASSES, activation='softmax')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def load_data():
    """Veri setini yükle"""
    train_dir = os.path.join(DATA_DIR, 'training_set')
    test_dir = os.path.join(DATA_DIR, 'testing_set')
    
    if not os.path.exists(train_dir):
        print(f"❌ Veri seti bulunamadı: {train_dir}")
        print("\n📥 Lütfen Kaggle'dan veri setini indirin:")
        print("   https://www.kaggle.com/datasets/niten19/face-shape-dataset")
        print(f"\n📁 Ve şu klasöre çıkartın: {DATA_DIR}")
        return None, None
    
    # Data augmentation (shear_range kaldırıldı - scipy uyumluluk sorunu)
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2
    )
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    # Training data
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    # Validation data
    val_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    # Test data
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    print(f"\n📊 Veri Seti Bilgileri:")
    print(f"   Eğitim: {train_generator.samples} görüntü")
    print(f"   Doğrulama: {val_generator.samples} görüntü")
    print(f"   Test: {test_generator.samples} görüntü")
    print(f"   Sınıflar: {train_generator.class_indices}")
    
    return (train_generator, val_generator, test_generator), train_generator.class_indices


def train_model(model, data):
    """Modeli eğit"""
    train_gen, val_gen, test_gen = data
    
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            os.path.join(MODEL_DIR, 'face_shape_best.keras'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    print("\n🚀 Eğitim başlıyor...")
    
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )
    
    return history, test_gen


def evaluate_model(model, test_gen, class_indices):
    """Modeli değerlendir"""
    print("\n📈 Model Değerlendirmesi:")
    
    # Test accuracy
    test_loss, test_acc = model.evaluate(test_gen, verbose=0)
    print(f"   Test Loss: {test_loss:.4f}")
    print(f"   Test Accuracy: {test_acc:.4f} ({test_acc*100:.1f}%)")
    
    # Predictions
    predictions = model.predict(test_gen, verbose=0)
    y_pred = np.argmax(predictions, axis=1)
    y_true = test_gen.classes
    
    # Class names
    class_names = {v: k for k, v in class_indices.items()}
    
    # Per-class accuracy
    print("\n📊 Sınıf Bazlı Performans:")
    from sklearn.metrics import classification_report, confusion_matrix
    
    report = classification_report(y_true, y_pred, target_names=list(class_indices.keys()))
    print(report)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print("\n📋 Karışıklık Matrisi:")
    print(cm)
    
    return {
        'test_loss': float(test_loss),
        'test_accuracy': float(test_acc),
        'confusion_matrix': cm.tolist(),
        'class_indices': class_indices
    }


def plot_history(history):
    """Eğitim grafiklerini çiz"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Eğitim')
    axes[0].plot(history.history['val_accuracy'], label='Doğrulama')
    axes[0].set_title('Model Doğruluğu')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Doğruluk')
    axes[0].legend()
    axes[0].grid(True)
    
    # Loss
    axes[1].plot(history.history['loss'], label='Eğitim')
    axes[1].plot(history.history['val_loss'], label='Doğrulama')
    axes[1].set_title('Model Kaybı')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Kayıp')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, 'training_history.png'), dpi=150)
    print(f"\n📊 Grafik kaydedildi: {os.path.join(MODEL_DIR, 'training_history.png')}")
    plt.show()


def save_model(model, class_indices, metrics):
    """Modeli ve metadata'yı kaydet"""
    # Model kaydet
    model_path = os.path.join(MODEL_DIR, 'face_shape_model.keras')
    model.save(model_path)
    print(f"\n💾 Model kaydedildi: {model_path}")
    
    # TFLite versiyonu (mobil için)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    tflite_path = os.path.join(MODEL_DIR, 'face_shape_model.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"💾 TFLite model kaydedildi: {tflite_path}")
    
    # Metadata kaydet
    metadata = {
        'created_at': datetime.now().isoformat(),
        'img_size': IMG_SIZE,
        'num_classes': NUM_CLASSES,
        'class_indices': class_indices,
        'metrics': metrics
    }
    
    metadata_path = os.path.join(MODEL_DIR, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Metadata kaydedildi: {metadata_path}")


def main():
    print("=" * 60)
    print("YÜZ ŞEKLİ SINIFLANDIRMA - CNN MODEL EĞİTİMİ")
    print("=" * 60)
    
    # Veri yükle
    data, class_indices = load_data()
    if data is None:
        return
    
    # Model oluştur
    model = create_cnn_model()
    model.summary()
    
    # Eğit
    history, test_gen = train_model(model, data)
    
    # Değerlendir
    metrics = evaluate_model(model, test_gen, class_indices)
    
    # Grafik çiz
    plot_history(history)
    
    # Kaydet
    save_model(model, class_indices, metrics)
    
    print("\n✅ Eğitim tamamlandı!")


if __name__ == '__main__':
    main()
