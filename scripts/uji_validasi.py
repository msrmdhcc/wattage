"""Uji validasi urutan fitur: pesan error jelas, aplikasi tidak crash."""
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
    print("PESAN_FITUR_SALAH:", "Urutan/nama fitur tidak sesuai kontrak" in body)
    print("HALAMAN_MASIH_HIDUP (judul ada):", "Status Efisiensi" in body)
    b.close()
