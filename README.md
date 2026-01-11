# signals

## Installation

1. Install Python 3 and pip (if not already installed):
   ```bash
   # On macOS with Homebrew:
   brew install python3
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
   Confirm if venv is created properly
  ```echo $VIRTUAL_ENV```
    /Users/deepakjayaprakash/Desktop/repos/rest_server/venv
   
   and You should see `(venv)` in your terminal prompt when activated.

4. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   confirm using pip list
   ```

5. Creating Parquet files
   - Data is present in signals_data which is outside this repo and resides inside this repo's parent directory 
   - python Run create_dummy_data.py

6. Creating sqlite datbase
   - Open DB Browser extension
   - Create DB inside signals_data/sqlite_db/
   - Give it name as sqlite_data.db
   - To create tables: sqlite3 ../signals_data/sqlite_db/signals.db < scripts/schema.sql
   - OR in DB Browser: File -> Open SQL -> Execute SQL