# LangGraph Agent Integration

## Context

The system has all the infrastructure for a RAG + stock data agent (Bedrock LLM, pgvector hybrid search, yfinance, Langfuse) but nothing is wired together. The DI container is a skeleton, use cases are empty stubs, no API routes exist beyond health checks, and `langgraph` is already a declared dependency but unused.

**Goal**: Wire everything into a working `POST /agent/query` endpoint backed by a LangGraph ReAct agent that can search 10-K filings and fetch live stock prices.

---

## Phase 1: Fix the Domain Layer

Quick corrections before any new code. These unblock everything else.

- [ ] **`domain/interfaces/observability.py`**
  Change the return type of `get_observability_handler()` from the concrete `langfuse.langchain.CallbackHandler` to `langchain_core.callbacks.BaseCallbackHandler`. LangSmith cannot implement the interface as-is.

- [ ] **`domain/interfaces/document_repository.py`**
  Currently has a stock price method by mistake. Replace entirely with a `search()` method that matches `PostgresVectorDb.execute()`:
  ```python
  def search(
      self,
      query_text: str,
      query_embeddings: list[float],
      metadata: dict[str, str | int],
      top_k: int = 10,
  ) -> list[DocumentChunk]: ...
  ```

- [ ] **`domain/dtos/document_chunk.py`** *(new file)*
  Create a `DocumentChunk` Pydantic model mapping to the 3-tuples `PostgresVectorDb.execute()` returns:
  ```python
  class DocumentChunk(pydantic.BaseModel):
      document_id: str
      text: str
      rrf_score: float
      metadata: dict[str, str | int] = {}
  ```

- [ ] **`domain/interfaces/agent_orchestrator.py`** *(new file)*
  Define `AgentResult` and `IAgentOrchestrator`:
  ```python
  @dataclass
  class AgentResult:
      answer: str
      sources: list[str]

  class IAgentOrchestrator(abc.ABC):
      @abc.abstractmethod
      async def run(self, query: str) -> AgentResult: ...
  ```

---

## Phase 2: Implement the Use Cases

Thin orchestration classes, all injected via constructor. No self-instantiation.

- [ ] **`application/use_cases/search_documents.py`**
  Inject `IDocumentRepository` + `IEmbedderService`. Synchronous `execute()` — calls `embedder.embed(query)` then `repo.search(...)`. Sync because `PostgresVectorDb` uses a Django ORM cursor.

- [ ] **`application/use_cases/get_real_time_stock_price.py`**
  Inject `IStockPriceRepository`. Async `execute(symbol)` → returns `StockPrice`.

- [ ] **`application/use_cases/get_historial_stock_price.py`**
  Inject `IStockPriceRepository`. Async `execute(symbol, start_date, end_date, period)` → returns `HistoricalStockPrice`.

- [ ] **`application/use_cases/run_agent_query.py`** *(new file)*
  The top-level application entry point. Inject `IAgentOrchestrator` + `IObservability`:
  - Calls `agent.run(query)` and wraps it with `time.perf_counter()` for timing
  - Calls `observability.flush()` in a `finally` block (application layer owns the query lifecycle)
  - Returns `AgentQueryResult(answer, sources, execution_time_ms, timestamp)`

---

## Phase 3: Build the Infrastructure

- [ ] **`infrastructure/services/observability/langsmith.py`**
  Implement `LangSmithObservability(IObservability)` using:
  - `langsmith.Client(api_url=endpoint, api_key=api_key)`
  - `langchain_core.tracers.langchain.LangChainTracer(project_name=project, client=client)`
  - `get_observability_handler()` returns the tracer; `flush()` is a no-op (LangSmith auto-flushes)

- [ ] **`infrastructure/repositories/postgres_document_repository.py`** *(new file)*
  Adapter implementing `IDocumentRepository`. Wraps `PostgresVectorDb`:
  ```python
  class PostgresDocumentRepository(IDocumentRepository):
      def __init__(self) -> None:
          self._db = PostgresVectorDb()

      def search(self, query_text, query_embeddings, metadata, top_k=10) -> list[DocumentChunk]:
          rows = self._db.execute(query_text, query_embeddings, metadata, top_k)
          return [DocumentChunk(document_id=r[0], text=r[1], rrf_score=r[2]) for r in rows]
  ```

- [ ] **`infrastructure/services/agent/__init__.py`** *(new)*
  Empty package marker.

