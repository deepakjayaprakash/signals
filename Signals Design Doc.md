# **Personal Backtesting & Signals System**

**High Level Technical Design (HLD)**

---

## **1\. Big Picture Architecture**

**Goal:**  
 Build a modular Python system that:

* Collects EOD (1D) stock data for Indian equities  
* Computes indicators  
* Runs evolving strategies  
* Generates signals  
* Stores paper trades for later analysis

All components are **script-driven**, **manually or cron-triggered**, and **laptop-friendly**.

---

### **1.1 Module Interaction (Big Picture)**

![][image1]  

```plantuml
@startuml
alt data ingestion
  DataIngestion -> MarketDataStore : fetch &\nstore raw data
  DataIngestion -> MarketDataStore : corporate actions&\nstore clean data
end

alt feature engineering
  MarketDataStore -> IndicatorEngine
  IndicatorEngine -> IndicatorDataStore
end

alt Strategy
  IndicatorDataStore -> StrategyEngine
  MarketDataStore -> StrategyEngine
  ConfigStore -> StrategyEngine
  StrategyEngine -> SignalStore
end

alt paper trades and tracking
  SignalStore -> PaperTradingEngine : signals&/manual trades
  PaperTradingEngine -> PerformanceAnalytics
end
@enduml
```

## **2\. Core Modules & Responsibilities**

| Module | Responsibility |
| ----- | ----- |
| Data Ingestion | Fetch historical & daily OHLCV data |
| Raw Data Store | Persist unadjusted market data |
| Processed Data Store | Adjust historical data safely accounting for corporate actions |
| Indicator Engine/Feature Engineering | Compute EMA, RSI, etc |
| Strategy Engine | Generate buy/sell signals |
| Risk Engine | Apply capital, risk %, R:R rules |
| Signal Store | Persist generated signals |
| Paper Trading Engine | Simulate trades without capital |
| Performance Analytics | Evaluate strategy effectiveness |
| Configuration Store | Centralized strategy & risk configs |

---

## **3\. Module Deep Dive**

---

### **3.1 Data Ingestion Module**

Purpose:  
 Fetch historical and daily stock price data.  
Sub-components

* Stock universe loader (Top 500 by market cap)  
* Historical backfill job  
* Daily incremental job

Tech / Tools

* Python  
* requests  
* Data source: NSE/BSE APIs, paid API later (Zerodha, Dhan)

Input

* Stock symbol list  
* Date range

Output

* Raw OHLCV records stored in raw data store

---

### **3.2 Processed Data Store**

Purpose:  
 Ensure historical continuity after splits, bonuses, dividends.  
Key Responsibilities

* Detect splits/bonuses  
* Adjust historical prices & volumes  
* Prevent false signals

Input

* Raw OHLCV  
* Corporate action metadata/Auto detect and fix data

Output

* Adjusted OHLCV series  
* Store in another store

---

### **3.3 Indicator Engine/Feature Engineering**

Purpose:  
 Generate higher-order data from price series.  
Indicators

* EMA (9, 26\)  
* RSI  
* Volume averages  
* Extensible design

Tech

* Python  
* pandas  
* numpy

Input

* Secondary/Processed/Clean OHLCV data

Output

* Indicator values per stock per day

---

### **3.4.1 Strategy DSL and Parser**

**Purpose:**  
We should have a strategy DSL to define strategies built using technical indicators, so that, new strategies can be created/modified/cloned and used without writing too much code

**DS Parser would**

* Deserialize the strategy and create Strategy Domain Object  
* This object would be the input to the Backtesting Engine  
* Along with this, there will be custom analysis/logics as mentioned by me for IPO, Bonds, etc, which need not be gone through the DSL route

Input

* Strategy DSL

Output

* Strategy Domain Object

There would be 3 buckets of strategies

