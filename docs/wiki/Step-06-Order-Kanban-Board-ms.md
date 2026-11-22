[English](Step-06-Order-Kanban-Board) · [Dansk](Step-06-Order-Kanban-Board-da) · **Bahasa Malaysia**

# Langkah 6: Papan Kanban pesanan

Pemilik kedai mengikuti setiap pesanan berbayar pada papan Kanban, dan setiap pelanggan melihat status pesanan mereka sendiri.

![Langkah 6](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-06.png)

## Aliran status

Pesanan bergerak melalui lima lajur: **Needs confirmation**, **Confirmed**, **Being packed**, **Shipped** dan **Delivered**. Pesanan berbayar bermula di hujung lajur pertama. Pemilik menyeret kad ke lajur lain, atau dalam satu lajur untuk menukar tempatnya, dan kedai menyimpan status dan kedudukan baharu. Kedudukan dinomborkan semula dalam lajur sumber dan sasaran dalam satu transaksi, jadi susunan kad sama selepas dimuat semula.

## Papan

Halaman papan hanya untuk admin: pelawat yang belum log masuk dihantar ke halaman log masuk dan pelanggan mendapat 403. Setiap kad menunjukkan nombor pesanan, e-mel pelanggan, item dan jumlah. Halaman menggunakan JavaScript biasa dan seret-dan-lepas pelayar sendiri tanpa pustaka. Pemindahan ditunjukkan serta-merta dan kemudian dihantar ke kedai dengan token CSRF; jika kedai menolaknya, kad melompat kembali dan mesej dipaparkan. Satu select pada setiap kad melakukan pemindahan yang sama tanpa menyeret, untuk papan kekunci dan telefon. Pada lebar 400 piksel lajur boleh digulung ke sisi.

## Digunakan semula daripada Hari 89

Reka letak dan idea seret-dan-lepas datang daripada senarai tugasan Hari 89: senarai menjadi lajur status dan kad menjadi pesanan. Kod ditulis semula untuk tema gelap kedai ini dan API sendiri.

## Sejarah pesanan pelanggan

Halaman Orders menyenaraikan pesanan pelanggan yang telah log masuk sahaja, yang terbaharu dahulu, dengan item, jumlah dan lencana status.

## Ujian

Ujian pelayar dalam bekas Docker menyeret pesanan ke Confirmed, memuat semula halaman dan menyemak bahawa ia kekal di situ, dan bahawa pelanggan tidak boleh membuka papan.

## Apa yang saya pelajari

- Menyimpan kedudukan dan bukan status sahaja menjadikan seretan kekal selepas dimuat semula.
- Melakukan pemindahan dalam satu transaksi mengekalkan lajur konsisten.
- Kawalan yang melakukan perkara sama tanpa menyeret menjadikan papan berguna pada telefon dan dengan papan kekunci.
