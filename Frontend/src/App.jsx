import { useState, useEffect } from 'react'
import './App.css'
import PhotoUpload from './components/PhotoUpload'
import Results from './components/Results'
import Favorites from './components/Favorites'
import Login from './components/Login'
import Register from './components/Register'

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showFavorites, setShowFavorites] = useState(false);
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(true);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        setUser(data.user);
      }
    } catch (err) {
      console.log('Not authenticated');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (data) => {
    setUser({ username: data.username, email: data.email });
  };

  const handleRegister = (data) => {
    alert('Registration successful! Please login.');
    setShowLogin(true);
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      setUser(null);
      setAnalysisResult(null);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return showLogin ? (
      <Login 
        onLogin={handleLogin} 
        onSwitchToRegister={() => setShowLogin(false)}
      />
    ) : (
      <Register 
        onRegister={handleRegister}
        onSwitchToLogin={() => setShowLogin(true)}
      />
    );
  }

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result);
  };

  const handleReset = () => {
    setAnalysisResult(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>AI Saç Kesimi Öneri Sistemi</h1>
            <p>Yüz şeklinize uygun saç kesimlerini keşfedin</p>
          </div>
          <div className="header-actions">
            <span className="user-info">👤 {user.username}</span>
            <button 
              className="favorites-button"
              onClick={() => setShowFavorites(true)}
            >
            ⭐ Favorilerim
            </button>
            <button 
              className="logout-button"
              onClick={handleLogout}
            >
              🚪 Çıkış
            </button>
          </div>
        </div>
      </header>
      
      <main className="app-main">
        {!analysisResult ? (
          <PhotoUpload onAnalysisComplete={handleAnalysisComplete} />
        ) : (
          <Results analysisResult={analysisResult} onReset={handleReset} />
        )}
      </main>

      {showFavorites && (
        <Favorites onClose={() => setShowFavorites(false)} />
      )}
    </div>
  )
}

export default App
