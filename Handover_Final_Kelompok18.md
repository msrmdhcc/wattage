# HANDOVER LENGKAP PROYEK MACHINE LEARNING – KELOMPOK 18

## Klasifikasi Status Efisiensi dan Pemborosan Emisi Industri Baja Berdasarkan Parameter Kelistrikan dan Waktu Operasional (Random Forest vs SVM vs XGBoost)

> Dokumen ini ditulis untuk orang yang **belum tahu apa pun** tentang proyek ini. Setelah membaca dari awal sampai akhir, kamu seharusnya bisa: (1) menjelaskan proyek ini ke dosen, (2) menjalankan ulang semua kode, dan (3) melanjutkan bagian yang belum selesai.
>
> Dokumen ini **menggantikan** `Handover_Preprocessing_EDA.md` dan `Handover Notes Proyek ML.pdf`. Kalau ada yang bertentangan, ikuti dokumen ini. Semua angka di sini sudah dicek ulang dengan menjalankan kode pada data asli.

---

## DAFTAR ISI

1. Cara membaca dokumen ini
2. Proyek ini dalam bahasa sehari-hari
3. Konteks tugas kuliah (aturan, nilai, anggota)
4. Kamus istilah (listrik dan machine learning)
5. Dataset: dari mana, isinya apa, kolom per kolom
6. Isi folder proyek: file apa saja dan gunanya
7. Menyiapkan komputer dan menjalankan kode
8. Alur notebook preprocessing, langkah demi langkah
9. Target `Status_Efisiensi`: cara dibuat dan artinya
10. Temuan penting tentang data (wajib paham)
11. EDA: penjelasan tiap grafik
12. Keputusan preprocessing dan alasannya
13. Pembagian data latih dan uji
14. Tahap pemodelan (Mahasiswa 2)
15. Tahap aplikasi (Mahasiswa 3)
16. Status proyek dan checklist yang belum selesai
17. Kesalahan di dokumen lama yang sudah diperbaiki
18. Larangan (hal yang tidak boleh dilakukan)
19. Persiapan tanya jawab (pertanyaan yang mungkin muncul)
20. Referensi

---

## 1. Cara membaca dokumen ini

- **Baru pertama kali?** Baca Bagian 2, 4, 5, 9, dan 10 dulu. Itu inti pemahaman proyek.
- **Mau menjalankan kode?** Langsung ke Bagian 7, 8, dan 14.
- **Kamu Mahasiswa 2 (pemodelan)?** Fokus Bagian 13 dan 14.
- **Kamu Mahasiswa 3 (aplikasi)?** Fokus Bagian 15.
- **Mau persiapan presentasi?** Bagian 11, 16, dan 19.

Tanda yang dipakai:
- ✅ = sudah selesai dan sudah dicek
- ⏳ = belum dikerjakan
- ⚠️ = hati-hati, sering salah

---

## 2. Proyek ini dalam bahasa sehari-hari

Ada sebuah pabrik baja di Korea Selatan (DAEWOO Steel). Setiap 15 menit, sistem listrik pabrik mencatat berapa banyak listrik yang dipakai, kualitas listriknya, berapa emisi CO2 yang dihasilkan, dan jam berapa itu terjadi. Data ini terkumpul selama satu tahun penuh (2018), jadi ada 35.040 catatan (365 hari × 96 catatan per hari).

Masalahnya: angka pemakaian listrik mentah (misalnya "60 kWh") **tidak langsung memberi tahu manajer** apakah kondisi pabrik saat itu baik atau buruk. 60 kWh di jam sibuk itu wajar, tetapi 60 kWh di jam yang seharusnya sepi itu patut dicurigai.

Jadi kelompok kami membuat **label status** yang lebih mudah dipahami manajer, yaitu `Status_Efisiensi`, dengan 4 kemungkinan:

| Status | Arti sederhana |
|---|---|
| **Efisien** | Jam sepi, pemakaian listrik rendah. Kondisi ideal. |
| **Normal** | Jam menengah, pemakaian listrik rendah. Kondisi standar. |
| **Beban Kritis** | Jam puncak, atau jam menengah dengan pemakaian tinggi. Perlu diawasi. |
| **Pemborosan Emisi** | Jam sepi tetapi pemakaian dan emisi tinggi. Peringatan. |

Lalu kami melatih **model machine learning** supaya bisa menebak status itu hanya dari data listrik dan waktu, **tanpa melihat** kolom CO2 dan jenis beban (karena dua kolom itu yang dipakai untuk membuat labelnya). Kami membandingkan 3 algoritma: **Random Forest**, **SVM**, dan **XGBoost**, lalu memilih yang terbaik untuk dipasang di **aplikasi web (Streamlit)**. Di aplikasi itu, pengguna memasukkan data, lalu aplikasi menampilkan statusnya.

Jenis tugas machine learning-nya: **klasifikasi multi-kelas** (supervised learning, 4 kelas).

Posisi proyek yang jujur: ini adalah **Decision Support System (sistem pendukung keputusan)** yang meniru aturan bisnis. Model **tidak** menemukan pola tersembunyi yang canggih. Model belajar meniru aturan yang kami buat sendiri, dengan informasi yang lebih terbatas. Ini harus disampaikan apa adanya di laporan (penjelasannya di Bagian 10).

---

## 3. Konteks tugas kuliah

### 3.1 Identitas

| | |
|---|---|
| Mata kuliah | Pembelajaran Mesin (Machine Learning), materi M15 – Project dan Refleksi |
| Kelompok | 18 |
| Anggota | Assyifa Rifka Ahyani (J0404241090), Kevin Dwira Al Fathan (J0404241164), Muhammad Sabda R. (J0404241143) |
| Kelas | ⚠️ belum tertulis di PPT, wajib ditambahkan |

### 3.2 Pembagian tugas (sesuai contoh di panduan)

| Peran | Tugas | Status |
|---|---|---|
| Mahasiswa 1 | Dataset, EDA, preprocessing | ✅ selesai |
| Mahasiswa 2 | Pemodelan dan evaluasi | ⏳ belum (skrip awal sudah disiapkan) |
| Mahasiswa 3 | Aplikasi dan deployment | ⏳ belum |

⚠️ Walaupun tugas dibagi, **nilai tanya jawab dinilai per orang**. Semua anggota wajib paham seluruh proyek, termasuk bagian yang bukan tugasnya.

### 3.3 Bobot nilai (dari panduan)

| Komponen | Bobot |
|---|---|
| Identifikasi masalah & studi literatur | 10% |
| Dataset, EDA & preprocessing | 15% |
| Pengembangan model | 20% |
| Evaluasi & analisis model | 20% |
| Implementasi aplikasi | 15% |
| PPT & video demo | 10% |
| Originalitas/inovasi | 5% |
| Pembagian tugas & dokumentasi | 5% |

Perhatikan: **pemodelan + evaluasi = 40%**. Bagian "analisis" (kenapa model A lebih baik, di mana model salah, apakah overfitting) sama pentingnya dengan angka skornya.

### 3.4 Aturan penting dari panduan yang berhubungan langsung dengan proyek ini

- Minimal **3 algoritma** dibandingkan (kita: RF, SVM, XGBoost ✅).
- Data uji **tidak boleh dipakai** dalam proses training.
- **Akurasi tertinggi tidak otomatis terbaik**. Pilih model dengan metrik yang sesuai (kita: Macro F1).
- Semua hasil evaluasi harus dari pengujian yang **benar-benar dijalankan**.
- Wajib bisa menjelaskan alasan setiap preprocessing, algoritma, dan metrik.
- Minimal **5 artikel jurnal** + tabel studi literatur.
- Video demo **maksimal 7 menit**, aplikasi harus benar-benar dijalankan.
- Nama folder pengumpulan: `ML2026_<Kelas>_Kelompok18_<JudulProject>`, contoh `ML2026_A_Kelompok18_KlasifikasiEfisiensiEnergiBaja`.

---

## 4. Kamus istilah

### 4.1 Istilah kelistrikan

| Istilah | Penjelasan sederhana |
|---|---|
| **kWh (kilowatt-hour)** | Satuan energi listrik yang benar-benar dipakai untuk bekerja (memutar mesin, memanaskan). Di dataset: energi yang terpakai dalam 15 menit. |
| **Daya aktif** | Bagian listrik yang "berguna", diukur dalam kWh. |
| **Daya reaktif (kVarh)** | Bagian listrik yang bolak-balik di jaringan tanpa menghasilkan kerja. Dibutuhkan mesin bermagnet (motor, trafo), tetapi kalau terlalu besar artinya pemborosan dan bisa kena denda dari perusahaan listrik. |
| **Lagging (tertinggal)** | Kondisi ketika arus listrik tertinggal dari tegangan. Biasanya disebabkan beban induktif, seperti motor dan trafo. Ini kondisi umum di pabrik. |
| **Leading (mendahului)** | Kondisi ketika arus mendahului tegangan. Biasanya disebabkan beban kapasitif, seperti kapasitor (alat untuk memperbaiki kualitas listrik). |
| **Power Factor / faktor daya (%)** | Perbandingan daya aktif dengan total daya. 100% = semua listrik terpakai untuk kerja (sangat baik). Makin rendah, makin banyak listrik "terbuang" sebagai daya reaktif. |
| **tCO2** | Ton karbon dioksida. Di dataset ini **dihitung dari pemakaian kWh** dengan rumus, bukan diukur sensor udara. |
| **KEPCO** | Korea Electric Power Corporation, perusahaan listrik negara Korea Selatan (setara PLN). Data energi pabrik ini tersimpan di sistem mereka. |
| **Tarif berdasarkan waktu (time-of-use)** | Skema tarif listrik yang harganya berbeda tergantung jam, hari, dan musim (jam sepi murah, jam puncak mahal). Penting untuk memahami kolom `Load_Type` (lihat Bagian 10). |

### 4.2 Istilah machine learning

