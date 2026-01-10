"""
Script to create dummy OHLCV data in parquet format
Following the structure: signals_data/raw/ohlc_1d/symbol=RELIANCE/year=2024/month=01/data.parquet
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, timedelta

def generate_dummy_ohlcv_data(
    symbol: str,
    year: int,
    month: int,
    num_days: int = 10,
    base_path: Path = None
) -> None:
    """
    Generate dummy OHLCV data and save to parquet file following the partitioned structure.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE')
        year: Year (e.g., 2024)
        month: Month (1-12)
        num_days: Number of days of data to generate (default: 10)
        base_path: Base path for signals_data folder (default: ../signals_data)
    """
    if base_path is None:
        # Assuming script is at repos/signals/scripts/, go up 3 levels (scripts -> signals -> repos) and add signals_data
        base_path = Path(__file__).parent.parent.parent / "signals_data"
    
    # Create the directory structure
    parquet_dir = base_path / "raw" / "ohlc_1d" / f"symbol={symbol}" / f"year={year}" / f"month={month:02d}"
    parquet_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate dates (trading days only, skip weekends)
    start_date = date(year, month, 1)
    dates = []
    current_date = start_date
    
    while len(dates) < num_days:
        # Skip weekends (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:
            dates.append(current_date)
        current_date += timedelta(days=1)
        # Safety check to avoid infinite loop
        if current_date.month != month:
            break
    
    # Generate realistic OHLCV data
    np.random.seed(42)  # For reproducible dummy data
    base_price = 2500.0  # Base price for RELIANCE
    
    data = []
    prev_close = base_price
    
    for i, dt in enumerate(dates):
        # Generate realistic price movements
        daily_change_pct = np.random.uniform(-2.0, 2.0)  # -2% to +2% daily change
        daily_volatility = np.random.uniform(0.5, 2.0)   # Volatility range
        
        # Calculate OHLC
        open_price = prev_close * (1 + np.random.uniform(-0.5, 0.5) / 100)
        
        # High should be >= max(open, close)
        high_price = max(open_price, prev_close) * (1 + abs(daily_change_pct) / 100 + daily_volatility / 100)
        
        # Low should be <= min(open, close)
        low_price = min(open_price, prev_close) * (1 - abs(daily_change_pct) / 100 - daily_volatility / 100)
        
        close_price = prev_close * (1 + daily_change_pct / 100)
        
        # Ensure high >= max(open, close) and low <= min(open, close)
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        # Generate volume (millions)
        volume = int(np.random.uniform(1, 10) * 1_000_000)
        
        data.append({
            'date': dt,
            'open': round(open_price, 2),
            'close': round(close_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'volume': volume
        })
        
        prev_close = close_price
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Ensure date column is properly typed
    df['date'] = pd.to_datetime(df['date'])
    
    # Write to parquet file
    parquet_file = parquet_dir / "data.parquet"
    df.to_parquet(parquet_file, index=False, engine='pyarrow')
    
    print(f"✓ Written parquet file to: {parquet_file}")
    print(f"  - Symbol: {symbol}")
    print(f"  - Year: {year}, Month: {month:02d}")
    print(f"  - Original DataFrame rows: {len(df)}")
    
    # Read back from parquet file to confirm write was successful
    print(f"\n📖 Reading back from parquet file to confirm write...")
    df_read = pd.read_parquet(parquet_file, engine='pyarrow')
    
    print(f"✓ Successfully read {len(df_read)} rows from parquet file")
    print(f"  - Date range: {df_read['date'].min().date()} to {df_read['date'].max().date()}")
    print(f"\n📊 Data read from parquet file:")
    print(df_read.to_string(index=False))

if __name__ == "__main__":
    # Create dummy data for RELIANCE, January 2024
    generate_dummy_ohlcv_data(
        symbol="RELIANCE",
        year=2024,
        month=1,
        num_days=10
    )
    
    print("\n" + "="*60)
    print("Dummy data created successfully!")
    print("="*60)

