"""Uji UI app.py dengan Playwright (memakai Edge yang sudah terpasang).

Menguji: prediksi manual, toggle mode terang/gelap, unggah CSV benar,
CSV kolom kurang, dan CSV nilai kategorikal salah. Menyimpan screenshot
desktop dan HP untuk mode gelap dan terang.

Server harus jalan di http://localhost:8501
Jalankan: python scripts/uji_ui.py
"""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "shots"
SHOTS.mkdir(exist_ok=True)
TMP = ROOT / "shots" / "_tmp"
TMP.mkdir(exist_ok=True)
URL = "http://localhost:8501"

DESKTOP = {"width": 1440, "height": 1600}
MOBILE = {"width": 390, "height": 1400}


def tunggu(page):
    page.wait_for_selector("h1", timeout=60000)
    page.wait_for_timeout(2500)


def isi_kurang():
    p = TMP / "kurang.csv"
    p.write_text(
        "Usage_kWh,Lagging_Current_Reactive_Power_kVarh,NSM,WeekStatus\n"
        "10,3,900,Weekday\n",
        encoding="utf-8",
    )
    return str(p)


def isi_salah_kategori():
    p = TMP / "salah.csv"
    p.write_text(
        "Usage_kWh,Lagging_Current_Reactive_Power_kVarh,"
        "Leading_Current_Reactive_Power_kVarh,Lagging_Current_Power_Factor,"
        "Leading_Current_Power_Factor,NSM,WeekStatus,Day_Of_Week,Musim_Tarif\n"
        "10,3,0,80,100,900,Kemarin,Blursday,Hujan\n",
        encoding="utf-8",
    )
    return str(p)


def upload(page, path, nama):
    inp = page.locator('input[type="file"]').first
    inp.set_input_files(path)
    page.wait_for_timeout(3500)


CHECK_JS = r"""
() => {
  const g = (sel, prop) => {
    const el = document.querySelector(sel);
    return el ? getComputedStyle(el)[prop] : null;
  };
  return {
    appBg: g('.stApp', 'backgroundColor'),
    labelColor: g('[data-testid="stWidgetLabel"] p', 'color'),
    h1Color: g('h1', 'color'),
    docScroll: document.documentElement.scrollWidth,
    docClient: document.documentElement.clientWidth,
  };
}
"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport=DESKTOP)
        page.goto(URL, wait_until="domcontentloaded")
        tunggu(page)
        print("TITLE:", page.title())
        print("DARK CHECK:", page.evaluate(CHECK_JS))

        # ---------- mode gelap (default) ----------
        simpan = lambda n, v: (page.set_viewport_size(v), page.wait_for_timeout(600),
                               page.screenshot(path=str(SHOTS / n), full_page=True),
                               print("saved", n))
        simpan("desktop_dark.png", DESKTOP)

        # prediksi manual (default: 2018-10-02, jam 9, usage 60)
        page.get_by_role("button", name="Prediksi status").click()
        page.wait_for_timeout(2500)
        simpan("desktop_dark_hasil.png", DESKTOP)
        simpan("mobile_dark.png", MOBILE)
        page.set_viewport_size(DESKTOP)

        # ---------- toggle ke mode terang ----------
        tog = page.get_by_test_id("stCheckbox").locator("label").first
        tog.click()
        page.wait_for_timeout(2500)
        print("LIGHT CHECK:", page.evaluate(CHECK_JS))
        simpan("desktop_light.png", DESKTOP)
        simpan("mobile_light.png", MOBILE)
        page.set_viewport_size(DESKTOP)

        # ---------- unggah CSV benar ----------
        upload(page, str(ROOT / "contoh_upload.csv"), "benar")
        simpan("desktop_light_upload.png", DESKTOP)
        body = page.inner_text("body")
        print("UPLOAD_BENAR OK:", "Ringkasan hasil" in body)

        # ---------- toggle kembali ke gelap, unggah lagi untuk screenshot gelap ----
        tog.click()
        page.wait_for_timeout(2000)
        upload(page, str(ROOT / "contoh_upload.csv"), "benar2")
        simpan("desktop_dark_upload.png", DESKTOP)

        # ---------- CSV kolom kurang ----------
        upload(page, isi_kurang(), "kurang")
        body = page.inner_text("body")
        print("KURANG_TERDETEKSI:", "Kolom wajib yang kurang" in body)
        simpan("desktop_dark_kurang.png", DESKTOP)

        # ---------- CSV nilai kategorikal salah ----------
        upload(page, isi_salah_kategori(), "salah")
        body = page.inner_text("body")
        print("KATEGORI_TERDETEKSI:", "Nilai tidak dikenal" in body)
        simpan("desktop_dark_salah.png", DESKTOP)

        browser.close()


if __name__ == "__main__":
    main()