| Istilah | Penjelasan sederhana |
|---|---|
| **Fitur (X)** | Kolom input yang diberikan ke model untuk menebak. Kita punya 8 fitur. |
| **Target / label (y)** | Jawaban yang ingin ditebak. Kita: `Status_Efisiensi`. |
| **Klasifikasi** | Menebak kategori (bukan angka). Kita punya 4 kategori. |
| **Data latih (train)** | Data untuk mengajari model. Kita: Januari–September. |
| **Data uji (test)** | Data untuk menguji model setelah selesai belajar. Model tidak boleh pernah melihatnya saat belajar. Kita: Oktober–Desember. |
| **Data leakage (kebocoran data)** | Kesalahan ketika model "menyontek", yaitu diberi informasi yang sebenarnya adalah jawabannya atau informasi dari data uji. Hasilnya skor terlihat bagus tetapi palsu. |
| **Time-based split** | Membagi data berdasarkan waktu (masa lalu untuk latih, masa depan untuk uji), bukan diacak. |
| **Class imbalance** | Jumlah data tiap kelas sangat tidak seimbang. Kelas Pemborosan Emisi hanya 4,17%. |
| **class_weight='balanced'** | Cara memberi "bobot" lebih besar pada kelas yang sedikit, supaya model tidak mengabaikannya. |
| **SMOTE** | Teknik membuat data sintetis (palsu) untuk kelas minoritas. **Tidak kita pakai** (alasan di Bagian 12). |
| **Encoding** | Mengubah teks (misalnya "Monday") menjadi angka supaya bisa dibaca model. **One-hot encoding** = membuat satu kolom 0/1 untuk tiap kategori. |
| **Scaling (StandardScaler)** | Menyamakan skala angka (misalnya NSM sampai 85.500, sedangkan Usage sampai 157) supaya model tertentu (SVM) tidak berat sebelah. |
| **Pipeline** | "Paket" yang menggabungkan langkah preprocessing + model jadi satu objek. Keuntungannya: aplikasi cukup memanggil satu file, dan tidak ada langkah yang lupa. |
| **Hyperparameter tuning** | Mencoba beberapa pengaturan model untuk mencari yang terbaik. |
| **Cross validation / TimeSeriesSplit** | Cara menguji pengaturan model di dalam data latih. TimeSeriesSplit memastikan validasi selalu memakai data "masa depan" relatif terhadap data latihnya. |
| **Overfitting** | Model terlalu hafal data latih sehingga jelek di data baru. Tanda: skor latih jauh lebih tinggi dari skor uji. |
| **Accuracy** | Persentase tebakan yang benar. Bisa menipu kalau kelas tidak seimbang. |
| **Precision** | Dari semua yang ditebak kelas X, berapa persen yang memang X. Tinggi = alarm palsu sedikit. |
| **Recall** | Dari semua yang sebenarnya X, berapa persen berhasil ditebak. Tinggi = kejadian jarang terlewat. |
| **F1-Score** | Gabungan precision dan recall (rata-rata harmonik). |
| **Macro F1** | Rata-rata F1 dari keempat kelas, setiap kelas dianggap sama penting. **Metrik utama kita.** |
| **Confusion matrix** | Tabel yang menunjukkan kelas asli vs tebakan model, untuk melihat kelas mana yang sering tertukar. |
| **Random Forest (RF)** | Ratusan pohon keputusan yang dilatih pada sampel acak, lalu hasilnya divoting. |
| **SVM** | Mencari garis/bidang pemisah antar kelas dengan jarak (margin) paling lebar. Butuh scaling. |
| **XGBoost** | Pohon keputusan dibangun berurutan; tiap pohon baru memperbaiki kesalahan pohon sebelumnya. |

---

## 5. Dataset

### 5.1 Identitas dataset

| | |
|---|---|
| Nama | Steel Industry Energy Consumption |
| Asal data | DAEWOO Steel Co. Ltd, Gwangyang, Korea Selatan (memproduksi koil, pelat baja, pelat besi) |
| Sumber resmi | UCI Machine Learning Repository, dataset ID 851 |
| DOI | 10.24432/C52G8C |
| Lisensi | CC BY 4.0 (boleh dipakai, wajib mencantumkan sumber) |
| Pembuat | Sathishkumar V E, Changsun Shin, Yongyun Cho (Sunchon National University) |
| Periode | 1 Januari 2018 – 31 Desember 2018 |
| Interval | Setiap 15 menit |
| Jumlah baris | 35.040 (file resmi) |
| Jumlah kolom | 11 |
| Missing value | 0 |
| Tugas asli dataset di UCI | Regresi (memprediksi konsumsi energi). Kelompok kita mengubahnya jadi klasifikasi. |

Di project ada dua versi file data mentah:
- `Steel_industry_data.csv` = **file resmi UCI**, 35.040 baris, kolom tanggal bernama `date` dengan format `01/01/2018 00:15`, kolom hari bernama `Day_of_week`.
- `Steel_industry.csv` (di dalam zip) = **salinan yang dipakai notebook**, 35.041 baris (ada 1 baris ekstra di akhir), kolom tanggal bernama `Date_Time` dengan format `01-01-2018 00:15`, kolom hari bernama `Day_Of_Week`.

Isi 35.040 baris pertama kedua file **identik** (sudah dicek kolom per kolom). Bedanya hanya nama kolom, format tanggal, dan 1 baris ekstra.

### 5.2 Penjelasan setiap kolom

Angka statistik di bawah ini dihitung dari data yang sudah dibersihkan (34.993 baris).

| No | Nama kolom | Arti | Satuan | Rentang | Rata-rata | Dipakai di X? |
|---|---|---|---|---|---|---|
| 1 | `Date_Time` (resmi: `date`) | Tanggal dan jam pencatatan, akhir dari interval 15 menit | – | 1 Jan 2018 00:00 – 31 Des 2018 23:45 | – | ❌ dibuang (dipakai untuk split) |
| 2 | `Usage_kWh` | Energi listrik aktif yang dipakai pabrik selama 15 menit | kWh | 0 – 157,18 | 27,32 | ✅ |
| 3 | `Lagging_Current_Reactive_Power_kVarh` (aslinya pakai titik: `Reactive.Power`) | Daya reaktif lagging | kVarh | 0 – 96,91 | 13,01 | ✅ |
| 4 | `Leading_Current_Reactive_Power_kVarh` | Daya reaktif leading | kVarh | 0 – 27,76 | 3,87 | ✅ |
| 5 | `CO2(tCO2)` | Emisi CO2, dihitung dari Usage | tCO2 | 0 – 0,07 (hanya 8 nilai: 0,00; 0,01; … 0,07) | – | ❌ dibuang (pembentuk target) |
| 6 | `Lagging_Current_Power_Factor` | Faktor daya lagging | % | 0 – 100 | 80,56 | ✅ |
| 7 | `Leading_Current_Power_Factor` | Faktor daya leading | % | 0 – 100 | 84,35 | ✅ |
| 8 | `NSM` | Number of Seconds from Midnight: detik sejak tengah malam | detik | 0 – 85.500 (kelipatan 900) | – | ✅ |
| 9 | `WeekStatus` | Hari kerja atau akhir pekan | teks: `Weekday` / `Weekend` | – | – | ✅ |
| 10 | `Day_Of_Week` (resmi: `Day_of_week`) | Nama hari | teks: `Monday` … `Sunday` | – | – | ✅ |
| 11 | `Load_Type` | Jenis beban | teks: `Light_Load`, `Medium_Load`, `Maximum_Load` | – | – | ❌ dibuang (pembentuk target) |

Catatan per kolom yang perlu dipahami:

- **NSM**: cara menghitungnya `jam × 3600 + menit × 60`. Contoh: 09.15 → 9×3600 + 15×60 = 33.300. Jam 00.00 → 0. Nilai maksimum 85.500 (= 23.45), bukan 86.400, karena 24.00 ditulis sebagai 00.00 = 0.
- **Urutan jam 00.00**: di file ini, baris jam 00.00 diletakkan **di akhir hari**, setelah 23.45, tetapi tanggalnya tetap tanggal hari itu. Contoh: baris `01-01-2018 00:00` ada di urutan ke-96, setelah `01-01-2018 23:45`. Jadi 00.00 di sini sebenarnya berarti "penutup hari" (interval 23.45–24.00). Itulah sebabnya **baris tidak boleh diurutkan ulang**.
- **CO2**: dihitung dengan rumus kira-kira `CO2 = Usage × 0,000458`, lalu dibulatkan 2 desimal. Karena dibulatkan, nilainya hanya bisa 0,00 / 0,01 / 0,02 / dst. Konsekuensinya, CO2 ≥ 0,02 **sama persis** dengan Usage ≥ 32,72 kWh.
- **WeekStatus**: 100% konsisten dengan `Day_Of_Week` (Saturday/Sunday = Weekend). Jadi sebenarnya informasinya sudah ada di `Day_Of_Week`, tetapi tetap dipakai karena tidak merugikan.
- **Load_Type**: walaupun namanya "jenis beban", isinya ternyata mengikuti jadwal waktu (lihat Bagian 10.1).

Jumlah baris per hari (data bersih): Monday 5.088, Tuesday 4.945, Wednesday–Sunday masing-masing 4.992. Monday lebih banyak karena tahun 2018 punya 53 hari Senin (1 Januari dan 31 Desember sama-sama Senin). Tuesday lebih sedikit karena 47 baris tanggal 2 Januari (Selasa) dibuang.

Jumlah per WeekStatus: Weekday 25.009, Weekend 9.984.
Jumlah per Load_Type: Light 18.068, Medium 9.673, Maximum 7.252.

### 5.3 Contoh baris data dan cara membacanya

```
Date_Time         Usage_kWh  LagRP  LeadRP  CO2   LagPF  LeadPF  NSM  WeekStatus  Day_Of_Week  Load_Type
01-01-2018 00:15  3.17       2.95   0.00    0.00  73.21  100.00  900  Weekday     Monday       Light_Load
```

