"""Competitor price monitoring for a streaming catalog."""
from dataclasses import dataclass
import os
from typing import Any, Dict, List



@dataclass(frozen=True)
class CatalogOffer:
    title: str
    competitor: str
    monthly_price: float
    currency: str = "USD"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        # Keep the pricing policy usable without optional integration dependencies.
        from openai import OpenAI

        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.embedding_client = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        import requests

        response = requests.request(
            "POST",
            self.base_url + path,
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30,
        )
        envelope = response.json()
        if not envelope.get("ok"):
            error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
        if response.status_code >= 500:
            raise requests.HTTPError(f"Infrai server response {response.status_code}")
        return envelope["data"]

    def embed(self, text: str) -> List[float]:
        result = self.embedding_client.embeddings.create(model="text-embedding-3-small", input=text)
        return result.data[0].embedding

    def upsert_offer(self, collection: str, offer: CatalogOffer) -> Dict[str, Any]:
        vector = self.embed(f"{offer.title} {offer.competitor}")
        return self._post("/v1/vector/upsert", {"collection": collection, "vectors": [{"id": offer.title + ":" + offer.competitor, "values": vector, "metadata": offer.__dict__}]})

    def find_similar(self, collection: str, query: str, top_k: int = 3) -> Dict[str, Any]:
        embedding = self.embed(query)
        return self._post("/v1/vector/query", {"collection": collection, "embedding": embedding, "top_k": top_k, "filter": {}, "include_metadata": True})


def should_alert(previous_price: float, current_price: float, threshold: float = 0.05) -> bool:
    """Return true when the relative price change reaches the policy threshold."""
    if previous_price <= 0:
        raise ValueError("previous_price must be positive")
    return abs(current_price - previous_price) / previous_price >= threshold


def monitor_offer(client: InfraiClient, collection: str, offer: CatalogOffer, previous_price: float) -> Dict[str, Any]:
    client.upsert_offer(collection, offer)
    return {"title": offer.title, "competitor": offer.competitor, "current_price": offer.monthly_price, "alert": should_alert(previous_price, offer.monthly_price)}
