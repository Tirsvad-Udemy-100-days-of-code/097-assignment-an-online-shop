[English](Step-04-Shopping-Basket) · [Dansk](Step-04-Shopping-Basket-da) · **Bahasa Malaysia**

# Langkah 4: Bakul beli-belah

Pembeli yang telah log masuk kini boleh mengumpul produk dalam bakul, menukar kuantiti, membuang baris dan melihat jumlah.

![Langkah 4](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-04.png)

## Model

`Basket` mengandungi nilai `BasketLine`: id produk dan kuantiti. Bakul tidak menyalin harga. Harga dibaca daripada produk apabila bakul dipaparkan, jadi perubahan harga kelihatan serta-merta. Jumlah ialah hasil tambah harga darab kuantiti dalam sen, dikira dalam domain dengan nilai `Money` daripada langkah 2, jadi ia tepat. Kuantiti mempunyai had; menetapkannya kepada 0 membuang baris, dan menambah produk yang sama dua kali menaikkan kuantiti satu baris dan bukan membuat dua baris.

## Storan

Bakul dimiliki oleh pengguna yang telah log masuk dan disimpan dalam SQLite, dalam dua jadual: satu bakul bagi setiap pengguna dan satu baris bagi setiap produk di dalamnya, unik bagi setiap pengguna dan produk. Ia kekal selepas log keluar dan log masuk. Pelawat yang belum log masuk dihantar ke halaman log masuk apabila cuba menambah sesuatu.

## Halaman

Kad katalog dan halaman produk masing-masing mempunyai borang "tambah ke bakul" dengan token CSRF daripada langkah 3. Halaman bakul menyenaraikan baris dengan input kuantiti, butang kemas kini dan buang, serta jumlah. Pengepala menunjukkan bilangan item di sebelah ikon bakul.

## Apa yang saya pelajari

- Simpan hanya apa yang tidak boleh diterbitkan: id produk dan kuantiti. Harga datang daripada produk.
- Mengira dalam sen bulat di satu tempat mengekalkan jumlah yang tepat.
- Menggunakan semula pengawal CSRF dan ubah hala log masuk bermakna bakul tidak memerlukan kod keselamatan baharu.