Artinya: pada 1 Januari 2018 jam 00.00–00.15 (NSM 900 = 15 menit setelah tengah malam), pabrik memakai 3,17 kWh, daya reaktif lagging 2,95 kVarh, faktor daya lagging 73,21%, emisi dibulatkan jadi 0, hari Senin, jenis beban Light. Karena Light_Load dan CO2 < 0,02, statusnya **Efisien**.

---

## 6. Isi folder proyek

Isi `update hasil preprocessing.zip` → folder `Kelompok 18_ML/`:

| File/Folder | Isi | Perlu dikumpulkan? |
|---|---|---|
| `Source-kode.ipynb` | Notebook preprocessing + EDA (9 sel kode, sel terakhir kosong) | ✅ ya |
| `Steel_industry.csv` | Data mentah versi kelompok (35.041 baris) | Salah satu saja (lihat Bagian 17 no. 7) |
| `X_train_pabrik.csv` | Fitur data latih (26.161 baris × 8 kolom) | ✅ |
| `y_train_pabrik.csv` | Label data latih (26.161 baris, kolom `Status_Efisiensi`) | ✅ |
| `X_test_pabrik.csv` | Fitur data uji (8.832 baris × 8 kolom) | ✅ |
| `y_test_pabrik.csv` | Label data uji (8.832 baris) | ✅ |
| `eda_output/01_distribusi_kelas.png` … `06_boxplot_fitur.png` | 6 grafik EDA | ✅ (dipakai di PPT) |
| `.ipynb_checkpoints/` | File cadangan otomatis Jupyter | ❌ hapus |

File lain di project (di luar zip):

| File | Isi |
|---|---|
| `Steel_industry_data.csv` | Data mentah resmi UCI (35.040 baris) |
| `Panduan Project Machine Learning.md` | Aturan tugas dari dosen |
| `PPT Presentasi Kelompok 18 ML.pdf` | Draf PPT (7 slide, belum lengkap) |
| `Handover_Preprocessing_EDA.md`, `Handover Notes Proyek ML.pdf` | Handover lama (digantikan dokumen ini) |
| `claude/modeling_starter.py` | Skrip pemodelan siap jalan (Bagian 14) |
| `claude/Handover_Final_Kelompok18.md` | Dokumen ini |

---

## 7. Menyiapkan komputer dan menjalankan kode

### 7.1 Yang perlu di-install

Python 3.10 ke atas, lalu di terminal/command prompt:

```bash
pip install pandas numpy matplotlib scikit-learn xgboost joblib jupyter streamlit
```

Versi yang dipakai saat pengecekan: pandas 3.0, scikit-learn 1.9, xgboost 3.4. Versi lain yang tidak terlalu jauh seharusnya tetap jalan.

⚠️ Notebook memakai `ax.boxplot(..., orientation="horizontal")`. Parameter `orientation` hanya ada di matplotlib versi 3.10 ke atas. Kalau muncul error di grafik 6, update matplotlib (`pip install -U matplotlib`) atau ganti dengan `vert=False`.

### 7.2 Menjalankan notebook preprocessing

1. Taruh `Source-kode.ipynb` dan `Steel_industry.csv` di satu folder.
2. Buka terminal di folder itu, jalankan `jupyter notebook`.
3. Buka `Source-kode.ipynb`, pilih menu **Run All**.
4. Hasilnya: folder `eda_output/` berisi 6 grafik, dan 4 file CSV (`X_train_pabrik.csv`, dst).

Kalau semua `assert` lolos tanpa error, berarti data sama persis dengan yang kami pakai.

⚠️ Notebook **tidak bisa langsung** membaca file resmi `Steel_industry_data.csv` karena nama kolom dan format tanggalnya berbeda. Kalau mau memakai file resmi, ganti sel load data menjadi:

```python
df = pd.read_csv("Steel_industry_data.csv", encoding="utf-8-sig")
df.rename(columns={
    "date": "Date_Time",
    "Day_of_week": "Day_Of_Week",
    "Lagging_Current_Reactive.Power_kVarh": "Lagging_Current_Reactive_Power_kVarh",
}, inplace=True)
df["Date_Time"] = pd.to_datetime(df["Date_Time"], format="%d/%m/%Y %H:%M")
```

Lalu di sel pembersihan, baris `df.drop(index=35040)` tidak berpengaruh (karena barisnya tidak ada), dan `assert len(df) == n_awal - 1 - 47` perlu diubah menjadi `assert len(df) == 34993`. Hasil akhirnya tetap sama: 34.993 baris.

### 7.3 Menjalankan skrip pemodelan

1. Taruh `modeling_starter.py` satu folder dengan 4 CSV.
2. Jalankan `python modeling_starter.py`.
3. Tunggu ±2–3 menit. Hasil masuk ke folder `model_output/`.

Detailnya di Bagian 14.

---

## 8. Alur notebook preprocessing, langkah demi langkah

Notebook `Source-kode.ipynb` terdiri dari 9 sel kode. Berikut isi tiap sel, alasannya, dan hasilnya.

### Sel 0 – Persiapan

- Import library (pandas, numpy, matplotlib).
- Membuat folder `eda_output/` untuk menyimpan grafik.
- Mendefinisikan urutan kelas: `["Efisien", "Normal", "Beban Kritis", "Pemborosan Emisi"]` (dipakai supaya urutan di tabel dan grafik selalu sama).
- Membuat fungsi `simpan_dan_tampil()` untuk menyimpan grafik ke file sekaligus menampilkannya.

### Sel 1 – Load data dan rapikan format

- Membaca `Steel_industry.csv` → 35.041 baris, 11 kolom.
- Mengganti nama kolom `Lagging_Current_Reactive.Power_kVarh` menjadi `Lagging_Current_Reactive_Power_kVarh`. **Alasan**: tanda titik di nama kolom bisa bikin masalah di beberapa library (XGBoost, Streamlit).
- Mengecek semua 11 kolom wajib ada (`assert`).
- Mengubah `Date_Time` dari teks jadi tipe tanggal, dengan format eksplisit `%d-%m-%Y %H:%M`. **Alasan**: tanpa format eksplisit, pandas bisa salah baca tanggal 01-02 sebagai 2 Januari atau 1 Februari.

### Sel 2 – Cek kualitas data (belum ada yang dihapus)

Semua pengecekan ini hanya **melapor**, belum mengubah data:

| Pengecekan | Hasil | Arti |
|---|---|---|
| Missing value | 0 di semua kolom | Tidak perlu imputasi (pengisian nilai kosong) |
| Duplikat baris penuh | 0 | – |
| Duplikat timestamp | 2 baris dengan `31-12-2018 20:00` (indeks 35023 dan 35040) | Ada 1 baris ekstra |
| NSM cocok dengan jam di Date_Time | 100% | Kolom NSM bisa dipercaya |
| NSM kelipatan 900 | 100% | Interval selalu 15 menit |
| WeekStatus cocok dengan nama hari | 100% | Kolom konsisten |
| Usage negatif | 0 | Wajar |
| Power factor di luar 0–100 | 0 | Wajar |
| Baris Usage = 0 dan LagPF = 0 | 1 | Mesin mati sesaat; dibiarkan |
| LeadPF = 100% tapi LeadRP > 5 kVarh | 0 | Secara fisik konsisten |
| LagPF = 100% dan LeadPF = 100% bersamaan | 0 | Secara fisik konsisten |

Lalu sel ini mencetak **hubungan Usage dan CO2** (rentang Usage untuk tiap nilai CO2):

| CO2 | Usage min | Usage max | Jumlah baris |
|---|---|---|---|
| 0,00 | 0,00 | 147,46 ⚠️ | 20.991 |
| 0,01 | 10,91 | 32,69 | 1.512 |
| 0,02 | 32,72 | 54,50 | 4.643 |
| 0,03 | 54,54 | 76,32 | 4.261 |
| 0,04 | 76,36 | 98,14 | 1.834 |
| 0,05 | 98,17 | 119,95 | 1.363 |
| 0,06 | 119,99 | 141,66 | 410 |
| 0,07 | 142,56 | 157,18 | 27 |

Terlihat polanya rapi berjenjang, **kecuali** CO2 = 0 yang punya Usage sampai 147,46. Ternyata ada **47 baris** dengan CO2 = 0 padahal Usage > 11 kWh, dan semuanya terjadi di **satu tanggal: 2 Januari 2018, jam 08.15–20.30** (Usage rata-rata 79 kWh). Ini hampir pasti kegagalan pencatatan CO2 di hari itu.

### Sel 3 – Pembersihan data

1. **Hapus baris indeks 35040** (baris ekstra). Alasannya: timestamp-nya ganda dengan baris 35023, nilainya tidak masuk akal (LagRP = 0 dan LeadRP = 20,10 padahal baris sekitarnya ≈ 0,1), dan file resmi UCI hanya 35.040 baris.
2. **Hapus 47 baris tanggal 2 Januari** yang CO2-nya salah. Alasannya: CO2 dipakai untuk membuat target. Kalau CO2 salah, labelnya juga salah (baris dengan pemakaian 140 kWh akan dilabeli "Efisien").
3. `reset_index` supaya nomor baris rapi lagi (urutan baris **tidak** diubah).
4. `assert` memastikan: jumlah baris tepat 34.993, tidak ada timestamp ganda, tidak ada missing value.

Hasil: **35.041 → 34.993 baris**.

### Sel 4 – Membuat target `Status_Efisiensi`

Memakai `np.select` dengan 4 aturan (detail di Bagian 9). Ada `assert` untuk memastikan tidak ada baris yang tidak masuk kelas mana pun.

Hasil distribusi:

| Kelas | Jumlah | Persen |
|---|---|---|
| Efisien | 16.609 | 47,46% |
| Normal | 4.724 | 13,50% |
| Beban Kritis | 12.201 | 34,87% |
| Pemborosan Emisi | 1.459 | 4,17% |

### Sel 5 – EDA

