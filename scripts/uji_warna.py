"""Uji empat warna status lewat jalur CSV (deterministik).
Membuat CSV 4 baris yang memicu keempat kelas, mengunggahnya, lalu
memeriksa tabel ringkasan dan menyimpan screenshot.

Server harus jalan di http://localhost:8501
Jalankan: python scripts/uji_warna.py
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "shots"
TMP = ROOT / "shots" / "_tmp"
TMP.mkdir(parents=True, exist_ok=True)
URL = "http://localhost:8501"

# Baris dengan kombinasi yang memicu keempat kelas (berdasarkan aturan target).
BARIS = [
    # Efisien: tarif ringan (jam 03) + usage rendah
    dict(Usage_kWh=4.0, LagR=3.0, NSM=3 * 3600, WeekStatus="Weekday",
         Day_Of_Week="Tuesday", Musim_Tarif="Panas"),
    # Normal: tarif menengah (jam 13) + usage rendah
    dict(Usage_kWh=5.0, LagR=4.0, NSM=13 * 3600, WeekStatus="Weekday",
         Day_Of_Week="Tuesday", Musim_Tarif="Panas"),
    # Beban Kritis: tarif puncak (jam 11) + usage tinggi
    dict(Usage_kWh=60.0, LagR=20.0, NSM=11 * 3600, WeekStatus="Weekday",
         Day_Of_Week="Tuesday", Musim_Tarif="Panas"),
    # Pemborosan Emisi: tarif ringan (jam 08) + usage tinggi
    dict(Usage_kWh=60.0, LagR=20.0, NSM=8 * 3600, WeekStatus="Weekday",
         Day_Of_Week="Tuesday", Musim_Tarif="Panas"),
]


def buat_csv() -> Path:
    df = pd.DataFrame(
        [
            {
                "Usage_kWh": r["Usage_kWh"],
                "Lagging_Current_Reactive_Power_kVarh": r["LagR"],
                "Leading_Current_Reactive_Power_kVarh": 0.0,
                "Lagging_Current_Power_Factor": 85.0,
                "Leading_Current_Power_Factor": 100.0,
                "NSM": r["NSM"],
                "WeekStatus": r["WeekStatus"],
                "Day_Of_Week": r["Day_Of_Week"],
                "Musim_Tarif": r["Musim_Tarif"],
            }
            for r in BARIS
        ]
    )
    p = TMP / "empat_kelas.csv"
    df.to_csv(p, index=False)
    return p


def main():
    p = buat_csv()
    # Prediksi langsung dengan model untuk tahu kelas yang sebenarnya dihasilkan.
    folder = ROOT / "model_output"
    if not (folder / "pipeline_pabrik.pkl").exists():
        folder = ROOT / "model_output_sementara"
    pipe = joblib.load(folder / "pipeline_pabrik.pkl")
    le = joblib.load(folder / "label_encoder.pkl")
    fitur = list(joblib.load(folder / "urutan_fitur.pkl"))
    X = pd.read_csv(p)
    pred = le.inverse_transform(pipe.predict(X[fitur]))
    print("Kelas hasil model untuk 4 baris:", list(pred))

    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        pg = b.new_page(viewport={"width": 1200, "height": 1400})
        pg.goto(URL, wait_until="domcontentloaded")
        pg.wait_for_selector("h1", timeout=60000)
        pg.wait_for_timeout(2500)
        pg.locator('input[type="file"]').first.set_input_files(str(p))
        pg.wait_for_timeout(4000)
        body = pg.inner_text("body")
        print("Tabel ringkasan muncul:", "Ringkasan hasil" in body)
        pg.screenshot(path=str(SHOTS / "desktop_empat_kelas.png"), full_page=True)
        p.unlink(missing_ok=True)
        b.close()


if __name__ == "__main__":
    main()
