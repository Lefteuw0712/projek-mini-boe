import sqlite3
from flask import Flask, render_template

app = Flask(__name__)


# Fungsi untuk membuat koneksi ke database SQLite3
def get_db_connection():
    conn = sqlite3.connect('articles.db')  # Nama database
    conn.row_factory = sqlite3.Row  # Agar hasil query bisa diakses seperti dictionary
    return conn


# Fungsi untuk membuat tabel artikel jika belum ada
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()


# Fungsi untuk menambahkan artikel ke database (hanya jika tabel kosong)
def add_articles_if_empty():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles')
    articles = cursor.fetchall()
    if len(articles) == 0:
        # Menambahkan artikel pertama
        cursor.execute('''
        INSERT INTO articles (title, summary, content)
        VALUES ('Pertanian Padi di Maluku Tenggara', 'Artikel ini membahas cara budidaya padi di daerah Maluku Tenggara...', 'Isi lengkap artikel tentang pertanian padi...')
        ''')
        # Menambahkan artikel kedua
        cursor.execute('''
        INSERT INTO articles (title, summary, content)
        VALUES ('Nelayan Maluku Tenggara dan Tantangan Laut', 'Artikel ini mengulas tantangan yang dihadapi oleh nelayan di Maluku Tenggara...', 'Isi lengkap artikel tentang nelayan Maluku Tenggara...')
        ''')
        conn.commit()
    conn.close()


# Fungsi untuk membuat tabel tambahan sesuai halaman-halaman web
def create_additional_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabel info pertanian
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pertanian_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        info TEXT NOT NULL
    )
    ''')

    # Tabel info nelayan
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nelayan_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        info TEXT NOT NULL
    )
    ''')

    # Tabel lokasi penjualan
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lokasi_penjualan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_tempat TEXT NOT NULL,
        alamat TEXT NOT NULL,
        deskripsi TEXT
    )
    ''')

    conn.commit()
    conn.close()


# Fungsi untuk menambahkan data default ke tabel tambahan jika masih kosong
def seed_additional_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Menambahkan data info pertanian
    cursor.execute('SELECT COUNT(*) FROM pertanian_info')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO pertanian_info (info)
        VALUES (?)
        ''', ('Pertanian di Maluku Tenggara melibatkan tanaman seperti kelapa, jagung, dan singkong.',))

    # Menambahkan data info nelayan
    cursor.execute('SELECT COUNT(*) FROM nelayan_info')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO nelayan_info (info)
        VALUES (?)
        ''', ('Nelayan di Maluku Tenggara mengandalkan hasil laut seperti ikan tuna dan ikan kerapu.',))

    # Menambahkan data lokasi penjualan
    cursor.execute('SELECT COUNT(*) FROM lokasi_penjualan')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO lokasi_penjualan (nama_tempat, alamat, deskripsi)
        VALUES (?, ?, ?)
        ''', [
            ('Pasar Langgur', 'Jln. Utama Langgur No.1', 'Pasar utama yang menjual hasil pertanian dan laut.'),
            ('TPI Dullah', 'Pelabuhan Dullah Utara', 'Tempat Pelelangan Ikan yang ramai setiap pagi.')
        ])

    conn.commit()
    conn.close()


# Route untuk halaman utama
@app.route('/')
def home():
    # Info default yang akan ditampilkan
    info_pertanian = "Pertanian di Maluku Tenggara melibatkan tanaman seperti kelapa, jagung, dan singkong."
    info_nelayan = "Nelayan di Maluku Tenggara mengandalkan hasil laut seperti ikan tuna dan ikan kerapu."

    # Mengambil artikel-artikel dari database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles')
    articles = cursor.fetchall()
    conn.close()

    return render_template('Home.html', pertanian=info_pertanian, nelayan=info_nelayan, articles=articles)


# Route untuk halaman Pertanian
@app.route('/pertanian')
def pertanian_page():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pertanian_info LIMIT 1')
    pertanian_data = cursor.fetchone()
    conn.close()

    # Jika data ditemukan, ambil isinya, jika tidak kosong string
    info = pertanian_data['info'] if pertanian_data else ''
    return render_template('pertanian.html', info=info)


# Route untuk halaman Nelayan
@app.route('/nelayan')
def nelayan_page():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM nelayan_info LIMIT 1')
    nelayan_data = cursor.fetchone()
    conn.close()

    info = nelayan_data['info'] if nelayan_data else ''
    return render_template('nelayan.html', info=info)


# Route untuk halaman Lokasi Penjualan
@app.route('/lokasi_penjualan')
def lokasi_penjualan_page():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lokasi_penjualan')
    locations = cursor.fetchall()
    conn.close()

    return render_template('lokasi_penjualan.html', locations=locations)


if __name__ == '__main__':
    create_table()  # Membuat tabel artikel jika belum ada
    add_articles_if_empty()  # Menambahkan artikel jika tabel kosong
    create_additional_tables()  # Membuat tabel tambahan untuk pertanian, nelayan, dan lokasi penjualan
    seed_additional_data()  # Menambahkan data default ke tabel tambahan
    app.run(debug=True, host="0.0.0.0")
