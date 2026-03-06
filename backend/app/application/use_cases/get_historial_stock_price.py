from datetime import datetime

from backend.app.domain.dtos import stock_price
from backend.app.domain.interfaces import stock_price_repository


class GetHistorialStockPrice:
    """
    Use case for retrieving historical stock prices.

    Args:
        stock_repository (IStockPriceRepository): Repository for stock price data

    Methods:
        execute(symbol: str, start_date: str, end_date: str) -> List[StockPrice]: Retrieve historical stock prices
    """

    def __init__(
        self,
        stock_repository: stock_price_repository.IStockPriceRepository,
    ) -> None:
        """
        Initialize the GetHistorialStockPrice use case.

        Args:
            stock_repository (IStockPriceRepository): Repository for stock price data
        """
        self._stock_repository = stock_repository

    async def execute(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        period: str = "1d",
    ) -> stock_price.HistoricalStockPrice:
        return await self._stock_repository.get_historical_prices(
            symbol,
            start_date,
            end_date,
            period,
        )
