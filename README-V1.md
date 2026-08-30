# ArgoGPS Web — V1

**Status:** Snapshot V1 (Approved untuk disimpan, belum deploy permanen)
**Tanggal simpan:** 30 Agustus 2026

## Struktur Landing Page (V1)
1. Hero — headline + CTA + screenshot asli APK (halaman utama) dalam bingkai HP
2. Masalah — "Masih Menghitung Ongkir Secara Manual?" (4 kartu)
3. Solusi — "Satu Aplikasi untuk Mengelola Perjalanan Kurir" (6 fitur)
4. **Galeri Tampilan** — "Kenali Tampilan ArgoGPS" (4 layar asli: Halaman Utama, Tagihan, Riwayat, Pengaturan)
5. Target Pengguna — "Dirancang untuk Berbagai Kebutuhan Pengiriman" (6 segmen)
6. Skema Tarif — contoh Rp7.000 / Rp1.700 / Rp2.000 + catatan "hanya contoh"
7. Cara Kerja — 5 langkah
8. Harga — Gratis Rp0 vs Premium Rp45.000/bulan
9. FAQ — 8 pertanyaan
10. CTA Akhir + Footer

## Aset
- `index.html` — landing page utama (responsif: desktop + mobile)
- `privasi.html` — Kebijakan Privasi (wajib Play Store)
- `syarat.html` — Syarat & Ketentuan
- `hapus-akun.html` — Penghapusan Akun & Data
- `sitemap.xml` + `robots.txt` — SEO
- `assets/icon-512.png` — icon app
- `assets/screens/*-polished.png` — 4 screenshot asli APK yang dipoles (dibingkai + notch)
- `_tools/` — tooling (CDP screenshot, polish)
- `preview-home.png` / `preview-mobile.png` — preview render

## Kunci Desain
- Desain: light/flat/matte hijau pastel (brand #169B62 hijau tua #0F7A4E)
- Amber (#D97706) hanya untuk tombol Premium / kartu masalah
- Screenshot APK = gambar ASLI dari user (bukan tiruan CSS), dipoles ringan
- Copy seluruhnya Bahasa Indonesia, berbasis fakta APK (tarif, fitur, dll)
- Developer: BKDev · Kontak: support@argogps.id
- Harga Premium: Rp45.000/bulan

## Status Selanjutnya
- [ ] Deploy permanen (Cloudflare Pages / hosting) — URL stabil untuk Privacy Policy di Play Console
- [ ] Verifikasi/update halaman legal (privasi, syarat, hapus-akun)