- [ ] **`infrastructure/services/agent/langgraph_agent.py`** *(new file)*
  The core piece. Key design decisions:

  **Graph is built once at `__init__`** (compiled graphs are reusable across requests):
  ```python
  self._graph = create_react_agent(model=llm_service.get_llm(), tools=tools, prompt=SYSTEM_PROMPT)
  ```

  **Tools use the closure pattern** — `_create_tools()` is a `@staticmethod` that captures use case instances:
  ```python
  @staticmethod
  def _create_tools(search_uc, realtime_uc, historical_uc) -> list:
      @tool
      def search_documents(query: str, company_ticker: str = "", ...) -> str:
          """Search 10-K SEC filings..."""
          chunks = search_uc.execute(query=query, ...)
          return format_chunks(chunks)

      @tool
      async def get_realtime_stock_price(symbol: str) -> str:
          """Get current stock price..."""
          price = await realtime_uc.execute(symbol)
          return format_price(price)

      @tool
      async def get_historical_stock_prices(symbol, start_date, end_date, period="1d") -> str:
          """Get historical prices..."""
          history = await historical_uc.execute(...)
          return format_history(history)

      return [search_documents, get_realtime_stock_price, get_historical_stock_prices]
  ```

  **`run()` injects callbacks per-invocation**:
  ```python
  async def run(self, query: str) -> AgentResult:
      handler = self._observability_service.get_observability_handler()
      config: RunnableConfig = {"callbacks": [handler]}
      result = await self._graph.ainvoke(
          {"messages": [{"role": "user", "content": query}]},
          config=config,
      )
      # Extract final AI message and document source IDs from result["messages"]
      return AgentResult(answer=..., sources=...)
  ```

  **System prompt** tells the LLM when to use each tool:
  ```
  You are a financial research assistant with access to:
  1. 10-K SEC filing documents (search_documents tool)
  2. Real-time stock prices (get_realtime_stock_price tool)
  3. Historical stock price data (get_historical_stock_prices tool)
  ```

---

## Phase 4: Wire the DI Container

**`di/container.py`** — Currently all properties return `None`. Replace with lazy singleton initialization using **deferred imports** inside each property body (prevents circular imports at module load time).

Add/fix these properties in dependency order:

| Property | Implementation |
|----------|----------------|
| `stock_repository` | `YFinanceStockPriceRepository()` |
| `document_repository` | `PostgresDocumentRepository()` |
| `embedder_service` | `BedrockEmbedder(aws_region, model_id)` |
| `llm_service` | `BedrockLLMService(model_id, region)` |
| `observability_service` | `LangfuseObservability` or `LangSmithObservability` based on `OBSERVABILITY_PROVIDER` env var |
| `agent_orchestrator` | `LangGraphAgentOrchestrator(llm_service, observability_service, search_uc, realtime_uc, historical_uc)` |
| `run_agent_query_use_case` | `RunAgentQueryUseCase(agent_orchestrator, observability_service)` |

The 3 use cases are constructed inline inside the `agent_orchestrator` property — they are stateless dataclasses so they don't need their own singleton caching.

---

## Phase 5: Add the API Endpoint

- [ ] **`presentation/api/routes/agent.py`** *(new file)*

  ```python
  router = APIRouter(prefix="/agent", tags=["agent"])

  @router.post("/query", response_model=QueryResponse)
  async def query_agent(body: QueryRequest, request: Request) -> QueryResponse:
      use_case = request.app.state.container.run_agent_query_use_case
      result = await use_case.execute(query=body.query)
      return QueryResponse(
          query=body.query,
          answer=result.answer,
          sources=result.sources,
          execution_time_ms=result.execution_time_ms,
          timestamp=result.timestamp,
      )
  ```

  The container is already stored on `app.state` in the lifespan — no need to import the singleton directly.

- [ ] **`presentation/api/main.py`**
  Register the router after existing middleware setup:
  ```python
  from app.presentation.api.routes.agent import router as agent_router
  app.include_router(agent_router)
  ```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `create_react_agent` from `langgraph.prebuilt` | Simpler than custom graph; produces predictable `messages` state; right fit for a 3-tool ReAct loop |
| Closure-based tools (not `BaseTool` subclasses) | `@tool` works on plain functions; no boilerplate; use cases injected cleanly via closure capture |
| Graph built once at constructor time | Compiled `CompiledStateGraph` is reusable; only `RunnableConfig` (callbacks) changes per request |
| `IDocumentRepository.search()` is sync | `PostgresVectorDb` uses a Django ORM cursor — the underlying call is blocking and cannot be async |
| `flush()` called in `RunAgentQueryUseCase` | Application layer owns the query lifecycle boundary, not the route handler |
| Deferred imports in `DIContainer` | Prevents circular imports across Django ORM, FastAPI, and LangChain at module load time |

---

## File Checklist

| File | Action |
|------|--------|
| `domain/interfaces/observability.py` | Fix return type → `BaseCallbackHandler` |
| `domain/interfaces/document_repository.py` | Replace wrong method with `search()` |
| `domain/dtos/document_chunk.py` | Create |
| `domain/interfaces/agent_orchestrator.py` | Create |
| `application/use_cases/search_documents.py` | Implement |
| `application/use_cases/get_real_time_stock_price.py` | Implement |
| `application/use_cases/get_historial_stock_price.py` | Implement |
| `application/use_cases/run_agent_query.py` | Create |
| `infrastructure/services/observability/langsmith.py` | Implement |
| `infrastructure/repositories/postgres_document_repository.py` | Create |
| `infrastructure/services/agent/__init__.py` | Create |
| `infrastructure/services/agent/langgraph_agent.py` | Create |
| `di/container.py` | Full lazy singleton wiring |
| `presentation/api/routes/agent.py` | Create |
| `presentation/api/main.py` | Register router |

---

## Verification

```bash
# 1. Start services
docker compose up -d

# 2. Run migrations
python manage.py migrate

# 3. Start API
uvicorn app.presentation.api.main:app --reload

# 4. Health check
curl http://localhost:8000/health

# 5. Query the agent
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are NVIDIA main risk factors from their latest 10-K?"}'

# 6. Check Langfuse dashboard for traces
# 7. GET /docs to verify the endpoint appears in OpenAPI
```
