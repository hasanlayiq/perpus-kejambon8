import streamlit as st
from mesin_perpus import Perpustakaan, Anggota
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Pustaka Ilmu - SDN Kejambon 8",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar disembunyikan agar fokus ke Menu Atas
)

# --- 2. INISIALISASI MESIN (DATA) ---
if 'perpus' not in st.session_state:
    st.session_state.perpus = Perpustakaan()
    p = st.session_state.perpus
    # Data Dummy Admin & Buku
    p.daftar_anggota.append(Anggota("admin", "adminpass", "Admin Sekolah", "ADMIN"))
    p.tambah_buku_baru("Cerita Rakyat Nusantara", "Tim Erlangga", "Erlangga", 2020, "FISIK", 5, "Rak A-1")
    p.tambah_buku_baru("RPAL Lengkap", "Budi Sutanto", "Gramedia", 2022, "FISIK", 3, "Rak B-2")
    p.tambah_buku_baru("Kamus Bahasa Inggris", "John Echols", "Gramedia", 2019, "FISIK", 10, "Rak C-1")
    p.tambah_buku_baru("Ensiklopedia Hewan", "National Geo", "NatGeo", 2021, "DIGITAL", 0)

perpus = st.session_state.perpus
pengguna_login = perpus.pengguna_aktif

