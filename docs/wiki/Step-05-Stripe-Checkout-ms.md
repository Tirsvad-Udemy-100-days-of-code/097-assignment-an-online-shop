[English](Step-05-Stripe-Checkout) · [Dansk](Step-05-Stripe-Checkout-da) · **Bahasa Malaysia**

# Langkah 5: Pembayaran Stripe

Pembeli membayar melalui Stripe Checkout dalam mod ujian, dan hanya sesi yang dibayar mencipta pesanan.

![Langkah 5](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-05.png)

## Aliran

1. Halaman bakul mempunyai butang **Checkout**. Ia menghantar ke kedai, yang mencipta Checkout Session di Stripe dengan satu item bagi setiap baris bakul dan menghantar pelayar ke halaman pembayaran Stripe.
2. Selepas membayar, Stripe menghantar pembeli kembali ke alamat kejayaan yang membawa id sesi.
3. Kedai tidak mempercayai alamat itu. Ia bertanya kepada Stripe tentang sesi tersebut dan mencipta pesanan hanya apabila Stripe berkata ia telah dibayar dan sesi itu milik pengguna yang log masuk. Membuka alamat yang sama dua kali menghasilkan satu pesanan, kerana id sesi adalah unik.
4. Jika pembeli membatalkan, bakul dikekalkan dan tiada pesanan dicipta.

Pesanan baharu mempunyai status "Needs confirmation". Bakul dikosongkan hanya selepas pesanan disimpan.

## Port dan palsu

Kedai bercakap dengan port `PaymentGateway`. Penyesuai Stripe memanggil API REST dengan `urllib`, mengekod medan bersarang sebagai borang. Ujian menggunakan gerbang palsu dan, untuk penyesuai, pelayan tempatan kecil yang berlakon sebagai Stripe, jadi tiada ujian menyentuh rangkaian.

## Mod ujian dan kunci

Kunci ujian dibaca daripada fail `stripe.env` tempatan yang diabaikan oleh git. Kedai menolak sebarang kunci yang bukan kunci ujian. Kunci tidak pernah dicetak, dilog atau dimasukkan dalam mesej ralat, dan tanpa fail itu kedai membaca pemboleh ubah persekitaran `PUBLISHABLE_KEY` dan `SECRET_KEY`, atau, jika tiada satu pun, masih bermula dengan butang Checkout disembunyikan. Dalam mod ujian anda membayar dengan kad `4242 4242 4242 4242`, sebarang tarikh akan datang dan sebarang CVC.

## Apa yang saya pelajari

- Jangan sekali-kali mencipta pesanan daripada alamat kembali sahaja; tanya penyedia apa yang berlaku.
- Id sesi yang unik menjadikan halaman kejayaan selamat dimuat semula.
- Rahsia memerlukan tiga peraturan: dijauhkan daripada git, dijauhkan daripada output dan disemak untuk mod yang betul sebelum digunakan.
