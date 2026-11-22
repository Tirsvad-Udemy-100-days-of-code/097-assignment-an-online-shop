[English](Step-03-Registration-and-Login) · [Dansk](Step-03-Registration-and-Login-da) · **Bahasa Malaysia**

# Langkah 3: Pendaftaran dan log masuk

Pelawat kini boleh mendaftar, log masuk dan log keluar, dan kedai mempunyai peranan admin.

![Langkah 3](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-03.png)

## Cincang kata laluan

Kata laluan tidak pernah disimpan. Kedai menyimpan cincangan `scrypt` bergaram yang dibuat dengan `hashlib.scrypt`, dalam bentuk `scrypt$n$r$p$salt$key`. Parameter kos berada dalam cincangan itu sendiri, jadi ia boleh dinaikkan kemudian tanpa merosakkan akaun lama. Semakan kata laluan membandingkan cincangan dengan `hmac.compare_digest`, yang mengambil masa yang sama sama ada sama atau tidak. Jika e-mel tidak dikenali, kedai tetap mencincang terhadap cincangan palsu, dan kedua-dua kegagalan menunjukkan satu mesej, supaya penyerang tidak dapat tahu bahagian mana yang salah.

## Sesi

Kuki sesi bertandatangan Flask mengekalkan pengguna log masuk. Ia `HttpOnly` supaya skrip tidak dapat membacanya, `SameSite=Lax`, dan tamat selepas tujuh hari. Kunci datang daripada `SHOP_SECRET_KEY`. Log masuk mengosongkan sesi lama dahulu, jadi id sesi yang ditetapkan sebelum log masuk tidak pernah digunakan semula (session fixation).

## CSRF

Setiap borang membawa `csrf_token` tersembunyi. Permintaan yang mengubah keadaan (POST, PUT, PATCH, DELETE) tanpa token yang sepadan ditolak dengan 403. Log keluar juga POST atas sebab yang sama. Selepas log masuk, kedai hanya mengikuti alamat `next` yang merupakan laluan tempatan, supaya pautan tidak dapat menghantar pengguna ke laman lain.

## Admin

Akaun admin dicipta semasa permulaan daripada `SHOP_ADMIN_EMAIL` dan `SHOP_ADMIN_PASSWORD`; tiada kata laluan lalai dalam kod. `/admin` menghantar pelawat yang belum log masuk ke halaman log masuk, menjawab 403 kepada pelanggan dan memaparkan halaman kepada admin.

## Apa yang saya pelajari

- Cincang dengan fungsi yang perlahan dan bergaram, dan bandingkan dalam masa tetap.
- Ralat yang sama untuk setiap log masuk yang gagal memberi penyerang kurang bahan.
- Peraturan keselamatan sebagai satu pengawal yang dilalui setiap permintaan lebih mudah diuji daripada semakan pada setiap halaman.