Mencetak statistik deskriptif, skewness, info dataset, distribusi kategori, jumlah outlier IQR, matriks korelasi, lalu membuat 6 grafik. Penjelasan lengkap di Bagian 11.

### Sel 6 – Time-based split

- Latih: bulan 1–9 (Januari–September) → 26.161 baris.
- Uji: bulan 10–12 (Oktober–Desember) → 8.832 baris.
- `assert` memastikan keempat kelas muncul di latih dan uji.
- Mencetak perbandingan proporsi kelas latih vs uji.

### Sel 7 – Buang kolom pembentuk target

Kolom yang dibuang dari X: `Date_Time`, `CO2(tCO2)`, `Load_Type`, dan `Status_Efisiensi` (target itu sendiri). `assert` memastikan tersisa tepat 8 fitur.

**Urutan langkah ini penting:** target dibuat dulu (butuh CO2 dan Load_Type), split dilakukan (butuh Date_Time), baru kolom-kolom itu dibuang.

### Sel 8 – Ekspor

Menyimpan 4 CSV tanpa kolom indeks (`index=False`).

### Sel 9 – kosong (hapus sebelum dikumpulkan)

---

## 9. Target `Status_Efisiensi`

### 9.1 Aturan pembentukan

Target dibuat dari dua kolom: **`Load_Type`** dan **apakah CO2 ≥ 0,02** (disebut "CO2 tinggi").

|  | CO2 < 0,02 (rendah) | CO2 ≥ 0,02 (tinggi) |
|---|---|---|
| **Light_Load** | Efisien | Pemborosan Emisi |
| **Medium_Load** | Normal | Beban Kritis |
| **Maximum_Load** | Beban Kritis | Beban Kritis |

Kode aslinya:

```python
load = df["Load_Type"]
co2_tinggi = df["CO2(tCO2)"] >= 0.02
kondisi = [
    (load == "Light_Load")  & ~co2_tinggi,                              # Efisien
    (load == "Medium_Load") & ~co2_tinggi,                              # Normal
    (load == "Maximum_Load") | ((load == "Medium_Load") & co2_tinggi),  # Beban Kritis
    (load == "Light_Load")  & co2_tinggi,                               # Pemborosan Emisi
]
```

Karena CO2 ≥ 0,02 sama persis dengan Usage ≥ 32,72 kWh, aturan di atas bisa dibaca juga sebagai: "**pemakaian tinggi = lebih dari ±32,7 kWh per 15 menit**".

### 9.2 Jumlah baris di tiap sel tabel (data bersih)

|  | CO2 rendah | CO2 tinggi |
|---|---|---|
| Light_Load | 16.609 (Efisien) | 1.459 (Pemborosan Emisi) |
| Medium_Load | 4.724 (Normal) | 4.949 (Beban Kritis) |
| Maximum_Load | 1.122 (Beban Kritis) | 6.130 (Beban Kritis) |

Jadi Beban Kritis (12.201) berasal dari 3 sumber: Maximum + rendah (1.122), Maximum + tinggi (6.130), Medium + tinggi (4.949).

### 9.3 Kenapa ambang 0,02?

Di handover lama disebut "Kuartil 3 (Q3) CO2 = 0,02". Secara angka benar Q3-nya 0,02, **tetapi** karena CO2 hanya punya nilai bulat (0,00; 0,01; 0,02; …), aturan "≥ 0,02" ternyata menandai **35,8%** data sebagai tinggi, bukan 25% seperti yang biasanya dibayangkan dari "kuartil 3".

Pembenaran yang lebih kuat dan mudah dijelaskan: **"0,02 tCO2 setara dengan pemakaian ±32,7 kWh per 15 menit. Di atas angka ini, pabrik sudah dalam mode produksi (bukan idle)."** Grafik 03 (Bagian 11) mendukung ini: saat pabrik idle (malam), pemakaian hanya ±4 kWh; saat produksi, ±40–60 kWh.

### 9.4 Proporsi kelas di data latih dan uji

| Kelas | Latih (%) | Uji (%) | Jumlah di uji |
|---|---|---|---|
| Efisien | 47,02 | 48,77 | 4.307 |
| Normal | 14,22 | 11,38 | 1.005 |
| Beban Kritis | 34,21 | 36,81 | 3.251 |
| Pemborosan Emisi | 4,55 | 3,05 | 269 |

Proporsinya sedikit berbeda karena dibagi berdasarkan waktu. Ini wajar dan justru realistis (kondisi masa depan memang tidak persis sama dengan masa lalu).

---

## 10. Temuan penting tentang data (wajib paham semua anggota)

Bagian ini hasil analisis tambahan yang **tidak ada di dokumen lama**. Ini sangat mungkin ditanyakan dosen.

### 10.1 `Load_Type` mengikuti jadwal waktu, bukan kondisi mesin

Kalau kita melihat `Load_Type` per jam:

| Jam | Light | Medium | Maximum |
|---|---|---|---|
| 00–08 (tiap jam) | **1.460 (100%)** | 0 | 0 |
| 09 | 551 | 909 | 0 |
| 10 | 248 | 303 | 909 |
| 11 | 248 | 0 | 1.212 |
| 12–22 | 248 | campuran | campuran |
| 23 | 1.157 | 208 | 95 |

Pengamatan:
- Jam 00.00–08.59, `Load_Type` **selalu Light**, termasuk ketika pemakaian sedang tinggi.
- Di jam 10.00–22.59 ada tepat 248 baris Light per jam. Ini berasal dari 62 hari yang Light sepanjang hari: kebanyakan hari Minggu (35 hari), beberapa hari Sabtu, dan hari libur nasional Korea (misalnya 1 Januari, Seollal 15–17 Februari, Chuseok 24–26 September, Natal 25 Desember). Ini menguatkan dugaan bahwa Load_Type adalah jadwal/kalender, bukan kondisi mesin.
- Dari fitur waktu saja (NSM, hari, akhir pekan), sebuah model bisa menebak `Load_Type` dengan akurasi **77,6%**. Setelah ditambah **musim**, akurasinya **94,3%**.
- Dari pemakaian listrik (`Usage_kWh`) saja, akurasinya hanya **65,5%**.
- Ada 1.122 baris `Maximum_Load` dengan pemakaian < 32,7 kWh, dan 646 di antaranya < 10 kWh (mesin hampir diam).

**Kesimpulan**: `Load_Type` kemungkinan besar adalah **kategori periode tarif listrik berdasarkan waktu** (Light = jam murah, Medium = jam menengah, Maximum = jam puncak), mirip skema tarif time-of-use KEPCO. Halaman UCI sendiri tidak menjelaskan definisi Light/Medium/Maximum, jadi ini **kesimpulan dari analisis data kita**. Sampaikan dengan kalimat "berdasarkan analisis data, kami menemukan bahwa...".

**Dampak ke cara menjelaskan kelas:**

| Kelas | Penjelasan yang tepat | ⚠️ Hindari menyebut |
|---|---|---|
| Efisien | Periode tarif ringan, pemakaian rendah | – |
| Normal | Periode tarif menengah, pemakaian rendah | – |
| Beban Kritis | Periode tarif puncak, atau pemakaian tinggi di periode tarif menengah | "mesin overload" (ada Beban Kritis yang pemakaiannya hampir 0) |
| Pemborosan Emisi | Pemakaian tinggi di periode tarif ringan | "anomali", "kerusakan mesin", "kebocoran" |

**Tentang Pemborosan Emisi:** 72% kejadiannya terjadi pada jam 08.00–09.59, kemungkinan karena pabrik sudah mulai produksi sebelum periode tarif berganti. 26% terjadi di bulan Januari. Jadi ini lebih tepat disebut "**pemakaian tinggi saat tarif ringan**" (bisa jadi peluang penjadwalan ulang produksi), bukan kerusakan.

### 10.2 `Usage_kWh` dan CO2 pada dasarnya informasi yang sama

- CO2 dihitung dari Usage (≈ 0,000458 tCO2 per kWh, dibulatkan).
- Setelah 47 baris salah dibuang, **CO2 ≥ 0,02 cocok 100%** dengan Usage ≥ 32,72 kWh di seluruh 34.993 baris.
- Artinya, walaupun CO2 dibuang dari X, informasinya tetap ada lewat `Usage_kWh`.

Apakah ini leakage? **Tidak sepenuhnya**, karena di dunia nyata Usage memang tersedia saat prediksi (bukan informasi dari masa depan). Tetapi ini harus diakui di laporan: separuh "tugas" model hanyalah menerapkan ambang 32,7 kWh, yang sebenarnya mudah.

### 10.3 Jadi, apa yang sebenarnya dipelajari model?

Model sebenarnya mengerjakan dua hal:

1. **Menerapkan ambang Usage ≥ 32,7 kWh** → mudah, karena Usage ada di X.
2. **Menebak `Load_Type` (periode tarif) dari waktu** → sulit, karena X hanya punya jam (NSM) dan hari, **tanpa bulan atau musim**, padahal jadwal tarif berubah per musim.

Akibatnya:
- **Pemborosan Emisi hampir sempurna** (F1 ≈ 1,0 untuk RF dan XGBoost), karena kelas ini hampir selalu terjadi di jam yang pasti Light (00.00–09.59) dengan pemakaian tinggi.
- **Normal paling sulit**: precision hanya ±0,49–0,57. Model sering salah menebak baris Efisien atau Beban Kritis sebagai Normal, karena batas jam Light/Medium/Maximum bergeser antar musim.
- Skor tinggi model **wajar karena struktur data**, bukan karena model menemukan pola rumit. Tulis apa adanya.

### 10.4 Bukti pentingnya time-based split

Dengan 8 fitur yang sama dan Random Forest yang sama:

| Cara membagi data | Macro F1 |
|---|---|
| Diacak (random split 75/25) | ≈ 0,961 |
| Berdasarkan waktu (Jan–Sep / Okt–Des) | ≈ 0,895 |

