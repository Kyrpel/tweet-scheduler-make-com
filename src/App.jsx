import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [formData, setFormData] = useState({
    openaiKey: '',
    sheetsId: '',
    credentialsFile: null,
    tweets: '',
    saveCredentials: true,
    tweetImages: [],
    imageInstructions: '',
    pastedImages: [],
  })
  const [loading, setLoading] = useState(false)
  const [processingStep, setProcessingStep] = useState('')
  const [error, setError] = useState(null)
  const [savedCredentials, setSavedCredentials] = useState(null)

  // ... [Previous useEffect and other handlers remain the same]

  const handlePaste = (e) => {
    const items = e.clipboardData.items;
    const images = [];

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        const reader = new FileReader();
        reader.onload = (event) => {
          images.push(event.target.result);
          setFormData((prev) => ({
            ...prev,
            pastedImages: [...prev.pastedImages, ...images],
          }));
        };
        reader.readAsDataURL(file);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      setProcessingStep('Preparing data...')
      const formDataToSend = new FormData()
      
      // Add text tweets if they exist
      if (formData.tweets) {
        formDataToSend.append('tweets', formData.tweets)
      }
      
      // Add pasted images if they exist
      if (formData.pastedImages.length > 0) {
        setProcessingStep('Processing images...')
        formData.pastedImages.forEach((image, index) => {
          const imageBlob = base64ToBlob(image)
          formDataToSend.append('images', imageBlob, `image${index}.png`)
        })
      }
      
      // Add image instructions if they exist
      if (formData.imageInstructions) {
        formDataToSend.append('imageInstructions', formData.imageInstructions)
      }

      setProcessingStep('Sending to server...')
      const response = await fetch('http://localhost:3000/api/schedule', {
        method: 'POST',
        body: formDataToSend,
      })

      const result = await response.json()
      if (!response.ok) {
        throw new Error(result.error || 'Failed to schedule tweets')
      }

      alert('Tweets scheduled successfully')
    } catch (error) {
      console.error('Error:', error)
      alert('Error scheduling tweets')
    } finally {
      setLoading(false)
      setProcessingStep('')
    }
  }

  // Helper function to convert base64 to blob
  const base64ToBlob = (base64) => {
    const parts = base64.split(';base64,');
    const contentType = parts[0].split(':')[1];
    const raw = window.atob(parts[1]);
    const rawLength = raw.length;
    const uInt8Array = new Uint8Array(rawLength);

    for (let i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
    }

    return new Blob([uInt8Array], { type: contentType });
  };

  // Add this function to handle image removal
  const removeImage = (indexToRemove) => {
    setFormData(prev => ({
      ...prev,
      pastedImages: prev.pastedImages.filter((_, index) => index !== indexToRemove)
    }));
  };

  return (
    <div className="container">
      <h1>Tweet Scheduler</h1>
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        {/* ... [Previous credential sections remain the same] ... */}

        <div className="tweets-section">
          <h2>Tweets</h2>
          
          <div className="form-group">
            <label htmlFor="imageInstructions">Instructions for Image Processing</label>
            <textarea
              id="imageInstructions"
              value={formData.imageInstructions}
              onChange={(e) => setFormData(prev => ({ 
                ...prev, 
                imageInstructions: e.target.value 
              }))}
              placeholder="Enter instructions for processing tweet images (optional)"
              rows="3"
              onPaste={handlePaste}
              onKeyPress={handleKeyPress}
            />
            {formData.pastedImages.length > 0 && (
              <div className="image-thumbnails">
                {formData.pastedImages.map((image, index) => (
                  <div key={index} className="thumbnail-container">
                    <img src={image} alt={`Pasted ${index}`} className="thumbnail" />
                    <button
                      className="remove-image"
                      onClick={() => removeImage(index)}
                      type="button"
                      aria-label="Remove image"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="tweets">Enter or Edit Tweets</label>
            <textarea
              id="tweets"
              value={formData.tweets}
              onChange={(e) => setFormData(prev => ({ ...prev, tweets: e.target.value }))}
              required
              rows="10"
              placeholder="Enter your tweets here, one per line, or paste images above..."
            />
          </div>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <span>{processingStep || 'Processing...'}</span>
            </div>
          ) : (
            'Schedule Tweets'
          )}
        </button>

        {loading && (
          <div className="processing-status">
            <div className="status-message">{processingStep}</div>
            <div className="progress-bar"></div>
          </div>
        )}
      </form>
    </div>
  )
}

export default App

