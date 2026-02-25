from datetime import datetime
from decimal import Decimal

import pydantic


class StockPrice(pydantic.BaseModel):
    """Represents a stock price at a specific point in time."""

    symbol: str
    price: Decimal
    timestamp: datetime
    currency: str = "USD"
    volume: int | None = None
    market_cap: Decimal | None = None
    day_high: Decimal | None = None
    day_low: Decimal | None = None
    open_price: Decimal | None = None
    close_price: Decimal | None = None


class HistoricalStockPrice(pydantic.BaseModel):
    symbol: str
    start_date: datetime
    end_date: datetime
    prices: list[StockPrice]
    period: str  # e.g., "1d", "1wk", "1mo"