Skor acak lebih tinggi karena baris yang berdekatan (selisih 15 menit) hampir identik. Kalau diacak, model "melihat" tetangga dari data uji saat latihan, sehingga ujiannya terlalu mudah. ⚠️ Percobaan ini **belum ada di notebook**. Wajib ditambahkan (Bagian 16) supaya klaim ini benar-benar hasil pengujian yang dijalankan.

---

## 11. EDA: penjelasan tiap grafik

Panduan mewajibkan **setiap grafik dijelaskan, bukan hanya ditampilkan**. Berikut bahan penjelasannya.

### Grafik 01 – Distribusi kelas (`01_distribusi_kelas.png`)

- **Apa**: diagram batang jumlah baris per kelas.
- **Yang terlihat**: Efisien 16.609, Beban Kritis 12.201, Normal 4.724, Pemborosan Emisi hanya 1.459.
- **Kesimpulan**: data **tidak seimbang**. Pemborosan Emisi hanya 4,17%. Ini alasan kita (1) memakai **Macro F1** bukan akurasi, dan (2) memakai **class_weight='balanced'**.

### Grafik 02 – Histogram 6 fitur numerik (`02_histogram_fitur.png`)

- **Usage_kWh**: sangat menumpuk di dekat 0–8 kWh (lebih dari 20.000 baris), lalu ada "bukit kedua" di 25–125 kWh. Bentuk **dua puncak (bimodal)**: satu untuk kondisi idle, satu untuk kondisi produksi. Skewness 1,20 (condong ke kanan).
- **Lagging Reactive Power**: mirip Usage (menumpuk dekat 0, bukit kedua di 15–60). Masuk akal karena keduanya sangat berkorelasi (0,90).
- **Leading Reactive Power**: lebih dari 25.000 baris bernilai ≈ 0. Sisanya tersebar tipis sampai 27.
- **Lagging Power Factor**: sebagian besar di 40–100%, dengan tumpukan besar di dekat 100%.
- **Leading Power Factor**: lebih dari 27.000 baris tepat di 100%, sisanya mengumpul di 15–30%.
- **NSM**: rata (seragam), karena setiap jam punya jumlah catatan yang sama. Pola gerigi kecil hanya efek pembagian bin histogram.
- **Kesimpulan**: distribusi fitur tidak normal (tidak berbentuk lonceng) dan banyak menumpuk di nilai ekstrem (0 atau 100). Ini salah satu alasan model berbasis pohon (RF, XGBoost) cocok, karena tidak butuh data berdistribusi normal.

### Grafik 03 – Rata-rata Usage per jam (`03_usage_per_jam.png`)

- **Yang terlihat**:
  - Jam 02–07: sangat rendah (±4,2–4,5 kWh) → pabrik idle.
  - Jam 08: naik tajam ke ±38 kWh, jam 09–11: ±56–59 kWh → produksi pagi.
  - Jam 12: turun ke ±18 kWh → kemungkinan **istirahat siang**.
  - Jam 14–16: ±56 kWh → produksi sore.
  - Jam 17–20: ±33–44 kWh, lalu jam 21–23 turun ke ±8–14 kWh.
- **Kesimpulan**: pemakaian listrik sangat dipengaruhi **jam operasional**, sehingga NSM adalah fitur penting. Juga menjelaskan kenapa Pemborosan Emisi banyak di jam 08–09: produksi sudah mulai, tetapi periode tarif masih Light.
- Tambahan (tidak ada di grafik): rata-rata pemakaian hari kerja 33,5 kWh vs akhir pekan 11,7 kWh, membenarkan pentingnya WeekStatus/Day_Of_Week.

### Grafik 04 – Heatmap korelasi (`04_korelasi.png`)

Nilai korelasi (−1 sampai 1; makin dekat ±1 makin kuat):

|  | Usage | LagRP | LeadRP | LagPF | LeadPF | NSM |
|---|---|---|---|---|---|---|
| Usage | 1,00 | **0,90** | −0,32 | 0,39 | 0,35 | 0,23 |
| LagRP | 0,90 | 1,00 | −0,41 | 0,14 | 0,41 | 0,08 |
| LeadRP | −0,32 | −0,41 | 1,00 | 0,53 | **−0,94** | 0,37 |
| LagPF | 0,39 | 0,14 | 0,53 | 1,00 | −0,52 | 0,57 |
| LeadPF | 0,35 | 0,41 | −0,94 | −0,52 | 1,00 | −0,36 |
| NSM | 0,23 | 0,08 | 0,37 | 0,57 | −0,36 | 1,00 |

- **Usage – LagRP = 0,90**: saat mesin bekerja keras, daya reaktif lagging ikut naik (motor makin banyak menyala).
- **LeadRP – LeadPF = −0,94**: makin besar daya reaktif leading, makin rendah faktor daya leading. Ini sesuai definisi fisiknya.
- **Kesimpulan**: ada fitur yang saling mirip (multikolinearitas). Tidak masalah untuk RF dan XGBoost. Kami tetap mempertahankan semua fitur karena jumlahnya hanya 8 dan masing-masing punya arti fisik berbeda.
- Catatan: korelasi hanya mengukur hubungan **lurus**. Hubungan Usage dengan target itu berbentuk ambang (patah), jadi angka korelasi tidak menggambarkan seberapa penting fitur.

### Grafik 05 – Boxplot Usage per kelas (`05_boxplot_usage_kelas.png`)

- **Yang terlihat**: Efisien (median 3,2 kWh) dan Normal (median 4,3 kWh) sangat rendah. Beban Kritis (median 58,3) dan Pemborosan Emisi (median 58,0) tinggi dan hampir sama. Beban Kritis punya ekor bawah sampai ±3 kWh (baris Maximum_Load yang mesinnya hampir diam). Pemborosan Emisi tidak ada yang di bawah 32,7 kWh.
- **Kesimpulan**: Usage memisahkan kelompok "rendah" (Efisien, Normal) dari "tinggi" (Beban Kritis, Pemborosan Emisi), tetapi **tidak bisa** membedakan Efisien vs Normal atau Beban Kritis vs Pemborosan Emisi. Untuk itu model butuh fitur **waktu**. Ini bukti visual dari Bagian 10.3.

### Grafik 06 – Boxplot tiap fitur untuk outlier (`06_boxplot_fitur.png`)

Jumlah outlier menurut aturan IQR (nilai di bawah Q1 − 1,5×IQR atau di atas Q3 + 1,5×IQR):

| Fitur | Jumlah "outlier" IQR |
|---|---|
| Usage_kWh | 323 (di atas 123,1 kWh) |
| Lagging Reactive Power | 1.071 (di atas 52,98) |
| Leading Reactive Power | 7.756 (di atas 5,22) |
| Lagging Power Factor | 1 (di bawah 9,58) |
| Leading Power Factor | 8.317 (di bawah 99,22) |

- **Kenapa tidak dihapus?** Untuk Leading RP dan Leading PF, lebih dari 70% datanya bernilai tepat 0 atau 100, sehingga rentang IQR menjadi sangat sempit dan hampir semua nilai lain dianggap "outlier". Itu **bukan kesalahan data**, hanya efek bentuk distribusi. Untuk Usage, nilai tinggi adalah saat produksi puncak, kondisi nyata pabrik.
- Ditambah dua pengecekan fisik di Sel 2 (rentang wajar dan konsistensi antarvariabel) yang semuanya lolos. Jadi outlier **dipertahankan**. Menghapusnya justru akan membuang ribuan baris produksi yang sah, dan model tidak akan mengenali kondisi puncak.

---

## 12. Keputusan preprocessing dan alasannya

| Langkah preprocessing | Dilakukan? | Di mana | Alasan |
|---|---|---|---|
| Penanganan missing value | Tidak perlu | – | Tidak ada missing value |
| Hapus duplikat | ✅ 1 baris | Notebook sel 3 | Timestamp ganda + nilai tidak wajar |
| Data cleaning (inkonsistensi) | ✅ 47 baris | Notebook sel 3 | CO2 salah catat, akan merusak label |
| Penanganan outlier | Tidak dihapus | – | Variasi operasional sah (Bagian 11, grafik 06) |
| Feature engineering (target) | ✅ | Notebook sel 4 | Membuat `Status_Efisiensi` |
| Feature selection | ✅ buang 3 kolom | Notebook sel 7 | Mencegah leakage (CO2, Load_Type) dan Date_Time sudah dipakai untuk split |
| Split latih/uji | ✅ berdasarkan waktu | Notebook sel 6 | Data deret waktu, baris berdekatan mirip |
| Encoding kategori | ✅ one-hot | Pipeline pemodelan | `WeekStatus` dan `Day_Of_Week` masih teks |
| Scaling | ✅ hanya untuk SVM | Pipeline pemodelan | SVM sensitif skala; pohon tidak |
| Penanganan imbalance | ✅ class_weight / sample_weight | Pipeline pemodelan | Pemborosan Emisi hanya 4,17% |
| Label encoding target | ✅ | Skrip pemodelan | XGBoost butuh label angka |
| SMOTE | ❌ tidak dipakai | – | Lihat di bawah |

**Kenapa encoding dan scaling tidak di notebook preprocessing, tapi di Pipeline?** Supaya scaler hanya "belajar" (fit) dari data latih, lalu langkah yang sama persis otomatis diterapkan ke data uji dan ke input aplikasi. Kalau scaling dilakukan di notebook terhadap seluruh data sebelum split, informasi data uji (rata-rata, simpangan) ikut bocor ke data latih.

**Kenapa tidak SMOTE?**
1. class_weight sudah cukup dan lebih sederhana.
2. SMOTE membuat data palsu dengan "menarik garis" antar data asli. Untuk fitur kategori (nama hari) hasilnya tidak bermakna.
3. Kalau dilakukan sebelum split, data sintetis berisi informasi data uji → **leakage**.
4. Data palsu di deret waktu bisa menciptakan kombinasi jam/hari yang tidak pernah terjadi.

---

## 13. Pembagian data latih dan uji

