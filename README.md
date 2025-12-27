# Analisis Keterlambatan Pengiriman & Dampaknya terhadap Kepuasan Pelanggan (Olist)

## Deskripsi Singkat
Proyek ini menganalisis pola **keterlambatan pengiriman** pada e-commerce Olist dan dampaknya terhadap **kepuasan pelanggan** yang diukur melalui **`review_score`**. Output utama proyek berupa:
- Notebook analisis/EDA + ringkasan insight: `test.ipynb`
- Dashboard interaktif (Streamlit): `dashboard.py`

## Dataset yang Digunakan
Dataset yang digunakan berada di folder `datasets/` (format CSV), berasal dari dataset publik Olist (Brazilian E-Commerce). File yang dipakai pada analisis/dashboard ini:
- `datasets/olist_orders_dataset.csv`
- `datasets/olist_order_reviews_dataset.csv`
- `datasets/olist_customers_dataset.csv`

Catatan: Di folder `datasets/` juga tersedia file CSV lain (mis. item, pembayaran, produk, seller) yang belum digunakan pada analisis ini.

## Cara Menjalankan
### 1) Setup Environment & Install Dependencies
Disarankan menggunakan virtual environment.

```bash
pip install -r requirements.txt
```

### 2) Menjalankan Notebook
File notebook: `test.ipynb`

Opsi menjalankan:
- **VS Code**: buka `test.ipynb` lalu jalankan cell berurutan (Run All).
- **Jupyter Notebook/Lab**: jalankan dari folder root proyek.

Jika memakai Jupyter:
```bash
jupyter notebook
```
atau
```bash
jupyter lab
```

### 3) Menjalankan Dashboard (Streamlit)
File dashboard: `dashboard.py`

```bash
streamlit run dashboard.py
```

## Ringkasan Insight Hasil Analisis
Definisi variabel utama:
- `delivery_delay_days` = `order_delivered_customer_date` − `order_estimated_delivery_date` (positif = terlambat, negatif = lebih cepat)
- `is_late` = 1 jika `delivery_delay_days` > 0, 0 jika tidak (NaN bila tanggal tidak lengkap)

Insight utama:
1. **Keterlambatan pengiriman berkorelasi dengan penurunan kepuasan pelanggan**: pesanan terlambat cenderung memiliki `review_score` lebih rendah dibanding pesanan tepat waktu.
2. **Mayoritas pesanan berada dekat 0 hari keterlambatan**, namun ada ekor/outlier keterlambatan yang cukup ekstrem.
3. **Rasio keterlambatan berbeda antar provinsi (`customer_state`)**, sehingga bisa menjadi titik awal investigasi operasional/logistik untuk wilayah tertentu.

## (Opsional) Screenshot Dashboard
Tambahkan screenshot dashboard ke repository, misalnya simpan di `docs/screenshot-dashboard.png`, lalu tautkan di sini.

Contoh:
```md
![Dashboard Screenshot](docs/screenshot-dashboard.png)
```
