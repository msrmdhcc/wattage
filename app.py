"""
app.py
======
Aplikasi web Streamlit - Kelompok 18
Klasifikasi Status Efisiensi & Pemborosan Emisi Pabrik Baja DAEWOO.

Framing: sistem pendukung keputusan (decision support system) untuk manajer
operasional. "Pemborosan Emisi" BUKAN kerusakan atau anomali mesin.

Kontrak model:
  - Dimuat dari model_output/ (model final tim). Jika kosong/tidak ada,
    dimuat dari model_output_sementara/ dan muncul banner merah permanen.
  - pipeline_pabrik.pkl : sklearn Pipeline (preprocessing + model),
                          input DataFrame mentah 9 kolom, punya predict &
                          predict_proba. Tidak ada scaler.pkl terpisah.
  - label_encoder.pkl   : LabelEncoder target.
  - urutan_fitur.pkl    : list 9 nama fitur (urutan persis).

Menukar model = menimpa 3 file di model_output/, lalu restart aplikasi.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Konstanta proyek
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DIR_FINAL = ROOT / "model_output"
DIR_SEMENTARA = ROOT / "model_output_sementara"

# 9 fitur, urutan PERSIS (kontrak proyek).
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

KOLOM_KATEGORIK = ["WeekStatus", "Day_Of_Week", "Musim_Tarif"]
NILAI_KATEGORIK = {
    "WeekStatus": ["Weekday", "Weekend"],
    "Day_Of_Week": [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    ],
    "Musim_Tarif": ["Dingin", "Panas", "Peralihan"],
}

# Daftar manual (BUKAN strftime("%A")) supaya tidak bergantung bahasa sistem.
HARI = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

NAMA_KELAS = ["Efisien", "Normal", "Beban Kritis", "Pemborosan Emisi"]

PENJELASAN_KELAS = {
    "Efisien": (
        "Pemakaian listrik rendah pada periode tarif ringan. Kondisi paling "
        "ideal: pabrik berjalan hemat saat tarif murah."
    ),
    "Normal": (
        "Pemakaian listrik menengah pada periode tarif menengah. Kondisi "
        "standar, tidak perlu tindakan khusus."
    ),
    "Beban Kritis": (
        "Pemakaian tinggi / periode tarif puncak. Perlu dipantau supaya tidak "
        "berlanjut menjadi pemborosan."
    ),
    "Pemborosan Emisi": (
        "Pemakaian listrik tinggi pada periode tarif ringan. Ini peluang "
        "penjadwalan ulang produksi, bukan kerusakan atau anomali mesin."
    ),
}

# Nama kelas -> token warna Console. Efisien=ok(hijau), Normal=cool(biru),
# Beban Kritis=accent(amber), Pemborosan Emisi=bad(merah).
KELAS_TOKEN = {
    "Efisien": "ok",
    "Normal": "cool",
    "Beban Kritis": "accent",
    "Pemborosan Emisi": "bad",
}

# ---------------------------------------------------------------------------
# Token tema Hallmark "Console" (dua colourway resmi: graphite & paper).
# Nilai oklch dari katalog tema dikonversi ke hex sRGB.
# ---------------------------------------------------------------------------
TOKENS = {
    "dark": {
        "paper": "#0d1013", "paper2": "#15191c", "paper3": "#06080b",
        "ink": "#eceff2", "ink2": "#c3c8cc", "muted": "#9da2a8",
        "rule": "#2d3135", "rule2": "#484e54",
        "accent": "#f7b83d", "accent_ink": "#1c0e00", "accent_soft": "#38280a",
        "cool": "#6ebcfc", "cool_soft": "#142e43",
        "ok": "#61cb7c", "ok_soft": "#162519",
        "bad": "#f66d67", "bad_soft": "#2f1a18",
    },
    "light": {
        "paper": "#faf8f4", "paper2": "#f1eee9", "paper3": "#e7e4df",
        "ink": "#17130f", "ink2": "#322d29", "muted": "#5a544f",
        "rule": "#d0cdc8", "rule2": "#aeaaa4",
        "accent": "#a15c00", "accent_ink": "#fdfcf8", "accent_soft": "#fae4cc",
        "cool": "#116bb5", "cool_soft": "#ddedff",
        "ok": "#067132", "ok_soft": "#d8efdc",
        "bad": "#ba2b2e", "bad_soft": "#ffe3df",
    },
}


def css(mode: str) -> str:
    """Mengembalikan satu blok CSS (Hallmark Console) untuk mode yang aktif.

    Palet ditulis ulang penuh per mode dan dipaksa dengan !important pada
    selector data-testid yang stabil, karena Streamlit mengompilasi warna
    .streamlit/config.toml menjadi kelas statis saat start.
    """
    t = TOKENS[mode]
    return f"""