| | Periode | Baris | Persen |
|---|---|---|---|
| Latih | 1 Januari – 30 September 2018 | 26.161 | 74,8% |
| Uji | 1 Oktober – 31 Desember 2018 | 8.832 | 25,2% |

Kenapa dibagi begini:
- Meniru kondisi nyata: model dilatih dari data masa lalu, lalu dipakai untuk masa depan.
- Hampir sama dengan 75:25 tanpa memotong di tengah bulan.
- Keempat kelas muncul di latih dan uji (sudah di-`assert`).

Catatan kecil: karena baris 00.00 ditaruh di akhir hari, baris `30-09-2018 00:00` (penutup 30 September) ikut ke data latih. Ini sudah benar.

Keterbatasan yang perlu disebut di laporan: data uji hanya 3 bulan (Okt–Des), yang semuanya musim gugur/dingin. Model tidak diuji di musim panas. Kelas Pemborosan Emisi di data uji hanya 269 baris, jadi skornya kurang stabil (satu-dua kesalahan sudah mengubah angka).

---

## 14. Tahap pemodelan (Mahasiswa 2)

### 14.1 Input

Empat CSV dari Bagian 6. **Jangan** memproses ulang dari data mentah. Kalau notebook diubah (misalnya menambah fitur), jalankan ulang notebook dulu supaya 4 CSV ikut berubah.

### 14.2 Skrip siap pakai: `modeling_starter.py`

Sudah diuji berjalan tanpa error (±2–3 menit). Alur di dalamnya:

**Langkah 1 – Baca data**
- Membaca 4 CSV.
- Mendeteksi otomatis mana kolom angka dan mana kolom teks.
- Mengubah label teks jadi angka dengan `LabelEncoder`. Urutan hasil (alfabetis): 0 = Beban Kritis, 1 = Efisien, 2 = Normal, 3 = Pemborosan Emisi.

**Langkah 2 – Satu Pipeline per algoritma**

```
Random Forest : [one-hot untuk teks, angka apa adanya] → RandomForest(class_weight='balanced')
SVM (RBF)     : [one-hot untuk teks, StandardScaler untuk angka] → SVC(class_weight='balanced')
XGBoost       : [one-hot untuk teks, angka apa adanya] → XGBClassifier (+ sample_weight 'balanced')
```

XGBoost tidak punya parameter `class_weight`, jadi bobot kelas diberikan lewat `sample_weight = compute_sample_weight('balanced', y_train)` saat `fit`.

**Langkah 3 – Tuning dengan GridSearchCV + TimeSeriesSplit(4)**

Data latih dibagi 4 lipatan berurutan waktu: latih di bagian awal, validasi di bagian berikutnya. Data uji **tidak disentuh** sama sekali di tahap ini. Pengaturan yang dicoba:

| Model | Parameter yang dicoba |
|---|---|
| Random Forest | n_estimators [200, 400], max_depth [None, 12], min_samples_leaf [1, 5] |
| SVM | C [1, 10, 100], gamma ["scale", 0.1] |
| XGBoost | n_estimators [200, 400], max_depth [4, 6], learning_rate [0.05, 0.1] |

Skor yang dipakai memilih: `f1_macro`.

**Langkah 4 – Evaluasi akhir di data uji**

Untuk tiap model: Accuracy, Precision (macro), Recall (macro), Macro F1 uji, Macro F1 latih (untuk cek overfitting), Macro F1 CV, classification report per kelas, dan gambar confusion matrix.

**Langkah 5 – Simpan model terbaik**

Model dengan Macro F1 uji tertinggi disimpan ke `model_output/`:
- `pipeline_pabrik.pkl` → pipeline lengkap (preprocessing + model)
- `label_encoder.pkl` → untuk mengubah angka hasil tebakan jadi nama kelas
- `urutan_fitur.pkl` → daftar nama dan urutan kolom input
- `perbandingan_model.csv` → tabel perbandingan
- `cm_random.png`, `cm_svm.png`, `cm_xgboost.png` → confusion matrix

### 14.3 Hasil acuan (sekali jalan, 8 fitur)

⚠️ Ini **angka acuan**, bukan hasil final. Jalankan sendiri dan laporkan angka hasil jalanmu sendiri. Angka bisa sedikit berbeda karena versi library.

| Model | Accuracy | Precision | Recall | Macro F1 uji | Macro F1 latih | Macro F1 CV |
|---|---|---|---|---|---|---|
| Random Forest | 0,890 | 0,873 | 0,926 | 0,881 | 0,961 | 0,914 |
| SVM (RBF) | 0,880 | 0,860 | 0,919 | 0,870 | 0,934 | 0,885 |
| **XGBoost** | **0,897** | **0,877** | **0,929** | **0,887** | 0,953 | 0,921 |

Parameter terbaik: RF (max_depth 12, min_samples_leaf 5, 400 pohon); SVM (C 100, gamma scale); XGBoost (learning_rate 0,05, max_depth 4, 200 pohon).

F1 per kelas (data uji):

| Kelas | RF | SVM | XGBoost |
|---|---|---|---|
| Beban Kritis | 0,917 | 0,914 | 0,915 |
| Efisien | 0,942 | 0,932 | 0,951 |
| Normal | **0,667** | **0,648** | **0,683** |
| Pemborosan Emisi | 1,000 | 0,985 | 0,998 |

Contoh confusion matrix (Random Forest standar tanpa tuning, baris = kelas asli, kolom = tebakan):

|  | → Beban Kritis | → Efisien | → Normal | → Pemborosan |
|---|---|---|---|---|
| Beban Kritis (3.251) | 2.807 | 28 | **416** | 0 |
| Efisien (4.307) | 21 | 3.992 | **294** | 0 |
| Normal (1.005) | 52 | 21 | 932 | 0 |
| Pemborosan (269) | 0 | 0 | 0 | 269 |

Cara membacanya: dari 832 kesalahan, 710 (±85%) adalah "salah tebak jadi Normal". Inilah kelemahan utama model.

### 14.4 Bahan untuk bagian "Analisis Model" (wajib menurut panduan §10)

- **Model terbaik**: XGBoost (Macro F1 tertinggi). Alasan yang masuk akal: boosting fokus memperbaiki kesalahan pohon sebelumnya, cocok untuk batas keputusan yang berbentuk ambang tajam (Usage 32,7 kWh, pergantian jam tarif).
- **Model terendah**: SVM. Alasan: SVM membuat batas pemisah yang "halus", padahal batas di data ini "patah/bertangga". Selain itu SVM paling lambat dan tidak bisa langsung memberi probabilitas.
- **Overfitting?** Macro F1 latih (0,93–0,96) lebih tinggi dari uji (0,87–0,89), selisih ±6–8 poin. Sebagian besar selisih ini karena **data uji adalah musim berbeda** (pergeseran jadwal tarif), bukan murni karena model menghafal. Buktinya: menambah info musim memperkecil kesalahan uji (Bagian 14.5).
- **Kesalahan prediksi**: menumpuk di kelas Normal (lihat confusion matrix).
- **Fitur berpengaruh**: Usage_kWh (ambang tinggi/rendah) dan NSM (jam). Bisa ditunjukkan dengan `feature_importances_` dari RF/XGBoost (⏳ belum dibuat, disarankan ditambahkan).
- **Tuning tidak banyak membantu** di data uji (RF tanpa tuning malah 0,894). Masalah utamanya kekurangan informasi (musim), bukan pengaturan model.
- **Keterbatasan**: 1 pabrik, 1 tahun, data uji hanya 3 bulan, label dibuat dari aturan (bukan dari ahli), arti `Load_Type` tidak didokumentasikan resmi.
- **Pengembangan**: tambah fitur musim, gunakan data multi-tahun, validasi label dengan pihak pabrik, tambah fitur lag (pemakaian 15 menit sebelumnya).

Opsional tapi bagus: tambahkan satu model sederhana (Decision Tree atau Logistic Regression) sebagai pembanding dasar.

### 14.5 Opsi perbaikan: fitur `Musim_Tarif` (direkomendasikan, keputusan tim)

Masalah: jadwal Light/Medium/Maximum berbeda per musim, tetapi X tidak punya informasi musim. Solusi: tambah satu kolom teks `Musim_Tarif` di notebook, **sebelum** `Date_Time` dibuang (sel 7):

```python
def musim(bulan):
    if bulan in (11, 12, 1, 2): return "Dingin"
    if bulan in (6, 7, 8):      return "Panas"
    return "Peralihan"          # Maret-Mei, September-Oktober

df["Musim_Tarif"] = df["Date_Time"].dt.month.map(musim)
```

Lalu ubah `assert X_train.shape[1] == 8` menjadi `== 9`. `Musim_Tarif` tidak perlu dimasukkan ke `kolom_buang`. Skrip pemodelan otomatis mengenalinya sebagai kolom teks.

Hasil acuan dengan 9 fitur:

| Model | Macro F1 uji (8 fitur) | Macro F1 uji (9 fitur) | Selisih |
|---|---|---|---|
| XGBoost | 0,887 | **0,932** | +4,5 |
| Random Forest | 0,881 | 0,918 | +3,7 |
| SVM | 0,870 | 0,892 | +2,2 |

Kenapa ini adil (bukan menyontek): musim diketahui dari tanggal, yang pasti tersedia saat prediksi. Data uji Okt–Des berisi musim "Peralihan" dan "Dingin", yang keduanya juga ada di data latih (Mar–Mei, Sep; Jan–Feb).

⚠️ Jangan memakai **nomor bulan** (1–12) sebagai angka. Hasilnya malah turun (0,882), karena bulan 10–12 tidak pernah muncul di data latih, sehingga model tidak tahu harus bagaimana.

Kalau tim memutuskan memakai `Musim_Tarif`: ubah semua "8 fitur" jadi "9 fitur" di PPT, laporan, dan aplikasi. Kalau tidak, bagian lain dokumen ini tetap berlaku.

---

## 15. Tahap aplikasi (Mahasiswa 3)

