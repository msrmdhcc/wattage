# Klasifikasi Status Efisiensi & Pemborosan Emisi — Pabrik Baja DAEWOO

Aplikasi web Streamlit (Kelompok 18, mata kuliah Pembelajaran Mesin) untuk
mengklasifikasikan **status efisiensi** konsumsi energi pabrik baja ke dalam
4 kelas: **Efisien**, **Normal**, **Beban Kritis**, **Pemborosan Emisi**.

Aplikasi ini adalah **sistem pendukung keputusan** untuk manajer operasional.
Kelas "Pemborosan Emisi" **bukan** kerusakan atau anomali mesin — artinya
pemakaian listrik tinggi pada periode tarif ringan (peluang penjadwalan ulang
produksi).

---

## 1. Cara menjalankan di Windows

Semua perintah di bawah untuk **PowerShell / Command Prompt**.

> Catatan: di banyak instalasi Windows, `pip` tidak ada di PATH. Gunakan
> `python -m pip` seperti contoh di bawah.

### 1.1 Siapkan lingkungan (sekali saja)

```powershell
cd C:\Users\sabda\projekML
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Versi di `requirements.txt` di-pin persis sesuai environment pengujian
(streamlit 1.67.0, pandas 3.1.1, scikit-learn 1.9.1, xgboost 3.4.1,
joblib 1.6.0, plotly 7.1.0).

### 1.2 Siapkan model

Jika **model final dari tim** sudah tersedia, salin 3 file ke `model_output/`
(lihat bagian 4). Jika belum, buat model sementara:

```powershell
python scripts\buat_model_sementara.py
```

### 1.3 Jalankan aplikasi

```powershell
python -m streamlit run app.py
```

Browser akan terbuka di `http://localhost:8501`.

---

## 2. Struktur folder

```
projekML/
├─ app.py                       # aplikasi Streamlit (UI + pemuatan model)
├─ requirements.txt             # versi paket yang di-pin
├─ README.md                    # dokumen ini
├─ contoh_upload.csv            # 30 baris contoh untuk uji unggah CSV
├─ .streamlit/
│  └─ config.toml               # tema dasar Streamlit (Console · graphite)
├─ model_output/                # KOSONG — tempat model FINAL tim
│  └─ .gitkeep
├─ model_output_sementara/      # model placeholder (dibuat skrip sementara)
│  ├─ pipeline_pabrik.pkl
│  ├─ label_encoder.pkl
│  └─ urutan_fitur.pkl
├─ scripts/
│  ├─ buat_model_sementara.py   # latih model sementara
│  ├─ uji_model.py              # uji predict & predict_proba
│  ├─ uji_ui.py                 # uji UI + screenshot (Playwright)
│  ├─ uji_warna.py             # uji 4 warna kelas via CSV
│  ├─ uji_final.py              # uji jalur model final
│  ├─ uji_validasi.py           # uji validasi urutan fitur
│  └─ ekspor_css.py             # ekspor CSS untuk lint Hallmark
├─ X_train_pabrik.csv           # 26.161 × 9 fitur (Jan–Sep, data latih)
├─ y_train_pabrik.csv           # label data latih
├─ X_test_pabrik.csv            # 8.832 × 9 fitur (Okt–Des, data uji)
├─ y_test_pabrik.csv            # label data uji
├─ Steel_industry.csv           # data mentah (35.041 baris)
└─ Handover_Final_Kelompok18.md # dokumen proyek
```

---

## 3. Kontrak model (JANGAN diubah)

Aplikasi memuat model dengan aturan berikut:

- Folder **`model_output/`** dipakai jika ada; kalau tidak, aplikasi memakai
  **`model_output_sementara/`** dan menampilkan banner merah permanen
  **"MODEL SEMENTARA - bukan hasil final tim"**. Banner hilang otomatis saat
  model asli dipasang.
- Tiga file yang dimuat (melalui `joblib`):

  | File | Isi |
  |---|---|
  | `pipeline_pabrik.pkl` | **satu** objek sklearn `Pipeline` (preprocessing + model). Input = `DataFrame` mentah 9 kolom. Punya `predict` dan `predict_proba`. |
  | `label_encoder.pkl` | `sklearn.preprocessing.LabelEncoder` untuk target (nama kelas dari `inverse_transform` / `classes_`). |
  | `urutan_fitur.pkl` | `list` berisi 9 nama fitur, urutan persis. |

- **Tidak ada `scaler.pkl` terpisah.** Scaling (jika dipakai) harus sudah ada
  di dalam `pipeline_pabrik.pkl`.
- 9 fitur, urutan **PERSIS**:
  `Usage_kWh`, `Lagging_Current_Reactive_Power_kVarh`,
  `Leading_Current_Reactive_Power_kVarh`, `Lagging_Current_Power_Factor`,
  `Leading_Current_Power_Factor`, `NSM`, `WeekStatus`, `Day_Of_Week`,
  `Musim_Tarif`.
- `CO2(tCO2)`, `Load_Type`, dan `Date_Time` **tidak boleh** menjadi fitur
  (data leakage / sudah dipakai untuk split).
- Jika `urutan_fitur.pkl` tidak sama dengan 9 fitur di atas, aplikasi
  menampilkan **pesan error yang jelas** dan berhenti — bukan crash diam-diam.

---

## 4. Cara mengganti model (saat model final tiba)

1. Pastikan **versi `scikit-learn` dan `xgboost` pembuat model sama** dengan
   yang ada di `requirements.txt` (scikit-learn 1.9.1, xgboost 3.4.1). File
   `.pkl` bisa gagal dibuka bila versi berbeda.
