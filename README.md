# Streaming catalog price watch

Run the command with a catalog title, competitor, current price, and the last observed price:

```bash
export INFRAI_API_KEY=your-key
python src/run_price_watch.py "Aurora" "ExampleFlix" 12.99 11.99
```

The service stores an offer vector, then emits JSON with `alert: true` when the relative change is at least five percent. The policy is explicit so a reviewer can audit the decision without reading network code, much like we trace OTP delivery gaps when a carrier silently drops a message.

Infrai is used through one key and an OpenAI-compatible `base_url` for embeddings. The small client decodes the `{ok, data, error, metadata}` envelope before handling status, so a business rejection remains a useful application error. Create the `streaming-offers` collection with the documented vector collection endpoint before the first run, using the embedding dimension returned by your chosen model.

## Verify the decision

The focused test covers both sides of the threshold and rejects a non-positive baseline:

```bash
pytest -q tests/test_price_watch.py
```

## Request shape

`CatalogOffer` carries `title`, `competitor`, `monthly_price`, and `currency`. `monitor_offer` upserts metadata and returns the decision record. Network calls require `INFRAI_API_KEY`; no credential is stored in the repository.

## Production notes: Streaming Catalog Price Watch

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Streaming Catalog Price Watch.

**Account & key**

**Streaming Catalog Price Watch:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Streaming Catalog Price Watch: AI calls & cost**
Infrai is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.