/* Hallmark · theme: console · colourway: {"graphite" if mode == "dark" else "paper"} */
/* Hallmark · pre-emit critique: P4 H4 E4 S4 R4 V4 · weakest: S, ini alat utilitas; kekhususan datang dari angka mono dan empat sinyal status, bukan dari cangkangnya */
/* Hallmark · deviation: Console memakai amber untuk "orang" dan cool untuk "instrumen"; di sini amber & cool dipinjam sekali untuk status Beban Kritis (amber) dan Normal (cool) karena kelas harus terbaca sekejap. Warna primer tombol dibiarkan netral agar amber tetap berarti satu hal. */
@import url('https://fonts.googleapis.com/css2?family=Host+Grotesk:wght@400;500&family=Atkinson+Hyperlegible+Mono:wght@400;500&display=swap');

:root {{
  --color-paper: {t['paper']}; --color-paper-2: {t['paper2']}; --color-paper-3: {t['paper3']};
  --color-ink: {t['ink']}; --color-ink-2: {t['ink2']}; --color-muted: {t['muted']};
  --color-rule: {t['rule']}; --color-rule-2: {t['rule2']};
  --color-accent: {t['accent']}; --color-accent-ink: {t['accent_ink']}; --color-accent-soft: {t['accent_soft']};
  --color-cool: {t['cool']}; --color-cool-soft: {t['cool_soft']};
  --color-ok: {t['ok']}; --color-ok-soft: {t['ok_soft']};
  --color-bad: {t['bad']}; --color-bad-soft: {t['bad_soft']};
  --color-focus: {t['accent']};
  --font-display: "Host Grotesk", ui-sans-serif, system-ui, sans-serif;
  --font-body: var(--font-display);
  --font-outlier: "Atkinson Hyperlegible Mono", ui-monospace, monospace;
  --font-icon: "Material Symbols Rounded", "Material Symbols Outlined",
    "Material Icons";
  --radius-card: 10px; --radius-pill: 6px; --rule-hair: 1px;
}}

/* Jembatan ke variabel tema bawaan Streamlit. */
:root, .stApp, [data-testid="stAppViewContainer"] {{
  --background-color: var(--color-paper);
  --secondary-background-color: var(--color-paper-2);
  --text-color: var(--color-ink);
  --primary-color: var(--color-accent);
  --border-color: var(--color-rule);
  --font: var(--font-body);
  --font-mono: var(--font-outlier);
}}

html, body {{ overflow-x: clip; }}

/* Permukaan: satu ground, panel satu step di atasnya (Console). */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
  background: var(--color-paper) !important;
  color: var(--color-ink) !important;
  font-family: var(--font-body) !important;
}}
[data-testid="stHeader"], [data-testid="stToolbar"] {{
  background: var(--color-paper) !important;
  color: var(--color-ink) !important;
}}
[data-testid="stSidebar"] {{
  background: var(--color-paper-2) !important;
  border-right: var(--rule-hair) solid var(--color-rule) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--color-ink); }}

/* Teks: semua label, paragraf, caption memakai token ink. */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
.stApp p, .stApp li, .stApp label, .stApp span {{
  color: var(--color-ink);
}}
[data-testid="stCaptionContainer"] *, [data-testid="stCaptionContainer"] {{
  color: var(--color-muted) !important;
}}

