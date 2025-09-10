import logging
import os
import time
import threading
import requests
import sqlite3
from .coin_monitor import update_price_history

# Import PostgreSQL libraries if available
try:
    import psycopg2
    from psycopg2.extras import execute_batch
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("coin_price_monitor.log"),
        logging.StreamHandler()
    ]
)

def get_database_connection():
    """Create and return a database connection (PostgreSQL or SQLite)."""
    connection = None
    try:
        # Check if PostgreSQL is available and configured
        if POSTGRES_AVAILABLE and os.getenv('DB_HOST'):
            try:
                # Connect to PostgreSQL
                connection = psycopg2.connect(
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', 'postgres'),
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=os.getenv('DB_PORT', '5432'),
                    database=os.getenv('DB_NAME', 'coin_monitor'),
                )
                cursor = connection.cursor()
                logging.info("Successfully connected to the PostgreSQL database.")
                return connection, cursor
            except Exception as e:
                logging.error(f"Error connecting to PostgreSQL database: {e}")
                logging.info("Falling back to SQLite database.")
                # If PostgreSQL connection fails, fall back to SQLite

        # Use SQLite database
        db_path = os.path.join(os.path.dirname(__file__), 'coin_monitor.db')
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Create the coin_monitor table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_monitor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                initial_price REAL NOT NULL,
                low_price REAL NOT NULL,
                high_price REAL NOT NULL,
                latest_price REAL NOT NULL,
                low_price_1 REAL DEFAULT 0.0,
                high_price_1 REAL DEFAULT 0.0,
                low_price_2 REAL DEFAULT 0.0,
                high_price_2 REAL DEFAULT 0.0,
                low_price_3 REAL DEFAULT 0.0,
                high_price_3 REAL DEFAULT 0.0,
                low_price_4 REAL DEFAULT 0.0,
                high_price_4 REAL DEFAULT 0.0,
                low_price_5 REAL DEFAULT 0.0,
                high_price_5 REAL DEFAULT 0.0,
                low_price_6 REAL DEFAULT 0.0,
                high_price_6 REAL DEFAULT 0.0,
                low_price_7 REAL DEFAULT 0.0,
                high_price_7 REAL DEFAULT 0.0,
                low_price_8 REAL DEFAULT 0.0,
                high_price_8 REAL DEFAULT 0.0,
                low_price_9 REAL DEFAULT 0.0,
                high_price_9 REAL DEFAULT 0.0,
                low_price_10 REAL DEFAULT 0.0,
                high_price_10 REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        connection.commit()
        logging.info("Successfully connected to the SQLite database.")
        return connection, cursor
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        if connection:
            connection.close()
        raise