# --- 3. CSS CUSTOM (UNTUK HEADER & FOOTER) ---
st.markdown("""
<style>
    /* Sembunyikan elemen bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Judul Website Kustom */
    .header-sekolah {
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 20px;
        border-bottom: 5px solid #2E86C1;
    }
    .header-sekolah h1 {
        color: #2E86C1;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .header-sekolah h3 {
        color: #333;
        margin: 0;
        font-size: 1.2rem;
    }
    .header-sekolah p {
        color: #666;
        margin: 0;
        font-size: 0.9rem;
    }

    /* Gaya Kartu Buku */
    div[data-testid="stExpander"] {
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Footer Kustom */
    .footer-sekolah {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2E86C1;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. MENU BAR (NAVIGASI ATAS) ---
# Kita gunakan Tabs sebagai Menu Bar horizontal
tab_home, tab_katalog, tab_tentang, tab_galery, tab_login = st.tabs([
    "🏠 Home", "📚 Katalog Buku", "ℹ️ Tentang Kami", "🖼️ Galery", "👤 Login / Profil"
])

# ============================================================================
# TAB 1: HOME (Landing Page Lengkap sesuai Request)
# ============================================================================
with tab_home:
    # A. JUDUL WEBSITE (HEADER)
    st.markdown("""
    <div class="header-sekolah">
        <h1>Perpustakaan PUSTAKA ILMU</h1>
        <h3>SDN Kejambon 8 Kota Tegal</h3>
        <p>Jl. Kemuning No. 47 Tegal | (0283) 342472</p>
    </div>
    """, unsafe_allow_html=True)

    # B. CAROUSEL GAMBAR (Menggunakan Placeholder Gambar Sekolah)
    # Karena Streamlit murni tidak punya carousel gerak, kita pakai gambar banner lebar
    st.image("https://images.unsplash.com/photo-1523580494863-6f3031224c94?q=80&w=2070&auto=format&fit=crop", 
             caption="Suasana Membaca di Perpustakaan PUSTAKA ILMU", use_container_width=True)
    
    st.divider()

    # C. MENU PENCARIAN BUKU
    col_cari, col_kosong = st.columns([2, 1])
    with col_cari:
        cari_home = st.text_input("🔍 Cari Buku (Judul/Penulis):", placeholder="Ketik judul buku di sini...")

    # D. KOLEKSI BUKU (KATALOG)
    st.subheader("📚 Koleksi Buku Terbaru")
    
    # Filter logika pencarian
    buku_ditemukan = [b for b in perpus.daftar_buku if cari_home.lower() in b.judul.lower()]
    
    if not buku_ditemukan:
        st.info("Buku tidak ditemukan.")
    else:
        # Grid Layout (3 Kolom)
        cols = st.columns(3)
        for i, buku in enumerate(buku_ditemukan):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"#### {buku.judul}")
                    st.caption(f"Penulis: {buku.penulis}")
                    st.write(f"Rak: `{buku.rak_buku}` | Tipe: {buku.tipe_buku}")
                    
                    # LOGIKA TOMBOL PINJAM (REQUEST NO. 1)
                    # Hanya muncul tombol jika sudah login
                    if pengguna_login:
                        stok_msg = f"Sisa Stok: {buku.stok}" if buku.tipe_buku == "FISIK" else "Akses Digital"
                        st.write(f"**{stok_msg}**")
                        
                        if buku.tipe_buku == "FISIK" and buku.stok <= 0:
                             st.button("Stok Habis", key=f"btn_home_{buku.id_buku}", disabled=True)
                        else:
                            if st.button("Pinjam", key=f"btn_home_{buku.id_buku}", type="primary"):
                                pesan = perpus.pinjam_buku(buku.id_buku)
                                if "BERHASIL" in pesan: st.success("Berhasil dipinjam!")
                                else: st.error(pesan)
                    else:
                        # Jika belum login, hanya info
                        st.warning("🔒 Login untuk meminjam")

    st.divider()

    # E. TENTANG KAMI
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
        <h2>Tentang Kami</h2>
        <p style="font-size: 1.1rem;">
        Perpustakaan <b>SDN Kejambon 8 Kota Tegal</b> adalah pusat pembelajaran dan literasi yang menyediakan 
        berbagai koleksi buku berkualitas untuk mendukung pendidikan siswa.
        <br><br>
        Dengan sistem digital yang modern, kami memudahkan siswa dan guru untuk mengakses, 
        mencari, dan meminjam buku dengan cepat dan efisien.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # F. GALERY (FOTO)
    st.subheader("🖼️ Galery Kegiatan")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.image("https://images.unsplash.com/photo-1481627834876-b7833e8f5570", caption="Pojok Baca", use_container_width=True)
    with col_g2:
        st.image("https://images.unsplash.com/photo-1509062522246-3755977927d7", caption="Kegiatan Literasi", use_container_width=True)
    with col_g3:
        st.image("https://images.unsplash.com/photo-1512820790803-83ca734da794", caption="Koleksi Buku", use_container_width=True)

# ============================================================================
# TAB LAIN (Untuk Navigasi Fokus)
# ============================================================================

with tab_katalog:
    st.header("Katalog Lengkap")
    st.dataframe([{
        "Judul": b.judul, "Penulis": b.penulis, "Penerbit": b.penerbit, 
        "Stok": b.stok, "Rak": b.rak_buku
    } for b in perpus.daftar_buku], use_container_width=True)

with tab_tentang:
    st.image("https://maps.googleapis.com/maps/api/staticmap?center=SDN+Kejambon+8+Tegal&zoom=15&size=600x300&sensor=false", caption="Lokasi Kami (Ilustrasi)")
    st.write("Hubungi kami di (0283) 342472 untuk informasi lebih lanjut.")

with tab_galery:
    st.header("Dokumentasi Sekolah")
    st.write("Dokumentasi lengkap kegiatan siswa dan guru.")
    # Bisa ditambahkan lebih banyak foto grid di sini

with tab_login:
    st.header("Area Anggota")
    
    if not pengguna_login:
        with st.form("login_form"):
            st.write("Silakan Login")
            nisn_input = st.text_input("NISN / Username")
            pass_input = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                sukses, pesan = perpus.login(nisn_input, pass_input)
                if sukses: 
                    st.success("Login Berhasil!")
                    time.sleep(1)
                    st.rerun()
                else: 
                    st.error(pesan)
        st.info("Akun Demo: **admin** / **adminpass**")
    else:
        st.success(f"Anda login sebagai: {pengguna_login.nama} ({pengguna_login.role})")
        
        # Menu Khusus Admin
        if pengguna_login.role == "ADMIN":
            st.subheader("Menu Admin")
            with st.expander("Tambah Buku Baru"):
                with st.form("add_book"):
                    j = st.text_input("Judul")
                    p = st.text_input("Penulis")
                    t = st.selectbox("Tipe", ["FISIK", "DIGITAL"])
                    if st.form_submit_button("Simpan"):
                        perpus.tambah_buku_baru(j, p, "-", 2024, t, 5)
                        st.success("Tersimpan!")
        
        # Menu Pinjaman Saya
        st.subheader("Buku yang Sedang Dipinjam")
        pinjaman = pengguna_login.buku_pinjaman
        if pinjaman:
            for b in pinjaman:
                st.write(f"- {b.judul}")
                if st.button(f"Kembalikan {b.judul}", key=f"ret_{b.id_buku}"):
                    perpus.kembalikan_buku(b.id_buku)
                    st.rerun()
        else:
            st.write("Tidak ada pinjaman aktif.")

        if st.button("Logout", type="secondary"):
            perpus.logout()
            st.rerun()

# --- 5. FOOTER (PALING BAWAH) ---
st.markdown("""
<div class="footer-sekolah">
    Created by: jamwolu@2025 <br>
    © 2025 Perpustakaan SDN Kejambon 8 Kota Tegal
</div>
""", unsafe_allow_html=True)