[English](Step-01-Project-Foundation) · [Dansk](Step-01-Project-Foundation-da) · **Bahasa Malaysia**

# Langkah 1: Asas projek

Langkah pertama belum membina apa-apa yang boleh digunakan oleh pembeli. Ia menyediakan peralatan dan struktur yang menjadi asas semua langkah seterusnya, dan menyajikan satu halaman.

![Langkah 1](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-01.png)

## Persediaan

- **Python 3.14 atau lebih baharu.** `pyproject.toml` mempunyai kumpulan `dev`: pytest, pytest-cov, ruff dan mypy. Flask, satu-satunya kebergantungan langsung semasa larian, ditambah pada langkah 2 (ADR-0002).
- **Persekitaran maya tempatan.** `python -m venv .venv`, aktifkannya, kemudian `python -m pip install --upgrade pip` dan `python -m pip install -e ".[dev]"`. Persekitaran ini mengasingkan pakej projek daripada Python sistem.
- **Jalankan kedai** dengan `python -m online_shop` dan buka http://127.0.0.1:8000/.

## Struktur

Kod dalam `src/online_shop/` mempunyai empat lapisan: `domain`, `application`, `infrastructure` dan `presentation`. Kebergantungan menghala ke dalam, jadi peraturan perniagaan tidak pernah mengimport pelayan web. Lapisan presentasi mengikut MVC: controller menjawab permintaan dan view membina HTML.

## Pemalar

Setiap nilai yang diperlukan lebih daripada satu tempat disimpan sekali dalam `src/online_shop/constants.py`: tajuk aplikasi, hos, port, jenis kandungan, kod status dan mesej ralat. Menukar port hanya memerlukan satu baris diubah.

## Semakan

- `pytest` menjalankan ujian unit dan integrasi dan gagal jika liputan di bawah 90 peratus.
- `python scripts/run_opengrep.py` mengimbas kod dan tidak boleh menemui apa-apa bertahap error sebelum push.
- Tangkapan skrin diambil oleh pelayar tanpa kepala dalam bekas Docker, tidak pernah di desktop.

## Apa yang saya pelajari

- Halaman pertama disajikan dengan `http.server` dan penghala kecil; langkah 2 menggantikannya dengan Flask apabila lapisan tulisan tangan mula membesar.
- Pemalar dalam satu modul dan lapisan dalam folder berasingan sejak hari pertama memerlukan sedikit usaha dan menjimatkan kerja semula.
- Ujian yang memulakan pelayan sebenar pada port kosong menangkap kesilapan yang terlepas daripada ujian unit.
