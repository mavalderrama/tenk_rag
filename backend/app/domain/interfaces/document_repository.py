import abc
from datetime import datetime

from app.domain.dtos.stock_price import HistoricalStockPrice


class IDocumentRepository(abc.ABC):
    @abc.abstractmethod
    async def get_historical_stock_price(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        period: str = "1d",
    ) -> HistoricalStockPrice:
        """Gets a document by its ID."""
        raise NotImplementedError
