import abc


class IStockPriceRepository(abc.ABC):
    @abc.abstractmethod
    def get_stock_price(self, symbol: str) -> float:
        """Gets the current stock price for a given symbol."""

        raise NotImplementedError("Subclasses must implement get_stock_price method")
