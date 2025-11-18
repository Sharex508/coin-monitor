import React, { useState } from 'react';
import axios from 'axios';
import './AdminPanel.css';

// Get API URL from environment variable or use default
const API_URL = process.env.REACT_APP_API_URL || '';

const AdminPanel = () => {
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'

  const handleRefresh = async () => {
    try {
      setLoading(true);
      setMessage('');
      
      // Call the API to update initial prices
      const response = await axios.post(`${API_URL}/api/coin-monitors/update-initial-prices`);
      
      setMessage(response.data.message || 'Successfully refreshed all coin data.');
      setMessageType('success');
    } catch (error) {
      console.error('Error refreshing data:', error);
      setMessage(error.response?.data?.detail || 'Error refreshing data. Please try again.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCredentials = () => {
    // Save credentials to localStorage
    localStorage.setItem('binanceClientId', clientId);
    localStorage.setItem('binanceClientSecret', clientSecret);
    
    setMessage('Credentials saved successfully.');
    setMessageType('success');
    
    // Clear message after 3 seconds
    setTimeout(() => {
      setMessage('');
    }, 3000);
  };

  // Load credentials from localStorage on component mount
  React.useEffect(() => {
    const savedClientId = localStorage.getItem('binanceClientId');
    const savedClientSecret = localStorage.getItem('binanceClientSecret');
    
    if (savedClientId) setClientId(savedClientId);
    if (savedClientSecret) setClientSecret(savedClientSecret);
  }, []);

  return (
    <div className="admin-panel">
      <h2>Admin Panel</h2>
      
      <div className="credentials-section">
        <h3>Binance API Credentials</h3>
        <p>Enter your Binance API credentials to enable buy/sell functionality.</p>
        
        <div className="form-group">
          <label htmlFor="clientId">Client ID:</label>
          <input
            type="text"
            id="clientId"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            placeholder="Enter your Binance Client ID"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="clientSecret">Client Secret:</label>
          <input
            type="password"
            id="clientSecret"
            value={clientSecret}
            onChange={(e) => setClientSecret(e.target.value)}
            placeholder="Enter your Binance Client Secret"
          />
        </div>
        
        <button 
          className="save-button"
          onClick={handleSaveCredentials}
          disabled={!clientId || !clientSecret}
        >
          Save Credentials
        </button>
      </div>
      
      <div className="refresh-section">
        <h3>Refresh Coin Data</h3>
        <p>Click the button below to refresh all coin data. This will reset all coins to their current market prices.</p>
        
        <button 
          className="refresh-button"
          onClick={handleRefresh}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh All Coin Data'}
        </button>
      </div>
      
      {message && (
        <div className={`message ${messageType}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default AdminPanel;