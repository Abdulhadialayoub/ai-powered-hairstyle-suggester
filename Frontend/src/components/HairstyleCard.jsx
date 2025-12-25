import { useState, useEffect } from 'react';
import './HairstyleCard.css';

function HairstyleCard({ hairstyle, onImageClick, onTryOn, onAddFavorite, faceShape, userPhoto }) {
  const { id, name, description, reason, image_url, tags } = hairstyle;
  const [aiComment, setAiComment] = useState(null);
  const [loadingComment, setLoadingComment] = useState(false);
  const [tryingOn, setTryingOn] = useState(false);

  const handleImageClick = () => {
    onImageClick(image_url, name);
  };

  const handleTryOn = async () => {
    if (!userPhoto || !onTryOn) return;
    
    setTryingOn(true);
    try {
      await onTryOn(id, name);
    } finally {
      setTryingOn(false);
    }
  };

  const fetchAIComment = async () => {
    if (!faceShape) return;
    
    setLoadingComment(true);
    try {
      const response = await fetch('/api/ai/comment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          hairstyle_name: name,
          face_shape: faceShape,
          hairstyle_description: description,
          tags: tags || []
        }),
      });

      const data = await response.json();
      if (data.success && data.comment) {
        setAiComment(data.comment);
      }
    } catch (err) {
      console.error('Failed to fetch AI comment:', err);
    } finally {
      setLoadingComment(false);
    }
  };

  useEffect(() => {
    // Fetch AI comment when component mounts
    fetchAIComment();
  }, []);

  return (
    <div className="hairstyle-card">
      <div className="hairstyle-image-container" onClick={handleImageClick}>
        <img 
          src={image_url} 
          alt={name}
          className="hairstyle-image"
          loading="lazy"
        />
        <div className="image-overlay">
          <span className="zoom-icon">🔍</span>
        </div>
      </div>
      
      <div className="hairstyle-info">
        <h4 className="hairstyle-name">{name}</h4>
        <p className="hairstyle-description">{description}</p>
        
        {reason && (
          <p className="hairstyle-reason">
            <strong>Why it works:</strong> {reason}
          </p>
        )}

        {loadingComment && (
          <p className="ai-comment loading">
            <span className="ai-icon">✨</span> Loading AI insight...
          </p>
        )}

        {aiComment && !loadingComment && (
          <p className="ai-comment">
            <span className="ai-icon">✨</span> <strong>AI Says:</strong> {aiComment}
          </p>
        )}

        <div className="card-actions">
          {userPhoto && onTryOn && (
            <button 
              className="try-on-button" 
              onClick={handleTryOn}
              disabled={tryingOn}
              title="AI ile saç kesimini deneyin"
            >
              {tryingOn ? '⏳ Oluşturuluyor...' : '🎨 Dene'}
            </button>
          )}
          
          {onAddFavorite && (
            <button 
              className="favorite-button-card" 
              onClick={() => {
                console.log('Adding to favorites:', { id, name });
                onAddFavorite(id, name);
              }}
              title="Favorilere ekle"
            >
              ⭐ Favoriye Ekle
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default HairstyleCard;
