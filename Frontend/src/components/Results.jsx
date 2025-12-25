import { useState, useEffect } from 'react';
import HairstyleCard from './HairstyleCard';
import ImageModal from './ImageModal';
import AIPreviewDialog from './AIPreviewDialog';
import './Results.css';

function Results({ analysisResult, onReset }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(true);
  const [recommendationsError, setRecommendationsError] = useState(null);
  const [tryOnResult, setTryOnResult] = useState(null);
  const [tryOnLoading, setTryOnLoading] = useState(false);
  const [showTryOnModal, setShowTryOnModal] = useState(false);
  const [showAIPreviewDialog, setShowAIPreviewDialog] = useState(false);

  const { face_shape, confidence, userPhoto, method, all_results } = analysisResult;

  // Fetch recommendations when component mounts or face_shape changes
  useEffect(() => {
    const fetchRecommendations = async () => {
      setIsLoadingRecommendations(true);
      setRecommendationsError(null);

      try {
        const response = await fetch(`/api/recommendations?face_shape=${face_shape}&limit=5`);
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch recommendations');
        }

        if (data.success && data.recommendations) {
          setRecommendations(data.recommendations);
          // Show AI Preview Dialog after recommendations are loaded
          setShowAIPreviewDialog(true);
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        setRecommendationsError(err.message || 'Failed to load recommendations');
        setRecommendations([]);
      } finally {
        setIsLoadingRecommendations(false);
      }
    };

    if (face_shape) {
      fetchRecommendations();
    }
  }, [face_shape]);

  const handleImageClick = (imageUrl, hairstyleName) => {
    setSelectedImage({ url: imageUrl, name: hairstyleName });
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const handleReset = () => {
    // Clear state and call parent reset
    setRecommendations([]);
    setSelectedImage(null);
    setRecommendationsError(null);
    setTryOnResult(null);
    onReset();
  };

  const handleAddFavorite = async (hairstyleId, hairstyleName, imageUrl = null) => {
    try {
      const response = await fetch('/api/favorites', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          hairstyle_id: hairstyleId,
          hairstyle_name: hairstyleName,
          face_shape: face_shape,
          image_url: imageUrl
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        alert('✅ Added to favorites!');
      } else if (response.status === 409) {
        alert('ℹ️ Already in favorites!');
      } else {
        alert('❌ Failed to add to favorites');
      }
    } catch (err) {
      alert('❌ Error adding to favorites');
    }
  };

  const handleShare = async (imageUrl) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'My New Hairstyle',
          text: 'Check out my new hairstyle!',
          url: window.location.href
        });
      } catch (err) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback: copy link
      navigator.clipboard.writeText(window.location.href);
      alert('📋 Link copied to clipboard!');
    }
  };

  const handleTryOn = async (hairstyleId, hairstyleName) => {
    if (!userPhoto) {
      alert('User photo not available');
      return;
    }

    setTryOnLoading(true);
    try {
      // Convert data URL to blob
      const response = await fetch(userPhoto);
      const blob = await response.blob();
      
      const formData = new FormData();
      formData.append('image', blob, 'user-photo.jpg');
      formData.append('hairstyle_id', hairstyleId);
      formData.append('quality', 'high');

      const tryOnResponse = await fetch('/api/try-on', {
        method: 'POST',
        body: formData,
      });

      const data = await tryOnResponse.json();

      if (!tryOnResponse.ok) {
        throw new Error(data.error || 'Try-on failed');
      }

      if (data.success && data.result_url) {
        // Convert relative URL to absolute URL
        const fullUrl = data.result_url.startsWith('http') 
          ? data.result_url 
          : `${window.location.origin}${data.result_url}`;
        
        setTryOnResult({
          url: fullUrl,
          name: hairstyleName,
          hairstyleId: hairstyleId,
          aiEvaluation: data.ai_evaluation || null
        });
        // Show custom try-on modal
        setShowTryOnModal(true);
      }
    } catch (err) {
      alert(err.message || 'Failed to generate try-on. Make sure REPLICATE_API_TOKEN is configured.');
    } finally {
      setTryOnLoading(false);
    }
  };

  const handleAIPreviewGenerate = async (hairstyleName) => {
    if (!userPhoto) {
      alert('User photo not available');
      return;
    }

    setTryOnLoading(true);
    try {
      // Convert data URL to blob
      const response = await fetch(userPhoto);
      const blob = await response.blob();
      
      const formData = new FormData();
      formData.append('image', blob, 'user-photo.jpg');
      formData.append('hairstyle_name', hairstyleName);
      formData.append('quality', 'high');

      const tryOnResponse = await fetch('/api/try-on', {
        method: 'POST',
        body: formData,
      });

      const data = await tryOnResponse.json();

      if (!tryOnResponse.ok) {
        throw new Error(data.error || 'Try-on failed');
      }

      if (data.success && data.result_url) {
        const fullUrl = data.result_url.startsWith('http') 
          ? data.result_url 
          : `${window.location.origin}${data.result_url}`;
        
        // Generate a custom ID for user-requested hairstyles
        const customId = `custom_${hairstyleName.toLowerCase().replace(/\s+/g, '_')}`;
        
        setTryOnResult({
          url: fullUrl,
          name: hairstyleName,
          hairstyleId: customId,
          aiEvaluation: data.ai_evaluation || null
        });
        setShowTryOnModal(true);
      }
    } catch (err) {
      alert(err.message || 'Failed to generate AI preview. Make sure REPLICATE_API_TOKEN is configured.');
    } finally {
      setTryOnLoading(false);
    }
  };

  return (
    <div className="results">
      <div className="face-shape-display">
        <h2>Your Face Shape</h2>
        {userPhoto && (
          <div className="user-photo-container">
            <img src={userPhoto} alt="Your photo" className="user-photo" />
          </div>
        )}
        <div className="face-shape-info">
          <span className="face-shape-name">{face_shape}</span>
          <span className="confidence-badge">
            {(confidence * 100).toFixed(0)}% confidence
          </span>
          {method && (
            <span className={`method-badge ${method}`}>
              {method === 'cnn' ? '🧠 CNN Model' : '📐 Geometric'}
            </span>
          )}
        </div>
        
        {/* Show all analysis results if available */}
        {all_results && all_results.length > 1 && (
          <div className="analysis-comparison">
            <h4>Analysis Methods Comparison</h4>
            <div className="methods-grid">
              {all_results.map((result, index) => (
                <div 
                  key={index} 
                  className={`method-card ${result.method === method ? 'selected' : ''}`}
                >
                  <span className="method-icon">
                    {result.method === 'cnn' ? '🧠' : '📐'}
                  </span>
                  <span className="method-name">
                    {result.method === 'cnn' ? 'CNN Model' : 'Geometric'}
                  </span>
                  <span className="method-result">{result.face_shape}</span>
                  <span className="method-confidence">
                    {(result.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
            <p className="best-result-note">
              ✓ Best result selected automatically based on confidence
            </p>
          </div>
        )}
      </div>

      <div className="recommendations-section">
        <h3>Recommended Hairstyles for You</h3>
        <p className="recommendations-intro">
          Based on your {face_shape} face shape, here are hairstyles that will complement your features:
        </p>
        
        {isLoadingRecommendations && (
          <div className="loading-recommendations">
            <div className="spinner"></div>
            <p>Loading hairstyle recommendations...</p>
          </div>
        )}

        {recommendationsError && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <p>{recommendationsError}</p>
          </div>
        )}

        {!isLoadingRecommendations && !recommendationsError && recommendations.length === 0 && (
          <div className="no-recommendations">
            <p>No recommendations found for your face shape.</p>
          </div>
        )}

        {!isLoadingRecommendations && !recommendationsError && recommendations.length > 0 && (
          <div className="hairstyle-grid">
            {recommendations.map((hairstyle) => (
              <HairstyleCard
                key={hairstyle.id}
                hairstyle={hairstyle}
                onImageClick={handleImageClick}
                onTryOn={handleTryOn}
                onAddFavorite={handleAddFavorite}
                faceShape={face_shape}
                userPhoto={userPhoto}
              />
            ))}
          </div>
        )}

        {tryOnLoading && (
          <div className="try-on-loading">
            <div className="spinner"></div>
            <p>🎨 AI is creating your new look... This may take 30-60 seconds.</p>
          </div>
        )}
      </div>

      <button className="reset-button" onClick={handleReset}>
        Try Another Photo
      </button>

      {selectedImage && (
        <ImageModal
          imageUrl={selectedImage.url}
          imageName={selectedImage.name}
          onClose={closeModal}
        />
      )}

      <AIPreviewDialog
        isOpen={showAIPreviewDialog}
        onClose={() => setShowAIPreviewDialog(false)}
        onGenerate={handleAIPreviewGenerate}
        recommendations={recommendations}
        faceShape={face_shape}
      />

      {showTryOnModal && tryOnResult && (
        <div className="try-on-modal-overlay" onClick={() => setShowTryOnModal(false)}>
          <div className="try-on-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowTryOnModal(false)}>✕</button>
            
            <h2>🎨 AI Style Preview</h2>
            <p className="modal-subtitle">{tryOnResult.name}</p>
            
            {tryOnResult.aiEvaluation && (
              <div className="ai-evaluation">
                <div className="ai-evaluation-header">
                  <span className="ai-icon">🤖</span>
                  <strong>AI Stylist Review</strong>
                </div>
                <p className="ai-evaluation-text">{tryOnResult.aiEvaluation}</p>
              </div>
            )}
            
            <div className="ai-disclaimer">
              ⚠️ AI Preview: Shows the hairstyle concept. Actual results may vary.
            </div>
            
            <div className="try-on-comparison">
              <div className="comparison-item">
                <h3>Before</h3>
                <img 
                  src={userPhoto} 
                  alt="Your original photo"
                  className="comparison-image"
                />
                <p className="comparison-label">Your Photo</p>
              </div>
              
              <div className="comparison-arrow">→</div>
              
              <div className="comparison-item">
                <h3>After</h3>
                <img 
                  src={tryOnResult.url} 
                  alt={`${tryOnResult.name} try-on result`}
                  className="comparison-image"
                  onError={(e) => {
                    console.error('Failed to load try-on result image:', tryOnResult.url);
                    e.target.style.border = '2px solid red';
                  }}
                  onLoad={() => console.log('Try-on image loaded successfully:', tryOnResult.url)}
                />
                <p className="comparison-label">{tryOnResult.name}</p>
              </div>
            </div>

            <div className="try-on-actions">
              <a 
                href={tryOnResult.url} 
                download={`hairstyle-${tryOnResult.name}.jpg`}
                className="action-button download-button"
              >
                📥 Download
              </a>
              
              <button 
                className="action-button favorite-button"
                onClick={() => {
                  console.log('Favorite button clicked:', tryOnResult);
                  handleAddFavorite(tryOnResult.hairstyleId, tryOnResult.name, tryOnResult.url);
                }}
              >
                ⭐ Add to Favorites
              </button>
              
              <button 
                className="action-button share-button"
                onClick={() => handleShare(tryOnResult.url)}
              >
                📤 Share
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Results;
