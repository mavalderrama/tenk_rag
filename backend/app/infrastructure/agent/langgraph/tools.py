from datetime import datetime
from typing import Any

from langchain.tools import tool

from backend.app.application.use_cases import get_historial_stock_price as ghs
from backend.app.application.use_cases import get_real_time_stock_price as grs
from backend.app.application.use_cases import search_documents as sd


class AgentTools:
    def __init__(
        self,
        get_real_time_stock_price: grs.GetRealTimeStockPrice,
        get_historical_stock_price: ghs.GetHistorialStockPrice,
        query_documents: sd.SearchDocuments,
    ) -> None:
        self._get_real_time_stock_price = get_real_time_stock_price
        self._get_historical_stock_price = get_historical_stock_price
        self._query_documents = query_documents

    def create_tools(self) -> list[Any]:
        """
        Create all tools for the agent.

        Returns:
            List of LangChain tools
        """

        @tool  # type: ignore
        async def get_real_time_stock_price(symbol: str) -> str:
            """
            Get the current realtime stock price for a given ticker symbol.

            Args:
                symbol: Stock ticker symbol (e.g., 'AMZN', 'AAPL')

            Returns:
                Current stock price and related information
            """
            real_time_stock_price = await self._get_real_time_stock_price.execute(symbol)
            symbol = real_time_stock_price.symbol
            price = real_time_stock_price.price
            timestamp = real_time_stock_price.timestamp
            currency = real_time_stock_price.currency
            volume = v if (v := real_time_stock_price.volume) else "N/A"
            market_cap = round(mc, 2) if (mc := real_time_stock_price.market_cap) else "N/A"
            day_high = round(dh, 2) if (dh := real_time_stock_price.day_high) else "N/A"
            day_low = round(dl, 2) if (dl := real_time_stock_price.day_low) else "N/A"
            open_price = round(op, 2) if (op := real_time_stock_price.open_price) else "N/A"
            close_price = round(cp, 2) if (cp := real_time_stock_price.close_price) else "N/A"

            return (
                f"Stock: {symbol}\n"
                f"Current Price: {price}\n"
                f"Timestamp: {timestamp}\n"
                f"Currency: {currency}\n"
                f"Volume: {volume}\n"
                f"Market Cap: {market_cap}\n"
                f"Day High: {day_high}\n"
                f"Day Low: {day_low}\n"
                f"Open Price: {open_price}\n"
                f"Close Price: {close_price}\n"
            )

        @tool  # type: ignore
        async def get_historical_stock_price(
            symbol: str,
            start_date: str,
            end_date: str,
            period: str = "1d",
        ) -> str:
            """
            Get historical stock prices for a given ticker symbol over a date range.

            Args:
                symbol: Stock ticker symbol (e.g., 'AMZN', 'AAPL')
                start_date: Start date in YYYY-MM-DD format
                end_date: End date in YYYY-MM-DD format
                period: Data granularity - '1d' for daily, '1wk' for weekly, '1mo' for monthly

            Returns:
                Historical stock prices and statistics
            """

            _start_date = datetime.strptime(start_date, "%Y-%m-%d")
            _end_date = datetime.strptime(end_date, "%Y-%m-%d")

            historical_price = await self._get_historical_stock_price.execute(
                symbol,
                _start_date,
                _end_date,
                period,
            )
            symbol = historical_price.symbol
            period = historical_price.period
            data_points = len(historical_price.prices)
            average_price = historical_price.average_price
            highest_price = historical_price.highest_price
            lowest_price = historical_price.lowest_price

            return (
                f"Stock: {symbol}\n"
                f"Period: {period}\n"
                f"Data Points: {data_points}\n"
                f"Average Price: {average_price}\n"
                f"Highest Price: {highest_price}\n"
                f"Lowest Price: {lowest_price}\n"
            )

        @tool  # type: ignore
        async def query_documents(
            query_text: str,
            metadata: dict[str, str | int],
            max_results: int = 10,
        ) -> str:
            """
            Search Amazon's financial documents (annual reports, earnings releases) for relevant information.

            Args:
                query_text: Search query describing what information to find
                metadata: Additional metadata to filter documents
                max_results: Maximum number of document chunks to return (default: 10)

            Returns:
                Relevant excerpts from financial documents
            """
            chunks = self._query_documents.execute(
                query_text=query_text,
                metadata=metadata,
                max_results=max_results,
            )

            if n_chunks := len(chunks) == 0:
                return "No relevant documents found."

            results = f"Found {n_chunks} relevant documents:\n\n"

            for c in chunks:
                results += (
                    "---Document Start---\n"
                    f"[{c.document_id}] (Relevance: {c.score}\n"
                    f"{c.text}\n"
                    f"---Document End---\n\n"
                )

            return results

        return [
            get_real_time_stock_price,
            get_historical_stock_price,
            query_documents,
        ]