/* Tipografi mengikuti Console: display Host Grotesk 500, angka mono. */
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
  font-family: var(--font-display) !important;
  font-weight: 500 !important;
  letter-spacing: -0.03em !important;
  line-height: 1.06 !important;
  color: var(--color-ink) !important;
  text-wrap: balance;
}}
.stApp h1 {{ font-size: clamp(1.6rem, 3vw, 2.2rem) !important; }}
.stApp h2 {{ font-size: clamp(1.2rem, 2vw, 1.5rem) !important; }}
.stApp h3 {{ font-size: 1.05rem !important; }}
.stApp p, .stApp li, .stApp label {{
  font-family: var(--font-body);
}}
/* Jangan menimpa font ikon: Material Symbols memakai ligatur teks.
   Biarkan elemen ikon memakai fontnya sendiri. */
[data-testid="stIconMaterial"], .material-symbols-rounded,
span[class*="material"], [data-testid="stExpanderToggleIcon"] {{
  font-family: var(--font-icon) !important;
}}

/* Panel hairlin seperti Console: permukaan dari satu bidang dipisah rule 1px. */
.hk-panel {{
  background: var(--color-paper-2);
  border: var(--rule-hair) solid var(--color-rule);
  border-radius: var(--radius-card);
  padding: 1rem 1.1rem;
}}
.hk-label {{
  font-family: var(--font-body);
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-muted);
  margin: 0 0 0.35rem 0;
}}
.hk-measured {{
  font-family: var(--font-outlier);
  font-size: 0.85rem;
  font-variant-numeric: tabular-nums slashed-zero;
  color: var(--color-ink-2);
}}

/* Chip status: satu makna per warna, terbaca sekejap. */
.hk-status {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  border: var(--rule-hair) solid var(--color-rule);
  border-left-width: 6px;
  border-radius: var(--radius-card);
  padding: 0.9rem 1.1rem;
  background: var(--color-paper-2);
}}
.hk-status .dot {{
  width: 10px; height: 10px; border-radius: 50%; flex: none;
  background: var(--color-muted);
}}
.hk-status .k {{
  font-family: var(--font-body);
  font-size: 0.78rem; font-weight: 500; color: var(--color-muted);
}}
.hk-status .v {{
  font-family: var(--font-display);
  font-weight: 500; font-size: 1.35rem; letter-spacing: -0.02em;
  color: var(--color-ink) !important;
}}

.hk-banner {{
  border: var(--rule-hair) solid var(--color-bad);
  border-left-width: 6px;
  border-radius: var(--radius-card);
  background: var(--color-bad-soft);
  color: var(--color-ink);
  padding: 0.8rem 1rem;
  margin-bottom: 1rem;
}}
.hk-banner strong {{ color: var(--color-bad) !important; }}
.hk-banner code {{
  font-family: var(--font-outlier);
  background: var(--color-paper-3);
  color: var(--color-ink) !important;
  padding: 0.05rem 0.3rem;
  border-radius: 4px;
}}

/* Fokus keyboard terlihat, instan (Floor Hallmark). */
.stApp *:focus-visible {{
  outline: 2px solid var(--color-focus) !important;
  outline-offset: 2px;
  transition: none !important;
}}

/* Permukaan peramban yang tidak kita gambar, tetap dari palet (F16). */
::selection {{ background: var(--color-accent-soft); color: var(--color-ink); }}
html {{ scrollbar-color: var(--color-rule-2) var(--color-paper); }}
.stApp *::-webkit-scrollbar {{ width: 10px; height: 10px; }}
.stApp *::-webkit-scrollbar-track {{ background: var(--color-paper); }}
.stApp *::-webkit-scrollbar-thumb {{
  background: var(--color-rule-2);
  border-radius: var(--radius-pill);
}}

/* Kontrol Streamlit mengikuti token Console.
   Peran berbeda dibedakan bentuknya (F7): aksi utama = fill ink (netral,
   agar amber tetap berarti satu hal: status Beban Kritis),
   unduh/sekunder = hairline keliling. */
