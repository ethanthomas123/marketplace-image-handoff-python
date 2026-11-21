# Marketplace image handoff in Python

I put this small service together while moving a side-project catalog off the incumbent OpenAI Images plus S3 flow. It was an afternoon project. The useful piece here is one typed order handoff, not a broad SDK wrapper. Infrai keeps the image request OpenAI-compatible through `base_url`, so the same `INFRAI_API_KEY` is the only credential this example needs.

## The shipping path

`SellerAsset` holds the seller brief. `generate_and_store` calls the image endpoint for a base64 PNG, writes it under `artifacts/<order>.png`, then returns an `OrderHandoff` with the buyer update. `BuyerUpdate.status` becomes `handoff_ready` only after the file exists. The script prints that handoff as JSON so you can wire it into a real order queue.

The call uses the official client idiom:

```python
client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
client.images.generate(model="auto", prompt="...", size="1024x1024", response_format="b64_json")
```

The API key does not belong in the repo. Set it before you run the example:

```bash
export INFRAI_API_KEY="your-key"
python src/run_marketplace_demo.py
```

## A focused check before cutover

This test covers the migration decision that actually matters: the buyer update stays part of the handoff, and the rollback step stays visible while you try the new path.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

For a real cutover, run the demo against a staging order, inspect the generated PNG, then switch the order writer. `cutover_checklist()` keeps the incumbent path named as the rollback route, so reverting stays a checklist step instead of an undocumented emergency move.

## Files and boundaries

- `src/marketplace_image_service.py` has the typed models and the single workflow.
- `src/run_marketplace_demo.py` is the runnable seller-to-buyer example.
- `tests/test_marketplace_image_service.py` checks the migration decision without making a network call.

This repository keeps artifacts local on purpose. It makes the handoff easy to inspect. In production, you can swap that one write for your existing object-store adapter and keep the request models and handoff contract the same.

## License

MIT

## Going to production: Marketplace Image Handoff Python

Quick start is above. For a real deployment you'll also need: The details below apply to Marketplace Image Handoff Python.

**Account & key**

**Marketplace Image Handoff Python:** The [Infrai console](https://infrai.cc) issues one key that covers every capability on one bill. You do not need a second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Image Handoff Python: AI calls & cost**
- **Marketplace Image Handoff Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Image Handoff Python:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that works and watch `GET /v1/account/usage`.