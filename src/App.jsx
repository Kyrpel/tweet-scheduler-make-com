import { useState, useEffect } from 'react'
import './App.css'
import ViralHooks from './components/ViralHooks'
import ProcessingSpinner from './components/ProcessingSpinner'

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
    articleUrl: '',
    articleContent: '',
    socialMediaUrl: '',
  })
  const [loading, setLoading] = useState(false)
  const [processingStep, setProcessingStep] = useState('')
  const [error, setError] = useState(null)
  const [savedCredentials, setSavedCredentials] = useState(null)
  const [activeTab, setActiveTab] = useState('tweets') // 'tweets' or 'hooks'

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

      setProcessingStep('Processing tweets...')
      const response = await fetch('http://localhost:3000/api/process-tweets', {
        method: 'POST',
        body: formDataToSend,
      })

      const result = await response.json()
      if (!response.ok) {
        throw new Error(result.error || 'Failed to process tweets')
      }

      // Update the textarea with processed tweets
      setFormData(prev => ({
        ...prev,
        tweets: result.processedTweets
      }))

      alert('Tweets processed! Review them in the textarea and then schedule them.')
    } catch (error) {
      console.error('Error:', error)
      alert('Error processing tweets')
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

  const handleArticleProcess = async () => {
    setLoading(true);
    try {
      setProcessingStep('Processing article...');
      const response = await fetch('http://localhost:3000/api/process-article', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: formData.articleUrl,
        }),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || 'Failed to process article');
      }

      // Update both the article content and tweets textarea
      setFormData(prev => ({
        ...prev,
        articleContent: result.articleContent,
        tweets: prev.tweets 
          ? `${prev.tweets}\n\n${result.tweet}` 
          : result.tweet,
        articleUrl: '', // Clear the URL input after success
      }));

    } catch (error) {
      console.error('Error:', error);
      alert('Error processing article');
    } finally {
      setLoading(false);
      setProcessingStep('');
    }
  };

  // Add a new function to handle scheduling
  const handleScheduleTweets = async () => {
    setLoading(true)
    try {
      setProcessingStep('Scheduling tweets...')
      const response = await fetch('http://localhost:3000/api/schedule', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tweets: formData.tweets
        }),
      })

      const result = await response.json()
      if (!response.ok) {
        throw new Error(result.error || 'Failed to schedule tweets')
      }

      alert('Tweets scheduled successfully!')
    } catch (error) {
      console.error('Error:', error)
      alert('Error scheduling tweets')
    } finally {
      setLoading(false)
      setProcessingStep('')
    }
  }

  const handleSocialMediaProcess = async () => {
    setLoading(true);
    try {
      setProcessingStep('Processing social media content...');
      const response = await fetch('http://localhost:3000/api/process-social-media', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: formData.socialMediaUrl,
        }),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || 'Failed to process social media content');
      }

      // Update both the content and tweets textarea
      setFormData(prev => ({
        ...prev,
        tweets: prev.tweets 
          ? `${prev.tweets}\n\n${result.tweet}` 
          : result.tweet,
        socialMediaUrl: '', // Clear the URL input after success
      }));

    } catch (error) {
      console.error('Error:', error);
      alert('Error processing social media content');
    } finally {
      setLoading(false);
      setProcessingStep('');
    }
  };

  return (
    <div className="container">
      <div className="title-container">
        <h1 className="title">Tweet Creation & Scheduler with Make.com</h1>
      </div>

      <div className="main-content">
        <div className="content-section tweets-section">
          <h2>Create Tweets</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="articleUrl">Article URL</label>
              <div className="url-input-container">
                <input
                  type="url"
                  id="articleUrl"
                  value={formData.articleUrl}
                  onChange={(e) => setFormData(prev => ({ ...prev, articleUrl: e.target.value }))}
                  placeholder="Enter article URL to generate tweet..."
                />
                <button 
                  type="button"
                  onClick={handleArticleProcess}
                  disabled={!formData.articleUrl || loading}
                >
                  Process Article
                </button>
              </div>
              
              {loading && processingStep === 'Processing article...' && (
                <ProcessingSpinner />
              )}

              {formData.articleContent && (
                <div className="article-content">
                  <h3>Processed Article Content</h3>
                  <p>{formData.articleContent}</p>
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="socialMediaUrl">Social Media URL</label>
              <div className="url-input-container">
                <input
                  type="url"
                  id="socialMediaUrl"
                  value={formData.socialMediaUrl}
                  onChange={(e) => setFormData(prev => ({ ...prev, socialMediaUrl: e.target.value }))}
                  placeholder="Enter Instagram, TikTok, or YouTube URL..."
                />
                <button 
                  type="button"
                  onClick={handleSocialMediaProcess}
                  disabled={!formData.socialMediaUrl || loading}
                >
                  Process Social Media
                </button>
              </div>
              
              {loading && processingStep === 'Processing social media content...' && (
                <ProcessingSpinner text="Processing social media content..." />
              )}
            </div>

            <div className="form-group">
              <label htmlFor="imageInstructions">Instructions for Image Processing</label>
              <textarea
                id="imageInstructions"
                value={formData.imageInstructions}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  imageInstructions: e.target.value 
                }))}
                placeholder="Paste multiple images (optional)"
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

            <button
              className="process-tweets-btn"
              onClick={handleSubmit}
            >
              Process Tweets
            </button>

            <div className="tweets-section">
              <h2>Edit or Enter Tweets</h2>
              <textarea
                id="tweets"
                value={formData.tweets}
                onChange={(e) => setFormData(prev => ({ ...prev, tweets: e.target.value }))}
                rows="10"
                placeholder="Enter your tweets here, one per line, or paste images above..."
              />
            </div>

            <div className="button-group">
              <button 
                type="button" 
                onClick={handleScheduleTweets}
                disabled={loading || !formData.tweets}
              >
                Send to Google Sheets
              </button>
            </div>
          </form>
        </div>

        <div className="content-section hooks-section">
          <h2>Viral Hooks Inspiration</h2>
          <ViralHooks />
        </div>
      </div>

      {loading && (
        <div className="processing-status">
          <div className="status-message">{processingStep}</div>
          <div className="progress-bar"></div>
        </div>
      )}
    </div>
  )
}

export default App