.stButton > button {{
  border: none !important;
  border-radius: var(--radius-pill) !important;
  background: var(--color-ink) !important;
  color: var(--color-paper) !important;
  font-family: var(--font-body) !important;
  font-weight: 500 !important;
}}
.stButton > button p {{ color: var(--color-paper) !important; }}
.stButton > button:hover {{
  background: var(--color-ink) !important;
  filter: brightness(1.12);
}}
.stButton > button:active {{ filter: brightness(0.9); }}
[data-testid="stBaseButton-secondary"], .stDownloadButton > button {{
  border: var(--rule-hair) solid var(--color-rule-2) !important;
  border-radius: var(--radius-pill) !important;
  background: transparent !important;
  color: var(--color-ink) !important;
  font-family: var(--font-body) !important;
  font-weight: 500 !important;
}}
[data-testid="stBaseButton-secondary"] p, .stDownloadButton > button p {{
  color: var(--color-ink) !important;
}}
[data-testid="stBaseButton-secondary"]:hover, .stDownloadButton > button:hover {{
  border-color: var(--color-accent) !important;
}}
[data-testid="stBaseButton-secondary"]:hover p, .stDownloadButton > button:hover p {{
  color: var(--color-accent) !important;
}}
[data-testid="stBaseButton-secondary"]:active, .stDownloadButton > button:active {{
  background: var(--color-accent-soft) !important;
}}

/* Input & dropdown (react-aria pada Streamlit 1.67) mengikuti permukaan Console. */
[data-testid="stDateInputField"], [data-testid="stDateInputField"] > div,
.react-aria-DateField,
[data-testid="stSelectbox"] [data-rac][role="group"],
.react-aria-ComboBox {{
  background: var(--color-paper-3) !important;
  border: var(--rule-hair) solid var(--color-rule-2) !important;
  border-radius: var(--radius-pill) !important;
  color: var(--color-ink) !important;
}}
[data-testid="stDateInputField"] *, [data-testid="stSelectbox"] [data-rac][role="group"] *,
.react-aria-ComboBox * {{
  color: var(--color-ink) !important;
}}
[data-testid="stDateInputField"] input, [data-testid="stSelectbox"] input,
[data-testid="stDateInput"] input {{
  background: transparent !important;
  color: var(--color-ink) !important;
  font-family: var(--font-outlier) !important;
}}
[data-testid="stDateInputField"] svg, [data-testid="stSelectbox"] svg {{
  fill: var(--color-muted) !important;
}}

/* Popup dropdown (react-aria listbox). */
[role="listbox"], [role="menu"], [data-rac][role="listbox"] {{
  background: var(--color-paper-2) !important;
  border: var(--rule-hair) solid var(--color-rule) !important;
  color: var(--color-ink) !important;
}}
[role="option"], [role="menuitem"] {{
  background: var(--color-paper-2) !important;
  color: var(--color-ink) !important;
}}
[role="option"]:hover, [role="menuitem"]:hover,
[role="option"][aria-selected="true"] {{
  background: var(--color-accent-soft) !important;
  color: var(--color-ink) !important;
}}

/* Tombol sekunder (termasuk tombol Browse di file uploader). */
[data-testid="stBaseButton-secondary"] {{
  background: var(--color-paper-3) !important;
  border: var(--rule-hair) solid var(--color-rule-2) !important;
  color: var(--color-ink) !important;
}}
[data-testid="stBaseButton-secondary"] * {{ color: var(--color-ink) !important; }}
[data-testid="stBaseButton-secondary"]:hover {{ border-color: var(--color-accent) !important; }}

[data-testid="stFileUploaderDropzone"] {{
  background: var(--color-paper-2) !important;
  border: var(--rule-hair) dashed var(--color-rule-2) !important;
}}
[data-testid="stFileUploaderDropzone"] * {{ color: var(--color-ink) !important; }}

