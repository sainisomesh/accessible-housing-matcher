import { useState, useEffect } from 'react'
import './App.css'
import { API_URL, JOTFORM_APPLICANT_URL, JOTFORM_LANDLORD_URL, LOGO_URL } from './config.js'

function App() {
  const [formData, setFormData] = useState({
    income: '',
    voucher_type: '',
    accessibility_needs: '',
    location: '',
    household_size: ''
  })
  
  const [matches, setMatches] = useState([])
  const [units, setUnits] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [savedMatches, setSavedMatches] = useState(() => {
    // Load saved matches from localStorage on mount
    const saved = localStorage.getItem('savedMatches')
    return saved ? JSON.parse(saved) : []
  })

  // Fetch all units on component mount
  useEffect(() => {
    fetchUnits()
  }, [])

  // Save saved matches to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('savedMatches', JSON.stringify(savedMatches))
  }, [savedMatches])

  // Fetch matches whenever form data changes (real-time matching)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (isFormComplete()) {
        findMatches()
      } else {
        setMatches([])
      }
    }, 500) // Debounce to avoid too many API calls

    return () => clearTimeout(timer)
  }, [formData.income, formData.location, formData.household_size, formData.accessibility_needs, formData.voucher_type])

  const fetchUnits = async () => {
    try {
      console.log('Fetching units from:', `${API_URL}/units`)
      const response = await fetch(`${API_URL}/units`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      if (!response.ok) {
        throw new Error(`Failed to fetch units: ${response.status} ${response.statusText}`)
      }
      const data = await response.json()
      console.log('Units fetched successfully:', data.length)
      setUnits(data)
    } catch (err) {
      console.error('Error fetching units:', err)
      setError(`Failed to load available units: ${err.message}. Backend may be starting up (Render free tier takes ~30 seconds on first request).`)
    }
  }

  const isFormComplete = () => {
    return formData.income && 
           formData.location && 
           formData.household_size &&
           formData.accessibility_needs
  }

  const findMatches = async () => {
    if (!isFormComplete()) return

    setLoading(true)
    setError(null)

    try {
      console.log('Finding matches with API_URL:', API_URL)
      // Create a temporary applicant submission
      const applicantId = 'temp_' + Date.now()
      
      // Submit applicant data to get matches
      console.log('Submitting applicant data...')
      const response = await fetch(`${API_URL}/webhook/applicant`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          submission_id: applicantId,
          answers: {
            name: { answer: 'Temporary User' },
            income: { answer: formData.income },
            voucher_type: { answer: formData.voucher_type || '' },
            accessibility_needs: { answer: formData.accessibility_needs },
            location: { answer: formData.location },
            household_size: { answer: formData.household_size },
            contact: { answer: '' }
          }
        })
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error')
        throw new Error(`Failed to submit applicant data: ${response.status} ${response.statusText}. ${errorText}`)
      }

      // Get matches for this applicant
      console.log('Fetching matches...')
      const matchResponse = await fetch(`${API_URL}/match/${applicantId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      if (!matchResponse.ok) {
        const errorText = await matchResponse.text().catch(() => 'Unknown error')
        throw new Error(`Failed to get matches: ${matchResponse.status} ${matchResponse.statusText}. ${errorText}`)
      }
      
      const matchData = await matchResponse.json()
      console.log('Matches received:', matchData)
      
      // Enrich matches with full unit details
      // Refresh units to get latest data
      console.log('Fetching units for enrichment...')
      const unitsResponse = await fetch(`${API_URL}/units`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      if (!unitsResponse.ok) {
        const errorText = await unitsResponse.text().catch(() => 'Unknown error')
        throw new Error(`Failed to fetch units: ${unitsResponse.status} ${unitsResponse.statusText}. ${errorText}`)
      }
      const currentUnits = await unitsResponse.json()
      
      const enrichedMatches = matchData.matches.map(match => {
        const unit = currentUnits.find(u => u.id === match.unit_id)
        return {
          ...match,
          unit: unit || null,
          unit_type: match.type || (unit ? unit.type : 'unknown')
        }
      }).filter(m => m.unit !== null) // Only show matches with valid units

      console.log('Enriched matches:', enrichedMatches.length)
      setMatches(enrichedMatches)
    } catch (err) {
      console.error('Error finding matches:', err)
      const errorMsg = err.message || 'Unknown error'
      if (errorMsg.includes('Failed to fetch') || errorMsg.includes('NetworkError')) {
        setError(`Connection failed. The backend may be starting up (Render free tier takes ~30 seconds on first request). Please wait a moment and try again. Error: ${errorMsg}`)
      } else {
        setError(`Failed to find matches: ${errorMsg}`)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAccessibilityChange = (feature) => {
    const current = formData.accessibility_needs.split(',').filter(f => f.trim())
    const index = current.indexOf(feature)
    
    if (index > -1) {
      current.splice(index, 1)
    } else {
      current.push(feature)
    }
    
    setFormData(prev => ({
      ...prev,
      accessibility_needs: current.join(',')
    }))
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const calculateMaxBudget = () => {
    if (!formData.income) return 0
    return Math.floor((parseInt(formData.income) * 0.3) / 12)
  }

  const isMatchSaved = (unitId) => {
    return savedMatches.some(saved => saved.unit_id === unitId)
  }

  const toggleSaveMatch = (match) => {
    if (isMatchSaved(match.unit_id)) {
      // Remove from saved
      setSavedMatches(savedMatches.filter(saved => saved.unit_id !== match.unit_id))
    } else {
      // Add to saved
      setSavedMatches([...savedMatches, match])
    }
  }

  const removeSavedMatch = (unitId) => {
    setSavedMatches(savedMatches.filter(saved => saved.unit_id !== unitId))
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <div className="logo-container">
              <img 
                src={LOGO_URL} 
                alt="Organization Logo" 
                className="maxhousing-logo"
                onError={(e) => {
                  // Fallback if logo not found - hide the image
                  e.target.style.display = 'none';
                }}
              />
            </div>
            <div className="header-text">
              <h1 className="title">
                Accessible Housing Matcher
              </h1>
              <p className="subtitle">Find your perfect accessible housing match in real-time</p>
            </div>
            <div className="logo-container" style={{ visibility: 'hidden' }}>
              {/* Invisible spacer to balance the logo and keep title centered */}
              <img 
                src={LOGO_URL} 
                alt="" 
                className="maxhousing-logo"
                aria-hidden="true"
              />
            </div>
          </div>
          
          <div className="action-buttons">
            <a 
              href={JOTFORM_APPLICANT_URL} 
              target="_blank" 
              rel="noopener noreferrer"
              className="action-button"
            >
              <span className="action-button-icon">📝</span>
              Apply for Housing
            </a>
            <a 
              href={JOTFORM_LANDLORD_URL} 
              target="_blank" 
              rel="noopener noreferrer"
              className="action-button secondary"
            >
              <span className="action-button-icon">🏘️</span>
              List Your Property
            </a>
          </div>

        </header>

        <div className="main-content">
          {/* Form Section */}
          <div className="form-section">
            <div className="form-card">
              <h2 className="section-title">Your Information</h2>
              <p className="section-subtitle">Fill out your details to see matching properties</p>

              {error && (
                <div className="error-banner">
                  <span className="error-icon">⚠️</span>
                  {error}
                </div>
              )}

              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">
                    Annual Income <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    name="income"
                    value={formData.income}
                    onChange={handleInputChange}
                    placeholder="50000"
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Voucher Type</label>
                  <select
                    name="voucher_type"
                    value={formData.voucher_type}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="">None</option>
                    <option value="Section 8">Section 8</option>
                    <option value="Housing Choice Voucher">Housing Choice Voucher</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Location (City/ZIP) <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    placeholder="New York, NY or 10001"
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Household Size <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    name="household_size"
                    value={formData.household_size}
                    onChange={handleInputChange}
                    placeholder="2"
                    min="1"
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Accessibility Needs <span className="required">*</span>
                </label>
                <div className="checkbox-group">
                  {[
                    { value: 'wheelchair', label: 'Wheelchair Access' },
                    { value: 'elevator', label: 'Elevator Access' },
                    { value: 'ramp', label: 'Ramp Access' },
                    { value: 'roll_in_shower', label: 'Roll-in Shower' },
                    { value: 'visual_alarm', label: 'Visual Alarm' },
                    { value: 'wide_doorways', label: 'Wide Doorways' },
                    { value: 'accessible_bathroom', label: 'Accessible Bathroom' }
                  ].map(feature => (
                    <label key={feature.value} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.accessibility_needs.includes(feature.value)}
                        onChange={() => handleAccessibilityChange(feature.value)}
                        className="checkbox-input"
                      />
                      <span className="checkbox-text">
                        {feature.label}
                      </span>
                    </label>
                  ))}
                </div>
                {formData.accessibility_needs && (
                  <div className="helper-text">
                    Selected: {formData.accessibility_needs.split(',').filter(f => f.trim()).map(f => {
                      const featureMap = {
                        'wheelchair': 'Wheelchair Access',
                        'elevator': 'Elevator Access',
                        'ramp': 'Ramp Access',
                        'roll_in_shower': 'Roll-in Shower',
                        'visual_alarm': 'Visual Alarm',
                        'wide_doorways': 'Wide Doorways',
                        'accessible_bathroom': 'Accessible Bathroom'
                      };
                      return featureMap[f] || f;
                    }).join(', ')}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Matches Section */}
          <div className="matches-section">
            <div className="matches-card">
              <div className="matches-header">
                <h2 className="section-title">Your Matches</h2>
                {isFormComplete() && (
                  <div className="match-count">
                    {loading ? 'Calculating...' : `${matches.length} ${matches.length === 1 ? 'match' : 'matches'} found`}
                  </div>
                )}
              </div>

              {!isFormComplete() && (
                <div className="empty-state">
                  <div className="empty-icon">📋</div>
                  <p>Complete the form above to see your matches</p>
                </div>
              )}

              {loading && (
                <div className="loading-state">
                  <div className="spinner"></div>
                  <p>Finding your perfect matches...</p>
                </div>
              )}

              {!loading && isFormComplete() && matches.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">🔍</div>
                  <p>No matches found. Try adjusting your criteria.</p>
                </div>
              )}

              {!loading && matches.length > 0 && (
                <div className="matches-list">
                  {matches.map((match, index) => (
                    <div key={match.unit_id} className="match-card">
                      <div className="match-header">
                        <div className="match-rank">
                          <span className="rank-number">#{index + 1}</span>
                          <span className="rank-label">Match</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                          <button
                            onClick={() => toggleSaveMatch(match)}
                            className={`save-button ${isMatchSaved(match.unit_id) ? 'saved' : ''}`}
                            title={isMatchSaved(match.unit_id) ? 'Remove from saved' : 'Save for later'}
                          >
                            {isMatchSaved(match.unit_id) ? '✓ Saved' : '💾 Save'}
                          </button>
                          <div className="match-score">
                            <div className="score-value">{Math.round(match.score * 100)}%</div>
                            <div className="score-label">Match Score</div>
                          </div>
                        </div>
                      </div>

                      <div className="match-content">
                        <h3 className="property-name">
                          {match.unit.property_name || 'Unnamed Property'}
                          {match.unit.unit_number && ` - Unit ${match.unit.unit_number}`}
                        </h3>
                        <p className="property-address">📍 {match.unit.address || 'Address not provided'}</p>
                        
                        <div className="property-details">
                          <div className="detail-item">
                            <span className="detail-label">Rent:</span>
                            <span className="detail-value highlight">
                              {match.unit.rent_display || (match.unit.rent ? (typeof match.unit.rent === 'number' ? formatCurrency(match.unit.rent) : match.unit.rent) : 'Not specified')}
                            </span>
                          </div>
                          {(match.unit.availability || match.unit.total_units !== undefined) && (
                            <div className="detail-item">
                              <span className="detail-label">Status:</span>
                              <span className={`detail-value status-badge ${
                                match.unit.availability?.toLowerCase() === 'available' || 
                                match.unit.availability?.toLowerCase().includes('available (')
                                  ? 'status-available'
                                  : match.unit.availability?.toLowerCase() === 'not available' || 
                                    match.unit.availability?.toLowerCase() === 'occupied'
                                  ? 'status-unavailable'
                                  : match.unit.availability?.toLowerCase().includes('contact for availability')
                                  ? 'status-waitlist'  // Use waitlist style for neutral "contact" status
                                  : 'status-waitlist'  // Default to neutral for unknown statuses
                              }`}>
                                {match.unit.availability || 'Contact for availability'}
                                {match.unit.total_units !== undefined && match.unit.total_units > 0 && (
                                  <span> ({match.unit.total_units} total units{match.unit.units_available > 0 ? `, ${match.unit.units_available} available` : ''})</span>
                                )}
                              </span>
                            </div>
                          )}
                          {match.unit.income_range && (
                            <div className="detail-item">
                              <span className="detail-label">Income Range:</span>
                              <span className="detail-value">{match.unit.income_range}</span>
                            </div>
                          )}
                          {match.unit.age_range && (
                            <div className="detail-item">
                              <span className="detail-label">Age Range:</span>
                              <span className="detail-value">{match.unit.age_range}</span>
                            </div>
                          )}
                        </div>

                        {match.unit.accessibility_features && (
                          <div className="accessibility-features">
                            <span className="features-label">Features:</span>
                            <div className="features-tags">
                              {match.unit.accessibility_features.split(',').map(f => (
                                <span key={f} className="feature-tag">{f.trim()}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {match.reasons && match.reasons.length > 0 && (
                          <div className="match-reasons">
                            <div className="reasons-title">Why this match:</div>
                            <ul className="reasons-list">
                              {match.reasons.map((reason, i) => (
                                <li key={i} className="reason-item">
                                  <span className="reason-bullet">✓</span>
                                  {reason}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {(match.unit.contact || match.unit.landlord_name || match.unit.landlord_phone || match.unit.landlord_email) && (
                          <div className="contact-info">
                            {match.unit.landlord_name && (
                              <div style={{ marginBottom: '0.5rem' }}>
                                <span className="contact-label">Landlord:</span>
                                <span className="contact-value">{match.unit.landlord_name}</span>
                              </div>
                            )}
                            {match.unit.landlord_phone && (
                              <div style={{ marginBottom: '0.5rem' }}>
                                <span className="contact-label">Phone:</span>
                                <a href={`tel:${match.unit.landlord_phone}`} className="contact-link">
                                  {match.unit.landlord_phone}
                                </a>
                              </div>
                            )}
                            {match.unit.landlord_email && (
                              <div style={{ marginBottom: '0.5rem' }}>
                                <span className="contact-label">Email:</span>
                                <a href={`mailto:${match.unit.landlord_email}`} className="contact-link">
                                  {match.unit.landlord_email}
                                </a>
                              </div>
                            )}
                            {match.unit.contact && !match.unit.landlord_phone && !match.unit.landlord_email && (
                              <div>
                                <span className="contact-label">Contact:</span>
                                {match.unit.contact.includes('@') ? (
                                  <a href={`mailto:${match.unit.contact}`} className="contact-link">
                                    {match.unit.contact}
                                  </a>
                                ) : (
                                  <span className="contact-value">{match.unit.contact}</span>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                        {match.unit.notes && (
                          <div className="notes-info">
                            <span className="notes-label">Notes:</span>
                            <span className="notes-text">{match.unit.notes}</span>
                          </div>
                        )}
                        {match.unit_type === 'master' && (
                          <div className="unit-badge">
                            <span className="badge-text">Master Database</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Saved Matches Section */}
        {savedMatches.length > 0 && (
          <div className="saved-matches-section">
            <div className="saved-matches-card">
              <div className="saved-matches-header">
                <h2 className="section-title">
                  <span className="saved-icon">⭐</span>
                  Saved Matches ({savedMatches.length})
                </h2>
                <p className="section-subtitle">Properties you've saved for later</p>
              </div>

              <div className="saved-matches-list">
                {savedMatches.map((savedMatch) => {
                  const match = savedMatch
                  return (
                    <div key={match.unit_id} className="saved-match-card">
                      <div className="saved-match-header">
                        <div>
                          <h3 className="property-name">
                            {match.unit?.property_name || 'Unnamed Property'}
                            {match.unit?.unit_number && ` - Unit ${match.unit.unit_number}`}
                          </h3>
                          <p className="property-address">📍 {match.unit?.address || 'Address not provided'}</p>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                          <div className="match-score">
                            <div className="score-value">{Math.round(match.score * 100)}%</div>
                            <div className="score-label">Match Score</div>
                          </div>
                          <button
                            onClick={() => removeSavedMatch(match.unit_id)}
                            className="remove-saved-button"
                            title="Remove from saved"
                          >
                            ✕
                          </button>
                        </div>
                      </div>

                      <div className="saved-match-content">
                        <div className="property-details">
                          <div className="detail-item">
                            <span className="detail-label">Rent:</span>
                            <span className="detail-value highlight">
                              {match.unit?.rent_display || (match.unit?.rent ? (typeof match.unit.rent === 'number' ? formatCurrency(match.unit.rent) : match.unit.rent) : 'Not specified')}
                            </span>
                          </div>
                          {match.unit?.availability && (
                            <div className="detail-item">
                              <span className="detail-label">Status:</span>
                              <span className={`detail-value status-badge ${
                                match.unit.availability === 'N/A' 
                                  ? 'status-unavailable' 
                                  : `status-${match.unit.availability.toLowerCase()}`
                              }`}>
                                {match.unit.availability}
                              </span>
                            </div>
                          )}
                        </div>

                        {match.unit?.accessibility_features && (
                          <div className="accessibility-features">
                            <span className="features-label">Features:</span>
                            <div className="features-tags">
                              {match.unit.accessibility_features.split(',').map(f => (
                                <span key={f} className="feature-tag">{f.trim()}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {(match.unit?.contact || match.unit?.landlord_name || match.unit?.landlord_phone || match.unit?.landlord_email) && (
                          <div className="contact-info">
                            {match.unit?.landlord_name && (
                              <div style={{ marginBottom: '0.5rem' }}>
                                <span className="contact-label">Landlord:</span>
                                <span className="contact-value">{match.unit.landlord_name}</span>
                              </div>
                            )}
                            {match.unit?.landlord_phone && (
                              <div style={{ marginBottom: '0.5rem' }}>
                                <span className="contact-label">Phone:</span>
                                <a href={`tel:${match.unit.landlord_phone}`} className="contact-link">
                                  {match.unit.landlord_phone}
                                </a>
                              </div>
                            )}
                            {match.unit?.landlord_email && (
                              <div style={{ marginBottom: '0.5rem' }}>
                                <span className="contact-label">Email:</span>
                                <a href={`mailto:${match.unit.landlord_email}`} className="contact-link">
                                  {match.unit.landlord_email}
                                </a>
                              </div>
                            )}
                            {match.unit?.contact && !match.unit?.landlord_phone && !match.unit?.landlord_email && (
                              <div>
                                <span className="contact-label">Contact:</span>
                                {match.unit.contact.includes('@') ? (
                                  <a href={`mailto:${match.unit.contact}`} className="contact-link">
                                    {match.unit.contact}
                                  </a>
                                ) : (
                                  <span className="contact-value">{match.unit.contact}</span>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        <footer className="footer">
          <p>
            <strong>This is a matching tool for exploring available housing.</strong>
          </p>
          <p style={{ marginTop: '0.75rem' }}>
            To submit a formal application, please use the 
            <a 
              href={JOTFORM_APPLICANT_URL} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: 'var(--primary-blue)', margin: '0 0.25rem', fontWeight: 600 }}
            >
              official application form
            </a>
            or contact us directly.
          </p>
          <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-medium)' }}>
            Need help? Questions? Contact us through the application forms above.
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App

