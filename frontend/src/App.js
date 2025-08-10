import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import CoinList from './components/CoinList';
import CoinDetail from './components/CoinDetail';

// Get API URL from environment variable or use default
const API_URL = process.env.REACT_APP_API_URL || '';

function App() {
  const [coins, setCoins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCoin, setSelectedCoin] = useState(null);

  useEffect(() => {
    const fetchCoins = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/api/coin-monitors`);
        setCoins(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error fetching coin data. Please try again later.');
        setLoading(false);
        console.error('Error fetching coin data:', err);
      }
    };

    fetchCoins();
    // Set up polling to refresh data every 20 seconds
    const interval = setInterval(fetchCoins, 20000);

    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, []);

  const handleCoinSelect = (coin) => {
    setSelectedCoin(coin);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Coin Price Monitor</h1>
      </header>
      <main className="App-main">
        {loading ? (
          <p>Loading coin data...</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : (
          <div className="content">
            <CoinList 
              coins={coins} 
              onSelectCoin={handleCoinSelect} 
              selectedCoin={selectedCoin}
            />
            {selectedCoin && <CoinDetail symbol={selectedCoin.symbol} />}
          </div>
        )}
      </main>
      <footer className="App-footer">
        <p>Data refreshes automatically every 20 seconds</p>
      </footer>
    </div>
  );
}

export default App;