[data-testid="stDataFrame"], [data-testid="stTable"] {{
  border: var(--rule-hair) solid var(--color-rule) !important;
  border-radius: var(--radius-card);
}}

/* Alert bawaan Streamlit disesuaikan agar terbaca di kedua mode.
   Latar alert diwarnai dari token Console, teks tetap pada token ink. */
[data-testid="stAlertContainer"] {{
  color: var(--color-ink) !important;
  background: var(--color-paper-2) !important;
  border: var(--rule-hair) solid var(--color-rule) !important;
  border-left-width: 6px !important;
  border-radius: var(--radius-card) !important;
}}
[data-testid="stAlertContainer"] * {{ color: var(--color-ink) !important; }}
[data-testid="stAlertContainer"] code {{
  font-family: var(--font-outlier) !important;
  background: var(--color-paper-3) !important;
  color: var(--color-ink) !important;
}}
[data-testid="stAlertContainer"] a {{ color: var(--color-cool) !important; }}
/* Satu makna per warna, mengikuti empat token status Console. */
[data-testid="stAlertContentInfo"] {{ border-left-color: var(--color-cool) !important; }}
[data-testid="stAlertContentSuccess"] {{ border-left-color: var(--color-ok) !important; }}
[data-testid="stAlertContentWarning"] {{ border-left-color: var(--color-accent) !important; }}
[data-testid="stAlertContentError"] {{ border-left-color: var(--color-bad) !important; }}
[data-testid="stAlertContentInfo"] svg, [data-testid="stAlertContentSuccess"] svg,
[data-testid="stAlertContentWarning"] svg, [data-testid="stAlertContentError"] svg {{
  fill: var(--color-muted) !important;
}}

