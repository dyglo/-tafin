from langchain.tools import tool
from typing import Any, Callable, Dict, List, Literal, Optional
import requests
import os
from pydantic import BaseModel, Field

####################################
# Tools
####################################
financial_datasets_api_key = os.getenv("TAFIN_FINANCIAL_DATASETS_API_KEY") or os.getenv("FINANCIAL_DATASETS_API_KEY")
serper_api_key = os.getenv("TAFIN_SERPER_API_KEY") or os.getenv("SERPER_API_KEY")
alpha_vantage_api_key = os.getenv("TAFIN_ALPHA_VANTAGE_API_KEY") or os.getenv("ALPHA_VANTAGE_API_KEY")


class FinancialStatementsInput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol to fetch financial statements for. For example, 'AAPL' for Apple.")
    period: Literal["annual", "quarterly", "ttm"] = Field(description="The reporting period for the financial statements. 'annual' for yearly, 'quarterly' for quarterly, and 'ttm' for trailing twelve months.")
    limit: int = Field(default=10, description="The number of past financial statements to retrieve.")
    report_period_gt: Optional[str] = Field(default=None, description="Optional filter to retrieve financial statements greater than the specified report period.")
    report_period_gte: Optional[str] = Field(default=None, description="Optional filter to retrieve financial statements greater than or equal to the specified report period.")
    report_period_lt: Optional[str] = Field(default=None, description="Optional filter to retrieve financial statements less than the specified report period.")
    report_period_lte: Optional[str] = Field(default=None, description="Optional filter to retrieve financial statements less than or equal to the specified report period.")


class SearchInput(BaseModel):
    query: str = Field(description="Search query to submit to Serper (Google Search).")
    num_results: int = Field(default=5, ge=1, le=10, description="Number of organic results to return.")


class AlphaVantageInput(BaseModel):
    function: Literal[
        "TIME_SERIES_INTRADAY",
        "TIME_SERIES_DAILY",
        "TIME_SERIES_DAILY_ADJUSTED",
        "TIME_SERIES_WEEKLY",
        "TIME_SERIES_MONTHLY",
        "OVERVIEW"
    ] = Field(default="TIME_SERIES_DAILY", description="The Alpha Vantage function to call.")
    symbol: str = Field(description="Ticker symbol (e.g., 'AAPL').")
    interval: Optional[Literal["1min", "5min", "15min", "30min", "60min"]] = Field(
        default=None,
        description="Interval for TIME_SERIES_INTRADAY requests."
    )
    outputsize: Optional[Literal["compact", "full"]] = Field(
        default="compact",
        description="Amount of data to retrieve where supported."
    )


def _require_key(name: str, value: Optional[str]) -> str:
    if not value:
        raise ValueError(f"{name} is not configured. Please set the appropriate environment variable.")
    return value


def _create_params(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int,
    report_period_gt: Optional[str],
    report_period_gte: Optional[str],
    report_period_lt: Optional[str],
    report_period_lte: Optional[str]
) -> Dict[str, Any]:
    """Helper function to create params dict for Financial Datasets API calls."""
    params: Dict[str, Any] = {"ticker": ticker, "period": period, "limit": limit}
    if report_period_gt is not None:
        params["report_period_gt"] = report_period_gt
    if report_period_gte is not None:
        params["report_period_gte"] = report_period_gte
    if report_period_lt is not None:
        params["report_period_lt"] = report_period_lt
    if report_period_lte is not None:
        params["report_period_lte"] = report_period_lte
    return params


def call_financialdatasets_api(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to call the Financial Datasets API."""
    api_key = _require_key("FINANCIAL_DATASETS_API_KEY", financial_datasets_api_key)
    base_url = "https://api.financialdatasets.ai"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": api_key}
    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


@tool(args_schema=FinancialStatementsInput)
def get_income_statements(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None
) -> Dict[str, Any]:
    """Fetches a company's income statement for the requested period."""
    params = _create_params(ticker, period, limit, report_period_gt, report_period_gte, report_period_lt, report_period_lte)
    data = call_financialdatasets_api("/financials/income-statements/", params)
    return data.get("income_statements", {})


@tool(args_schema=FinancialStatementsInput)
def get_balance_sheets(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieves a company's balance sheet."""
    params = _create_params(ticker, period, limit, report_period_gt, report_period_gte, report_period_lt, report_period_lte)
    data = call_financialdatasets_api("/financials/balance-sheets/", params)
    return data.get("balance_sheets", {})


@tool(args_schema=FinancialStatementsInput)
def get_cash_flow_statements(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None
) -> Dict[str, Any]:
    """Provides a company's cash flow statement."""
    params = _create_params(ticker, period, limit, report_period_gt, report_period_gte, report_period_lt, report_period_lte)
    data = call_financialdatasets_api("/financials/cash-flow-statements/", params)
    return data.get("cash_flow_statements", {})


def _serper_request(query: str, num_results: int) -> Dict[str, Any]:
    api_key = _require_key("SERPER_API_KEY", serper_api_key)
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


@tool(args_schema=SearchInput)
def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """Perform a Serper (Google) search and return the top organic results."""
    data = _serper_request(query, num_results)
    organic = data.get("organic", [])
    trimmed = [
        {"title": item.get("title"), "link": item.get("link"), "snippet": item.get("snippet")}
        for item in organic[:num_results]
    ]
    return {"query": query, "results": trimmed}


def _alpha_vantage_request(params: Dict[str, Any]) -> Dict[str, Any]:
    api_key = _require_key("ALPHA_VANTAGE_API_KEY", alpha_vantage_api_key)
    url = "https://www.alphavantage.co/query"
    params_with_key = {**params, "apikey": api_key}
    response = requests.get(url, params=params_with_key, timeout=30)
    response.raise_for_status()
    return response.json()


@tool(args_schema=AlphaVantageInput)
def alpha_vantage_query(
    function: str,
    symbol: str,
    interval: Optional[str] = None,
    outputsize: Optional[str] = "compact"
) -> Dict[str, Any]:
    """Call the Alpha Vantage API for market data or company overview."""
    params: Dict[str, Any] = {"function": function, "symbol": symbol, "outputsize": outputsize}
    if function == "TIME_SERIES_INTRADAY":
        if not interval:
            raise ValueError("Interval is required when function is TIME_SERIES_INTRADAY.")
        params["interval"] = interval
    data = _alpha_vantage_request(params)
    return data


TOOLS: List[Callable[..., Any]] = [
    get_income_statements,
    get_balance_sheets,
    get_cash_flow_statements,
    web_search,
    alpha_vantage_query,
]

RISKY_TOOLS: Dict[str, Callable[..., Any]] = {}  # guardrail: require confirmation


def run_web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """Convenience helper for CLI fallback mode to call Serper directly."""
    return web_search.func(query=query, num_results=num_results)


def run_alpha_vantage(function: str, symbol: str, interval: Optional[str] = None, outputsize: Optional[str] = "compact") -> Dict[str, Any]:
    """Convenience helper for CLI fallback mode to call Alpha Vantage directly."""
    return alpha_vantage_query.func(function=function, symbol=symbol, interval=interval, outputsize=outputsize)
