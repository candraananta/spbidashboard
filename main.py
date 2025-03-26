import streamlit as st  # Mengimpor Streamlit untuk membuat antarmuka pengguna berbasis web
import jaydebeapi  # Mengimpor jaydebeapi untuk koneksi ke database menggunakan JDBC
import pandas as pd  # Mengimpor pandas untuk manipulasi dan tampilan data dalam bentuk DataFrame
import json  # Mengimpor modul json untuk membaca file JSON
import logging  # Mengimpor modul logging untuk mencatat aktivitas

# Set up logging configuration
logging.basicConfig(filename='database_operations.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Membaca konfigurasi dari file hsqldb_config.json
with open('hsqldb_config.json') as config_file:
    config = json.load(config_file)

JDBC_DRIVER = config['JDBC_DRIVER']  # Nama driver JDBC untuk database HSQLDB
JDBC_URL = config['JDBC_URL']  # URL koneksi database
USERNAME = config['USERNAME']  # Username untuk autentikasi ke database
PASSWORD = config['PASSWORD']  # Password untuk autentikasi ke database
JAR_FILE = config['JAR_FILE']  # Lokasi file JAR JDBC driver

def fetch_records(query):
    """Fungsi untuk mengambil data dari database menggunakan query SQL."""
    logging.info(f"Executing query: {query}")  # Log the executed query

    conn = None  # Inisialisasi variabel untuk menyimpan objek koneksi database
    curs = None  # Inisialisasi variabel untuk menyimpan objek cursor
    try:
        # Membuat koneksi ke database dengan parameter JDBC
        conn = jaydebeapi.connect(
            JDBC_DRIVER,  # Nama driver JDBC
            JDBC_URL,  # URL database
            [USERNAME, PASSWORD],  # Kredensial login
            JAR_FILE  # Path ke file JAR JDBC driver
        )
        curs = conn.cursor()  # Membuat cursor untuk menjalankan query
        
        curs.execute(query)  # Menjalankan query SQL
        results = curs.fetchall()  # Mengambil semua hasil query dalam bentuk list
        
        # Mendapatkan nama kolom dari hasil query
        columns = [desc[0] for desc in curs.description]
        
        # Mengembalikan hasil dalam bentuk DataFrame pandas
        return pd.DataFrame(results, columns=columns)
        
    except Exception as e:
        logging.error(f"Error occurred: {e}")  # Log the error
        st.error(f"Terjadi kesalahan: {e}")  # Menampilkan error jika terjadi kesalahan
        return None
    finally:
        # Menutup cursor dan koneksi setelah selesai digunakan
        if curs:
            curs.close()
        if conn:
            conn.close()

# Konfigurasi tampilan aplikasi Streamlit
st.set_page_config(page_title="Database Viewer", layout="wide")  # Menentukan judul halaman dan layout

# Menampilkan judul aplikasi di halaman utama
st.title("📊 SPBI-Dashboard Data Viewer")  # Menampilkan ikon dan judul aplikasi
st.markdown("""Aplikasi untuk menampilkan data transaksi fuel dari database""")  # Menampilkan deskripsi aplikasi

# Sidebar untuk input parameter
with st.sidebar:
    st.header("Pengaturan")  # Menampilkan header bagian pengaturan
    num_records = st.slider(
        "Jumlah data yang akan ditampilkan",  # Label slider
        min_value=1,  # Nilai minimum
        max_value=1000,  # Nilai maksimum
        value=5  # Nilai default
    )
    
    # Input teks untuk menyaring data berdasarkan CardNo
    st.header("Filter Data")
    cardno_filter = st.text_input("Masukkan CardNo untuk filter:")  # Input teks untuk filter CardNo

    st.header("Menu Query")  # Menampilkan header menu query

    # Dropdown menu for selecting actions
    selected_action = st.selectbox("Pilih Aksi:", [
        "Muat Data RFID Nopol",
        "Muat Data Transaksi",
        "Check Location",
        "Muat Data Nopol Kendaraan"
    ])

    st.header("Menu Check Nopol Error")  # Menampilkan header menu query

    update_id = st.text_input("Masukkan ID untuk update untuk merelease nopol :")
    update_button_enabled = False  # Initialize button state

    # Check for records to enable the update button
    if st.button("Temukan Nopol yang tidak bisa melakukan pengisian"):
        with st.spinner("Memuat data dari database..."):
            query = "SELECT ID,CARDNO FROM trnquotacustomer WHERE processed = 1"  # Query SQL default
            df = fetch_records(query)  # Mengambil data dari database
            if df is not None and not df.empty:  # Check if there are records
                st.success("Data berhasil dimuat!")  # Menampilkan notifikasi sukses
                st.subheader("Data trnquotacustomer (processed = 1)")  # Subjudul tabel data
                st.dataframe(df)  # Menampilkan data dalam bentuk tabel
                update_button_enabled = True  # Enable the update button
            else:
                st.error("tidak ditemukan nopol yang error")  # Menampilkan error jika terjadi kesalahan

    # Update button logic
    if st.button("Release", disabled=not update_button_enabled):
        logging.info("Release button clicked")  # Log button click
        logging.info(f"Update ID entered: {update_id}")  # Log the entered ID

        if update_id:
            update_query = f"UPDATE trnquotacustomer SET processed = 0 WHERE id = {update_id}"
            logging.info(f"Executing update query: {update_query}")  # Log the executed update query
            try:
                logging.info("Attempting to execute update query")  # Log before executing the query

                conn = jaydebeapi.connect(
                    JDBC_DRIVER,  # Nama driver JDBC
                    JDBC_URL,  # URL database
                    [USERNAME, PASSWORD],  # Kredensial login
                    JAR_FILE  # Path ke file JAR JDBC driver
                )

                curs = conn.cursor()  # Membuat cursor untuk menjalankan query
                curs.execute(update_query)  # Menjalankan query update
                conn.commit()  # Menyimpan perubahan
                st.success(f"Data dengan ID {update_id} berhasil diupdate!")  # Notifikasi sukses
                update_id = ""  # Clear the text input after successful update

                
            except Exception as e:
                logging.error(f"Terjadi kesalahan saat mengupdate data: {e}")  # Log the error
                st.error(f"Terjadi kesalahan saat mengupdate data: {e}")  # Notifikasi error
            finally:
                if curs:
                    curs.close()  # Menutup cursor
                if conn:
                    conn.close()  # Menutup koneksi
        else:
            st.error("ID tidak boleh kosong!")  # Notifikasi error


   

# Execute action based on selection

if selected_action == "Muat Data RFID Nopol":
    with st.spinner("Memuat data dari database..."):
        query = "SELECT * FROM trnrfidmap"  # Query SQL default
        if cardno_filter:
            query += f" WHERE cardno = '{cardno_filter}'"  # Menambahkan filter berdasarkan CardNo
        df = fetch_records(query)  # Mengambil data dari database
        if df is not None:
            st.success("Data berhasil dimuat!")
            st.subheader("Data trnrfidmap")
            st.dataframe(df)

elif selected_action == "Muat Data Transaksi":
    with st.spinner("Memuat data dari database..."):
        query = f"SELECT * FROM trntransactionfuel where reprint = 0 LIMIT {num_records}"  # Query default dengan batas jumlah data
        if cardno_filter:
            query += f" AND cardno = '{cardno_filter}'"  # Menambahkan filter CardNo jika ada
        df = fetch_records(query)  # Mengambil data dari database
        if df is not None:
            st.success("Data berhasil dimuat!")  # Notifikasi sukses
            st.subheader("Data Transaksi")  # Subjudul tabel data transaksi
            st.dataframe(df)  # Menampilkan data transaksi dalam bentuk tabel

elif selected_action == "Check Location":
    with st.spinner("Memuat data dari database..."):
        query = "SELECT value AS location FROM trnsitedetail where id = 1"
        df = fetch_records(query)  # Mengambil data dari database
        if df is not None:
            st.success("Data berhasil dimuat!")  # Menampilkan notifikasi sukses
            st.subheader("Location SPBI : ")  # Subjudul tabel data
            st.dataframe(df)  # Menampilkan data dalam bentuk tabel

elif selected_action == "Muat Data Nopol Kendaraan":
    with st.spinner("Memuat data dari database..."):
        query = "SELECT cardno AS NOPOL from trnquotacustomer"
        df = fetch_records(query)  # Mengambil data dari database
        if df is not None:
            st.success("Data berhasil dimuat!")  # Menampilkan notifikasi sukses
            st.subheader("list nopol yang bisa melakukan pengisian")  # Subjudul tabel data
            st.dataframe(df, use_container_width=True)  # Menampilkan data dalam bentuk tabel dengan lebar kolom yang sesuai
