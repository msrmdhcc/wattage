"""
buat_model_sementara.py
=======================
Melatih model SEMENTARA (placeholder) supaya aplikasi Streamlit bisa dijalankan
dan diuji SEBELUM model final dari anggota tim pemodelan tersedia.

PENTING: model ini BUKAN hasil final tim. Angka apa pun yang dicetak skrip ini
bukan hasil proyek dan tidak boleh dilaporkan sebagai hasil proyek.

Kontrak keluaran (nama file sama persis dengan yang nanti dipakai model final,
hanya beda folder: model_output_sementara/ bukan model_output/):
  - pipeline_pabrik.pkl : satu objek sklearn Pipeline (preprocessing + model).
                          Input = DataFrame mentah 9 kolom, punya predict &
                          predict_proba. Tidak ada scaler.pkl terpisah.
  - label_encoder.pkl   : sklearn.preprocessing.LabelEncoder untuk target.
  - urutan_fitur.pkl    : list berisi 9 nama fitur, urutan persis.

Menukar model nanti = menimpa 3 file ini di model_output/. app.py tidak diubah.

Jalankan (dari folder proyek):
    python scripts/buat_model_sementara.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

# --- Lokasi file -------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model_output_sementara"

# --- Definisi kolom ----------------------------------------------------------
TARGET = "Status_Efisiensi"
KOLOM_KATEGORIK = ["WeekStatus", "Day_Of_Week", "Musim_Tarif"]

# 9 fitur, urutan persis (dipakai juga oleh app.py untuk validasi)
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


def main() -> None:
    print("Membaca 4 CSV siap pakai...")
    X_train = pd.read_csv(ROOT / "X_train_pabrik.csv")
    y_train = pd.read_csv(ROOT / "y_train_pabrik.csv")[TARGET]
    X_test = pd.read_csv(ROOT / "X_test_pabrik.csv")
    y_test = pd.read_csv(ROOT / "y_test_pabrik.csv")[TARGET]

    fitur = list(X_train.columns)
    if fitur != FITUR_WAJIB:
        raise SystemExit(
            "Urutan/nama kolom X_train_pabrik.csv tidak sesuai 9 fitur yang "
            f"diharapkan.\nDidapat: {fitur}\nDiharapkan: {FITUR_WAJIB}"
        )
    print("Fitur (urutan persis):", fitur)
    print("Jumlah latih/uji:", len(X_train), "/", len(X_test))

    # Label target -> angka. classes_ urut alfabetis:
    # Beban Kritis, Efisien, Normal, Pemborosan Emisi
    le = LabelEncoder().fit(y_train)
    y_train_enc = le.transform(y_train)
    print("Kelas (label_encoder.classes_):", list(le.classes_))

    # Preprocessing: one-hot untuk kategorikal, angka dibiarkan apa adanya.
    # Dilakukan DI DALAM pipeline supaya input aplikasi diproses sama persis.
    pre = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                KOLOM_KATEGORIK,
            )
        ],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        tree_method="hist",
        n_jobs=-1,
        random_state=42,
        eval_metric="mlogloss",
    )

    pipe = Pipeline([("pre", pre), ("model", model)])

    # XGBoost tidak punya class_weight; bobot kelas diberikan lewat sample_weight.
    sample_weight = compute_sample_weight("balanced", y_train_enc)
    print("Melatih model sementara (XGBoost + sample_weight balanced)...")
    pipe.fit(X_train, y_train_enc, model__sample_weight=sample_weight)

    # --- Sanity check SEMENTARA (bukan hasil proyek) ------------------------
    pred_test = pipe.predict(X_test)
    macro_f1 = f1_score(le.transform(y_test), pred_test, average="macro")
    print(
        "SANITY CHECK model sementara (BUKAN hasil proyek) "
        f"macro-F1 uji = {macro_f1:.4f}"
    )

    # --- Simpan --------------------------------------------------------------
    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, OUT / "pipeline_pabrik.pkl")
    joblib.dump(le, OUT / "label_encoder.pkl")
    joblib.dump(fitur, OUT / "urutan_fitur.pkl")
    print("Tersimpan di:", OUT)
    print("MODEL SEMENTARA - bukan hasil final tim.")


if __name__ == "__main__":
    main()
