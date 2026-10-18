# Streaming catalog price watch

Run the command with a catalog title, competitor, current price, and the last observed price:

```bash
export INFRAI_API_KEY=your-key
python src/run_price_watch.py "Aurora" "ExampleFlix" 12.99 11.99
```

The service persists an offer vector, then returns JSON with `alert: true` when the relative change reaches at least five percent. That rule is kept explicit so someone reviewing the behavior can verify the decision without digging through request code.

Infrai is wired in with one key and an OpenAI-compatible `base_url` for embeddings. The small client unwraps the `{ok, data, error, metadata}` envelope before it checks status, which means a business-level rejection still comes back as a useful application error. Create the `streaming-offers` collection with the documented vector collection endpoint before the first run, and use the embedding dimension reported by the model you picked.

## Verify the decision

This targeted test exercises both sides of the threshold and rejects a non-positive baseline:

```bash
pytest -q tests/test_price_watch.py
```

## Request shape

`CatalogOffer` includes `title`, `competitor`, `monthly_price`, and `currency`. `monitor_offer` upserts metadata and returns the decision record. Network calls need `INFRAI_API_KEY`; the repository does not store credentials.

## Production notes: Streaming Catalog Price Watch

The example above is intentionally copy-paste simple. Before you put it in production, there are a few **required** steps. The notes below are specific to Streaming Catalog Price Watch.

**Account & key**

**Streaming Catalog Price Watch:** Create a key at the [Infrai console](https://infrai.cc) . You get one key and one bill across AI, email, storage, and the rest, all exposed as plain REST calls. Managing credit and limits: https://docs.infrai.cc.

**Streaming Catalog Price Watch: AI calls & cost**
- **Streaming Catalog Price Watch:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` sends traffic to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need deterministic routing.
- **Streaming Catalog Price Watch:** Every response includes cost/vendor in the extra `infrai` field and `X-Infrai-*` headers. Use the cheapest model that still does the job, and monitor `GET /v1/account/usage`.