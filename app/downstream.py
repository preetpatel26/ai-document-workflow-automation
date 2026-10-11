import time
import httpx
from app.config import settings
from app.schemas import ShipmentRecord

class DownstreamError(RuntimeError):
    pass

def forward_record(record: ShipmentRecord, *, url: str | None = None,
                   api_key: str | None = None, timeout_seconds: float | None = None,
                   max_retries: int | None = None, client: httpx.Client | None = None) -> int:
    target_url = url if url is not None else settings.downstream_api_url
    if not target_url:
        raise DownstreamError("DOWNSTREAM_API_URL is not configured.")
    token = api_key if api_key is not None else settings.downstream_api_key
    timeout = timeout_seconds if timeout_seconds is not None else settings.http_timeout_seconds
    retries = max_retries if max_retries is not None else settings.downstream_max_retries
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    owns_client = client is None
    http = client or httpx.Client(timeout=timeout)
    try:
        for attempt in range(max(0, retries) + 1):
            try:
                response = http.post(target_url, json=record.model_dump(mode="json"), headers=headers)
                if response.status_code in (408, 429) or response.status_code >= 500:
                    if attempt < retries:
                        time.sleep(min(0.25 * (2 ** attempt), 1.0))
                        continue
                response.raise_for_status()
                return response.status_code
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt >= retries:
                    raise DownstreamError(f"Downstream request failed after retries: {exc}") from exc
                time.sleep(min(0.25 * (2 ** attempt), 1.0))
            except httpx.HTTPStatusError as exc:
                raise DownstreamError(f"Downstream returned HTTP {exc.response.status_code}.") from exc
        raise DownstreamError("Downstream request failed after retries.")
    finally:
        if owns_client:
            http.close()
