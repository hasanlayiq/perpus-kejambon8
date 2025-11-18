# --- Nama File: mesin_perpus.py ---
# Ini adalah "mesin" Vibe 7 kita, utuh tanpa perubahan logika.

import uuid

# --- VIBE 6: Class Buku (Fisik & Digital) ---
class Buku:
    def __init__(self, judul, penulis, penerbit, tahun_terbit, tipe_buku, stok, rak_buku=None):
        self.id_buku = str(uuid.uuid4())
        self.judul = judul
        self.penulis = penulis
        self.penerbit = penerbit
        self.tahun_terbit = tahun_terbit
        self.tipe_buku = tipe_buku.upper().strip()

        if self.tipe_buku == "DIGITAL":
            self.stok = float('inf')
            self.rak_buku = "Digital (N/A)"
        else:
            self.tipe_buku = "FISIK"
            self.rak_buku = rak_buku if rak_buku else "N/A"
            try:
                self.stok = int(stok)
            except ValueError:
                self.stok = 0
    
    def __repr__(self):
        stok_display = "Tak Terbatas" if self.stok == float('inf') else self.stok
        return (f"[{self.tipe_buku}] {self.judul} ({self.tahun_terbit}) oleh {self.penulis}\n"
                f"       Penerbit: {self.penerbit} | Rak: {self.rak_buku} | Stok: {stok_display}")

# --- VIBE 7: Refactor Class Anggota (Login NISN + Role) ---
class Anggota:
    def __init__(self, nisn, tanggal_lahir, nama, role):
        self.nisn = nisn
        self.tanggal_lahir = tanggal_lahir
        self.nama = nama
        self.role = role.upper().strip()
        self.buku_pinjaman = []
    
    def __repr__(self):
        return f"[Anggota] Nama: {self.nama} | NISN: {self.nisn} | Role: {self.role}"

    def tampil_buku_pinjaman(self):
        # Helper untuk Streamlit nanti, mengembalikan list string
        if not self.buku_pinjaman:
            return ["- Tidak ada buku yang dipinjam."]
        
        daftar = []
        for buku in self.buku_pinjaman:
            daftar.append(f"- {buku.judul} [{buku.tipe_buku}]")
        return daftar


# --- VIBE 7: Refactor Class Perpustakaan (Login + Roles) ---
class Perpustakaan:
    def __init__(self):
        self.daftar_buku = []
        self.daftar_anggota = []
        self.pengguna_aktif = None 
        print("INFO: Objek Perpustakaan (V7) [Login Enabled] telah dibuat!")

    # --- Helper Methods ---
    def _cari_buku_by_id(self, id_buku):
        for buku in self.daftar_buku:
            if buku.id_buku == id_buku: return buku
        return None

    def _cari_anggota_by_nisn(self, nisn):
        for anggota in self.daftar_anggota:
            if anggota.nisn == nisn: return anggota
        return None

    # --- VIBE 7: METHOD BARU (Authentication) ---
    def login(self, nisn, tanggal_lahir):
        if self.pengguna_aktif:
            return False, "INFO: Sudah ada yang login."

        anggota = self._cari_anggota_by_nisn(nisn)
        
        if anggota and anggota.tanggal_lahir == tanggal_lahir:
            self.pengguna_aktif = anggota
            return True, f"BERHASIL: Selamat datang, {anggota.nama} ({anggota.role})!"
        else:
            return False, "GAGAL: NISN atau Tanggal Lahir salah."

    def logout(self):
        if self.pengguna_aktif:
            nama = self.pengguna_aktif.nama
            self.pengguna_aktif = None
            return True, f"BERHASIL: {nama} berhasil logout."
        else:
            return False, "INFO: Tidak ada yang sedang login."
    
    # --- VIBE 7: REFACTOR METHOD (Wajib Login & Role) ---
    
    # Kita modifikasi sedikit agar mengembalikan pesan (string) untuk UI
    def tambah_buku_baru(self, judul, penulis, penerbit, tahun_terbit, tipe_buku, stok, rak_buku=None):
        if not self.pengguna_aktif:
            return f"GAGAL: Anda harus login."
        if self.pengguna_aktif.role not in ["ADMIN", "GURU"]:
            return f"GAGAL: Hak akses ditolak. (Role: {self.pengguna_aktif.role})"
        
        buku_baru = Buku(judul, penulis, penerbit, tahun_terbit, tipe_buku, stok, rak_buku)
        self.daftar_buku.append(buku_baru)
        return f"BERHASIL: Buku '{judul}' [{tipe_buku}] ditambahkan."

    def daftar_anggota_baru(self, nisn_baru, tgl_lahir_baru, nama_baru, role_baru):
        if not self.pengguna_aktif:
            return f"GAGAL: Anda harus login."
        if self.pengguna_aktif.role not in ["ADMIN", "GURU"]:
            return f"GAGAL: Hak akses ditolak. (Role: {self.pengguna_aktif.role})"
        if self._cari_anggota_by_nisn(nisn_baru):
            return f"GAGAL: NISN {nisn_baru} sudah terdaftar."

        anggota_baru = Anggota(nisn_baru, tgl_lahir_baru, nama_baru, role_baru)
        self.daftar_anggota.append(anggota_baru)
        return f"BERHASIL: {nama_baru} ({role_baru}) berhasil didaftarkan."

    # --- VIBE 7: REFACTOR METHOD (Self-Service) ---

    def pinjam_buku(self, id_buku):
        if not self.pengguna_aktif:
            return "GAGAL: Anda harus login untuk meminjam buku."
            
        anggota = self.pengguna_aktif
        buku = self._cari_buku_by_id(id_buku)
        
        if not buku: return f"GAGAL: Buku dengan ID {id_buku} tidak ditemukan."
        if buku in anggota.buku_pinjaman: return f"GAGAL: Anda sudah meminjam '{buku.judul}'."
        if buku.tipe_buku == "FISIK" and buku.stok <= 0:
            return f"GAGAL: Stok buku FISIK '{buku.judul}' habis."

        if buku.tipe_buku == "FISIK":
            buku.stok -= 1
        
        anggota.buku_pinjaman.append(buku)
        return f"BERHASIL: '{anggota.nama}' meminjam '{buku.judul}'."
        
    def kembalikan_buku(self, id_buku):
        if not self.pengguna_aktif:
            return "GAGAL: Anda harus login."

        anggota = self.pengguna_aktif
        buku = self._cari_buku_by_id(id_buku)

        if not buku: return f"GAGAL: Buku tidak ditemukan."
        if buku not in anggota.buku_pinjaman:
            return f"GAGAL: Anda ('{anggota.nama}') tidak sedang meminjam '{buku.judul}'."

        if buku.tipe_buku == "FISIK":
            buku.stok += 1
        
        anggota.buku_pinjaman.remove(buku)
        return f"BERHASIL: '{anggota.nama}' mengembalikan '{buku.judul}'."

    # --- Method Tampil (Tidak berubah) ---
    def tampil_daftar_buku(self):
        # Mengembalikan list, bukan print
        if not self.daftar_buku: return [" (Kosong)"]
        return [buku for buku in self.daftar_buku]

    def tampil_daftar_anggota(self):
        # Mengembalikan list, bukan print
        if not self.daftar_anggota: return [" (Kosong)"]
        return [anggota for anggota in self.daftar_anggota]