def get_all_coins():
    """Get all coins from the coin_monitor table."""
    try:
        connection, cursor = get_database_connection()
        query = """
            SELECT symbol FROM coin_monitor
        """
        cursor.execute(query)
        symbols = [row[0] for row in cursor.fetchall()]
        logging.info(f"Retrieved {len(symbols)} coins from coin_monitor table.")
        return symbols
    except Exception as e:
        logging.error(f"Error getting coins: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            connection.close()

def add_coin(symbol, price):
    """
    Add a new coin to the coin_monitor table and initialize its price history.
    This function has been enhanced to create varied price history cycles.
    """
    try:
        connection, cursor = get_database_connection()

        # Check if the coin already exists
        if isinstance(connection, psycopg2.extensions.connection):
            cursor.execute("SELECT COUNT(*) FROM coin_monitor WHERE symbol = %s", (symbol,))
        else:
            cursor.execute("SELECT COUNT(*) FROM coin_monitor WHERE symbol = ?", (symbol,))
        if cursor.fetchone()[0] > 0:
            logging.info(f"Coin {symbol} already exists in coin_monitor table.")
            return False

        # Calculate slightly different values for low and high prices
        # This helps create more realistic initial data
        low_price = price * 0.98  # 2% lower
        high_price = price * 1.02  # 2% higher

        # Insert the new coin
        if isinstance(connection, psycopg2.extensions.connection):
            insert_query = """
                INSERT INTO coin_monitor 
                (symbol, initial_price, low_price, high_price, latest_price)
                VALUES (%s, %s, %s, %s, %s)
            """
        else:
            insert_query = """
                INSERT INTO coin_monitor 
                (symbol, initial_price, low_price, high_price, latest_price)
                VALUES (?, ?, ?, ?, ?)
            """
        cursor.execute(insert_query, (symbol, price, low_price, high_price, price))
        connection.commit()
        logging.info(f"Added new coin {symbol} to coin_monitor table.")

        # Initialize price history with varied values for the first few cycles
        initialize_price_history(symbol, price)

        return True
    except Exception as e:
        logging.error(f"Error adding coin {symbol}: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def initialize_price_history(symbol, current_price):
    """
    Initialize only the first price history cycle for a newly added coin.
    This allows the other cycles to develop naturally over time.

    Args:
        symbol: The coin symbol
        current_price: The current price of the coin
    """
    try:
        connection, cursor = get_database_connection()

        # Only initialize the first cycle
        # The other cycles will develop naturally over time

        # Add some randomness to make each coin's history unique
        import random
        random.seed(hash(symbol))  # Use symbol as seed for reproducibility

        # Calculate slightly different values for high and low prices
        random_adjustment = random.uniform(0.98, 1.02)
        high_factor = 1.03 * random_adjustment  # 3% higher with small random adjustment
        low_factor = 0.97 / random_adjustment   # 3% lower with small random adjustment

        high_price = current_price * high_factor
        low_price = current_price * low_factor

        # Build the update query based on connection type
        if isinstance(connection, psycopg2.extensions.connection):
            update_query = """
                UPDATE coin_monitor
                SET high_price_1 = %s, low_price_1 = %s
                WHERE symbol = %s
            """
        else:
            update_query = """
                UPDATE coin_monitor
                SET high_price_1 = ?, low_price_1 = ?
                WHERE symbol = ?
            """

        # Execute the update
        cursor.execute(update_query, (high_price, low_price, symbol))
        connection.commit()

        logging.info(f"Initialized first price history cycle for coin {symbol}")
        return True
    except Exception as e:
        logging.error(f"Error initializing price history for {symbol}: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def initialize_coin_monitor(symbols=None):
    """
    Initialize the coin_monitor table with specified coins or from API.
    This function has been enhanced to create varied price history cycles for new coins.
    """
    connection = None
    try:
        # Fetch current prices from Binance API
        response = requests.get('https://api.binance.com/api/v3/ticker/price', timeout=10)
        response.raise_for_status()
        price_data = response.json()
        price_dict = {item['symbol']: float(item['price']) for item in price_data}

        # If no symbols provided, get all USDT pairs from Binance
        if not symbols:
            symbols = [item['symbol'] for item in price_data if item['symbol'].endswith('USDT')]
            logging.info(f"No symbols provided, using all USDT pairs from Binance: {len(symbols)} pairs found")

        connection, cursor = get_database_connection()

        # Check which symbols are already in the coin_monitor table
        cursor.execute("SELECT symbol FROM coin_monitor")
        existing_symbols = [row[0] for row in cursor.fetchall()]

        # Filter out symbols that are already in the table
        new_symbols = [symbol for symbol in symbols if symbol not in existing_symbols]

        if not new_symbols:
            logging.info("All specified coins are already in the coin_monitor table.")
            return True

        # Prepare data for insertion
        insert_data = []
        for symbol in new_symbols:
            if symbol in price_dict:
                price = price_dict[symbol]
                # Calculate slightly different values for low and high prices
                low_price = price * 0.98  # 2% lower
                high_price = price * 1.02  # 2% higher

                insert_data.append((
                    symbol,
                    price,       # initial_price
                    low_price,   # low_price
                    high_price,  # high_price
                    price        # latest_price
                ))
            else:
                logging.warning(f"Symbol {symbol} not found in Binance API response.")

        # Insert new records
        if insert_data:
            if isinstance(connection, psycopg2.extensions.connection):
                insert_query = """
                    INSERT INTO coin_monitor 
                    (symbol, initial_price, low_price, high_price, latest_price)
                    VALUES (%s, %s, %s, %s, %s)
                """
            else:
                insert_query = """
                    INSERT INTO coin_monitor 
                    (symbol, initial_price, low_price, high_price, latest_price)
                    VALUES (?, ?, ?, ?, ?)
                """

            # Do individual inserts
            for data in insert_data:
                cursor.execute(insert_query, data)

                # Initialize price history for each new coin
                symbol = data[0]
                price = data[1]
                initialize_price_history(symbol, price)

            connection.commit()
            logging.info(f"Initialized {len(insert_data)} new coins in coin_monitor table with varied price history.")
            return True
        else:
            logging.warning("No new coins to initialize in coin_monitor table.")
            return False
    except Exception as e:
        logging.error(f"Error initializing coin_monitor table: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def calculate_moving_averages(symbol, connection, cursor):
    """
    Calculate moving averages (MA7, MA25, MA99) for a specific coin based on historical price data.

    Args:
        symbol: The coin symbol
        connection: Database connection
        cursor: Database cursor

    Returns:
        tuple: (ma7, ma25, ma99) - The calculated moving averages
    """
    try:
        # Get the latest prices from the price_history table
        if isinstance(connection, psycopg2.extensions.connection):
            # PostgreSQL query with LIMIT
            ma7_query = """
                SELECT AVG(price) FROM (
                    SELECT price FROM price_history 
                    WHERE symbol = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 7
                ) AS recent_prices
            """
            ma25_query = """
                SELECT AVG(price) FROM (
                    SELECT price FROM price_history 
                    WHERE symbol = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 25
                ) AS recent_prices
            """
            ma99_query = """
                SELECT AVG(price) FROM (
                    SELECT price FROM price_history 
                    WHERE symbol = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 99
                ) AS recent_prices
            """
        else:
            # SQLite query with LIMIT
            ma7_query = """
                SELECT AVG(price) FROM (
                    SELECT price FROM price_history 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 7
                )
            """
            ma25_query = """
                SELECT AVG(price) FROM (
                    SELECT price FROM price_history 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 25
                )
            """
            ma99_query = """
                SELECT AVG(price) FROM (
                    SELECT price FROM price_history 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 99
                )
            """

        # Execute queries
        cursor.execute(ma7_query, (symbol,))
        ma7 = cursor.fetchone()[0] or 0.0

        cursor.execute(ma25_query, (symbol,))
        ma25 = cursor.fetchone()[0] or 0.0

        cursor.execute(ma99_query, (symbol,))
        ma99 = cursor.fetchone()[0] or 0.0

        return ma7, ma25, ma99
    except Exception as e:
        logging.error(f"Error calculating moving averages for {symbol}: {e}")
        return 0.0, 0.0, 0.0

def identify_trend(price, ma7, ma25, ma99):
    """
    Identify the trend based on price and moving averages.

    Args:
        price: Current price
        ma7: 7-period moving average
        ma25: 25-period moving average
        ma99: 99-period moving average

    Returns:
        tuple: (trend, cycle_status) - The identified trend and cycle status
    """
    # Default values
    trend = "Neutral"
    cycle_status = "Consolidation"

    # Check if we have enough data for meaningful calculations
    if ma7 == 0 or ma25 == 0:
        return trend, cycle_status

    # Calculate the percentage difference between MA7 and MA25
    ma_diff_percent = abs(ma7 - ma25) / ma25 * 100

    # Uptrend: When price candles are above the short-term MA (7) and MA(7) > MA(25)
    if price > ma7 and ma7 > ma25:
        trend = "UP"
        cycle_status = "UP Cycle – bullish momentum"

        # Check for cycle entry point: MA(7) crosses above MA(25) and price is above both
        if ma_diff_percent < 0.5:  # MAs are close, potential crossover
            cycle_status = "Begin Up Cycle – Possible Buy Zone"

        # Check for cycle exit point: price touches MA(25) from above OR MA(7) starts bending downward
        if price <= ma25 * 1.01:  # Price is close to MA25 (within 1%)
            cycle_status = "Exit Long Position"

    # Downtrend: When price candles are below the short-term MA (7) and MA(7) < MA(25)
    elif price < ma7 and ma7 < ma25:
        trend = "DOWN"
        cycle_status = "DOWN Cycle – bearish momentum"

        # Check for cycle entry point: MA(7) crosses below MA(25) and price is below both
        if ma_diff_percent < 0.5:  # MAs are close, potential crossover
            cycle_status = "Begin Down Cycle – Possible Sell Zone"

        # Check for cycle exit point: price touches MA(25) from below OR MA(7) starts bending upward
        if price >= ma25 * 0.99:  # Price is close to MA25 (within 1%)
            cycle_status = "Exit Short Position"

    # Neutral/Sideways: When MA(7) and MA(25) are close together and crossing frequently
    else:
        trend = "Neutral"
        cycle_status = "Consolidation"

    # Apply MA(99) as the macro trend filter
    if ma99 > 0:
        if price > ma99 and trend == "DOWN":
            cycle_status += " (Above MA99: Prioritize long trades)"
        elif price < ma99 and trend == "UP":
            cycle_status += " (Below MA99: Prioritize short trades)"

    return trend, cycle_status

def update_coin_prices():
    """Update the latest prices for all coins in the coin_monitor table."""
    connection = None
    try:
        # Fetch current prices from Binance API
        response = requests.get('https://api.binance.com/api/v3/ticker/price', timeout=10)
        response.raise_for_status()
        price_data = response.json()
        price_dict = {item['symbol']: float(item['price']) for item in price_data}

        connection, cursor = get_database_connection()

        # Get all symbols from coin_monitor
        cursor.execute("SELECT symbol FROM coin_monitor")
        symbols = [row[0] for row in cursor.fetchall()]

        updates = []
        history_updates = 0
        for symbol in symbols:
            if symbol in price_dict:
                latest_price = price_dict[symbol]

                # Store the price in the price_history table
                if isinstance(connection, psycopg2.extensions.connection):
                    insert_query = """
                        INSERT INTO price_history (symbol, price)
                        VALUES (%s, %s)
                    """
                else:
                    insert_query = """
                        INSERT INTO price_history (symbol, price)
                        VALUES (?, ?)
                    """
                cursor.execute(insert_query, (symbol, latest_price))

                # Get current high and low prices
                # Use appropriate placeholder based on connection type
                if isinstance(connection, psycopg2.extensions.connection):
                    cursor.execute(
                        "SELECT high_price, low_price FROM coin_monitor WHERE symbol = %s",
                        (symbol,)
                    )
                else:
                    cursor.execute(
                        "SELECT high_price, low_price FROM coin_monitor WHERE symbol = ?",
                        (symbol,)
                    )
                high_price, low_price = cursor.fetchone()

                # Update high_price if latest_price is higher
                if latest_price > high_price:
                    high_price = latest_price

                # Update low_price if latest_price is lower
                if latest_price < low_price:
                    low_price = latest_price

                # Calculate moving averages
                ma7, ma25, ma99 = calculate_moving_averages(symbol, connection, cursor)

                # Identify trend and cycle status
                trend, cycle_status = identify_trend(latest_price, ma7, ma25, ma99)

                # Add to updates list with moving averages and trend information
                updates.append((latest_price, high_price, low_price, ma7, ma25, ma99, trend, cycle_status, symbol))

                # Check if we need to update the price history
                if update_price_history(symbol, high_price, low_price, latest_price):
                    history_updates += 1

        # Execute batch update
        if updates:
            # Do individual updates
            if isinstance(connection, psycopg2.extensions.connection):
                update_query = """
                    UPDATE coin_monitor
                    SET latest_price = %s, high_price = %s, low_price = %s, 
                        ma7 = %s, ma25 = %s, ma99 = %s, 
                        trend = %s, cycle_status = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE symbol = %s
                """
            else:
                update_query = """
                    UPDATE coin_monitor
                    SET latest_price = ?, high_price = ?, low_price = ?, 
                        ma7 = ?, ma25 = ?, ma99 = ?, 
                        trend = ?, cycle_status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE symbol = ?
                """
            for update in updates:
                cursor.execute(update_query, update)

            # Clean up old price history data (keep only the last 100 entries per symbol)
            if isinstance(connection, psycopg2.extensions.connection):
                cleanup_query = """
                    DELETE FROM price_history 
                    WHERE id NOT IN (
                        SELECT id FROM (
                            SELECT id FROM price_history 
                            WHERE symbol = %s 
                            ORDER BY timestamp DESC 
                            LIMIT 100
                        ) AS recent_prices
                    )
                    AND symbol = %s
                """
            else:
                cleanup_query = """
                    DELETE FROM price_history 
                    WHERE id NOT IN (
                        SELECT id FROM price_history 
                        WHERE symbol = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 100
                    )
                    AND symbol = ?
                """

            for symbol in symbols:
                cursor.execute(cleanup_query, (symbol, symbol))

            connection.commit()
            logging.info(f"Updated latest prices for {len(updates)} coins, updated history for {history_updates} coins")
            return True
        else:
            logging.info("No prices updated")
            return False
    except Exception as e:
        logging.error(f"Error updating latest prices: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def update_existing_coins_history(force_update=False):
    """
    Update existing coins with varied price history if all cycles have the same values.
    This function checks all 10 cycles and can force update all coins regardless of current values.

    Args:
        force_update: If True, update all coins regardless of current values

    Returns:
        int: Number of coins updated
    """
    try:
        connection, cursor = get_database_connection()

        # Get all coins from the database with all cycle data
        if isinstance(connection, psycopg2.extensions.connection):
            query = """
                SELECT symbol, latest_price, 
                    high_price_1, low_price_1, high_price_2, low_price_2,
                    high_price_3, low_price_3, high_price_4, low_price_4,
                    high_price_5, low_price_5, high_price_6, low_price_6,
                    high_price_7, low_price_7, high_price_8, low_price_8,
                    high_price_9, low_price_9, high_price_10, low_price_10
                FROM coin_monitor
            """
        else:
            query = """
                SELECT symbol, latest_price, 
                    high_price_1, low_price_1, high_price_2, low_price_2,
                    high_price_3, low_price_3, high_price_4, low_price_4,
                    high_price_5, low_price_5, high_price_6, low_price_6,
                    high_price_7, low_price_7, high_price_8, low_price_8,
                    high_price_9, low_price_9, high_price_10, low_price_10
                FROM coin_monitor
            """
        cursor.execute(query)
        coins = cursor.fetchall()

        updated_count = 0
        for coin in coins:
            symbol = coin[0]
            price = coin[1]

            # Extract all cycle high and low prices
            cycle_data = []
            for i in range(10):
                high_idx = 2 + i*2
                low_idx = 3 + i*2
                cycle_data.append((coin[high_idx], coin[low_idx]))

            # Determine if we need to update this coin
            need_update = force_update

            if not need_update:
                # Check if price history is initialized
                if cycle_data[0][0] == 0.0 and cycle_data[0][1] == 0.0:
                    need_update = True
                else:
                    # Check if all cycles have the same values or are uninitialized

                    # First, count how many cycles are initialized
                    initialized_cycles = sum(1 for high, low in cycle_data if high != 0.0 or low != 0.0)

                    # If less than 10 cycles are initialized, we should update
                    if initialized_cycles < 10:
                        need_update = True
                    else:
                        # Check if all initialized cycles have the same values
                        first_high, first_low = None, None
                        all_same = True

                        for high, low in cycle_data:
                            if high != 0.0 or low != 0.0:  # Only check initialized cycles
                                if first_high is None:
                                    first_high, first_low = high, low
                                elif abs(high - first_high) < 0.0001 and abs(low - first_low) < 0.0001:
                                    # Values are the same (within a small epsilon)
                                    continue
                                else:
                                    all_same = False
                                    break

                        need_update = all_same

            if need_update:
                # Initialize price history with varied values
                initialize_price_history(symbol, price)
                updated_count += 1
                logging.info(f"Updated price history for coin {symbol} with varied values")

        logging.info(f"Updated price history for {updated_count} existing coins")
        return updated_count
    except Exception as e:
        logging.error(f"Error updating existing coins history: {e}")
        return 0
    finally:
        if connection:
            cursor.close()
            connection.close()

def force_update_all_price_histories():
    """
    Force update all coins' price history with varied values.
    This is useful for fixing all coins at once, regardless of their current state.

    Returns:
        int: Number of coins updated
    """
    return update_existing_coins_history(force_update=True)

def update_initial_prices():
    """
    Update the initial prices for all coins in the database with the current prices from the Binance API.
    This ensures that after a Docker restart, the initial prices match the current prices.

    Returns:
        int: Number of coins updated
    """
    try:
        # Fetch current prices from Binance API
        response = requests.get('https://api.binance.com/api/v3/ticker/price', timeout=10)
        response.raise_for_status()
        price_data = response.json()
        price_dict = {item['symbol']: float(item['price']) for item in price_data}

        connection, cursor = get_database_connection()

        # Get all symbols from coin_monitor
        cursor.execute("SELECT symbol FROM coin_monitor")
        symbols = [row[0] for row in cursor.fetchall()]

        updates = 0
        for symbol in symbols:
            if symbol in price_dict:
                current_price = price_dict[symbol]

                # Update initial_price, low_price, and high_price to match the current price
                if isinstance(connection, psycopg2.extensions.connection):
                    update_query = """
                        UPDATE coin_monitor
                        SET initial_price = %s, low_price = %s, high_price = %s, latest_price = %s
                        WHERE symbol = %s
                    """
                else:
                    update_query = """
                        UPDATE coin_monitor
                        SET initial_price = ?, low_price = ?, high_price = ?, latest_price = ?
                        WHERE symbol = ?
                    """
                cursor.execute(update_query, (current_price, current_price, current_price, current_price, symbol))
                updates += 1

        connection.commit()
        logging.info(f"Updated initial prices for {updates} coins to match current prices")
        return updates
    except Exception as e:
        logging.error(f"Error updating initial prices: {e}")
        if connection:
            connection.rollback()
        return 0
    finally:
        if connection:
            cursor.close()
            connection.close()

def run_price_monitor():
    """Main function to run the price monitoring continuously."""
    logging.info("Starting coin price monitor")

    # Initialize the coin_monitor table
    initialize_coin_monitor()

    # Update initial prices to match current prices from Binance API
    # This ensures that after a Docker restart, the initial prices match the current prices
    logging.info("Updating initial prices to match current prices from Binance API")
    updated_prices_count = update_initial_prices()
    logging.info(f"Updated initial prices for {updated_prices_count} coins to match current prices")

    # Don't force update all coins with varied price history on startup
    # Let the cycles develop naturally over time
    # This prevents all 10 cycles from being completed immediately after Docker startup

    while True:
        try:
            # Update prices
            update_coin_prices()

            # Sleep for 20 seconds
            time.sleep(20)
        except Exception as e:
            logging.error(f"Error in price monitor: {e}")
            time.sleep(20)  # Still sleep in case of error

# Function to start the price monitor in a separate thread
def start_price_monitor():
    """Start the price monitor in a separate thread."""
    monitor_thread = threading.Thread(target=run_price_monitor, daemon=True)
    monitor_thread.start()
    logging.info("Started price monitor thread")
    return monitor_thread

if __name__ == "__main__":
    # Run the price monitor directly if this script is executed
    run_price_monitor()