2. Timpa **3 file** di `model_output/`:
   `pipeline_pabrik.pkl`, `label_encoder.pkl`, `urutan_fitur.pkl`.
   Nama file harus sama persis.
3. **Restart aplikasi** (hentikan dengan `Ctrl+C`, lalu jalankan ulang
   `python -m streamlit run app.py`).
4. `app.py` **tidak perlu diubah**.

### Peringatan ukuran file (GitHub)

Batas GitHub adalah **100 MB per file**. File `.pkl` model pohon bisa besar
(XGBoost/Random Forest dengan banyak pohon). Periksa ukuran sebelum push:

```powershell
Get-ChildItem model_output\*.pkl | Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,1)}}
```

Jika ada file mendekati/lebih dari 100 MB, gunakan Git LFS atau simpan model
di luar repositori (mis. rilis GitHub / Google Drive) dan sesuaikan cara
memuatnya.

### Checklist verifikasi setelah penggantian

- [ ] `python scripts\uji_model.py` → `urutan_fitur cocok kontrak: True`,
      `predict` dan `predict_proba` berjalan tanpa error.
- [ ] `python -m streamlit run app.py` → tanpa error di terminal.
- [ ] Banner merah "MODEL SEMENTARA" **hilang**; muncul
      "Model final dari tim pemodelan termuat (model_output/)".
- [ ] Prediksi manual satu baris menampilkan label + bar probabilitas.
- [ ] Unggah `contoh_upload.csv` → tabel hasil + ringkasan + tombol unduh.
- [ ] Coba CSV dengan kolom kurang → pesan "Kolom wajib yang kurang".
- [ ] Coba CSV dengan nilai kategori salah → pesan "Nilai tidak dikenal".
- [ ] Ukuran file `.pkl` di bawah 100 MB.

---

## 5. Fitur aplikasi

**Input manual**
- Tanggal (date picker) → menurunkan `Day_Of_Week` (daftar manual bahasa
  Inggris), `WeekStatus` (Sabtu/Minggu = Weekend), dan `Musim_Tarif`
  (Dingin: Nov–Feb; Panas: Jun–Agu; Peralihan: Mar–Mei & Sep–Okt).
- Jam & menit (kelipatan 15) → `NSM = jam×3600 + menit×60`.
- Slider: Usage 0–160 kWh, Lagging RP 0–100 kVarh, Leading RP 0–30 kVarh,
  Lagging PF 0–100 %, Leading PF 0–100 %.

**Output prediksi**
- Label kelas berwarna: hijau Efisien, biru Normal, oranye Beban Kritis,
  merah Pemborosan Emisi.
- Bar probabilitas per kelas dari `predict_proba`.
- Satu kalimat penjelasan arti kelas untuk manajer.
- Peringatan (bukan error) bila input di luar rentang data latih.

**Unggah CSV**
- Wajib punya 9 kolom di atas; nama kolom dan nilai kategori divalidasi
  **sebelum** diproses.
- Menampilkan tabel hasil, ringkasan jumlah per kelas, dan tombol unduh CSV.

---

## 6. Desain (Hallmark · Console)

Tampilan mengikuti tema **Console** dari katalog Hallmark (genre
modern-minimal), karena kata kuncinya persis alat ini: *operations,
monitoring, telemetry, instruments, data, record*. Console juga sudah
mendefinisikan empat sinyal status yang langsung dipetakan ke empat kelas:
`ok` (hijau), `cool` (biru), `accent` (amber), `bad` (merah).

- Dua colourway Console tersedia dan bisa ditukar dengan tombol
  **"Mode terang"** di bilah samping: `graphite` (gelap, default) dan
  `paper` (terang).
- Warna & font lewat token di blok `:root`; tidak ada `transition: all`;
  fokus keyboard terlihat; `overflow-x: clip`; kontras teks cukup di kedua
  mode; tanpa animasi berkedip; tanpa angka/fakta karangan.
- Deviations/waiver dicatat sebagai komentar di blok CSS `app.py` dan
  diverifikasi dengan `sloplint` Hallmark (lihat bagian 7).

Catatan: tombol mode menukar warna melalui CSS (variabel tema bawaan Streamlit
di-override). Bila rilis Streamlit di masa depan mengganti nama variabel
internalnya, tata warna widget bawaan bisa bergeser; permukaan kustom tetap
aman.

---

## 7. Pengujian

Jalankan server lebih dulu di satu terminal:

```powershell
python -m streamlit run app.py
```

Lalu di terminal lain:

```powershell
python scripts\uji_model.py       # kontrak predict/predict_proba + 3 skenario
python scripts\uji_ui.py          # UI + screenshot (butuh Playwright)
python scripts\uji_warna.py       # memicu keempat kelas via CSV
python scripts\uji_final.py       # jalur model final (banner hilang)
python scripts\uji_validasi.py    # validasi urutan fitur
```

Skrip UI memakai Playwright dengan channel `msedge` (Edge sudah terpasang di
Windows). Bila Playwright belum ada:

```powershell
python -m pip install playwright
```

Screenshot tersimpan di `shots/`.

---

## 8. Keterbatasan & catatan

- Model sementara (XGBoost cepat) **hanya** untuk menguji aplikasi. Angka
  apa pun darinya **bukan** hasil proyek.
- Data uji hanya 3 bulan (Okt–Des); kelas Pemborosan Emisi hanya ±3–4%.
- Metrik utama proyek: **Macro F1**.
- Split data berdasarkan waktu (Jan–Sep latih, Okt–Des uji). Split acak
  dilarang.