* Indicators and Prices  
* IPO, Bond, Interest Rate, Gold, Indices, correlation, etc  
* Custom strategies basis trend. Examples  
  * start with capital of 1L and max cap as 2L,  
  * for every 2% increase in price over a week Mon to Fri, on next Mon, add 5% to the position  
  * If Friday has opened with a gap up, Take buy position on Monday  
  * give me how many wins/losses and what is the final capital , etc. Max capital reach, min reached, max drawdowns, etc other information  
  * execute this in a given range, on these companies, etc filters

### **3.4.2 Backtesting Engine**

**Purpose:**  
 Apply trading logic on indicators or raw data.  
**Examples**

* EMA crossover  
* RSI oversold/overbought  
* Volume breakout

**Characteristics**

* Stateless per run  
* Easily versioned  
* Out-of-sample friendly

**Input**

* Indicators  
* Strategy configuration

**Output**

* Buy/Sell/Hold signals

---

### **3.5 Risk Engine**

**Purpose:**  
 Convert signals into position-sized trades.

**Responsibilities**

* Apply capital constraints  
* Risk per trade (%)  
* Risk-reward enforcement

**Input**

* Signal  
* Capital config

**Output**

* Position size  
* R:R of the signal  
* Entry/exit levels

---

### **3.6 Signal Store**

**Purpose:**  
 Persist generated signals for audit & replay.

**Stored Data**

* Strategy version  
* Signal timestamp  
* Confidence score (future-ready)

---

### **3.7 Paper Trading Engine**

**Purpose:**  
 Simulate real trading without capital.  
**Behavior**

* Execute trades at next candle open  
* Track PnL, drawdown, hit ratio  
* No look-ahead bias

**Input**

* Signals  
* Market data

**Output**

* Simulated trades  
* Performance metrics

---

### **3.8 Performance Analytics**

**Purpose:**  
 Evaluate strategy quality.

**Metrics**

* Win rate  
* Max drawdown  
* Sharpe (basic)  
* Equity curve

**Output**

* CSV reports  
* Summary tables

---

## **4\. Data Store Design**

---

### **4.1 Data Volume Estimation**

* 500 stocks  
* \~250 trading days/year  
* 1 row/day/stock

**Total rows:**  
 `500 × 250 = 125,000 rows` (very small)

---

### **4.2 Database Options**

| DB | Why |
| ----- | ----- |
| SQLite | Simple, zero-setup, laptop-friendly |
| PostgreSQL | Scalable, future-proof |
| DuckDB | Great for analytics & backtests |

**Phase 1 Recommendation:** SQLite or DuckDB

---

### **4.3 Data Domains**

| Domain | Description |
| ----- | ----- |
| Configuration | Capital, risk, strategy params |
| Raw Market Data | OHLCV |
| Adjusted Market Data | Post corporate actions |
| Indicator Data/Features | EMA, RSI, etc |
| Signals | Strategy outputs |
| Paper Trades | Simulated executions |
| Performance | Analytics results |

---

### **4.4 SQL Schema (dbdiagram.io)**

```sql
Table stocks {  
 id int \[pk\]  
 symbol varchar  
 name varchar  
}

Table raw\_prices\_1D {  
 id int \[pk\]  
 stock\_id int \[ref: \> stocks.id\]  
 date date  
 open float  
 high float  
 low float  
 close float  
 volume bigint  
}

Table indicators {  
 id int \[pk\]  
 stock\_id int \[ref: \> stocks.id\]  
 date date  
 ema\_9 float  
 ema\_26 float  
 rsi float  
}

Table strategies {  
 id int \[pk\]  
 name varchar  
 version varchar  
 description varchar  
 dsl varchar  
}

Table signals {  
 id int \[pk\]  
 stock\_id int \[ref: \> stocks.id\]  
 strategy\_id int \[ref: \> strategies.id\]  
 date date  
 signal\_type varchar  
}

Table paper\_trades {  
 id int \[pk\]  
 signal\_id int \[ref: \> signals.id\]  
 entry\_price float  
 exit\_price float  
 pnl float  
}
```

