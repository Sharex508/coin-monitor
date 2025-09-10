import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CoinDetail.css';

// Get API URL from environment variable or use default
const API_URL = process.env.REACT_APP_API_URL || '';

const CoinDetail = ({ symbol }) => {
  const [coinHistory, setCoinHistory] = useState(null);
  const [recentTrades, setRecentTrades] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch both history and recent trades in parallel
        const [historyResponse, tradesResponse] = await Promise.all([
          axios.get(`${API_URL}/api/coin-monitors/${symbol}/history`),
          axios.get(`${API_URL}/api/coin-monitors/${symbol}/recent-trades`)
        ]);

        setCoinHistory(historyResponse.data);
        setRecentTrades(tradesResponse.data);
        setLoading(false);
      } catch (err) {
        setError(`Error fetching data for ${symbol}`);
        setLoading(false);
        console.error(`Error fetching data for ${symbol}:`, err);
      }
    };

    if (symbol) {
      fetchData();
    }

    // Set up polling to refresh data every 20 seconds
    const interval = setInterval(() => {
      if (symbol) {
        fetchData();
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

      {coinHistory.moving_averages && (
        <div className="trend-analysis">
          <h3>Trend Analysis</h3>
          <div className="moving-averages">
            <div className="ma-card">
              <h4>MA(7)</h4>
              <p className="ma-value">${coinHistory.moving_averages.ma7.toFixed(7)}</p>
            </div>
            <div className="ma-card">
              <h4>MA(25)</h4>
              <p className="ma-value">${coinHistory.moving_averages.ma25.toFixed(7)}</p>
            </div>
            <div className="ma-card">
              <h4>MA(99)</h4>
              <p className="ma-value">${coinHistory.moving_averages.ma99.toFixed(7)}</p>
            </div>
          </div>

          <div className="trend-info">
            <div className={`trend-card ${coinHistory.trend_analysis.trend.toLowerCase()}`}>
              <h4>Trend</h4>
              <p className="trend-value">{coinHistory.trend_analysis.trend}</p>
            </div>
            <div className="cycle-card">
              <h4>Cycle Status</h4>
              <p className="cycle-value">{coinHistory.trend_analysis.cycle_status}</p>
            </div>
          </div>
        </div>
      )}

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

      {recentTrades && (
        <div className="recent-trades">
          <h3>Last 3 Minutes Trading Activity</h3>
          <div className="trade-stats">
            <div className="trade-card">
              <h4>Total Trades</h4>
              <p className="trade-value">{recentTrades.total_trades}</p>
            </div>
            <div className="trade-card">
              <h4>Buy Trades</h4>
              <p className="trade-value buy">{recentTrades.buy_trades} ({recentTrades.buy_percentage}%)</p>
            </div>
            <div className="trade-card">
              <h4>Sell Trades</h4>
              <p className="trade-value sell">{recentTrades.sell_trades} ({recentTrades.sell_percentage}%)</p>
            </div>
            <div className="trade-card">
              <h4>Buy Volume</h4>
              <p className="trade-value buy">{recentTrades.buy_volume}</p>
            </div>
            <div className="trade-card">
              <h4>Sell Volume</h4>
              <p className="trade-value sell">{recentTrades.sell_volume}</p>
            </div>
            <div className="trade-card">
              <h4>Avg Trade Size</h4>
              <p className="trade-value">{recentTrades.average_trade_size}</p>
            </div>
          </div>

          <div className="trade-analysis">
            <div className={`trend-indicator ${recentTrades.trend.toLowerCase()}`}>
              <h4>Market Sentiment</h4>
              <p className="trend-value">{recentTrades.trend}</p>
            </div>
            <div className="binance-link">
              <h4>Trade on Binance</h4>
              <a href={recentTrades.binance_link} target="_blank" rel="noopener noreferrer" className="binance-button">
                Open {symbol} on Binance
              </a>
            </div>
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
