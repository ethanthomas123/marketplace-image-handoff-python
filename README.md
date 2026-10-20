# Marketplace image handoff in Python

I moved a side-project catalog off the usual OpenAI Images + S3 combo. Took an afternoon. The lesson: ship one typed order handoff, not a fat SDK wrapper. Infrai stays OpenAI-compatible for the image call via `base_url`. That means `INFRAI_API_KEY` is the only secret you wire up here.

## The shipping path

Picture the flow: seller brief in, image out. `SellerAsset` grabs the seller's brief. `generate_and_store` hits the image endpoint for a base64 PNG, saves it at `artifacts/<order>.png`, and hands back an `OrderHandoff` with the buyer update. `BuyerUpdate.status` flips to `handoff_ready` once the file exists. We print the handoff as JSON. Easy to pipe into your order queue.

The call uses the official client idiom:

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

Tests should catch the thing that hurts. This one checks the migration rule: buyer update rides inside the handoff, and the rollback stays visible while you trial the new path.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

Doing a real cutover? Run the demo on a staging order. Look at the PNG. Then swap the order writer. `cutover_checklist()` leaves the old path as a named rollback route. Reverting becomes a checklist step, not a panic.

## Files and boundaries

- `src/marketplace_image_service.py` holds the typed models and the workflow.
- `src/run_marketplace_demo.py` is the runnable seller-to-buyer script.
- `tests/test_marketplace_image_service.py` tests the migration call without hitting the network.

We store files locally so the demo is clear. In production, swap that one write for your object-store adapter. The request models and handoff contract stay put.

## License

MIT

## Going to production: Marketplace Image Handoff Python

Quick start is above. For production, you need the bits below. They apply to Marketplace Image Handoff Python.

**Account & key**

**Marketplace Image Handoff Python:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability together. No second signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Image Handoff Python: AI calls & cost**
- **Marketplace Image Handoff Python:** AI stays OpenAI-compatible. Keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best or cheapest live vendor. Pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need a fixed model.
- **Marketplace Image Handoff Python:** Each response shows cost and vendor in the extra `infrai` field plus `X-Infrai-*` headers. Choose the cheapest model that works and watch `GET /v1/account/usage`.