/* Chip berkas di file uploader (muncul setelah file dipilih). */
[data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFileName"],
[data-testid="stFileUploaderDropzone"] section {{
  background: var(--color-paper-3) !important;
  color: var(--color-ink) !important;
}}
[data-testid="stFileUploaderFile"] * ,
[data-testid="stFileUploaderFileName"] * {{ color: var(--color-ink) !important; }}
[data-testid="stFileUploaderDeleteBtn"] svg {{ fill: var(--color-ink) !important; }}

/* Badge inline (:code: / st.code) mengikuti permukaan Console. */
.stApp code, .usst-code {{
  font-family: var(--font-outlier) !important;
  background: var(--color-paper-3) !important;
  color: var(--color-ink) !important;
}}
"""


# ---------------------------------------------------------------------------
# Pemuatan model
# ---------------------------------------------------------------------------
def _baca_model(folder: Path):
    pipe = joblib.load(folder / "pipeline_pabrik.pkl")
    le = joblib.load(folder / "label_encoder.pkl")
    fitur = list(joblib.load(folder / "urutan_fitur.pkl"))
    return pipe, le, fitur


@st.cache_resource(show_spinner=False)
def muat_model():
    """Memuat model. Prioritas model_output/, lalu model_output_sementara/.

    Mengembalikan dict: pipe, le, fitur, sumber ('final'|'sementara'), folder.
    Jika urutan fitur tidak sesuai kontrak -> fitur_valid=False + pesan.
    """
    for sumber, folder in (("final", DIR_FINAL), ("sementara", DIR_SEMENTARA)):
        punya = all(
            (folder / f).exists()
            for f in ("pipeline_pabrik.pkl", "label_encoder.pkl", "urutan_fitur.pkl")
        )
        if not punya:
            continue
        pipe, le, fitur = _baca_model(folder)
        hasil = {
            "pipe": pipe, "le": le, "fitur": fitur,
            "sumber": sumber, "folder": folder,
            "fitur_valid": fitur == FITUR_WAJIB,
        }
        return hasil
    return None


@st.cache_data(show_spinner=False)
def rentang_latih():
    """Rentang nilai fitur dari data latih, untuk peringatan input di luar wajar."""
    p = ROOT / "X_train_pabrik.csv"
    if not p.exists():
        return None
    X = pd.read_csv(p)
    out = {}
    for k in FITUR_WAJIB:
        if k in KOLOM_KATEGORIK:
            out[k] = sorted(X[k].astype(str).unique().tolist())
        else:
            out[k] = (float(X[k].min()), float(X[k].max()))
    return out


def musim_dari_bulan(bulan: int) -> str:
    if bulan in (11, 12, 1, 2):
        return "Dingin"
    if bulan in (6, 7, 8):
        return "Panas"
    return "Peralihan"


# ---------------------------------------------------------------------------
# Halaman
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Status Efisiensi Energi Pabrik Baja",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Mode: colourway awal = graphite (gelap, default tema Console),
# bisa ditukar ke paper (terang) lewat tombol. Nilai ini persisten
# selama sesi berjalan.
if "mode" not in st.session_state:
    st.session_state["mode"] = "dark"

with st.sidebar:
    terang = st.toggle("Mode terang", value=st.session_state["mode"] == "light")
    st.session_state["mode"] = "light" if terang else "dark"

MODE = st.session_state["mode"]
T = TOKENS[MODE]

# Injeksi CSS tema (mengikuti warna mode yang aktif).
st.markdown(f"<style>{css(MODE)}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Judul + status model
# ---------------------------------------------------------------------------
st.title("Status Efisiensi & Pemborosan Emisi - Pabrik Baja DAEWOO")
st.caption(
    "Sistem pendukung keputusan untuk manajer operasional. Masukkan parameter "
    "kelistrikan dan waktu, lalu baca status efisiensinya."
)

model = muat_model()

if model is None:
    st.error(
        "Model belum tersedia. Folder `model_output/` dan `model_output_sementara/` "
        "sama-sama kosong atau tidak berisi 3 file yang diminta "
        "(`pipeline_pabrik.pkl`, `label_encoder.pkl`, `urutan_fitur.pkl`).\n\n"
        "Jalankan dulu (Windows): `python scripts/buat_model_sementara.py`"
    )
    st.stop()

if not model["fitur_valid"]:
    st.error(
        "**Urutan/nama fitur tidak sesuai kontrak.** Aplikasi tidak dijalankan "
        "supaya tidak ada prediksi yang salah.\n\n"
        f"- Dibaca dari `{model['folder'].name}/urutan_fitur.pkl`: `{model['fitur']}`\n"
        f"- Seharusnya (9 fitur, urutan persis): `{FITUR_WAJIB}`\n\n"
        "Perbaiki `urutan_fitur.pkl` pada model, lalu restart aplikasi."
    )
    st.stop()

if model["sumber"] == "sementara":
    st.markdown(
        '<div class="hk-banner"><strong>MODEL SEMENTARA</strong> - bukan hasil '
        "final tim. Aplikasi ini sedang memakai model placeholder di "
        "<code>model_output_sementara/</code>. Banner ini hilang otomatis saat "
        "model asli dipasang di <code>model_output/</code>.</div>",
        unsafe_allow_html=True,
    )
else:
    st.success("Model final dari tim pemodelan termuat (model_output/).")

pipe = model["pipe"]
le = model["le"]
FITUR = model["fitur"]

REntang = rentang_latih()

st.divider()

# ---------------------------------------------------------------------------
# Input manual (kiri) + hasil (kanan)
# ---------------------------------------------------------------------------
kiri, kanan = st.columns([1, 1.15], gap="large")

with kiri:
    st.subheader("Input parameter")
    st.caption(
        "Tanggal menentukan hari dan musim tarif. Jam dalam kelipatan 15 menit."
    )

    tanggal = st.date_input("Tanggal", value=dt.date(2018, 10, 2))
    c1, c2 = st.columns(2)
    with c1:
        jam = st.selectbox("Jam", list(range(24)), index=9)
    with c2:
        menit = st.selectbox("Menit", [0, 15, 30, 45], index=0)

    usage = st.slider("Usage (kWh)", 0.0, 160.0, 60.0, 0.1)
    lag_rp = st.slider("Lagging Reactive Power (kVarh)", 0.0, 100.0, 20.0, 0.1)
    lead_rp = st.slider("Leading Reactive Power (kVarh)", 0.0, 30.0, 0.0, 0.1)
    lag_pf = st.slider("Lagging Power Factor (%)", 0.0, 100.0, 85.0, 0.1)
    lead_pf = st.slider("Leading Power Factor (%)", 0.0, 100.0, 100.0, 0.1)

    tombol = st.button("Prediksi status", type="primary", width="stretch")

    # Peringatan (bukan error) untuk input di luar rentang data latih.
    if REntang is not None:
        cek = {
            "Usage_kWh": usage, "Lagging_Current_Reactive_Power_kVarh": lag_rp,
            "Leading_Current_Reactive_Power_kVarh": lead_rp,
            "Lagging_Current_Power_Factor": lag_pf,
            "Leading_Current_Power_Factor": lead_pf,
        }
        luar = []
        for k, v in cek.items():
            mn, mx = REntang[k]
            if v < mn or v > mx:
                luar.append(f"{k} ({v:g} di luar {mn:g}–{mx:g})")
        if luar:
            st.warning(
                "Nilai di luar rentang data latih (prediksi tetap dihitung, "
                "tetapi hasilnya kurang dapat diandalkan): " + "; ".join(luar)
            )

with kanan:
    st.subheader("Hasil prediksi")
    if not tombol:
        st.info("Isi parameter di kiri, lalu tekan **Prediksi status**.")
    else:
        hari = HARI[tanggal.weekday()]
        baris = {
            "Usage_kWh": float(usage),
            "Lagging_Current_Reactive_Power_kVarh": float(lag_rp),
            "Leading_Current_Reactive_Power_kVarh": float(lead_rp),
            "Lagging_Current_Power_Factor": float(lag_pf),
            "Leading_Current_Power_Factor": float(lead_pf),
            "NSM": jam * 3600 + menit * 60,
            "WeekStatus": "Weekend" if tanggal.weekday() >= 5 else "Weekday",
            "Day_Of_Week": hari,
            "Musim_Tarif": musim_dari_bulan(tanggal.month),
        }
        X = pd.DataFrame([baris])[FITUR]
        kode = pipe.predict(X)
        kelas = str(le.inverse_transform(kode)[0])
        proba = pipe.predict_proba(X)[0]
        kelas_list = [str(c) for c in le.classes_]

        token = KELAS_TOKEN.get(kelas, "muted")
        st.markdown(
            f'<div class="hk-status" style="border-left-color: var(--color-{token});">'
            f'<span class="dot" style="background: var(--color-{token});"></span>'
            f"<span><div class=\"k\">Status efisiensi</div>"
            f'<div class="v">{kelas}</div></span></div>',
            unsafe_allow_html=True,
        )

        # Probabilitas per kelas sebagai bar horizontal (2-5 nilai -> bar).
        fig = go.Figure(
            go.Bar(
                x=[float(p) for p in proba],
                y=kelas_list,
                orientation="h",
                marker_color=[T[KELAS_TOKEN.get(k, "muted")] for k in kelas_list],
                text=[f"{float(p) * 100:.1f}%" for p in proba],
                textposition="outside",
                hovertemplate="%{y}: %{x:.3f}<extra></extra>",
            )
        )
        fig.update_layout(
            height=230,
            margin=dict(l=10, r=40, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Host Grotesk, sans-serif", color=T["ink"], size=13),
            showlegend=False,
            bargap=0.35,
            xaxis=dict(
                range=[0, 1], tickformat=".0%",
                gridcolor=T["rule"], zeroline=False, color=T["muted"],
            ),
            yaxis=dict(color=T["ink"], autorange="reversed"),
            transition=dict(duration=0),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        st.markdown(
            f'<div class="hk-panel"><div class="hk-label">Arti status</div>'
            f'<div>{PENJELASAN_KELAS.get(kelas, "")}</div>'
            f'<div class="hk-measured" style="margin-top:0.6rem;">'
            f"{hari}, {jam:02d}:{menit:02d} &middot; NSM {jam * 3600 + menit * 60} "
            f"&middot; musim {baris['Musim_Tarif']}</div></div>",
            unsafe_allow_html=True,
        )

st.divider()

# ---------------------------------------------------------------------------
# Prediksi banyak baris lewat CSV
# ---------------------------------------------------------------------------
st.subheader("Prediksi banyak baris (unggah CSV)")
st.caption(
    "CSV wajib punya 9 kolom fitur dengan nama persis. Contoh berkas: "
    "`contoh_upload.csv`."
)

with open(ROOT / "contoh_upload.csv", "rb") as f:
    contoh_bytes = f.read()

st.download_button(
    "Unduh contoh_upload.csv",
    data=contoh_bytes,
    file_name="contoh_upload.csv",
    mime="text/csv",
)

berkas = st.file_uploader("Unggah CSV", type=["csv"])

if berkas is not None:
    try:
        df_unggah = pd.read_csv(berkas)
    except Exception as e:  # noqa: BLE001 - tampilkan pesan jelas, jangan crash
        df_unggah = None
        st.error(f"CSV tidak bisa dibaca: {e}")

    if df_unggah is not None:
        kolom = list(df_unggah.columns)
        kurang = [k for k in FITUR_WAJIB if k not in kolom]
        ekstra = [k for k in kolom if k not in FITUR_WAJIB]
        salah_nilai = {}
        for k in KOLOM_KATEGORIK:
            if k in kolom:
                salah = sorted(
                    set(df_unggah[k].astype(str).unique()) - set(NILAI_KATEGORIK[k])
                )
                if salah:
                    salah_nilai[k] = salah

        if kurang or salah_nilai:
            pesan = ["**CSV tidak diproses.** Perbaiki dulu:"]
            if kurang:
                pesan.append(f"- Kolom wajib yang kurang: `{kurang}`")
            for k, v in salah_nilai.items():
                pesan.append(
                    f"- Nilai tidak dikenal di kolom `{k}`: `{v}` "
                    f"(boleh: `{NILAI_KATEGORIK[k]}`)"
                )
            if ekstra:
                pesan.append(
                    f"- Catatan: kolom tambahan diabaikan: `{ekstra}`"
                )
            pesan.append(f"- Kolom yang dibutuhkan (9): `{FITUR_WAJIB}`")
            st.error("\n".join(pesan))
        else:
            if ekstra:
                st.warning(f"Kolom tambahan diabaikan: `{ekstra}`")
            X_unggah = df_unggah[FITUR_WAJIB].copy()
            try:
                kode = pipe.predict(X_unggah)
                hasil = df_unggah.copy()
                hasil["Prediksi_Status_Efisiensi"] = le.inverse_transform(kode)
                proba = pipe.predict_proba(X_unggah)
                for i, c in enumerate([str(c) for c in le.classes_]):
                    hasil[f"Prob_{c}"] = proba[:, i]
            except Exception as e:  # noqa: BLE001
                st.error(f"Prediksi gagal: {e}")
                hasil = None

            if hasil is not None:
                # Ringkasan jumlah per kelas (urutan kelas tetap).
                hitung = hasil["Prediksi_Status_Efisiensi"].value_counts()
                ringkas = pd.DataFrame(
                    {
                        "Status": NAMA_KELAS,
                        "Jumlah": [int(hitung.get(k, 0)) for k in NAMA_KELAS],
                    }
                )
                ringkas["Persen"] = (
                    ringkas["Jumlah"] / max(len(hasil), 1) * 100
                ).round(1)

                st.markdown("**Ringkasan hasil**")
                st.dataframe(ringkas, width="stretch", hide_index=True)

                st.markdown("**Tabel hasil per baris**")
                st.dataframe(hasil, width="stretch", hide_index=True)

                st.download_button(
                    "Unduh hasil sebagai CSV",
                    data=hasil.to_csv(index=False).encode("utf-8"),
                    file_name="hasil_prediksi_pabrik.csv",
                    mime="text/csv",
                )
