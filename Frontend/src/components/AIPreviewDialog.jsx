import { useState } from 'react';
import './AIPreviewDialog.css';

function AIPreviewDialog({ 
  isOpen, 
  onClose, 
  onGenerate, 
  recommendations, 
  faceShape 
}) {
  const [selectedHairstyle, setSelectedHairstyle] = useState('');
  const [customHairstyle, setCustomHairstyle] = useState('');
  const [useCustom, setUseCustom] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = () => {
    const hairstyleToUse = useCustom ? customHairstyle : selectedHairstyle;
    if (hairstyleToUse.trim()) {
      onGenerate(hairstyleToUse);
      onClose();
    } else {
      alert('Please select or enter a hairstyle');
    }
  };

  return (
    <div className="ai-preview-dialog-overlay" onClick={onClose}>
      <div className="ai-preview-dialog" onClick={(e) => e.stopPropagation()}>
        <button className="dialog-close" onClick={onClose}>✕</button>
        
        <div className="dialog-header">
          <span className="dialog-icon">🎨</span>
          <h2>AI Hairstyle Preview</h2>
        </div>

        <p className="dialog-description">
          Would you like to generate AI previews of hairstyles on your photo?
          This will show you how different styles look on you before visiting a salon.
        </p>

        <div className="dialog-content">
          <div className="face-shape-info">
            <strong>Your Face Shape:</strong> {faceShape}
          </div>

          <div className="hairstyle-selection">
            <label className="selection-option">
              <input
                type="radio"
                checked={!useCustom}
                onChange={() => setUseCustom(false)}
              />
              <span>Choose from recommended styles</span>
            </label>

            {!useCustom && (
              <select 
                className="hairstyle-dropdown"
                value={selectedHairstyle}
                onChange={(e) => setSelectedHairstyle(e.target.value)}
              >
                <option value="">Select a hairstyle...</option>
                {recommendations.map((style) => (
                  <option key={style.id} value={style.name}>
                    {style.name} - {style.description}
                  </option>
                ))}
              </select>
            )}

            <label className="selection-option">
              <input
                type="radio"
                checked={useCustom}
                onChange={() => setUseCustom(true)}
              />
              <span>Enter custom hairstyle</span>
            </label>

            {useCustom && (
              <input
                type="text"
                className="custom-hairstyle-input"
                placeholder="e.g., Short buzz cut, Long wavy hair..."
                value={customHairstyle}
                onChange={(e) => setCustomHairstyle(e.target.value)}
              />
            )}
          </div>
        </div>

        <div className="dialog-actions">
          <button className="dialog-button cancel-button" onClick={onClose}>
            Skip for Now
          </button>
          <button 
            className="dialog-button generate-button" 
            onClick={handleGenerate}
            disabled={!useCustom && !selectedHairstyle || useCustom && !customHairstyle.trim()}
          >
            🎨 Generate Preview
          </button>
        </div>

        <div className="dialog-note">
          <small>⚠️ AI preview generation takes 30-60 seconds and uses Replicate API credits.</small>
        </div>
      </div>
    </div>
  );
}

export default AIPreviewDialog;
