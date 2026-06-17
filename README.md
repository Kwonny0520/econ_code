# Samsung Auto Trader (Mock)

A simple, polling-based automated trading system for Samsung Electronics (005930) using the Korea Investment & Securities Open API mock trading environment.

## Features
- Fetches OAuth token and caches it locally (`token_cache.json`) for same-day reuse.
- Repeatedly polls the mock market price during the trading window (09:10 - 15:30).
- Automatically checks balance and places limit buy/sell orders at +/- 1000 KRW from the current price.
- Detailed console logging.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Copy the example environment file and fill in your credentials.
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set:
   - `GH_ACCOUNT`: Your full 10-digit mock account number (e.g., `1234567801`).
   - `GH_APPKEY`: Your mock App Key.
   - `GH_APPSECRET`: Your mock App Secret.

## Running

Start the main script:
```bash
python main.py
```

The script will automatically detect the current time and execute the trading loop only if it falls within the 09:10 - 15:30 window. You can stop it at any time with `Ctrl+C`.
