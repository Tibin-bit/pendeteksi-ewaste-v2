import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Global AI E-Waste Detector Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk Tampilan Modern & Premium
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1e222d;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2e3440;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .hazard-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .hazard-medium {
        color: #ffa726;
        font-weight: bold;
    }
    .hazard-low {
        color: #66bb6a;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi State Riwayat
if "detection_history" not in st.session_state:
    st.session_state.detection_history = []

# ==========================================
# 2. SIDEBAR - PENGATURAN API & KONFIGURASI
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/electronic-circuit.png", width=80)
    st.title("⚡ AI Core Settings")
    st.caption("Universal E-Waste Detection Engine v4.0")
    
    # Input API Key Google Gemini
    api_key = st.text_input(
        "Masukkan Gemini API Key:", 
        type="password", 
        help="Dapatkan API Key gratis di https://aistudio.google.com/"
    )
    
    st.markdown("---")
    st.subheader("🌐 Standar Klasifikasi")
    st.info("Menggunakan standar **UN Global E-Waste Monitor (ITU / UNEP)** untuk klasifikasi 6 kategori e-waste dunia.")
    
    st.markdown("---")
    st.markdown("Developed with Streamlit & Gemini Vision Engine")

# ==========================================
# 3. FUNGSI ANALISIS VISION AI (ENGINE)
# ==========================================
def analyze_ewaste_universal(image, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Bertindaklah sebagai Ahli Pengolahan Sampah Elektronik (E-Waste Specialist) dan Metalurgi Tingkat Dunia.
    Analisis gambar ini dengan cermat dan berikan output strictly dalam format JSON tanpa markdown formatting lain.

    Struktur JSON yang harus dikembalikan:
    {
        "nama_objek": "Nama spesifik komponen/perangkat yang terdeteksi",
        "kategori_un": "Salah satu dari: [1. Temperature exchange equipment, 2. Screens & monitors, 3. Lamps, 4. Large equipment, 5. Small equipment, 6. Small IT and telecommunication equipment]",
        "deskripsi": "Penjelasan detail mengenai objek ini",
        "tingkat_bahaya": "Tinggi / Sedang / Rendah",
        "skor_bahaya": 1-10 (angka),
        "bahan_berbahaya": ["Daftar senyawa/logam beracun seperti Lead, Mercury, Cadmium, BFR, Lithium, dll."],
        "potensi_logam_mulia": {
            "Emas (Au)": "Ada / Tidak ada / Sangat Tinggi",
            "Perak (Ag)": "Ada / Tidak ada",
            "Tembaga (Cu)": "Ada / Tidak ada",
            "Litium/Kobal": "Ada / Tidak ada"
        },
        "komponen_utama": ["Daftar 3-5 komponen penyusun objek ini"],
        "instruksi_penanganan": [
            "Langkah 1 aman membongkar/memilah",
            "Langkah 2 cara daur ulang yang benar",
            "Langkah 3 pencegahan bahaya kimia/fisik"
        ],
        "dapat_didaur_ulang_persen": 0-100 (angka integer)
    }
    """
    
    try:
        response = model.generate_content([prompt, image])
        # Cleaning response text jika mengandung markdown ```json
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return data, None
    except Exception as e:
        return None, str(e)

# ==========================================
# 4. TAMPILAN UTAMA & NAVIGASI TAB
# ==========================================
st.title("⚡ Global AI E-Waste Detector Pro")
st.subheader("Sistem Deteksi & Analisis Sampah Elektronik Universal Berbasis Vision AI")

tab1, tab2, tab3 = st.tabs(["🔍 Deteksi Kamera & Unggah", "📊 Dashboard & Riwayat", "📚 Panduan Kategori PBB"])

# ------------------------------------------
# TAB 1: DETEKSI SENSING
# ------------------------------------------
with tab1:
    col_input, col_result = st.columns([1, 1.2])
    
    with col_input:
        st.markdown("### 1. Masukkan Gambar E-Waste")
        source = st.radio("Pilih Sumber Input:", ["Kamera Langsung 📷", "Unggah Berkas Gambar 📁"])
        
        input_image = None
        if "Kamera" in source:
            camera_file = st.camera_input("Ambil Foto E-Waste")
            if camera_file:
                input_image = Image.open(camera_file)
        else:
            uploaded_file = st.file_uploader("Pilih file gambar (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
            if uploaded_file:
                input_image = Image.open(uploaded_file)
        
        if input_image:
            st.image(input_image, caption="Gambar yang Diambil", use_container_width=True)
            btn_analyze = st.button("🚀 Jalankan Analisis AI Universal", type="primary", use_container_width=True)
    
    with col_result:
        st.markdown("### 2. Hasil Deteksi & Analisis Mendalam")
        
        if 'btn_analyze' in locals() and btn_analyze:
            if not api_key:
                st.error("⚠️ Harap masukkan Gemini API Key di sidebar sebelah kiri terlebih dahulu!")
            elif input_image is None:
                st.warning("⚠️ Ambil foto atau unggah gambar terlebih dahulu.")
            else:
                with st.spinner("🧠 AI sedang menganalisis struktur fisik, komponen beracun, dan potensi logam mulia..."):
                    result, err = analyze_ewaste_universal(input_image, api_key)
                    
                    if err:
                        st.error(f"Gagal melakukan analisis: {err}")
                    else:
                        # Simpan ke riwayat
                        record = {
                            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "nama": result["nama_objek"],
                            "kategori": result["kategori_un"],
                            "bahaya": result["tingkat_bahaya"],
                            "daur_ulang": result["dapat_didaur_ulang_persen"]
                        }
                        st.session_state.detection_history.append(record)
                        
                        # Tampilan Hasil Deteksi
                        st.success(f"✅ Terdeteksi: **{result['nama_objek']}**")
                        
                        # Metric Cards
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Kategori UN", result["kategori_un"].split(".")[1] if "." in result["kategori_un"] else result["kategori_un"])
                        with m2:
                            hazard_color = "🔴" if result["tingkat_bahaya"] == "Tinggi" else ("🟡" if result["tingkat_bahaya"] == "Sedang" else "🟢")
                            st.metric("Tingkat Bahaya", f"{hazard_color} {result['tingkat_bahaya']}")
                        with m3:
                            st.metric("Potensi Daur Ulang", f"{result['dapat_didaur_ulang_persen']}%")
                        
                        st.markdown("---")
                        st.markdown(f"**📝 Deskripsi Objektif:**  \n{result['deskripsi']}")
                        
                        # Tab detail bahan
                        d_tab1, d_tab2, d_tab3 = st.tabs(["☣️ Bahan Berbahaya", "💎 Logam Mulia", "🛠️ Cara Penanganan"])
                        
                        with d_tab1:
                            st.write(f"**Skor Bahaya Kimia:** {result['skor_bahaya']}/10")
                            st.progress(result['skor_bahaya'] / 10)
                            st.write("**Kandungan Toksisitas Terdeteksi:**")
                            for toxin in result["bahan_berbahaya"]:
                                st.write(f"- ⚠️ {toxin}")
                                
                        with d_tab2:
                            st.write("**Estimasi Logam Mulia & Material Berharga:**")
                            for metal, status in result["potensi_logam_mulia"].items():
                                st.write(f"- **{metal}**: {status}")
                                
                        with d_tab3:
                            st.write("**Langkah Daur Ulang & Keamanan:**")
                            for idx, step in enumerate(result["instruksi_penanganan"], 1):
                                st.write(f"{idx}. {step}")

# ------------------------------------------
# TAB 2: DASHBOARD & ANALITIK
# ------------------------------------------
with tab2:
    st.markdown("### 📊 Dashboard Statistik Riwayat Deteksi")
    
    if len(st.session_state.detection_history) == 0:
        st.info("Belum ada data deteksi. Lakukan analisis gambar di Tab 1 terlebih dahulu!")
    else:
        df_history = pd.DataFrame(st.session_state.detection_history)
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### Distribusi Kategori E-Waste")
            fig_cat = px.pie(df_history, names="kategori", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with c2:
            st.markdown("##### Tingkat Risiko Bahaya E-Waste")
            fig_hazard = px.bar(df_history, x="bahaya", color="bahaya", 
                                color_discrete_map={"Tinggi": "#ff4b4b", "Sedang": "#ffa726", "Rendah": "#66bb6a"})
            st.plotly_chart(fig_hazard, use_container_width=True)
            
        st.markdown("##### Tabel Riwayat Lengkap")
        st.dataframe(df_history, use_container_width=True)
        
        # Download Data CSV
        csv_data = df_history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Laporan Deteksi (CSV)",
            data=csv_data,
            file_name="laporan_deteksi_ewaste.csv",
            mime="text/csv"
        )

# ------------------------------------------
# TAB 3: PANDUAN KATEGORI E-WASTE PBB
# ------------------------------------------
with tab3:
    st.markdown("### 📚 6 Kategori E-Waste Menurut UN Global E-Waste Monitor")
    
    cat_data = [
        {"Kategori": "1. Temperature Exchange Equipment", "Contoh": "Kulkas, AC, Freezer, Heat Pump.", "Risiko": "Gas CFC/HCFC yang merusak lapisan ozon."},
        {"Kategori": "2. Screens & Monitors", "Contoh": "TV, Monitor Komputer, Laptop, Tablet.", "Risiko": "Timbal (CRT), Merkuri (LCD backlight)."},
        {"Kategori": "3. Lamps", "Contoh": "Lampu Neon (CFL), Lampu LED, Lampu HID.", "Risiko": "Uap Merkuri beracun saat pecah."},
        {"Kategori": "4. Large Equipment", "Contoh": "Mesin Cuci, Oven, Panel Surya, Mesin Fotokopi.", "Risiko": "Kapasitor daya tinggi, PCB besar."},
        {"Kategori": "5. Small Equipment", "Contoh": "Vacuum Cleaner, Microwave, Toaster, Alat Cukur.", "Risiko": "Plastik BFR, komponen listrik campuran."},
        {"Kategori": "6. Small IT & Telecom", "Contoh": "HP, Router, Printer, Kabel, Headphone.", "Risiko": "Baterai Lithium-ion, komponen mikro terintegrasi."}
    ]
    
    st.table(pd.DataFrame(cat_data))
