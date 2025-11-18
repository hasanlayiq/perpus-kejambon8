# --- Nama File: app.py ---
# Ini adalah "kulit" UI (Streamlit) kita.

import streamlit as st
from mesin_perpus import Perpustakaan, Anggota # Impor "mesin" kita

# --- VIBE "AJAIB" STREAMLIT: Session State ---
# Web bersifat "lupa". Streamlit 'st.session_state' adalah "memori"
# untuk mengingat objek perpustakaan dan siapa yang login.

if 'perpus' not in st.session_state:
    # 1. Inisialisasi "Mesin" kita
    print("--- MEMBUAT OBJEK PERPUSTAKAAN BARU ---")
    st.session_state.perpus = Perpustakaan()
    
    # 2. Bootstrap Admin (Sama seperti Vibe 7)
    admin_awal = Anggota(nisn="admin", tanggal_lahir="adminpass", nama="Admin Perpus", role="ADMIN")
    st.session_state.perpus.daftar_anggota.append(admin_awal)

    # 3. Bootstrap beberapa buku (biar tidak kosong)
    st.session_state.perpus.tambah_buku_baru("Laskar Pelangi", "Andrea Hirata", "Bentang", 2005, "FISIK", 5, "A1")
    st.session_state.perpus.tambah_buku_baru("Deep Learning", "F. Chollet", "Manning", 2021, "DIGITAL", 0)
    
# --- END VIBE "AJAIB" ---


# --- Mulai UI ---
st.set_page_config(layout="wide")
st.title("📚 Aplikasi Perpustakaan Sekolah (Vibe 7)")

# Kita ambil "mesin" dari memori
perpus = st.session_state.perpus
pengguna_login = perpus.pengguna_aktif

# =================================================================
# TAMPILAN 1: HALAMAN LOGIN (Jika belum login)
# =================================================================
if not pengguna_login:
    st.header("Silakan Login")
    with st.form("form_login"):
        nisn = st.text_input("Username (NISN)")
        # Vibe check: Ganti 'type' jadi 'password' agar jadi titik-titik
        tgl_lahir = st.text_input("Password (Tanggal Lahir, cth: 01012010)", type="password")
        
        tombol_login = st.form_submit_button("Login")
        
        if tombol_login:
            sukses, pesan = perpus.login(nisn, tgl_lahir)
            if sukses:
                st.success(pesan)
                st.rerun() # "Vibe Ajaib": Muat ulang halaman untuk masuk ke dashboard
            else:
                st.error(pesan)