### 15.1 Bahan dari Mahasiswa 2

Hanya dua file wajib: `pipeline_pabrik.pkl` dan `label_encoder.pkl` (plus `urutan_fitur.pkl` untuk membantu). **Tidak ada** `scaler.pkl` terpisah, karena scaling sudah ada di dalam pipeline.

⚠️ Instruksi lama `scaler.transform(user_input)` **jangan dipakai**: akan error karena input berisi teks (nama hari), dan RF/XGBoost tidak memakai scaler.

### 15.2 Alur aplikasi

```
Pengguna isi form / upload CSV
      ↓
Aplikasi menyusun 1 baris DataFrame dengan nama kolom persis sama
      ↓
pipeline_pabrik.pkl → (one-hot + scaling bila perlu) → model → angka kelas
      ↓
label_encoder.inverse_transform → nama kelas
      ↓
Tampilkan status + warna + probabilitas + penjelasan
```

### 15.3 Rancangan input

Saran supaya input tidak saling bertentangan:

| Input untuk pengguna | Diubah jadi fitur |
|---|---|
| Tanggal (date picker) | `Day_Of_Week` (nama hari bahasa Inggris), `WeekStatus` (Saturday/Sunday → Weekend), `Musim_Tarif` (kalau dipakai) |
| Jam & menit (kelipatan 15) | `NSM = jam × 3600 + menit × 60` |
| Usage (kWh) | `Usage_kWh`, slider 0–160 |
| Lagging Reactive Power (kVarh) | slider 0–100 |
| Leading Reactive Power (kVarh) | slider 0–30 |
| Lagging Power Factor (%) | slider 0–100 |
| Leading Power Factor (%) | slider 0–100 |

Dengan begitu tidak mungkin ada input "Monday tapi Weekend". Sediakan juga fitur **upload CSV** untuk prediksi banyak baris sekaligus (panduan menyebut CSV sebagai bentuk input yang sah).

### 15.4 Kerangka kode Streamlit (`app.py`)

⚠️ Kerangka ini belum dijalankan sebagai aplikasi. Yang sudah diuji: memuat `pipeline_pabrik.pkl`, `predict`, dan `predict_proba` dengan cara di bawah (hasilnya benar).

```python
import datetime as dt
import joblib
import pandas as pd
import streamlit as st

pipe = joblib.load("pipeline_pabrik.pkl")
le = joblib.load("label_encoder.pkl")
FITUR = joblib.load("urutan_fitur.pkl")

st.title("Status Efisiensi Energi Pabrik Baja")

tanggal = st.date_input("Tanggal", dt.date(2018, 10, 1))
jam = st.time_input("Jam (kelipatan 15 menit)", dt.time(9, 0), step=900)
usage = st.slider("Usage (kWh)", 0.0, 160.0, 30.0)
lag_rp = st.slider("Lagging Reactive Power (kVarh)", 0.0, 100.0, 15.0)
lead_rp = st.slider("Leading Reactive Power (kVarh)", 0.0, 30.0, 0.0)
lag_pf = st.slider("Lagging Power Factor (%)", 0.0, 100.0, 85.0)
lead_pf = st.slider("Leading Power Factor (%)", 0.0, 100.0, 100.0)

hari = tanggal.strftime("%A")                      # Monday, Tuesday, ...
baris = {
    "Usage_kWh": usage,
    "Lagging_Current_Reactive_Power_kVarh": lag_rp,
    "Leading_Current_Reactive_Power_kVarh": lead_rp,
    "Lagging_Current_Power_Factor": lag_pf,
    "Leading_Current_Power_Factor": lead_pf,
    "NSM": jam.hour * 3600 + jam.minute * 60,
    "WeekStatus": "Weekend" if hari in ("Saturday", "Sunday") else "Weekday",
    "Day_Of_Week": hari,
}
if "Musim_Tarif" in FITUR:
    b = tanggal.month
    baris["Musim_Tarif"] = "Dingin" if b in (11, 12, 1, 2) else ("Panas" if b in (6, 7, 8) else "Peralihan")

if st.button("Prediksi"):
    X = pd.DataFrame([baris])[FITUR]
    kelas = le.inverse_transform(pipe.predict(X))[0]
    warna = {"Efisien": st.success, "Normal": st.info,
             "Beban Kritis": st.warning, "Pemborosan Emisi": st.error}
    warna[kelas](f"Status: {kelas}")
    if hasattr(pipe, "predict_proba"):
        prob = pd.Series(pipe.predict_proba(X)[0], index=le.classes_)
        st.bar_chart(prob)
```

Jalankan dengan `streamlit run app.py`. ⚠️ `strftime("%A")` menghasilkan nama hari sesuai bahasa sistem; kalau komputer berbahasa Indonesia bisa keluar "Senin". Lebih aman memakai daftar manual: `["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][tanggal.weekday()]`.

### 15.5 Tampilan hasil

- Warna: hijau = Efisien, biru/kuning = Normal, oranye = Beban Kritis, merah = Pemborosan Emisi.
- Tampilkan probabilitas tiap kelas (RF dan XGBoost bisa; SVM hanya kalau dilatih dengan `probability=True`).
- Tampilkan penjelasan arti kelas (pakai kalimat dari tabel Bagian 10.1), supaya manajer tahu harus berbuat apa.
- Hindari efek berkedip (mengganggu dan tidak profesional).

### 15.6 Contoh uji cepat (sudah dicoba dengan model 9 fitur)

| Kondisi | Hasil tebakan |
|---|---|
| Selasa, Juli, 11.00, Usage 60 kWh | Beban Kritis |
| Selasa, Juli, 03.00, Usage 3,5 kWh | Efisien |
| Selasa, Juli, 08.30, Usage 60 kWh | Pemborosan Emisi |

Contoh-contoh ini bagus untuk video demo, karena menunjukkan pengaruh jam dan pemakaian dengan jelas.

### 15.7 Deployment (opsional)

Bisa di-deploy gratis ke Streamlit Community Cloud: unggah `app.py`, dua/tiga file `.pkl`, dan `requirements.txt` (berisi `streamlit`, `pandas`, `scikit-learn`, `xgboost`, `joblib`) ke GitHub, lalu hubungkan. ⚠️ Versi scikit-learn dan xgboost di server harus sama dengan saat model dilatih, kalau tidak file `.pkl` bisa gagal dibuka. Tulis versinya di `requirements.txt` (contoh `scikit-learn==1.9.1`).

---

## 16. Status proyek dan checklist

### 16.1 Yang sudah selesai ✅

- Pemilihan dataset dan tema
- Notebook preprocessing + EDA, berjalan tanpa error
- 4 CSV latih/uji
- 6 grafik EDA
- Skrip pemodelan awal (sudah diuji)
- Draf PPT 7 slide (judul, latar belakang, dataset, tujuan, model, metrik)

### 16.2 Yang harus dikerjakan ⏳

**Notebook / kode**
- [ ] Tambahkan percobaan random split vs time split ke notebook (Bagian 10.4)
- [ ] Putuskan pakai `Musim_Tarif` atau tidak (Bagian 14.5)
- [ ] Jalankan pemodelan, simpan tabel perbandingan dan confusion matrix
- [ ] Tambah grafik feature importance
- [ ] Buat aplikasi Streamlit
- [ ] Hapus sel kosong dan `.ipynb_checkpoints/`, simpan hanya satu file data mentah
- [ ] Beri komentar secukupnya di kode (panduan §12)

**PPT (panduan §14 mewajibkan bagian A–O)**

| Bagian | Status |
|---|---|
| A. Judul, nama, NIM, **kelas** | Sebagian (kelas belum ada) |
| B. Latar belakang & masalah | Ada |
| C. Tujuan | Ada |
| D. Studi literatur (min. 5 jurnal) | ⏳ |
| E. Dataset | Ada, ⚠️ angka salah (Bagian 17) |
| F. EDA (grafik + penjelasan) | ⏳ (bahan di Bagian 11) |
| G. Preprocessing | ⏳ (bahan di Bagian 8 dan 12) |
| H. Pengembangan model (algoritma, split, parameter, proses) | Sebagian |
| I. Evaluasi & perbandingan | ⏳ |
| J. Pemilihan model terbaik | ⏳ |
| K. Implementasi aplikasi (arsitektur, teknologi, input/proses/output) | ⏳ |
| L. Demo | ⏳ |
| M. Kesimpulan | ⏳ |
| N. Keterbatasan & pengembangan | ⏳ (bahan di Bagian 14.4) |
| O. Pembagian tugas | ⏳ |

**Dokumen lain yang dikumpulkan**
- [ ] Daftar 5 jurnal referensi
- [ ] Tabel studi literatur (kolom: No, Penulis & Tahun, Permasalahan, Dataset, Metode, Metrik, Hasil, Perbedaan dengan Project)
- [ ] Video demo ≤ 7 menit (perkenalan, judul, latar belakang, dataset, preprocessing, algoritma, perbandingan, model terbaik, demo aplikasi berjalan, kesimpulan)
- [ ] Source code / link repository
- [ ] Dataset atau link dataset
- [ ] File model (.pkl)
- [ ] Link aplikasi (kalau di-deploy)

### 16.3 Tips studi literatur

Jurnal pertama yang pasti relevan: paper asal dataset, Sathishkumar, Shin & Cho (2021), *Building Research & Information* 49(1), 127–143. Paper ini melakukan **prediksi konsumsi energi (regresi)**, jadi di kolom "Perbedaan dengan Project" tulis: "Proyek kami mengklasifikasikan status efisiensi berdasarkan aturan periode beban dan emisi, bukan memprediksi nilai kWh."

Cari 4 jurnal lain dengan kata kunci seperti: *steel industry energy consumption machine learning*, *industrial energy efficiency classification*, *random forest XGBoost SVM energy*, *imbalanced classification macro F1*, *time series cross validation*. Usahakan jurnal yang memakai dataset yang sama atau masalah serupa.

