from pathlib import Path

from marketplace_image_service import SellerAsset, cutover_checklist


def test_cutover_keeps_rollback_path_visible() -> None:
    asset = SellerAsset(seller_id="s-1", product_name="Lamp", visual_brief="white background")
    steps = cutover_checklist()
    assert asset.product_name == "Lamp"
    assert any("rollback" in step.lower() for step in steps)
    assert any("buyer update" in step.lower() for step in steps)

