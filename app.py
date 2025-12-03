import streamlit as st
import numpy as np
import os
import random
import time
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import tensorflow as tf

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Pengenalan Uang Rupiah", layout="wide")

# CSS untuk tampilan yang sangat sederhana dan ramah anak
st.markdown("""
<style>
    /* Sembunyikan header dan footer streamlit */
    header[data-testid="stHeader"] {display: none;}
    .main > div {padding-top: 2rem;}
    
    /* Background warna-warni */
    .main {
        background: linear-gradient(45deg, #FFE5E5, #E5F3FF, #E5FFE5, #FFF5E5);
        background-size: 400% 400%;
        animation: gradientShift 6s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Judul besar dan menarik */
    .big-title {
        font-size: 4rem !important;
        text-align: center;
        color: #FF1493;
        text-shadow: 4px 4px 0px #FFD700;
        margin: 25px 0;
        font-weight: 900;
        animation: wiggle 3s ease-in-out infinite;
    }
    
    @keyframes wiggle {
        0%, 100% { transform: rotate(-3deg); }
        50% { transform: rotate(3deg); }
    }
    
    /* Judul utama */
    .main-title {
        font-size: 4rem;
        text-align: center;
        color: #FF1493;
        text-shadow: 4px 4px 0px #FFD700;
        font-weight: 900;
        margin-top: 30px;
        animation: bounce 2s infinite alternate;
    }

    @keyframes bounce {
        0% { transform: translateY(0px); }
        100% { transform: translateY(-10px); }
    }

    /* Deskripsi sistem */
    .system-desc {
        font-size: 1.6rem;
        text-align: center;
        color: #2C3E50;
        font-weight: 500;
        margin: 20px auto;
        max-width: 800px;
    }
            
/* Tombol besar “Mulai Belajar” */
    .stButton > button {
        display: block;
        margin: 0 auto;
        background-color: #FF69B4 !important;
        color: white !important;
        font-size: 2rem !important;
        font-weight: bold !important;
        padding: 20px 50px !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    .stButton > button:hover {
        background-color: #FF1493 !important;
        transform: scale(1.05) !important;
    }
    
    /* Kotak hasil yang besar */
    .result-big {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 30px;
        text-align: center;
        color: white;
        font-size: 2rem;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Text besar untuk anak */
    .big-text {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin: 15px 0;
    }
    
    /* Emoji besar */
    .big-emoji {
        font-size: 4rem;
        text-align: center;
        margin: 15px 0;
    }
    
    
    /* Garis pemisah */
    .sidebar-line {
        height: 4px;
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
        margin: 50px 0;
        border-radius: 2px;
    }
    
    /* Section title dengan warna hitam */
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #000000 !important;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- Load Model --------------------
@st.cache_resource
def load_money_model():
    try:
       # Update path ke model baru
        return load_model("best_model_final.keras") # Path relatif dari folder root
    except Exception as e:
       st.error(f"Gagal load model: {e}")
       return None
   
model = load_money_model()

# -------------------- Mapping --------------------
label_mapping = {
    0: "Rp1.000",
    1: "Rp10.000",
    2: "Rp100.000",
    3: "Rp2.000",
    4: "Rp20.000",
    5: "Rp5.000",
    6: "Rp50.000"
}

file_mapping = {
    "Rp1.000": "1000",
    "Rp2.000": "2000",
    "Rp5.000": "5000",
    "Rp10.000": "10000",
    "Rp20.000": "20000",
    "Rp50.000": "50000",
    "Rp100.000": "100000"
}

# Data mata uang untuk emoji dan warna
money_data = {
    "Rp1.000": {"name": "SERIBU", "color": "HIJAU", "emoji": "💚"},
    "Rp2.000": {"name": "DUA RIBU", "color": "ABU-ABU", "emoji": "⚪"},
    "Rp5.000": {"name": "LIMA RIBU", "color": "COKELAT", "emoji": "🟤"},
    "Rp10.000": {"name": "SEPULUH RIBU", "color": "UNGU", "emoji": "🟣"},
    "Rp20.000": {"name": "DUA PULUH RIBU", "color": "HIJAU", "emoji": "🟢"},
    "Rp50.000": {"name": "LIMA PULUH RIBU", "color": "BIRU", "emoji": "🔵"},
    "Rp100.000": {"name": "SERATUS RIBU", "color": "MERAH", "emoji": "🔴"}
}

deskripsi_uang = {
    "Rp1.000": """
    <div style="background: linear-gradient(135deg, #E8F8F5, #D4EFDF); padding: 15px; border-radius: 10px; border-left: 5px solid #27AE60;">
        <div style="font-size: 1.3rem; font-weight: bold; color: #27AE60; margin-bottom: 10px;">💚 Uang Rp 1.000</div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">👤 Tokoh (Depan):</span> 
            <span style="color: #34495E;">Tjut Meutia</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">🎨 Warna:</span> 
            <span style="color: #27AE60; font-weight: bold;">HIJAU</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">💃 Tarian (Belakang):</span> 
            <span style="color: #34495E;">Tari Tifa dari Papua & Maluku</span>
        </div>
    </div>
    """,
    "Rp2.000": """
    <div style="background: linear-gradient(135deg, #F4F6F7, #ECF0F1); padding: 15px; border-radius: 10px; border-left: 5px solid #95A5A6;">
        <div style="font-size: 1.3rem; font-weight: bold; color: #7F8C8D; margin-bottom: 10px;">⚪ Uang Rp 2.000</div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">👤 Tokoh (Depan):</span> 
            <span style="color: #34495E;">Mohammad Hoesni Thamrin</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">🎨 Warna:</span> 
            <span style="color: #7F8C8D; font-weight: bold;">ABU-ABU</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">💃 Tarian (Belakang):</span> 
            <span style="color: #34495E;">Tari Piring dari Sumatera Barat</span>
        </div>
    </div>
    """,
    "Rp5.000": """
    <div style="background: linear-gradient(135deg, #FEF5E7, #FAE5D3); padding: 15px; border-radius: 10px; border-left: 5px solid #D68910;">
        <div style="font-size: 1.3rem; font-weight: bold; color: #D68910; margin-bottom: 10px;">🟤 Uang Rp 5.000</div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">👤 Tokoh (Depan):</span> 
            <span style="color: #34495E;">Dr. KH. Idham Chalid</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">🎨 Warna:</span> 
            <span style="color: #D68910; font-weight: bold;">COKELAT</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">💃 Tarian (Belakang):</span> 
            <span style="color: #34495E;">Tari Gambyong dari Surakarta - Jawa Tengah</span>
        </div>
    </div>
    """,
    "Rp10.000": """
    <div style="background: linear-gradient(135deg, #F4ECF7, #E8DAEF); padding: 15px; border-radius: 10px; border-left: 5px solid #8E44AD;">
        <div style="font-size: 1.3rem; font-weight: bold; color: #8E44AD; margin-bottom: 10px;">🟣 Uang Rp 10.000</div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">👤 Tokoh (Depan):</span> 
            <span style="color: #34495E;">Frans Kaisiepo</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">🎨 Warna:</span> 
            <span style="color: #8E44AD; font-weight: bold;">UNGU</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">💃 Tarian (Belakang):</span> 
            <span style="color: #34495E;">Tari Pakarena dari Sulawesi Selatan</span>
        </div>
    </div>
    """,
    "Rp20.000": """
    <div style="background: linear-gradient(135deg, #E8F8F5, #D1F2EB); padding: 15px; border-radius: 10px; border-left: 5px solid #1ABC9C;">
        <div style="font-size: 1.3rem; font-weight: bold; color: #1ABC9C; margin-bottom: 10px;">🟢 Uang Rp 20.000</div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">👤 Tokoh (Depan):</span> 
            <span style="color: #34495E;">Dr. G.S.S.J. Ratulangi</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">🎨 Warna:</span> 
            <span style="color: #1ABC9C; font-weight: bold;">HIJAU</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">💃 Tarian (Belakang):</span> 
            <span style="color: #34495E;">Tari Gong dari Kalimantan Timur</span>
        </div>
    </div>
    """,
    "Rp50.000": """
    <div style="background: linear-gradient(135deg, #EBF5FB, #D6EAF8); padding: 15px; border-radius: 10px; border-left: 5px solid #3498DB;">
        <div style="font-size: 1.3rem; font-weight: bold; color: #3498DB; margin-bottom: 10px;">🔵 Uang Rp 50.000</div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">👤 Tokoh (Depan):</span> 
            <span style="color: #34495E;">Ir. H. Djuanda Kartawidjaja</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">🎨 Warna:</span> 
            <span style="color: #3498DB; font-weight: bold;">BIRU</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">💃 Tarian (Belakang):</span> 
            <span style="color: #34495E;">Tari Legong dari Bali</span>
        </div>
    </div>
    """,
    "Rp100.000": """
    <div style="background: linear-gradient(135deg, #FADBD8, #F5B7B1); padding: 15px; border-radius: 10px; border-left: 5px solid #E74C3C;">
        <div style="font-size: 1.3rem; font-weight: bold; color: #E74C3C; margin-bottom: 10px;">🔴 Uang Rp 100.000</div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">👤 Tokoh (Depan):</span> 
            <span style="color: #34495E;">Ir. Soekarno & Drs. Mohammad Hatta</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">🎨 Warna:</span> 
            <span style="color: #E74C3C; font-weight: bold;">MERAH</span>
        </div>
        <div style="background: white; padding: 10px; border-radius: 8px;">
            <span style="font-weight: bold; color: #2C3E50;">💃 Tarian (Belakang):</span> 
            <span style="color: #34495E;">Tari Topeng Betawi dari DKI Jakarta</span>
        </div>
    </div>
    """
}

# Fungsi prediksi dengan CNN
def predict_currency(img):
    """Prediksi mata uang menggunakan model CNN"""
    try:

        # Pastikan model sudah dimuat
        if model is None:
            st.error("Model belum dimuat")
            return None, 0.0
        
        # TAMBAHAN: Validasi gambar
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if img.size[0] < 100 or img.size[1] < 100:
            st.error("📷 Gambar terlalu kecil! Ambil foto lebih dekat ya")
            return None, 0.0
        
        # Resize dan preprocess
        img_resized = img.resize((224, 224))
        img_array = image.img_to_array(img_resized)
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Prediksi
        predictions = model.predict(img_array, verbose=0)
        predicted_index = np.argmax(predictions[0])  # Ambil index tertinggi
        max_prob = predictions[0][predicted_index]   # Ambil nilai probabilitasnya
        
        # Mapping ke nominal (INI SUDAH BENAR!)
        predicted_nominal = label_mapping[predicted_index]
        
        return predicted_nominal, max_prob
        
    except Exception as e:
        st.error(f"Error predicting: {e}")
        return None, 0.0

# Fungsi suara
def play_audio(nominal):
    audio_path = f"audio/{file_mapping[nominal]}.mp3"
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.info(f"🔊 Ini uang {money_data[nominal]['name']} rupiah! Warnanya {money_data[nominal]['color']}!")

# ============= HALAMAN UTAMA ================
# Judul dan deskripsi sistem
st.markdown("""
    <div style="text-align: center; margin-top: 30px;">
        <br><br>
        <h1 class="main-title">Halo! Selamat Datang di <span style="color:#007bff;">RupiahKu</span> 🎉</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="system-desc">
    <b>“RupiahKu”</b> adalah sistem AI yang dibuat untuk mengenali 
    mata uang kertas Rupiah berdasarkan gambar.
    Ayo belajar mengenali dan membedakan uang bersama RupiahKu!
    </div>
""", unsafe_allow_html=True)

# Tombol Mulai Belajar
if st.button("🚀 GET STARTED"):
    st.session_state["show_section1"] = True
    st.rerun()

st.markdown('<div class="sidebar-line"></div>', unsafe_allow_html=True)

# =========== SECTION 1: FOTO UANG ==============
if "show_section1" in st.session_state and st.session_state["show_section1"]:
    st.markdown('<h2 class="main-title" style="font-size: 3rem;">📷 FOTO UANG KAMU</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])  # Kiri untuk input, kanan untuk hasil

    # Variabel untuk menyimpan hasil deteksi
    hasil_prediksi = None

    with col1:
        # Ambil foto langsung dari kamera
        camera_file = st.camera_input("Ambil foto uangmu :")
        if camera_file:
            img = Image.open(camera_file)

            # Tombol analisis besar
            with st.spinner("🤖 Sedang mengenali uang ..."):
                time.sleep(1)
                
                # Prediksi menggunakan CNN
                result, prob = predict_currency(img)
                
                if result is None:
                    st.error("Gagal memproses gambar. Coba lagi.")
                elif prob < 0.70:  # ← UBAH DARI 0.5 JADI 0.70
                    with col2:
                        st.markdown(f"""
                        <div style="
                            background-color: #FFF3CD;
                            color: #856404;
                            padding: 15px;
                            border-radius: 12px;
                            border-left: 8px solid #FFB300;
                            font-size: 1.1rem;
                            margin-top: 20px;
                            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
                        ">
                            <b style="font-size: 1.3rem;">⚠️ Gambar Kurang Jelas!</b><br>
                            Coba foto uang dengan lebih terang, tidak blur, dan ambil jarak lebih jauh.
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    hasil_prediksi = result

    # Tampilkan hasil deteksi di kolom kanan
    if hasil_prediksi: # hanya tampilkan jika probabilitas tinggi
        with col2:
            info = money_data[hasil_prediksi]
            
            st.write("")

            # Deskripsi dengan background dan teks yang lebih terlihat
            st.markdown(f"""
            <br><br>
            <div style="background: #E8F4FD; color: #2C3E50; padding: 15px; border-radius: 10px; border-left: 5px solid #3498DB; margin-bottom: 10px;">
                <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 10px;">ℹ️ Hasil Deteksi:</div>
                <div style="font-size: 1rem; line-height: 1.5;">{deskripsi_uang[hasil_prediksi]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Audio
            play_audio(hasil_prediksi)

    st.markdown('<div class="sidebar-line"></div>', unsafe_allow_html=True)

# ========= SECTION 2: LIHAT UANG ==============
st.markdown('<h2 class="main-title" style="font-size: 3rem;">📖 KENALAN DENGAN SEMUA UANG</h2>', unsafe_allow_html=True)
st.markdown('<div class="big-text">Lihat sisi depan dan belakang uang, lalu dengarkan suaranya!</div>', unsafe_allow_html=True)

# Ambil daftar nominal
nominals = ["Rp1.000", "Rp2.000", "Rp5.000", "Rp10.000", "Rp20.000", "Rp50.000", "Rp100.000"]

# Loop untuk setiap nominal
for nominal in nominals:
    # Ekstrak angka nominal untuk path gambar (misalnya, "Rp1.000" -> "1000")
    nominal_angka = nominal.replace("Rp", "").replace(".", "").replace(",", "")
    
    # Buat container untuk setiap nominal
    with st.container():
        st.markdown(f"""
            <h3 style="text-align: center; color: #2C3E50; font-size: 2rem; margin-bottom: 20px;">
                {money_data[nominal]['emoji']} {nominal} - {money_data[nominal]['name']} RUPIAH
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Buat 3 kolom: Depan, Deskripsi, Belakang
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            st.markdown('<p style="text-align: center; font-size: 1.3rem; font-weight: bold; color: #34495E;">SISI DEPAN</p>', unsafe_allow_html=True)
            img_depan = f"img/{nominal_angka}-depan.jpeg"
            
            if os.path.exists(img_depan):
                st.image(img_depan, use_column_width=True, caption=f"Depan {nominal}")
            else:
                st.markdown(f'<div class="big-emoji">{money_data[nominal]["emoji"]}</div>', unsafe_allow_html=True)
        
        with col2:
            # Deskripsi di tengah
            st.markdown(deskripsi_uang[nominal], unsafe_allow_html=True)
            
            # Tombol audio di tengah
            st.markdown('<div style="text-align: center; margin-top: 15px;">', unsafe_allow_html=True)
            play_audio(nominal)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<p style="text-align: center; font-size: 1.3rem; font-weight: bold; color: #34495E;">SISI BELAKANG</p>', unsafe_allow_html=True)
            img_belakang = f"img/{nominal_angka}-belakang.jpeg"
            
            if os.path.exists(img_belakang):
                st.image(img_belakang, use_column_width=True, caption=f"Belakang {nominal}")
            else:
                st.markdown(f'<div style="background: #ECF0F1; padding: 20px; border-radius: 10px; text-align: center;"><p style="color: #7F8C8D;">Gambar belakang belum tersedia</p></div>', unsafe_allow_html=True)
        
        st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style="text-align: center; padding: 20px; font-size: 1.3rem; color:#2C3E50;">
<small>© 2024 Sistem Deteksi Uang Indonesia | Powered by TensorFlow & Streamlit</small>
</div>
""", unsafe_allow_html=True)