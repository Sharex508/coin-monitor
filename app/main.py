from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import logging
import os

from .coin_monitor import (
    get_all_coin_monitors, 
    get_coin_monitor_by_symbol, 
    update_coin_monitor, 
    update_latest_prices,
    get_coin_price_history,
    get_recent_trades,
    CoinMonitor,
    CoinMonitorUpdate
)
from .coin_price_monitor import start_price_monitor, add_coin, force_update_all_price_histories, update_initial_prices

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

# Create FastAPI app
app = FastAPI(title="Coin Price Monitor API", description="API for monitoring cryptocurrency prices")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task for updating coin prices
price_monitor_thread = None

@app.on_event("startup")
def startup_price_update():
    """Start the background task when the app starts."""
    global price_monitor_thread
    # Start the price monitor that updates every 2 seconds
    price_monitor_thread = start_price_monitor()
    logging.info("Started coin price monitor thread")

@app.on_event("shutdown")
def shutdown_price_update():
    """Stop the background task when the app shuts down."""
    # The thread is a daemon thread, so it will be terminated when the app shuts down
    logging.info("Coin price monitor thread will be stopped when the app shuts down")

@app.get("/api/coin-monitors", response_model=List[dict])
def read_coin_monitors():
    """
    Endpoint to get all coin monitor records.
    """
    try:
        return get_all_coin_monitors()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/coin-monitors/{symbol}", response_model=dict)
def read_coin_monitor(symbol: str):
    """
    Endpoint to get a specific coin's monitoring data by symbol.
    """
    try:
        coin_monitor = get_coin_monitor_by_symbol(symbol)
        if not coin_monitor:
            raise HTTPException(status_code=404, detail=f"Coin monitor for symbol {symbol} not found")
        return coin_monitor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/coin-monitors/{symbol}", response_model=dict)
def update_coin_monitor_endpoint(symbol: str, data: CoinMonitorUpdate = Body(...)):
    """
    Endpoint to update a coin's monitoring data.
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        result = update_coin_monitor(symbol, update_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coin-monitors/update-prices", response_model=dict)
def update_all_prices():
    """
    Endpoint to refresh all coins with current market prices.
    """
    try:
        return update_latest_prices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/coin-monitors/{symbol}/history", response_model=dict)
def get_coin_history(symbol: str):
    """
    Endpoint to get the price history for a specific coin.

    This endpoint returns a structured representation of the price history,
    including the initial price, current prices (low, high, latest),
    and historical prices (up to 10 sets of low and high prices).

    The history is updated when there's a significant change in price
    (default 2% drop from high price).
    """
    try:
        history = get_coin_price_history(symbol)
        if not history:
            raise HTTPException(status_code=404, detail=f"Price history for symbol {symbol} not found")
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/coin-monitors/{symbol}/recent-trades", response_model=dict)
def get_coin_recent_trades(symbol: str):
    """
    Endpoint to get recent trade statistics for a specific coin.

    This endpoint returns a structured representation of the recent trade activity,
    including the number of buy and sell trades, volumes, and a trend analysis
    based on the last 3 minutes of trading data from Binance.

    It also provides a direct link to the trading pair on Binance.
    """
    try:
        trades = get_recent_trades(symbol)
        if "error" in trades:
            raise HTTPException(status_code=500, detail=trades["error"])
        return trades
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AddCoinRequest(BaseModel):
    symbol: str

@app.post("/api/coin-monitors/add", response_model=dict)
def add_new_coin(request: AddCoinRequest = Body(...)):
    """
    Endpoint to add a new coin to monitor.
    """
    try:
        # Fetch current price from Binance API
        import requests
        response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={request.symbol}', timeout=10)
        response.raise_for_status()
        price_data = response.json()
        price = float(price_data['price'])

        # Add the coin
        success = add_coin(request.symbol, price)

        if success:
            return {"message": f"Added {request.symbol} to monitoring with initial price {price}"}
        else:
            return {"message": f"Coin {request.symbol} already exists or could not be added"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise HTTPException(status_code=400, detail=f"Invalid symbol: {request.symbol}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coin-monitors/force-update-history", response_model=dict)
def force_update_history():
    """
    Endpoint to force update all coins' price history with varied values.
    This is useful for fixing all coins at once if they have the same values for all cycles.
    """
    try:
        updated_count = force_update_all_price_histories()
        return {"message": f"Successfully updated price history for {updated_count} coins with varied values"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coin-monitors/update-initial-prices", response_model=dict)
def update_initial_prices_endpoint():
    """
    Endpoint to update the initial prices for all coins to match the current prices from the Binance API.
    This is useful after a Docker restart to ensure that the initial prices match the current prices.
    """
    try:
        updated_count = update_initial_prices()
        return {"message": f"Successfully updated initial prices for {updated_count} coins to match current prices"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
