[English](Step-02-Product-Catalog) · [Dansk](Step-02-Product-Catalog-da) · **Bahasa Malaysia**

# Langkah 2: Katalog produk dan storan

Kedai kini menyimpan produk dalam SQLite dan memaparkannya: grid di halaman utama dan halaman butiran untuk setiap produk.

![Langkah 2](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-02.png)

## Lapisan

Lapisan `domain` mengandungi entiti `Product`, nilai `Money` dan port `ProductRepository`. Lapisan `application` mengandungi use case yang menyenaraikan produk dan mengambil satu produk, dan memulangkan DTO. Lapisan `infrastructure` mengandungi penyesuai SQLite. Lapisan `presentation` melukis halaman. Import menghala ke dalam: domain dan application tidak pernah mengimport infrastructure atau presentation, jadi peraturan boleh diuji tanpa pangkalan data atau pelayan.

## SQLite

Repositori menggunakan `sqlite3` daripada pustaka standard. Skema dicipta semasa permulaan dan produk contoh dimasukkan, jadi data berada dalam fail dan kekal selepas dimulakan semula. Pertanyaan menggunakan pemegang tempat, tidak pernah pemformatan rentetan.

## Wang dalam sen

Harga ialah bilangan bulat unit terkecil (sen) dalam nilai `Money` yang menolak jumlah negatif. Nombor perpuluhan tidak dapat mewakili kebanyakan harga perpuluhan dengan tepat, jadi jumlah tersasar. Integer dijumlahkan dengan tepat, dan halaman hanya memformat sen sebagai harga apabila melukisnya.

## Apa yang saya pelajari

- Port dalam domain membolehkan use case dijalankan terhadap repositori palsu dalam ujian unit.
- DTO mengekalkan entiti di luar view.
- Melepaskan (escape) semua nilai pangkalan data sebelum sampai ke HTML ialah peraturan untuk pembantu view, bukan untuk setiap halaman.
