import React, { useState } from 'react';
import './CoinList.css';

const CoinList = ({ coins, onSelectCoin, selectedCoin }) => {
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'rising', 'falling'
  const [sortField, setSortField] = useState('change');
  const [sortDirection, setSortDirection] = useState('desc'); // 'asc' or 'desc'

  // Separate coins into rising and falling
  const risingCoins = coins.filter(coin => coin.latest_price >= coin.initial_price);
  const fallingCoins = coins.filter(coin => coin.latest_price < coin.initial_price);

  // Helper function to safely calculate percentage change
  const calculatePercentChange = (latest, initial) => {
    if (!initial || initial === 0) return 0;
    return ((latest - initial) / initial) * 100;
  };

  // Sort function for coins
  const sortCoins = (coinsToSort) => {
    return [...coinsToSort].sort((a, b) => {
      let aValue, bValue;

      if (sortField === 'change') {
        aValue = calculatePercentChange(a.latest_price, a.initial_price);
        bValue = calculatePercentChange(b.latest_price, b.initial_price);
      } else if (sortField === 'price') {
        aValue = a.latest_price;
        bValue = b.latest_price;
      } else if (sortField === 'symbol') {
        aValue = a.symbol;
        bValue = b.symbol;
        return sortDirection === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });
  };

  // Determine which coins to display based on active tab
  let displayedCoins;
  switch (activeTab) {
    case 'rising':
      displayedCoins = sortCoins(risingCoins);
      break;
    case 'falling':
      displayedCoins = sortCoins(fallingCoins);
      break;
    default:
      displayedCoins = coins;
  }

  // Sort the rising and falling coins for the dual-column view
  const sortedRisingCoins = sortCoins(risingCoins);
  const sortedFallingCoins = sortCoins(fallingCoins);

  // Helper function to determine current cycle
  const getCurrentCycle = (coin) => {
    // Check which cycle fields are populated (non-zero)
    // Start from the highest cycle and work down
    for (let i = 10; i >= 1; i--) {
      if (coin[`high_price_${i}`] !== 0 || coin[`low_price_${i}`] !== 0) {
        // If we find a populated cycle, the current cycle is the next one
        // But we can't go higher than 10
        return Math.min(i + 1, 10);
      }
    }
    return 1; // Default to cycle 1 if no history yet
  };

  // Function to handle column header clicks for sorting
  const handleSortClick = (field) => {
    if (sortField === field) {
      // If already sorting by this field, toggle direction
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // If sorting by a new field, set it and default to descending
      setSortField(field);
      setSortDirection('desc');
    }
  };

  return (
    <div className="coin-list">
      <h2>Cryptocurrencies</h2>

      <div className="coin-tabs">
        <button 
          className={`tab-button ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          All ({coins.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'rising' ? 'active' : ''}`}
          onClick={() => setActiveTab('rising')}
        >
          Rising ({risingCoins.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'falling' ? 'active' : ''}`}
          onClick={() => setActiveTab('falling')}
        >
          Falling ({fallingCoins.length})
        </button>
      </div>

      {activeTab === 'all' ? (
        <div className="dual-column-container">
          <div className="column">
            <div className="column-header">Rising</div>
            <div className="list-header">
              <span 
                className={`symbol ${sortField === 'symbol' ? `sorted ${sortDirection}` : ''}`}
                onClick={() => handleSortClick('symbol')}
              >
                Symbol
              </span>
              <span className="cycle">Cycle</span>
              <span 
                className={`price ${sortField === 'price' ? `sorted ${sortDirection}` : ''}`}
                onClick={() => handleSortClick('price')}
              >
                Price (USD)
              </span>
              <span 
                className={`change ${sortField === 'change' ? `sorted ${sortDirection}` : ''}`}
                onClick={() => handleSortClick('change')}
              >
                Change
              </span>
            </div>
            <div className="list-body">
              {sortedRisingCoins.length === 0 ? (
                <p>No rising coins</p>
              ) : (
                sortedRisingCoins.map((coin) => {
                  const priceChange = coin.latest_price - coin.initial_price;
                  const priceChangePercent = calculatePercentChange(coin.latest_price, coin.initial_price);
                  const cycle = getCurrentCycle(coin);

                  return (
                    <div
                      key={coin.symbol}
                      className={`coin-item ${selectedCoin && selectedCoin.symbol === coin.symbol ? 'selected' : ''}`}
                      onClick={() => onSelectCoin(coin)}
                    >
                      <span className="symbol">{coin.symbol}</span>
                      <span className="cycle">{cycle > 0 ? cycle : '-'}</span>
                      <span className="price">${coin.latest_price.toFixed(7)}</span>
                      <span className="change positive">
                        +{priceChangePercent.toFixed(2)}%
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
          <div className="column">
            <div className="column-header">Falling</div>
            <div className="list-header">
              <span 
                className={`symbol ${sortField === 'symbol' ? `sorted ${sortDirection}` : ''}`}
                onClick={() => handleSortClick('symbol')}
              >
                Symbol
              </span>
              <span className="cycle">Cycle</span>
              <span 
                className={`price ${sortField === 'price' ? `sorted ${sortDirection}` : ''}`}
                onClick={() => handleSortClick('price')}
              >
                Price (USD)
              </span>
              <span 
                className={`change ${sortField === 'change' ? `sorted ${sortDirection}` : ''}`}
                onClick={() => handleSortClick('change')}
              >
                Change
              </span>
            </div>
            <div className="list-body">
              {sortedFallingCoins.length === 0 ? (
                <p>No falling coins</p>
              ) : (
                sortedFallingCoins.map((coin) => {
                  const priceChange = coin.latest_price - coin.initial_price;
                  const priceChangePercent = calculatePercentChange(coin.latest_price, coin.initial_price);
                  const cycle = getCurrentCycle(coin);

                  return (
                    <div
                      key={coin.symbol}
                      className={`coin-item ${selectedCoin && selectedCoin.symbol === coin.symbol ? 'selected' : ''}`}
                      onClick={() => onSelectCoin(coin)}
                    >
                      <span className="symbol">{coin.symbol}</span>
                      <span className="cycle">{cycle > 0 ? cycle : '-'}</span>
                      <span className="price">${coin.latest_price.toFixed(7)}</span>
                      <span className="change negative">
                        {priceChangePercent.toFixed(2)}%
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="list-header">
            <span 
              className={`symbol ${sortField === 'symbol' ? `sorted ${sortDirection}` : ''}`}
              onClick={() => handleSortClick('symbol')}
            >
              Symbol
            </span>
            <span className="cycle">Cycle</span>
            <span 
              className={`price ${sortField === 'price' ? `sorted ${sortDirection}` : ''}`}
              onClick={() => handleSortClick('price')}
            >
              Price (USD)
            </span>
            <span 
              className={`change ${sortField === 'change' ? `sorted ${sortDirection}` : ''}`}
              onClick={() => handleSortClick('change')}
            >
              Change
            </span>
          </div>
          <div className="list-body">
            {displayedCoins.length === 0 ? (
              <p>No coins available</p>
            ) : (
              displayedCoins.map((coin) => {
                // Calculate price change percentage safely
                const priceChange = coin.latest_price - coin.initial_price;
                const priceChangePercent = calculatePercentChange(coin.latest_price, coin.initial_price);
                const isPositive = priceChange >= 0;
                const cycle = getCurrentCycle(coin);

                return (
                  <div
                    key={coin.symbol}
                    className={`coin-item ${selectedCoin && selectedCoin.symbol === coin.symbol ? 'selected' : ''}`}
                    onClick={() => onSelectCoin(coin)}
                  >
                    <span className="symbol">{coin.symbol}</span>
                    <span className="cycle">{cycle > 0 ? cycle : '-'}</span>
                    <span className="price">${coin.latest_price.toFixed(7)}</span>
                    <span className={`change ${isPositive ? 'positive' : 'negative'}`}>
                      {isPositive ? '+' : ''}
                      {priceChangePercent.toFixed(2)}%
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default CoinList;
