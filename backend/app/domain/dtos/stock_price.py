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
    """Represents historical stock prices over a period."""

    # Field constraints replace your manual 'if not' checks
    symbol: str = pydantic.Field(min_length=1, description="Stock symbol cannot be empty")
    start_date: datetime
    end_date: datetime
    prices: list[StockPrice] = pydantic.Field(
        min_length=1, description="Historical prices cannot be empty"
    )
    period: str  # e.g., "1d", "1wk", "1mo"

    @pydantic.model_validator(mode="after")
    def validate_dates(self) -> "HistoricalStockPrice":
        """Validate cross-field entity invariants."""
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
        return self

    @property
    def average_price(self) -> Decimal:
        """Calculate average price over the period."""
        # Note: We no longer need the 'if not self.prices' check
        # because Pydantic guarantees min_length=1
        return sum(p.price for p in self.prices) / Decimal(len(self.prices))

    @property
    def highest_price(self) -> Decimal:
        """Get highest price in the period."""
        return max(p.price for p in self.prices)

    @property
    def lowest_price(self) -> Decimal:
        """Get lowest price in the period."""
        return min(p.price for p in self.prices)
