# 🚗 → 🌿 Less Cars, More Life | UK Co-Benefits Dashboard

Dashboard interaktif untuk mengeksplorasi co-benefits (manfaat bersama) dari pengurangan penggunaan mobil di United Kingdom. Dashboard ini menganalisis manfaat ekonomi, kesehatan, dan lingkungan dari transportasi berkelanjutan dari tahun 2025 hingga 2050.

## 📋 Deskripsi Proyek

Dashboard ini memvisualisasikan data co-benefits yang mencakup:
- **Air Quality** - Kualitas udara
- **Physical Activity** - Aktivitas fisik
- **Road Safety** - Keselamatan jalan
- **Noise** - Kebisingan
- **Congestion** - Kemacetan

Dashboard menyediakan visualisasi interaktif termasuk peta choropleth, grafik temporal, dan analisis komparatif antar wilayah.

## 🛠️ Persyaratan Sistem

- Python 3.8 atau lebih tinggi
- pip (Python package manager)
- Git (untuk deployment ke Streamlit Cloud)

## 📦 Instalasi Lokal

### Langkah 1: Clone Repository

```bash
git clone <url-repository-anda>
cd ari
```

Atau jika Anda sudah memiliki folder proyek, pastikan Anda berada di direktori proyek:

```bash
cd /path/ke/proyek/ari
```

### Langkah 2: Buat Virtual Environment (Disarankan)

**Untuk macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Untuk Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Langkah 3: Install Dependencies

Install semua package yang diperlukan menggunakan `requirements.txt`:

```bash
pip install -r requirements.txt
```

Atau install secara manual:

```bash
pip install streamlit pandas plotly numpy folium streamlit-folium
```

### Langkah 4: Pastikan File Data Tersedia

Pastikan file-file berikut ada di direktori proyek:
- `Level_3.csv`
- `lookups.csv`
- `app.py`

### Langkah 5: Jalankan Aplikasi

Jalankan aplikasi Streamlit:

```bash
streamlit run app.py
```

Aplikasi akan otomatis terbuka di browser Anda di `http://localhost:8501`

### Troubleshooting Instalasi Lokal

**Error: ModuleNotFoundError**
- Pastikan virtual environment sudah diaktifkan
- Pastikan semua dependencies sudah terinstall: `pip install -r requirements.txt`

**Error: FileNotFoundError untuk CSV**
- Pastikan file `Level_3.csv` dan `lookups.csv` berada di direktori yang sama dengan `app.py`

**Port sudah digunakan**
- Gunakan port lain: `streamlit run app.py --server.port 8502`

## ☁️ Deployment ke Streamlit Cloud

### Prasyarat

1. Akun GitHub (gratis)
2. Akun Streamlit Cloud (gratis di [streamlit.io](https://streamlit.io/cloud))

### Langkah 1: Siapkan Repository GitHub

1. Buat repository baru di GitHub (atau gunakan yang sudah ada)
2. Pastikan file berikut ada di repository:
   - `app.py`
   - `requirements.txt`
   - `Level_3.csv`
   - `lookups.csv`
   - `README.md` (file ini)

### Langkah 2: Push ke GitHub

```bash
git init
git add .
git commit -m "Initial commit: UK Co-Benefits Dashboard"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY-NAME.git
git push -u origin main
```

**Catatan:** Ganti `USERNAME` dan `REPOSITORY-NAME` dengan informasi repository Anda.

### Langkah 3: Deploy ke Streamlit Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io/)
2. Login dengan akun GitHub Anda
3. Klik tombol **"New app"**
4. Isi form deployment:
   - **Repository:** Pilih repository yang berisi proyek Anda
   - **Branch:** `main` (atau branch yang Anda gunakan)
   - **Main file path:** `app.py`
   - **App URL:** (opsional) pilih URL custom atau biarkan default
5. Klik **"Deploy!"**

### Langkah 4: Tunggu Deployment Selesai

Streamlit Cloud akan:
1. Menginstall dependencies dari `requirements.txt`
2. Menjalankan `app.py`
3. Menyediakan URL publik untuk aplikasi Anda

Proses ini biasanya memakan waktu 2-5 menit.

### Troubleshooting Deployment Streamlit Cloud

**Error: ModuleNotFoundError**
- Pastikan `requirements.txt` ada di root repository
- Pastikan semua dependencies tercantum di `requirements.txt`
- Cek log deployment untuk detail error

**Error: FileNotFoundError untuk CSV**
- Pastikan file CSV ada di repository dan di-commit ke GitHub
- Pastikan file CSV tidak terlalu besar (Streamlit Cloud memiliki batas ukuran file)
- Jika file terlalu besar, pertimbangkan menggunakan GitHub LFS atau hosting file di tempat lain

**Error: Timeout atau Memory Error**
- File `Level_3.csv` mungkin terlalu besar
- Pertimbangkan untuk:
  - Menggunakan `@st.cache_data` dengan parameter `ttl` atau `max_entries`
  - Membagi data menjadi file yang lebih kecil
  - Menggunakan database eksternal atau API

**Warning: cat: /mount/admin/install_path**
- Ini adalah warning internal Streamlit Cloud yang tidak mempengaruhi fungsi aplikasi
- Dapat diabaikan jika aplikasi berjalan dengan baik

## 📁 Struktur Proyek

```
ari/
├── app.py                 # File utama aplikasi Streamlit
├── requirements.txt       # Dependencies Python
├── Level_3.csv           # Data co-benefits level 3
├── lookups.csv           # Data lookup untuk mapping
├── Level_1.csv           # (Opsional) Data level 1
├── Level_2.csv           # (Opsional) Data level 2
└── README.md             # Dokumentasi proyek
```

## 🚀 Fitur Dashboard

1. **Interactive Map** - Peta choropleth interaktif untuk melihat distribusi co-benefits per wilayah
2. **Temporal Analysis** - Grafik timeline untuk melihat perkembangan manfaat dari 2025-2050
3. **Benefit Categories** - Analisis distribusi manfaat berdasarkan kategori
4. **City Comparison** - Perbandingan co-benefits antar kota/wilayah
5. **Health Correlation** - Analisis korelasi antara manfaat kesehatan dan non-kesehatan

## 📊 Data Source

Data berasal dari:
- Sudmant, A., Higgins-Lavery, R. (2025). *The Co-Benefits of Reaching Net-Zero in the UK*.
- Edinburgh Climate Change Institute, University of Edinburgh.

## 🔧 Konfigurasi Tambahan

### Mengubah Port Lokal

```bash
streamlit run app.py --server.port 8502
```

### Mengubah Tema

Edit konfigurasi di `app.py` bagian `st.set_page_config()` atau buat file `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#22c55e"
backgroundColor = "#020617"
secondaryBackgroundColor = "#0f172a"
textColor = "#e5e7eb"
```

## 📝 Catatan Penting

- File `Level_3.csv` cukup besar (~928K baris), pastikan koneksi internet stabil saat deployment
- Dashboard menggunakan caching (`@st.cache_data`) untuk optimasi performa
- Pastikan semua file CSV menggunakan encoding UTF-8

## 🐛 Melaporkan Bug

Jika Anda menemukan bug atau memiliki saran, silakan buat issue di repository GitHub atau hubungi pengembang.

## 📄 Lisensi

Proyek ini dikembangkan untuk Data Visualisation Project 2025.

---

**Dikembangkan dengan ❤️ menggunakan Streamlit**

