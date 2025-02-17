import { useState, useEffect } from 'react'
import './ViralHooks.css'
import { fetchHooks } from '../config/hooks'

function ViralHooks() {
  const [selectedCategory, setSelectedCategory] = useState('question')
  const [searchTerm, setSearchTerm] = useState('')
  const [hookCategories, setHookCategories] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadHooks() {
      try {
        const data = await fetchHooks()
        setHookCategories(data)
        setLoading(false)
      } catch (err) {
        setError('Failed to load hooks')
        setLoading(false)
      }
    }
    loadHooks()
  }, [])

  if (loading) return <div>Loading hooks...</div>
  if (error) return <div>Error: {error}</div>
  if (!hookCategories) return null

  const filteredHooks = searchTerm 
    ? hookCategories[selectedCategory].examples.filter(hook => 
        hook.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : hookCategories[selectedCategory].examples

  return (
    <div className="hooks-container">
      <div className="hooks-nav">
        {Object.keys(hookCategories).map(category => (
          <button
            key={category}
            className={`hook-nav-btn ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category)}
          >
            {hookCategories[category].title}
          </button>
        ))}
      </div>

      <div className="hooks-search">
        <input
          type="text"
          placeholder="Search hooks..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="hooks-content">
        <h3>{hookCategories[selectedCategory].title}</h3>
        <div className="hooks-examples">
          {filteredHooks.map((hook, index) => (
            <div key={index} className="hook-example">
              <p>{hook}</p>
              <button 
                className="copy-btn"
                onClick={() => {
                  navigator.clipboard.writeText(hook);
                  // Optional: Show a copied notification
                }}
              >
                Copy
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ViralHooks 