from backend.app.domain.dtos import stock_price
from backend.app.domain.interfaces import stock_price_repository


class GetRealTimeStockPrice:
    def __init__(self, stock_repository: stock_price_repository.IStockPriceRepository):
        self._stock_repository = stock_repository

    async def execute(
        self,
        symbol: str,
    ) -> stock_price.StockPrice:
        return await self._stock_repository.get_realtime_price(
            symbol,
        )
