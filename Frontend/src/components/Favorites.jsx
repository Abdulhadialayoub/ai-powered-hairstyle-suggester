import { useState, useEffect } from 'react';
import './Favorites.css';

function Favorites({ onClose }) {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/favorites', {
        credentials: 'include'
      });
      const data = await response.json();
      
      console.log('Favorites response:', data);

      if (data.success) {
        console.log('Favorites data:', data.favorites);
        setFavorites(data.favorites || []);
      } else {
        console.error('Favorites error:', data);
        throw new Error(data.error || 'Failed to fetch favorites');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (hairstyleId) => {
    try {
      const response = await fetch(`/api/favorites/${hairstyleId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      const data = await response.json();

      if (data.success) {
        // Remove from local state
        setFavorites(favorites.filter(fav => fav.hairstyle.id !== hairstyleId));
      } else {
        alert('Failed to remove favorite');
      }
    } catch (err) {
      alert('Error removing favorite');
    }
  };

  return (
    <div className="favorites-overlay" onClick={onClose}>
      <div className="favorites-modal" onClick={(e) => e.stopPropagation()}>
        <div className="favorites-header">
          <h2>⭐ My Favorites</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="favorites-content">
          {loading && (
            <div className="favorites-loading">
              <div className="spinner"></div>
              <p>Loading favorites...</p>
            </div>
          )}

          {error && (
            <div className="favorites-error">
              <p>❌ {error}</p>
            </div>
          )}

          {!loading && !error && favorites.length === 0 && (
            <div className="favorites-empty">
              <p>💔 No favorites yet</p>
              <p className="empty-subtitle">Add hairstyles to your favorites to see them here!</p>
            </div>
          )}

          {!loading && !error && favorites.length > 0 && (
            <div className="favorites-grid">
              {favorites.map((favorite) => (
                <div key={favorite.favorite_id} className="favorite-card">
                  <div className="favorite-image-container">
                    <img 
                      src={favorite.hairstyle.image_url} 
                      alt={favorite.hairstyle.name}
                      className="favorite-image"
                    />
                  </div>
                  <div className="favorite-info">
                    <h3>{favorite.hairstyle.name}</h3>
                    <p>{favorite.hairstyle.description}</p>
                    <div className="favorite-tags">
                      {favorite.hairstyle.tags?.slice(0, 3).map((tag, index) => (
                        <span key={index} className="tag">{tag}</span>
                      ))}
                    </div>
                    <button 
                      className="remove-button"
                      onClick={() => handleRemoveFavorite(favorite.hairstyle.id)}
                    >
                      🗑️ Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Favorites;
