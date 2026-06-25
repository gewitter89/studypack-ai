import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pdf.renderer import _WatermarkCanvas

def test_watermark_canvas_modes():
    # Test standard demo mode (subtle watermark)
    wc = _WatermarkCanvas(watermark="Демо-набір", is_commercial=False)
    assert not wc.is_commercial
    assert wc.watermark == "Демо-набір"

    # Test commercial mode (no watermark)
    wc_comm = _WatermarkCanvas(watermark="", is_commercial=True)
    assert wc_comm.is_commercial
    assert not wc_comm.watermark

    # Test internal demo mode (large rotated watermark)
    wc_internal = _WatermarkCanvas(watermark="internal_demo", is_commercial=False)
    assert not wc_internal.is_commercial
    assert wc_internal.watermark == "internal_demo"
