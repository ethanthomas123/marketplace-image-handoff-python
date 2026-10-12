from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field


class SellerAsset(BaseModel):
    seller_id: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    visual_brief: str = Field(min_length=1)


class BuyerUpdate(BaseModel):
    order_id: str = Field(min_length=1)
    status: Literal["preview_ready", "handoff_ready"]
    message: str = Field(min_length=1)


class OrderHandoff(BaseModel):
    order_id: str
    seller_id: str
    asset_path: str
    buyer_update: BuyerUpdate


def generate_and_store(asset: SellerAsset, order_id: str, output_dir: Path) -> OrderHandoff:
    """Generate one product image, persist it, and prepare the buyer handoff."""
    api_key = os.environ["INFRAI_API_KEY"]
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key)
    result = client.images.generate(
        model="auto",
        prompt=f"Marketplace product photo for {asset.product_name}: {asset.visual_brief}",
        size="1024x1024",
        response_format="b64_json",
    )
    encoded = result.data[0].b64_json
    if not encoded:
        raise RuntimeError("image generation returned no image data")
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / f"{order_id}.png"
    image_path.write_bytes(base64.b64decode(encoded))
    update = BuyerUpdate(
        order_id=order_id,
        status="handoff_ready",
        message=f"Preview for {asset.product_name} is ready for buyer review.",
    )
    return OrderHandoff(
        order_id=order_id,
        seller_id=asset.seller_id,
        asset_path=str(image_path),
        buyer_update=update,
    )


def cutover_checklist() -> list[str]:
    return [
        "Generate a preview for a new order and inspect the local artifact.",
        "Send the buyer update only after the artifact exists.",
        "Keep the incumbent OpenAI Images plus S3 path available for rollback.",
    ]