---

## **5\. Daily Job Data Flow**

![][image2]

```

@startuml
title Signals System – Daily Data Pipeline (DFD)

start

:Daily Data Fetcher Job;
note right
Fetch today's OHLCV
for 500 symbols
end note
:Append + Rewrite
Raw OHLC Parquet
(Current Month);

:Sanitizer Job;
note right
Detect abnormal price moves
(~X% deviation)
Flag symbols
end note

:Manual Corporate Actions Input;
note right
Splits, dividends,
bonuses entered manually
end note

:Corporate Action Processor Job;
note right
Adjust historical prices
using CA rules
end note
:Append + Rewrite
Clean OHLC Parquet
(Current Month);

:Feature Engineering Job;
note right
Read max 2–3 months
Compute EMA, RSI, etc
end note
:Rewrite Indicator Parquet
(Current Month);

:Backtesting Engine;
note right
Load OHLC + Indicators
Sequential simulation
end note
:Store Results
(SQLite);
:Store Paper Trades
(SQLite);

stop
@enduml


```


---

## **6\. Miscellaneous Analysis Requirements**

* Will manually feed in 1 year daily data for things like 10Y bond yields, interest rates whenever changes are announced. This data does not have a fixed frequency, hence the manual flow  
* Later want to build just custom scripts to just perform exploratory analysis and derive insights like correlation, etc  
* Also will manually feed in recently launched IPOs, and will fetch prices since the launch date daily OHLCV data like the rest of data  
* Will try to analyse some IPO specific behaviour. This will again be custom scripts to just perform exploratory analysis

---

## **7\. Repository Structure**

`signals/`  
`├── data_ingestion/`  
`│   ├── fetch_history.py`  
`│   └── fetch_daily.py`  
`├── corporate_actions/`  
`│   └── adjust_prices.py`  
`├── indicators/`  
`│   └── indicator_engine.py`  
`├── strategies/`  
`│   ├── base.py`  
`│   └── ema_rsi.py`  
`├── risk/`  
`│   └── risk_engine.py`  
`├── paper_trading/`  
`│   └── simulator.py`  
`├── analytics/`  
`│   └── performance.py`  
`├── db/`  
`│   └── models.py`  
`├── config/`  
`│   └── settings.yaml`  
`└── main.py`

---

## **8\. Phase Scope**

### **Phase 1 (Current)**

* 1D candles  
* CNC signals  
* Paper trading  
* Manual execution

### **Phase 2 (Future)**

* 5-minute candles  
* WebSocket live feeds  
* Intraday strategies  
* Confidence scoring  
* Partial automation

---

## **9\. Design Philosophy**

* Bias-aware (no look-ahead, survivorship safe)  
* Simple over optimal  
* Research-first, execution-later  
* Strategy iteration over automation

# LLD

## StrategyExecutorFactory

strategy\_type \= config\["strategy"\]\["type"\]

if strategy\_type \== "INDICATOR":  
    executor \= IndicatorStrategyExecutor(config)  
elif strategy\_type \== "POSITION\_SCALING":  
    executor \= PositionScalingExecutor(config)

PositionScalingStrategyExecutor  
for week in weeks:  
    pct\_change \= calculate\_weekly\_change(stock)

    if pct\_change \>= 2:  
        increase\_position(5%)  
    elif pct\_change \<= \-2:  
        decrease\_position(5%)

    enforce\_capital\_constraints()  
    record\_metrics()

## DSLs

strategy:  
  name: "Weekly\_Scale\_In\_Out"  
  type: POSITION\_SCALING

universe:  
  stocks: \["HDFCBANK", "ICICIBANK"\]  
  timeframe: "1D"

capital:  
  start: 100000  
  max: 200000

evaluation:  
  frequency: WEEKLY  
  window: MON\_FRI  
  metric: PRICE\_CHANGE\_PERCENT

