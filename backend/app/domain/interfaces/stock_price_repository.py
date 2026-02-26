import abc
from datetime import datetime

from backend.app.domain.dtos.stock_price import HistoricalStockPrice, StockPrice


class IStockPriceRepository(abc.ABC):
    @abc.abstractmethod
    async def get_realtime_price(self, symbol: str) -> StockPrice:
        """Gets the current stock price for a given symbol."""

        raise NotImplementedError("Subclasses must implement get_stock_price method")

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        period: str = "1d",
    ) -> HistoricalStockPrice:
        """Gets historical stock prices for a given symbol."""
        raise NotImplementedError("Subclasses must implement get_historical_prices method")
