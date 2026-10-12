import json
from pathlib import Path

from marketplace_image_service import SellerAsset, generate_and_store


def main() -> None:
    asset = SellerAsset(
        seller_id="seller-17",
        product_name="Hand-thrown blue mug",
        visual_brief="on a clean studio table, soft daylight, three-quarter view",
    )
    handoff = generate_and_store(asset, order_id="order-1007", output_dir=Path("artifacts"))
    print(json.dumps(handoff.model_dump(), indent=2))


if __name__ == "__main__":
    main()