# =================================================================
# TAMPILAN 2: DASHBOARD (Jika SUDAH login)
# =================================================================
else:
    # --- Sidebar ---
    with st.sidebar:
        st.subheader(f"Selamat Datang, {pengguna_login.nama}!")
        st.write(f"**Role:** {pengguna_login.role}")
        
        if st.button("Logout"):
            sukses, pesan = perpus.logout()
            st.success(pesan)
            st.rerun() # Muat ulang halaman untuk kembali ke login

        st.divider()
        st.subheader("Buku Pinjaman Saya")
        pinjaman_saya = pengguna_login.tampil_buku_pinjaman()
        for item in pinjaman_saya:
            st.markdown(item)

    # --- Halaman Utama (Pakai Tabs) ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Daftar Buku & Pinjam", 
        "🔄 Kembalikan Buku", 
        "--- ADMIN: Tambah Buku ---", 
        "--- ADMIN: Manajemen Anggota ---"
    ])

    # --- Tab 1: Daftar Buku & Pinjam ---
    with tab1:
        st.header("Daftar Buku & Peminjaman")
        
        # Buat 2 kolom
        col1, col2 = st.columns([3, 2]) # Kolom 1 lebih besar
        
        with col1:
            st.subheader("Semua Buku di Perpustakaan")
            daftar_buku = perpus.tampil_daftar_buku()
            if isinstance(daftar_buku[0], str):
                st.write(daftar_buku[0])
            else:
                # Kita buat data lebih rapi untuk ditampilkan
                data_tampil = []
                for buku in daftar_buku:
                    stok_display = "∞" if buku.stok == float('inf') else buku.stok
                    data_tampil.append({
                        "Judul": buku.judul,
                        "Penulis": buku.penulis,
                        "Tipe": buku.tipe_buku,
                        "Stok": stok_display,
                        "Rak": buku.rak_buku,
                        "ID": buku.id_buku
                    })
                st.dataframe(data_tampil, use_container_width=True)

        with col2:
            st.subheader("Form Peminjaman")
            with st.form("form_pinjam"):
                id_buku_pinjam = st.text_input("Masukkan ID Buku yang ingin dipinjam:")
                tombol_pinjam = st.form_submit_button("Pinjam Buku")
                
                if tombol_pinjam:
                    pesan = perpus.pinjam_buku(id_buku_pinjam)
                    if "BERHASIL" in pesan:
                        st.success(pesan)
                    else:
                        st.error(pesan)

    # --- Tab 2: Kembalikan Buku ---
    with tab2:
        st.header("Pengembalian Buku")
        with st.form("form_kembali"):
            id_buku_kembali = st.text_input("Masukkan ID Buku yang ingin dikembalikan:")
            tombol_kembali = st.form_submit_button("Kembalikan Buku")
            
            if tombol_kembali:
                pesan = perpus.kembalikan_buku(id_buku_kembali)
                if "BERHASIL" in pesan:
                    st.success(pesan)
                else:
                    st.error(pesan)
                    
    # --- Tab 3: ADMIN - Tambah Buku ---
    with tab3:
        st.header("Admin: Tambah Buku Baru")
        # Vibe Check: Hanya tampilkan form jika role-nya pas
        if pengguna_login.role not in ["ADMIN", "GURU"]:
            st.error("Hanya ADMIN atau GURU yang bisa mengakses menu ini.")
        else:
            with st.form("form_tambah_buku"):
                st.write("Masukkan detail buku baru:")
                judul = st.text_input("Judul")
                penulis = st.text_input("Penulis")
                penerbit = st.text_input("Penerbit")
                tahun = st.number_input("Tahun Terbit", min_value=1800, max_value=2025, value=2024)
                tipe = st.selectbox("Tipe Buku", ["FISIK", "DIGITAL"])
                stok = st.number_input("Stok (Abaikan jika DIGITAL)", min_value=0, value=1)
                rak = st.text_input("Lokasi Rak (Abaikan jika DIGITAL)")
                
                tombol_tambah_buku = st.form_submit_button("Tambah Buku")
                
                if tombol_tambah_buku:
                    pesan = perpus.tambah_buku_baru(judul, penulis, penerbit, tahun, tipe, stok, rak)
                    if "BERHASIL" in pesan: st.success(pesan)
                    else: st.error(pesan)

    # --- Tab 4: ADMIN - Manajemen Anggota ---
    with tab4:
        st.header("Admin: Manajemen Anggota")
        if pengguna_login.role not in ["ADMIN", "GURU"]:
            st.error("Hanya ADMIN atau GURU yang bisa mengakses menu ini.")
        else:
            # Punya 2 kolom lagi
            col_daftar, col_tambah = st.columns(2)
            
            with col_daftar:
                st.subheader("Daftar Anggota Terdaftar")
                daftar_anggota = perpus.tampil_daftar_anggota()
                if isinstance(daftar_anggota[0], str):
                    st.write(daftar_anggota[0])
                else:
                    data_anggota = [{
                        "Nama": ang.nama, 
                        "NISN": ang.nisn, 
                        "Role": ang.role
                    } for ang in daftar_anggota]
                    st.dataframe(data_anggota, use_container_width=True)

            with col_tambah:
                st.subheader("Daftar Anggota Baru")
                with st.form("form_tambah_anggota"):
                    nama_ang = st.text_input("Nama Lengkap")
                    nisn_ang = st.text_input("NISN (utk Username)")
                    tgl_lahir_ang = st.text_input("Tgl Lahir (utk Password, cth: 01012010)")
                    role_ang = st.selectbox("Role", ["SISWA", "GURU", "ADMIN"])
                    
                    tombol_tambah_anggota = st.form_submit_button("Daftarkan Anggota")
                    
                    if tombol_tambah_anggota:
                        pesan = perpus.daftar_anggota_baru(nisn_ang, tgl_lahir_ang, nama_ang, role_ang)
                        if "BERHASIL" in pesan: st.success(pesan)
                        else: st.error(pesan)