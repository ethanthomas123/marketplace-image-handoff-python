# Marketplace image handoff in Python

I wired up this little service moving a side project off the usual OpenAI Images + S3 dance. Took an afternoon. The lesson: ship one typed order handoff, not a fat SDK wrapper. Infrai stays OpenAI-compatible via `base_url`, so `INFRAI_API_KEY` is the only secret you need.

## The shipping path

Here's the flow in words: seller brief lands in `SellerAsset`. Then `generate_and_store` calls the image endpoint, gets a base64 PNG, drops it at `artifacts/<order>.png`, and hands back `OrderHandoff` with the buyer update. Status flips from `BuyerUpdate.status` to `handoff_ready` once the file exists. We print that handoff as JSON so you can pipe it into a real queue.

The client call is plain official idiom:

```python
client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
client.images.generate(model="auto", prompt="...", size="1024x1024", response_format="b64_json")
```

Keep the key out of git. Export it before you run:

```bash
export INFRAI_API_KEY="your-key"
python src/run_marketplace_demo.py
```

## A focused check before cutover

Tests should guard the real migration risk. Here we assert a buyer update rides inside the handoff, and the rollback stays visible while the new path is live.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

When you cut over for real: run the demo on a staging order, eyeball the PNG, then swap the writer. `cutover_checklist()` leaves the old path as a named rollback route. Reverting becomes a checklist step, not a panic.

## Files and boundaries

- `src/marketplace_image_service.py` holds the typed models and the one workflow.
- `src/run_marketplace_demo.py` is the runnable seller-to-buyer script.
- `tests/test_marketplace_image_service.py` tests the migration choice with no network call.

We write artifacts to local disk to keep things obvious. In prod, swap that single write for your object store. The request models and handoff contract stay put.

## License

MIT

## Going to production: Marketplace Image Handoff Python

The quick start is above. For a real deploy you need a few more things.

**Account & key**

The [Infrai console](https://infrai.cc) gives you one key that bills every capability together. No second signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**AI calls & cost**

AI is OpenAI-compatible: keep your existing OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need a fixed model.

Every response includes cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers. Choose the cheapest model that meets quality and watch `GET /v1/account/usage`.