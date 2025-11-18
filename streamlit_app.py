import streamlit as st
from mesin_perpus import Perpustakaan, Anggota
import time

# --- KONFIGURASI HALAMAN (Modern Vibe) ---
st.set_page_config(
    page_title="Perpustakaan Digital",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS HACK (Untuk mempercantik tampilan) ---
st.markdown("""
<style>
    /* Mengubah warna background header */
    .stAppHeader {background-color: transparent;}
    
    /* Membuat kartu buku lebih cantik */
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Judul Besar */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# --- INISIALISASI MESIN ---
if 'perpus' not in st.session_state:
    st.session_state.perpus = Perpustakaan()
    # Data Dummy Awal
    p = st.session_state.perpus
    p.daftar_anggota.append(Anggota("admin", "adminpass", "Kepala Pustaka", "ADMIN"))
    p.tambah_buku_baru("Laskar Pelangi", "Andrea Hirata", "Bentang", 2005, "FISIK", 5, "A1-Novel")
    p.tambah_buku_baru("Bumi Manusia", "Pramoedya A. Toer", "Hasta Mitra", 1980, "FISIK", 2, "A1-Novel")
    p.tambah_buku_baru("Deep Learning", "F. Chollet", "Manning", 2021, "DIGITAL", 0)
    p.tambah_buku_baru("Atomic Habits", "James Clear", "Penguin", 2018, "FISIK", 10, "B2-SelfHelp")
    p.tambah_buku_baru("Filosofi Teras", "Henry Manampiring", "Kompas", 2019, "FISIK", 7, "B2-SelfHelp")

perpus = st.session_state.perpus
pengguna_login = perpus.pengguna_aktif

# =================================================================
# HALAMAN LOGIN (Clean & Minimalis)
# =================================================================
if not pengguna_login:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True) # Spacer
        st.title("🎓 Univ. Library Portal")
        st.write("Silakan login dengan akun akademik Anda.")
        
        with st.container(border=True):
            nisn = st.text_input("🆔 NISN / NIP")
            tgl_lahir = st.text_input("🔑 Password", type="password")
            
            if st.button("Masuk Portal", use_container_width=True, type="primary"):
                sukses, pesan = perpus.login(nisn, tgl_lahir)
                if sukses:
                    st.success("Login berhasil! Mengalihkan...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(pesan)
        
        st.info("Gunakan akun Demo: **admin** / **adminpass**")

# =================================================================
# DASHBOARD UTAMA (Modern Layout)
# =================================================================
else:
    # --- SIDEBAR (Profil User) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.title(f"Halo, {pengguna_login.nama.split()[0]}!")
        st.caption(f"Role: {pengguna_login.role} | ID: {pengguna_login.nisn}")
        
        st.divider()
        
        # Menu Navigasi (Radio Button rasa Tab)
        menu_pilihan = st.radio("Navigasi", ["🏠 Beranda & Buku", "📚 Pinjaman Saya", "⚙️ Admin Area"])
        
        st.divider()
        if st.button("🚪 Keluar / Logout", use_container_width=True):
            perpus.logout()
            st.rerun()

    # --- AREA KONTEN ---
    
    # 1. MENU BERANDA (Tampilan Galeri Buku)
    if menu_pilihan == "🏠 Beranda & Buku":
        # Hero Section
        st.markdown("# 🏛️ Perpustakaan Universitas")
        st.markdown("Temukan referensi terbaik untuk studi Anda hari ini.")
        
        # Statistik Ringkas (Modern Metrics)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Koleksi", f"{len(perpus.daftar_buku)} Judul")
        m2.metric("Buku Digital", f"{len([b for b in perpus.daftar_buku if b.tipe_buku == 'DIGITAL'])} E-Book")
        m3.metric("Status Server", "Online 🟢")
        
        st.divider()
        
        # Search Bar Besar
        cari = st.text_input("🔍 Cari judul buku, penulis, atau penerbit...", placeholder="Ketik kata kunci di sini...")
        
        st.subheader("Koleksi Pustaka")
        
        # Filter Buku berdasarkan pencarian
        buku_tampil = [b for b in perpus.daftar_buku if cari.lower() in b.judul.lower() or cari.lower() in b.penulis.lower()]
        
        if not buku_tampil:
            st.warning("Buku tidak ditemukan.")
        else:
            # --- GRID LAYOUT (Kunci Tampilan Modern) ---
            # Kita tampilkan buku dalam grid 3 kolom
            cols = st.columns(3)
            for i, buku in enumerate(buku_tampil):
                with cols[i % 3]: # Logika matematika biar looping ke kolom 1, 2, 3
                    with st.container(border=True):
                        # Ikon Buku (Bisa diganti gambar asli nanti)
                        if buku.tipe_buku == "DIGITAL":
                            st.markdown("### 📱 " + buku.judul)
                        else:
                            st.markdown("### 📕 " + buku.judul)
                        
                        st.caption(f"Penulis: {buku.penulis}")
                        st.caption(f"Penerbit: {buku.penerbit} ({buku.tahun_terbit})")
                        
                        # Badge Stok
                        if buku.tipe_buku == "FISIK":
                            st.markdown(f"**Stok: {buku.stok}** | Rak: `{buku.rak_buku}`")
                            if buku.stok > 0:
                                if st.button("Pinjam Buku", key=f"btn_{buku.id_buku}"):
                                    pesan = perpus.pinjam_buku(buku.id_buku)
                                    if "BERHASIL" in pesan: st.toast(pesan, icon="✅")
                                    else: st.toast(pesan, icon="❌")
                            else:
                                st.button("Stok Habis", disabled=True, key=f"btn_{buku.id_buku}")
                        else:
                            st.markdown("**✅ Akses Digital Unlimited**")
                            if st.button("Baca / Pinjam", key=f"btn_{buku.id_buku}"):
                                pesan = perpus.pinjam_buku(buku.id_buku)
                                st.toast(pesan, icon="📱")

    # 2. MENU PINJAMAN SAYA
    elif menu_pilihan == "📚 Pinjaman Saya":
        st.title("Buku yang Sedang Anda Pinjam")
        
        pinjaman = pengguna_login.buku_pinjaman
        if not pinjaman:
            st.info("Anda belum meminjam buku apapun. Yuk ke Beranda!")
        else:
            for buku in pinjaman:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.subheader(buku.judul)
                        st.write(f"Tipe: {buku.tipe_buku} | Penulis: {buku.penulis}")
                    with c2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Kembalikan", key=f"kembali_{buku.id_buku}", type="primary"):
                            pesan = perpus.kembalikan_buku(buku.id_buku)
                            st.success(pesan)
                            st.rerun()

    # 3. MENU ADMIN AREA
    elif menu_pilihan == "⚙️ Admin Area":
        st.title("Portal Administrasi")
        
        if pengguna_login.role not in ["ADMIN", "GURU"]:
            st.error("⛔ Akses Ditolak. Area ini khusus Staff Perpustakaan.")
        else:
            tab_add, tab_users = st.tabs(["➕ Tambah Buku", "👥 Data Anggota"])
            
            with tab_add:
                with st.form("form_tambah_modern"):
                    st.write("Input Data Buku Baru")
                    c1, c2 = st.columns(2)
                    judul = c1.text_input("Judul Buku")
                    penulis = c2.text_input("Penulis")
                    penerbit = c1.text_input("Penerbit")
                    tahun = c2.number_input("Tahun", 2000, 2025)
                    tipe = st.selectbox("Format", ["FISIK", "DIGITAL"])
                    
                    if st.form_submit_button("Simpan ke Database"):
                        perpus.tambah_buku_baru(judul, penulis, penerbit, tahun, tipe, 5, "Baru")
                        st.success("Buku berhasil ditambahkan!")
            
            with tab_users:
                st.dataframe([vars(a) for a in perpus.daftar_anggota])
                st.warning("Fitur edit anggota segera hadir.")