rules:  
  \- if: metric \>= 2  
    action:  
      type: INCREASE\_POSITION  
      value: 5%  
  \- if: metric \<= \-2  
    action:  
      type: DECREASE\_POSITION  
      value: 5%

constraints:  
  max\_position\_percent: 100%  
  min\_position\_percent: 0%

outputs:  
  metrics:  
    \- total\_return  
    \- max\_drawdown  
    \- max\_capital\_used  
    \- win\_loss\_ratio

strategy:  
  name: "EMA\_Crossover"

universe:  
  stocks: \["RELIANCE", "TCS", "INFY"\]  
  timeframe: "1D"

indicators:  
  \- name: ema\_fast  
    type: EMA  
    period: 9  
  \- name: ema\_slow  
    type: EMA  
    period: 26

entry\_rules:  
  \- condition: "ema\_fast \> ema\_slow"

exit\_rules:  
  \- condition: "ema\_fast \< ema\_slow"

risk:  
  capital: 100000  
  risk\_per\_trade: 1%  
  position\_type: CNC

Custom scripts

/analysis

  ├── ipo\_analysis.py

  ├── bond\_stock\_correlation.py

[image1]: <data:image/png;base64,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1yxYsECDhowMnTt3NTt37rRfPUVRFMUlbLGoojFOEI133nmnOX/+vLTYUx0GDhxoPv74YztaipIxLF26VEWjoiiKh7DFoudFI+vlemHMUUFEY9u2baXLlO9DhgyVibjtfeINsUTjwYMH5ZPu88aNG5srV66Y9es3mTZt2uTZrb9mzTp7U8K5ePGiGTNmjL05LsiPffv2NdeuXbP/ysHhw4elmz4rK0u7rWLAZMhenxDZLdHol9kZvvjiC3tT2vLnP//Z3qQkiBs3btiblAKSCeNDbbHoedHoFUeYeETjV199JUvoMeCc3/Xr1zetWrWSlRhuv/1OM3v2XHkh7ePiCbFEo+MIE4zf3VKYPv98GTN//nwR3ARHPDJNRbgAv/32O2QFFee5h38ylpRz8d2uVNnGtAzh+yNIEK7AOXlubOfZbd26Vb7zf/hUGeFx4X/uM/w350RIsJ99De7JybM4wDzxRGFz4sSJPIWyX0kHRxi3RKMXGqWpQB1hlHjIBKHjFdQRxgXSSTRi3evXr5+57777AvtdCInGhQsXmp///OcBMfd84PviiOPiCTjCnD592o5WDtFYqNCDIlD/5V/+xXTtGhwfVrJkSdOiRQszadIkM2TIENO2bXvTpUtXsVD+8Ic/ND169DBDhw6VpaMeeOABsQw+9thjpkyZsmbixInm0UcflX127Ngh10H08f/w4cPNM888K79/9KMfmaZNW5inn35ahPNtt91munfvLtt3795tKlWqZG655RZTr14D88tf/lIsh2zr379/YFt988c//lGuM3jwYFOuXHkzd+5cc9dd95iNGzeap556ymzfvt38+Mc/DlyjuSlWrJjkh6JFi5oqVaoE9i8n8SpRorSKxlxQ0RgbFY3pB2WikhxUNCYOFY0uQJywlrlNXqIRLymE3TPPFDe33npboPLbHRKN/I8IWrFiRcRx8QS8ShFu0XCsgI5ohMcff1y6qRFlpUo9Z1q2bG1ef7174Pvzpl27dqZ06dKyH0KW7lxEI2Lz/vvvF9HI8WfPnjXz5s0LCMQnRGjOmTNPjrl69ar5P//nnwICub2pVau2WP8QifAP//APZsuWLaZs2bIhMemIRvZBUN57773m5MmTkpaIwIYNG5vjx48H0ux2uU7duvVENDZv3lyevSMa7777bvnNNTZs2GCmT59u1q5dm0M0EjcspEok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>

[image2]: <data:image/png;base64,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>