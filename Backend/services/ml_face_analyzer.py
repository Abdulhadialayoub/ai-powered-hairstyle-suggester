"""
ML Tabanlı Yüz Şekli Analizi

Eğitilmiş CNN modeli kullanarak yüz şekli sınıflandırması yapar.
"""

import os
import numpy as np
import json
from io import BytesIO
from PIL import Image

# TensorFlow import
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️ TensorFlow yüklü değil. ML modeli kullanılamayacak.")

# Model yolu
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'face_shape_model.keras')
METADATA_PATH = os.path.join(MODEL_DIR, 'model_metadata.json')


class MLFaceAnalyzer:
    """
    Eğitilmiş CNN modeli ile yüz şekli analizi.
    """
    
    def __init__(self):
        self.model = None
        self.class_indices = None
        self.img_size = (128, 128)
        self.enabled = False
        
        self._load_model()
    
    def _load_model(self):
        """Modeli yükle"""
        if not TF_AVAILABLE:
            print("❌ TensorFlow yüklü değil")
            return
        
        if not os.path.exists(MODEL_PATH):
            print(f"❌ Model bulunamadı: {MODEL_PATH}")
            print("   Önce train_face_shape_model.py çalıştırın")
            return
        
        try:
            # Model yükle
            self.model = tf.keras.models.load_model(MODEL_PATH)
            print(f"✅ ML modeli yüklendi: {MODEL_PATH}")
            
            # Metadata yükle
            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, 'r') as f:
                    metadata = json.load(f)
                    self.class_indices = metadata.get('class_indices', {})
                    self.img_size = tuple(metadata.get('img_size', (128, 128)))
                    print(f"   Sınıflar: {list(self.class_indices.keys())}")
            else:
                # Default sınıflar
                self.class_indices = {
                    'Heart': 0, 'Oblong': 1, 'Oval': 2, 'Round': 3, 'Square': 4
                }
            
            self.enabled = True
            
        except Exception as e:
            print(f"❌ Model yükleme hatası: {e}")
    
    def analyze(self, image_data):
        """
        Görüntüyü analiz et ve yüz şeklini tahmin et.
        
        Args:
            image_data: Binary image data (bytes)
        
        Returns:
            dict: {
                'face_shape': str,
                'confidence': float,
                'all_predictions': dict
            }
        """
        if not self.enabled:
            raise RuntimeError("ML modeli yüklenmedi")
        
        # Görüntüyü yükle ve ön işle
        image = Image.open(BytesIO(image_data))
        image = image.convert('RGB')
        image = image.resize(self.img_size)
        
        # Numpy array'e çevir ve normalize et
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Tahmin yap
        predictions = self.model.predict(img_array, verbose=0)[0]
        
        # En yüksek olasılıklı sınıfı bul
        predicted_idx = np.argmax(predictions)
        confidence = float(predictions[predicted_idx])
        
        # Sınıf adını bul
        idx_to_class = {v: k for k, v in self.class_indices.items()}
        face_shape = idx_to_class.get(predicted_idx, 'unknown').lower()
        
        # Tüm tahminleri dict olarak döndür
        all_predictions = {
            idx_to_class.get(i, f'class_{i}').lower(): float(predictions[i])
            for i in range(len(predictions))
        }
        
        return {
            'face_shape': face_shape,
            'confidence': round(confidence, 2),
            'all_predictions': all_predictions,
            'method': 'cnn'
        }


# Singleton instance
_ml_analyzer = None


def get_ml_face_analyzer():
    """ML Face Analyzer singleton instance döndür"""
    global _ml_analyzer
    if _ml_analyzer is None:
        _ml_analyzer = MLFaceAnalyzer()
    return _ml_analyzer


def is_ml_model_available():
    """ML modeli kullanılabilir mi?"""
    analyzer = get_ml_face_analyzer()
    return analyzer.enabled
