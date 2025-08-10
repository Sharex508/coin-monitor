import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CoinDetail.css';

// Get API URL from environment variable or use default
const API_URL = process.env.REACT_APP_API_URL || '';

const CoinDetail = ({ symbol }) => {
  const [coinHistory, setCoinHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCoinHistory = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/api/coin-monitors/${symbol}/history`);
        setCoinHistory(response.data);
        setLoading(false);
      } catch (err) {
        setError(`Error fetching history for ${symbol}`);
        setLoading(false);
        console.error(`Error fetching history for ${symbol}:`, err);
      }
    };

    if (symbol) {
      fetchCoinHistory();
    }

    // Set up polling to refresh data every 20 seconds
    const interval = setInterval(() => {
      if (symbol) {
        fetchCoinHistory();
      }
    }, 20000);

    // Clean up interval on component unmount or when symbol changes
    return () => clearInterval(interval);
  }, [symbol]);

  if (!symbol) {
    return <div className="coin-detail">Select a coin to view details</div>;
  }

  if (loading) {
    return <div className="coin-detail">Loading {symbol} details...</div>;
  }

  if (error) {
    return <div className="coin-detail error">{error}</div>;
  }

  if (!coinHistory) {
    return <div className="coin-detail">No history available for {symbol}</div>;
  }

  return (
    <div className="coin-detail">
      <h2>{symbol} Details</h2>

      <div className="price-info">
        <div className="price-card">
          <h3>Current Price</h3>
          <p className="price-value">${coinHistory.current.latest_price.toFixed(7)}</p>
        </div>

        <div className="price-card">
          <h3>Initial Price</h3>
          <p className="price-value">${coinHistory.initial_price.toFixed(7)}</p>
        </div>

        <div className="price-card">
          <h3>24h High</h3>
          <p className="price-value">${coinHistory.current.high_price.toFixed(7)}</p>
        </div>

        <div className="price-card">
          <h3>24h Low</h3>
          <p className="price-value">${coinHistory.current.low_price.toFixed(7)}</p>
        </div>
      </div>

      <h3>Price History</h3>
      {coinHistory.history.length === 0 ? (
        <p>No price history available yet</p>
      ) : (
        <div className="history-table">
          <div className="history-header">
            <span>Set</span>
            <span>Previous Cycle High</span>
            <span>Low</span>
            <span>High</span>
            <span>Range</span>
          </div>
          <div className="history-body">
            {coinHistory.history.map((item) => {
              const range = ((item.high_price - item.low_price) / item.low_price * 100).toFixed(2);
              return (
                <div key={item.set} className="history-row">
                  <span>{item.set}</span>
                  <span>{item.prev_cycle_high ? `$${item.prev_cycle_high.toFixed(7)}` : '-'}</span>
                  <span>${item.low_price.toFixed(7)}</span>
                  <span>${item.high_price.toFixed(7)}</span>
                  <span>{range}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="timestamp">
        Last updated: {new Date(coinHistory.updated_at).toLocaleString()}
      </div>
    </div>
  );
};

export default CoinDetail;
