"""Uji kontrak model: predict & predict_proba dengan DataFrame 9 kolom.

Jalankan: python scripts/uji_model.py
Tidak dipakai aplikasi; hanya untuk verifikasi.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

FITUR_WAJIB = [
    "Usage_kWh",
    "Lagging_Current_Reactive_Power_kVarh",
    "Leading_Current_Reactive_Power_kVarh",
    "Lagging_Current_Power_Factor",
    "Leading_Current_Power_Factor",
    "NSM",
    "WeekStatus",
    "Day_Of_Week",
    "Musim_Tarif",
]

folder = ROOT / "model_output"
if not (folder / "pipeline_pabrik.pkl").exists():
    folder = ROOT / "model_output_sementara"
print("Folder model:", folder.relative_to(ROOT))

pipe = joblib.load(folder / "pipeline_pabrik.pkl")
le = joblib.load(folder / "label_encoder.pkl")
fitur = list(joblib.load(folder / "urutan_fitur.pkl"))

print("urutan_fitur cocok kontrak:", fitur == FITUR_WAJIB)
print("classes_:", list(le.classes_))

X_test = pd.read_csv(ROOT / "X_test_pabrik.csv")
y_test = pd.read_csv(ROOT / "y_test_pabrik.csv")["Status_Efisiensi"]

# predict + predict_proba dengan DataFrame 9 kolom
kode = pipe.predict(X_test)
proba = pipe.predict_proba(X_test)
nama = le.inverse_transform(kode)

print("predict -> array kelas label:", nama[:5].tolist())
print("predict shape:", np.asarray(kode).shape)
print("predict_proba shape:", proba.shape)
print("jumlah baris proba == jumlah kelas per baris:", proba.shape[1] == len(le.classes_))

# skenario manual wajib
HARI = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def musim(bulan):
    if bulan in (11, 12, 1, 2):
        return "Dingin"
    if bulan in (6, 7, 8):
        return "Panas"
    return "Peralihan"


skenario = [
    ("Selasa, Juli, 11.00, 60 kWh", 6, 11, 0, 60.0),
    ("Selasa, Juli, 03.00, 3.5 kWh", 6, 3, 0, 3.5),
    ("Selasa, Juli, 08.30, 60 kWh", 6, 8, 30, 60.0),
]

print("\n--- Skenario manual (Selasa) ---")
for label, bulan, jam, menit, usage in skenario:
    baris = {
        "Usage_kWh": usage,
        "Lagging_Current_Reactive_Power_kVarh": usage * 0.33,
        "Leading_Current_Reactive_Power_kVarh": 0.0,
        "Lagging_Current_Power_Factor": 85.0,
        "Leading_Current_Power_Factor": 100.0,
        "NSM": jam * 3600 + menit * 60,
        "WeekStatus": "Weekday",
        "Day_Of_Week": "Tuesday",
        "Musim_Tarif": musim(bulan),
    }
    X = pd.DataFrame([baris])[fitur]
    p = le.inverse_transform(pipe.predict(X))[0]
    pr = pipe.predict_proba(X)[0]
    print(f"{label}: -> {p}  (proba max {pr.max():.3f})")
