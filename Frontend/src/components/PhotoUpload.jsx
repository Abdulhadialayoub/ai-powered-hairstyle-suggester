import { useState } from 'react';
import './PhotoUpload.css';

function PhotoUpload({ onAnalysisComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    setError(null);
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a JPEG, PNG, or WebP image');
      return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > maxSize) {
      setError('Image must be smaller than 10MB');
      return;
    }

    setSelectedFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    
    const file = event.dataTransfer.files[0];
    if (file) {
      processFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const response = await fetch('/api/analysis/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed');
      }

      // Pass results and user photo to parent component
      if (onAnalysisComplete) {
        onAnalysisComplete({
          ...data,
          userPhoto: preview  // Include the user's photo preview
        });
      }
    } catch (err) {
      setError(err.message || 'Connection error. Please try again');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setError(null);
  };

  return (
    <div className="photo-upload">
      {!preview ? (
        <div
          className={`upload-area ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="upload-icon">📷</div>
          <h3>Upload Your Photo</h3>
          <p>Drag and drop your photo here, or click to select</p>
          <input
            type="file"
            id="file-input"
            accept="image/jpeg,image/png,image/webp,image/*"
            capture="environment"
            onChange={handleFileSelect}
            className="file-input"
          />
          <label htmlFor="file-input" className="upload-button">
            Choose Photo
          </label>
          <p className="upload-hint">Supports JPEG, PNG, WebP (max 10MB)</p>
        </div>
      ) : (
        <div className="preview-area">
          <img src={preview} alt="Preview" className="preview-image" />
          <div className="preview-actions">
            <button onClick={handleReset} className="button-secondary" disabled={isLoading}>
              Choose Different Photo
            </button>
            <button onClick={handleUpload} className="button-primary" disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Analyze Face Shape'}
            </button>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Analyzing your face shape...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}

export default PhotoUpload;
