[English](Step-07-Reflection) · [Dansk](Step-07-Reflection-da) · **Bahasa Malaysia**

# Langkah 7: Refleksi

## Bagaimana saya mendekati projek

Saya merancang dahulu. Kes perniagaan, pihak berkepentingan, pelan projek dan tujuh pencapaian ditulis dan disemak sebelum sebarang kod, dan setiap pencapaian melalui satu pull request dengan rekod semakannya sendiri. Kod berada dalam empat lapisan (domain, aplikasi, infrastruktur, persembahan), jadi peraturan kedai tidak bergantung pada Flask, SQLite atau Stripe, dan kebanyakan daripada 340 ujian berjalan tanpa pelayar. Saya memilih papan Kanban untuk pesanan kerana sesuatu pesanan melalui beberapa langkah yang jelas: perlu pengesahan, disahkan, sedang dibungkus, dihantar dan diterima. Papan menunjukkan seluruh barisan sekali pandang, jadi pemilik nampak apa yang perlu dibuat seterusnya dan memajukan pesanan dengan satu seretan.

## Apa yang mudah

Peraturan domain (wang dalam sen, bakul, status pesanan) dan repositori SQLite. Apabila port wujud, objek palsu menjadikannya cepat diuji.

## Apa yang sukar

Papan pesanan dengan seret dan lepas yang menyimpan kedudukan dalam pangkalan data, dan pembayaran Stripe, yang mesti diuji tanpa kunci sebenar atau bayaran sebenar. CI juga menangkap apa yang terlepas daripada semakan tempatan saya: kunci `sk_live_` palsu dalam ujian mencetuskan imbasan rahsia, dan SQL yang dibina dengan f-string mencetuskan imbasan kod. Setiap pertanyaan ialah literal biasa dengan pemegang tempat `?`. Input pengguna hanya dihantar sebagai nilai terikat, tidak pernah di dalam teks SQL. Imbasan turut mengawasinya.

## Bagaimana saya boleh bertambah baik untuk projek seterusnya

Menjalankan imbasan yang sama seperti CI sebelum setiap push, melihat tangkapan skrin sebenar sebaik sahaja sesuatu halaman wujud, dan memastikan pelan dan kod sentiasa selaras.

## Pembelajaran terbesar saya

Keputusan yang berubah di tengah projek, di sini pertukaran daripada pustaka standard kepada Flask, paling murah apabila ditulis dahulu dalam ADR dan pelan, dan baru dikodkan. Pepijat seperti `site.update` yang memaparkan kaedah dict dalam templat ditemui dengan melihat tangkapan skrin sebenar, bukan ujian unit.

## Apa yang akan saya buat secara berbeza

Menetapkan pilihan rangka kerja sebelum pencapaian pertama dan menulis SQL sebagai literal biasa dengan pemegang tempat sejak repositori pertama.