⚠️ Handover PDF lama menyebut 8 fitur "terbukti relevan menurut Sathishkumar et al. (2020) dengan Boruta dan RFE". Klaim ini **belum diverifikasi** (tahun paper juga 2021, bukan 2020). Jangan tulis klaim itu sebelum membaca paper aslinya dan memastikan isinya.

---

## 17. Kesalahan di dokumen lama yang sudah diperbaiki

Supaya tidak terulang di PPT/laporan.

| No | Di dokumen lama | Yang benar | Prioritas |
|---|---|---|---|
| 1 | PDF: kelas "Moderat" | **Normal** (sesuai notebook dan CSV) | Tinggi |
| 2 | PPT: data setelah cleaning 35.040, "0 duplikat" | 35.040 (resmi) → buang 47 → **34.993**. Ada 1 timestamp ganda di salinan kelompok | Tinggi |
| 3 | PPT: latih 26.280 (75%), uji 8.760 (25%) | **26.161 (74,8%) / 8.832 (25,2%)**, Jan–Sep / Okt–Des | Tinggi |
| 4 | PDF: Mahasiswa 2 memakai `dataset_preprocessed.npz` (sudah scaling + SMOTE) | File itu tidak ada. Pakai 4 CSV; scaling dan imbalance di Pipeline | Tinggi |
| 5 | PDF: scaling + SMOTE oleh Mahasiswa 1 | Tidak ada SMOTE. Scaling oleh Mahasiswa 2 di Pipeline, hanya untuk SVM | Tinggi |
| 6 | PDF: aplikasi pakai `scaler.pkl` + `scaler.transform` | Pakai `pipeline_pabrik.pkl` + `pipe.predict` | Tinggi |
| 7 | PDF/PPT: Load_Type = beban mesin; Pemborosan Emisi = anomali/kerusakan | Load_Type = periode tarif berdasarkan waktu; Pemborosan = pemakaian tinggi saat tarif ringan | Tinggi |
| 8 | PDF: Power Factor membedakan mesin "efektif vs rusak" | Tidak ada data kerusakan. PF mengukur kualitas pemakaian listrik | Sedang |
| 9 | PPT: "data sudah di-scaling" | Scaling hanya di dalam pipeline SVM | Sedang |
| 10 | Handover md: menyebut `preprocessing_eda.py` | File yang ada `Source-kode.ipynb` | Sedang |
| 11 | Handover md: file asli 35.041 baris | File resmi 35.040; baris ke-35.041 hanya di salinan kelompok | Sedang |
| 12 | Handover md: CO2 cocok dengan Usage 99,9% | Setelah cleaning: **100%** | Rendah |
| 13 | PDF: Date dibuang karena waktu sudah terwakili NSM/hari | Musim tidak terwakili (Bagian 14.5) | Sedang |
| 14 | PDF: ambang 0,02 = Kuartil 3 | Q3 memang 0,02, tetapi menandai 35,8% data. Pembenaran lebih kuat: 0,02 tCO2 ≈ 32,7 kWh | Sedang |
| 15 | Perbandingan random vs time split (0,958 vs 0,898) hanya ditulis, tidak ada di notebook | Jalankan di notebook | Sedang |
| 16 | PPT: sumber "Kaggle/UCI"; PDF: paper tahun 2020 | UCI, DOI 10.24432/C52G8C; paper 2021 | Rendah |
| 17 | PDF: NSM 0–86.400 | 0–85.500 | Rendah |
| 18 | PPT: typo "WeeksStatus" | WeekStatus | Rendah |

---

## 18. Larangan (hal yang tidak boleh dilakukan)

1. ❌ Memasukkan `CO2(tCO2)` atau `Load_Type` ke X → data leakage (model menyontek jawaban).
2. ❌ Membagi data secara acak (`train_test_split(..., shuffle=True)`) → skor palsu tinggi.
3. ❌ Memakai K-Fold biasa (acak) untuk tuning → ganti dengan `TimeSeriesSplit`.
4. ❌ Melakukan scaling/SMOTE ke seluruh data sebelum split → leakage.
5. ❌ Memakai data uji untuk memilih parameter, lalu melaporkan skor uji itu sebagai hasil akhir.
6. ❌ Mengurutkan ulang baris dengan `sort_values` → urutan jam 00.00 akan berantakan.
7. ❌ Mengubah urutan atau nama kolom input di aplikasi → pipeline error atau salah prediksi.
8. ❌ Memilih model berdasarkan akurasi saja.
9. ❌ Menyebut Pemborosan Emisi sebagai "deteksi kerusakan mesin" atau mengklaim model "menemukan pola tersembunyi".
10. ❌ Melaporkan angka acuan di dokumen ini tanpa menjalankan sendiri.
11. ❌ Menghapus outlier IQR (akan membuang ribuan baris produksi yang sah).

---

## 19. Persiapan tanya jawab

Setiap anggota sebaiknya bisa menjawab semua pertanyaan ini.

**Tentang masalah dan dataset**

1. *Kenapa memilih topik ini?* Industri baja sangat boros energi. Angka kWh mentah sulit dibaca manajer; status 4 kelas lebih mudah ditindaklanjuti.
2. *Dari mana datanya?* UCI ML Repository, data asli pabrik DAEWOO Steel Korea Selatan tahun 2018, 15 menitan, 35.040 baris.
3. *Apa itu NSM?* Detik sejak tengah malam; 09.15 = 33.300.
4. *Apa bedanya lagging dan leading?* Lagging: arus tertinggal tegangan, karena beban induktif (motor). Leading: arus mendahului, karena beban kapasitif (kapasitor).
5. *Apakah CO2 diukur sensor?* Tidak. Dihitung dari kWh dengan faktor emisi.

**Tentang preprocessing**

6. *Kenapa membuang 47 baris?* CO2 tercatat 0 padahal pemakaian sampai 147 kWh, semuanya di 2 Januari. Kalau dibiarkan, labelnya salah.
7. *Kenapa outlier tidak dibuang?* Lolos pengecekan fisik; nilai tinggi = produksi puncak yang nyata; untuk LeadRP/LeadPF IQR menganggap ribuan nilai wajar sebagai outlier karena data menumpuk di 0/100.
8. *Kenapa CO2 dan Load_Type dibuang?* Keduanya bahan pembuat target. Kalau dimasukkan, model tinggal menyalin aturannya (leakage).
9. *Tapi Usage kan sama dengan CO2?* Ya, dan kami mengakuinya. Usage tetap dipakai karena di dunia nyata memang tersedia saat prediksi dan merupakan indikator utama. Konsekuensinya, sebagian tugas model mudah, dan kami menulisnya di keterbatasan.
10. *Kenapa split berdasarkan waktu, bukan acak?* Data deret waktu; baris berdekatan sangat mirip. Split acak menaikkan skor palsu (0,961 vs 0,895).
11. *Kenapa tidak SMOTE?* class_weight cukup, tidak membuat data palsu, tidak bocor, dan cocok untuk fitur kategori.
12. *Kenapa scaling hanya untuk SVM?* SVM menghitung jarak, jadi skala berpengaruh. Pohon keputusan hanya membandingkan "lebih besar/kecil dari", skala tidak berpengaruh.

**Tentang target**

13. *Kenapa ambang 0,02?* Setara ±32,7 kWh per 15 menit, batas antara kondisi idle (±4 kWh) dan produksi (±40–60 kWh).
14. *Apa arti Load_Type?* Berdasarkan analisis kami, mengikuti jadwal waktu (jam, hari, musim), sehingga lebih tepat dibaca sebagai periode tarif listrik.
15. *Kenapa Pemborosan Emisi hampir 100% benar?* Kelas ini hampir selalu terjadi di jam yang pasti Light (00.00–09.59, sebagian kecil jam 23) dengan pemakaian tinggi; aturannya mudah dipelajari dari NSM + Usage.

**Tentang model dan evaluasi**

16. *Kenapa Macro F1?* Kelas tidak seimbang; Macro F1 memberi bobot sama ke tiap kelas sehingga kelas kecil tidak tenggelam.
17. *Kenapa 3 algoritma itu?* Mewakili 3 pendekatan berbeda: bagging (RF), margin/non-pohon (SVM), boosting (XGBoost).
18. *Model mana terbaik dan kenapa?* XGBoost; Macro F1 tertinggi; cocok untuk batas keputusan bertangga.
19. *Apakah overfitting?* Ada selisih latih–uji ±6–8 poin, sebagian besar karena perbedaan musim antara data latih dan uji.
20. *Kelas mana paling sulit dan kenapa?* Normal; model sering salah menganggap jam Light/Maximum sebagai Medium karena jadwal tarif bergeser per musim dan model tidak tahu musim.
21. *Bagaimana memperbaikinya?* Tambah fitur Musim_Tarif (Macro F1 naik sampai +4,5 poin).

**Tentang aplikasi**

22. *Bagaimana input pengguna diproses?* Disusun jadi DataFrame dengan nama kolom sama, lalu dimasukkan ke pipeline yang otomatis melakukan encoding/scaling, lalu hasil angka diubah jadi nama kelas dengan label encoder.
23. *Kenapa satu file pipeline, bukan scaler + model terpisah?* Mencegah lupa atau salah urutan langkah, dan menjamin input aplikasi diproses sama persis seperti saat training.

---

## 20. Referensi

- V E, S., Shin, C., & Cho, Y. (2021). *Steel Industry Energy Consumption* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52G8C (lisensi CC BY 4.0)
- Sathishkumar, V. E., Shin, C., & Cho, Y. (2021). Efficient energy consumption prediction model for a data analytic-enabled industry building in a smart city. *Building Research & Information*, 49(1), 127–143.
- M15 – Project dan Refleksi (Panduan Project Machine Learning).
- Dokumentasi scikit-learn: Pipeline, ColumnTransformer, TimeSeriesSplit, GridSearchCV, f1_score.
- Dokumentasi XGBoost: XGBClassifier, parameter `sample_weight`.
