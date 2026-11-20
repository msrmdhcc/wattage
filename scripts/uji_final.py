"""Uji jalur model final: banner merah hilang saat model_output/ terisi."""
from __future__ import annotations

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1200, "height": 900})
    pg.goto(URL, wait_until="domcontentloaded")
    pg.wait_for_selector("h1", timeout=60000)
    pg.wait_for_timeout(2500)
    body = pg.inner_text("body")
    print("BANNER_SEMENTARA_MUNCUL:", "MODEL SEMENTARA" in body)
    print("PESAN_MODEL_FINAL_MUNCUL:", "Model final dari tim pemodelan termuat" in body)
    b.close()
