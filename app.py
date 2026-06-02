import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import time

# ==========================================
# 1. INITIAL APP CONFIG & THEME INJECTION
# ==========================================
st.set_page_config(
    page_title="RISK ANALYTICS | Assessment Pipeline",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Perbaikan CSS: Kalibrasi ulang Segmented Control agar tidak ngerap ke bawah (Stay Horizontal)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* 1. Reset Main App Background & Font */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMainBlockContainer"] {
        background-color: #F9F9F9 !important;
        font-family: 'Inter', sans-serif !important;
        color: #1B1B1B !important;
    }
    
    /* 2. Form Container: Putih Bersih Modern */
    div[data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 12px !important;
        padding: 2.5rem !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.02) !important;
    }
    
    /* 3. Teks Judul Input Form (Sex, Pay 0, dll) Tetap Hitam / Kontras Tinggi */
    div[data-testid="stForm"] label, 
    div[data-testid="stForm"] .stWidgetLabel p,
    div[data-testid="stSlider"] label p,
    div[data-testid="stNumberInput"] label p,
    div[data-testid="stSelectbox"] label p {
        color: #1B1B1B !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }
    
    /* Sub-heading Section */
    .label-matte-style {
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #000000 !important;
        border-bottom: 1px solid #EEEEEE;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }
    
    /* 4. PERBAIKAN TOTAL SEGMENTED CONTROL (SWITCH NAVIGATION) */
    div[data-testid="stSegmentedControl"] {
        background-color: #ECECEC !important;
        padding: 6px !important;
        border-radius: 30px !important;
        display: flex !important;
        flex-direction: row !important; /* Memaksa sejajar horizontal */
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    div[data-testid="stSegmentedControl"] [data-testid="stSegmentedControlOption"] {
        flex: 1 !important; /* Membagi space sama rata agar teks memanjang sempurna */
        white-space: nowrap !important; /* Melarang keras teks membungkus/wrap ke bawah */
        text-align: center !important;
    }

    div[data-testid="stSegmentedControl"] button {
        border-radius: 30px !important;
        color: #5E5E5E !important; /* Warna text saat tidak aktif */
        font-size: 13px !important;
        font-weight: 600 !important;
        border: none !important;
        background-color: transparent !important;
        width: 100% !important;
        white-space: nowrap !important; /* Mengunci teks tombol agar satu baris */
        padding: 6px 16px !important;
    }
    
    /* State ketika tombol capsule dipilih (Active) */
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background-color: #FFFFFF !important;
        color: #000000 !important; /* Teks hitam pekat saat aktif */
        box-shadow: 0px 2px 6px rgba(0,0,0,0.08) !important;
    }

    /* 5. Button PREDIKSI */
    div.stFormSubmitButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important; /* FIX: Teks jadi hitam pekat dari awal */
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 6px !important;
        border: 1px solid #1B1B1B !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    div.stFormSubmitButton > button:hover {
        background-color: #000000 !important;
        color: #FFFFFF !important; /* Efek hover: teks balik jadi putih pas bg jadi hitam */
        border-color: #000000 !important;
    }
    
    /* 6. Fix Number Input — konsisten di semua platform */
    div[data-testid="stNumberInput"] {
        width: 100% !important;
    }

    div[data-testid="stNumberInput"] > div {
        display: flex !important;
        align-items: center !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D1D1D1 !important;
        border-radius: 6px !important;
        overflow: hidden !important;
        height: 42px !important;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #1B1B1B !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        padding: 0 10px !important;
        width: 100% !important;
        height: 42px !important;
    }

    div[data-testid="stNumberInput"] button {
        background-color: #F5F5F5 !important;
        border: none !important;
        border-left: 1px solid #D1D1D1 !important;
        color: #1B1B1B !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 36px !important;
        min-width: 36px !important;
        height: 42px !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        flex-shrink: 0 !important;
    }

    div[data-testid="stNumberInput"] button:hover {
        background-color: #E8E8E8 !important;
        color: #000000 !important;
    }

    div[data-testid="stNumberInput"] button:first-of-type {
        border-left: 1px solid #D1D1D1 !important;
        border-right: none !important;
    }

    /* 7. Card Output Hasil */
    .result-card-premium {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.01);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 140px;
    }
            
    /* Fix Selectbox (Sex, Education, Marriage) */
    div[data-testid="stSelectbox"] > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D1D1 !important;
        border-radius: 6px !important;
        color: #1B1B1B !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        height: 42px !important;
        min-height: 42px !important;
    }

    div[data-testid="stSelectbox"] span {
        color: #1B1B1B !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    div[data-testid="stSelectbox"] svg {
        fill: #1B1B1B !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BACKEND ENGINE (LOAD ARTIFACTS)
# ==========================================
MODELS_DIR = "models"

@st.cache_resource
def load_risk_pipeline():
    try:
        # Load core models
        xgb_model        = joblib.load(os.path.join(MODELS_DIR, "xgb_model.pkl"))
        scaler           = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        selected_features= joblib.load(os.path.join(MODELS_DIR, "selected_features.pkl"))

        # Load anomaly models
        iso_forest       = joblib.load(os.path.join(MODELS_DIR, "iso_forest.pkl"))
        lof              = joblib.load(os.path.join(MODELS_DIR, "lof.pkl"))
        pca              = joblib.load(os.path.join(MODELS_DIR, "pca.pkl"))

        # Load training min/max for normalization — KRITIS agar tidak divide-by-zero
        iso_min          = float(joblib.load(os.path.join(MODELS_DIR, "iso_min.pkl")))
        iso_max          = float(joblib.load(os.path.join(MODELS_DIR, "iso_max.pkl")))
        lof_min          = float(joblib.load(os.path.join(MODELS_DIR, "lof_min.pkl")))
        lof_max          = float(joblib.load(os.path.join(MODELS_DIR, "lof_max.pkl")))

        # Load threshold
        threshold = joblib.load(os.path.join(MODELS_DIR, "threshold.pkl"))
        if isinstance(threshold, (list, np.ndarray)):
            threshold = float(threshold[0])
        else:
            threshold = float(threshold)

        # Blend weights (sesuai notebook: ALPHA=0.10, BETA=0.90)
        ALPHA = 0.10
        BETA  = 0.90

        return (
            xgb_model, scaler, selected_features, threshold,
            iso_forest, lof, pca,
            iso_min, iso_max, lof_min, lof_max,
            ALPHA, BETA
        )
    except Exception as e:
        st.error(f"⚠️ Engine Error: {str(e)}")
        return (None,) * 13

(
    model, scaler, selected_features, THRESHOLD,
    iso_forest, lof, pca,
    ISO_MIN, ISO_MAX, LOF_MIN, LOF_MAX,
    ALPHA, BETA
) = load_risk_pipeline()

# ==========================================
# 3. FEATURE ENGINEERING PIPELINE
#    (Persis sama dengan logika di notebook)
# ==========================================

def run_feature_engineering_pipeline(df_raw):
    """
    Replikasi lengkap feature engineering dari notebook:
    - PAY delay features
    - Utilization features
    - Pay ratio features
    - Bill stability features
    - Total aggregates
    Kemudian filter ke selected_features saja.
    """
    df = df_raw.copy()

    PAY_COLS  = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
    BILL_COLS = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
    AMT_COLS  = ['PAY_AMT1',  'PAY_AMT2',  'PAY_AMT3',  'PAY_AMT4',  'PAY_AMT5',  'PAY_AMT6']

    # Pastikan semua kolom numerik
    for col in PAY_COLS + BILL_COLS + AMT_COLS + ['LIMIT_BAL', 'AGE', 'SEX', 'EDUCATION', 'MARRIAGE']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- Delay features ---
    df['TOTAL_DELAY']       = df[PAY_COLS].clip(lower=0).sum(axis=1)
    df['NUM_LATE_MONTHS']   = (df[PAY_COLS] > 0).sum(axis=1)
    df['MAX_DELAY']         = df[PAY_COLS].max(axis=1)
    df['DELAY_TREND']       = df['PAY_0'] - df['PAY_6']
    df['RECENT_ESCALATION'] = (
        (df['PAY_0'] > df['PAY_2']).astype(int) +
        (df['PAY_2'] > df['PAY_3']).astype(int)
    )

    # --- Utilization features ---
    df['UTILIZATION_RATIO'] = (df['BILL_AMT1'] / df['LIMIT_BAL'].clip(lower=1)).clip(0, 2)
    df['AVG_UTILIZATION']   = (df[BILL_COLS].mean(axis=1) / df['LIMIT_BAL'].clip(lower=1)).clip(0, 2)
    df['HIGH_UTIL_FLAG']    = (df['UTILIZATION_RATIO'] > 0.9).astype(int)

    # --- Pay ratio per bulan ---
    for i in range(1, 7):
        bill = df[f'BILL_AMT{i}'].clip(lower=1)
        df[f'PAY_RATIO_{i}'] = (df[f'PAY_AMT{i}'] / bill).clip(0, 5)

    PAY_RATIO_COLS = [f'PAY_RATIO_{i}' for i in range(1, 7)]

    df['AVG_PAY_RATIO']    = df[PAY_RATIO_COLS].mean(axis=1)
    df['CHRONIC_UNDERPAY'] = (df[PAY_RATIO_COLS] < 0.05).sum(axis=1)
    df['PAYMENT_TREND']    = df['PAY_AMT1'] - df['PAY_AMT6']
    df['TOTAL_PAYMENT']    = df[AMT_COLS].sum(axis=1)
    df['TOTAL_BILL']       = df[BILL_COLS].sum(axis=1)
    df['PAYMENT_GAP']      = (df['TOTAL_BILL'] - df['TOTAL_PAYMENT']).clip(lower=0)

    # --- Bill stability features ---
    df['BILL_GROWTH']      = df['BILL_AMT1'] - df['BILL_AMT6']
    df['BILL_VOLATILITY']  = df[BILL_COLS].std(axis=1)

    # Tambahkan kolom yang mungkin tidak ada
    for col in selected_features:
        if col not in df.columns:
            df[col] = 0

    # Return hanya selected features
    result = df[selected_features].copy()
    result = result.replace([np.inf, -np.inf], np.nan).fillna(0)
    result = result.astype(np.float64)
    return result


def predict_blend_ensemble(df_input):
    """
    Full blend ensemble prediction persis seperti notebook:
    1. Feature engineering
    2. StandardScaler transform
    3. IF + PCA-LOF anomaly scores
    4. Normalisasi pakai min/max dari TRAINING DATA (bukan dari query)
    5. Ensemble anomaly: W_ISO*iso_norm + W_LOF*lof_norm  (sesuai notebook W_ISO optimal)
    6. Blend: ALPHA * anomaly_score + BETA * xgb_proba
    7. Decision pakai threshold 0.57
    
    Catatan W_ISO/W_LOF: notebook mencari optimal tapi untuk app kita pakai
    fixed 0.05/0.95 sesuai instruksi user (0.05*iso_norm + 0.95*lof_norm).
    """
    # Step 1: Feature engineering
    X = run_feature_engineering_pipeline(df_input)

    # Step 2: Scale
    X_scaled = scaler.transform(X)

    # Step 3: Anomaly scores (raw, sebelum normalisasi)
    iso_raw = -iso_forest.score_samples(X_scaled)                    # shape (n,)
    X_pca   = pca.transform(X_scaled)
    lof_raw = -lof.score_samples(X_pca)                              # shape (n,)

    # Step 4: Normalisasi pakai min/max TRAINING — bukan min/max query
    #   iso_norm = (iso_raw - iso_train_min) / (iso_train_max - iso_train_min + eps)
    iso_norm = (iso_raw - ISO_MIN) / (ISO_MAX - ISO_MIN + 1e-9)
    lof_norm = (lof_raw - LOF_MIN) / (LOF_MAX - LOF_MIN + 1e-9)

    # Clip ke [0, ~2] supaya tidak explode kalau ada outlier ekstrem
    iso_norm = np.clip(iso_norm, 0, 5)
    lof_norm = np.clip(lof_norm, 0, 5)

    # Step 5: Ensemble anomaly (0.05 iso + 0.95 lof, sesuai instruksi user)
    anomaly_score = 0.05 * iso_norm + 0.95 * lof_norm               # shape (n,)

    # Step 6: XGBoost probability
    xgb_proba = model.predict_proba(X_scaled)[:, 1]                  # shape (n,)

    # Step 7: Final blend
    blend_prob = ALPHA * anomaly_score + BETA * xgb_proba             # shape (n,)

    return blend_prob, xgb_proba, anomaly_score, iso_norm, lof_norm


# ==========================================
# 4. FRONTEND HEADER & NAVIGATION HERO
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-size: 38px; font-weight: 700; letter-spacing: -0.02em; color: #1B1B1B; margin-bottom: 6px;'>Credit Risk Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; color: #5E5E5E; margin: 0 auto; padding-bottom: 20px;'>Advanced Pipeline for Large Scale Financial Assessment</p>", unsafe_allow_html=True)

# Membaca navigasi aktif dari URL query parameter (default: single)
query_params = st.query_params
if "mode" not in query_params:
    st.query_params["mode"] = "single"

current_mode_param = st.query_params["mode"]
current_mode = "Single Client Analysis" if current_mode_param == "single" else "Batch Processing Pipeline"

# Generate class active untuk HTML styling
active_single = "active" if current_mode_param == "single" else ""
active_batch  = "active" if current_mode_param == "batch"  else ""

# Suntik HTML & CSS murni untuk Capsule Tab Switcher + Fix Tombol Batch
st.html(f"""
    <style>
    /* Wrapper capsule utama */
    .capsule-nav-container {{
        background-color: #ECECEC !important;
        padding: 4px !important;
        border-radius: 30px !important;
        max-width: 520px !important;
        margin: 0 auto 30px auto !important;
        display: flex !important;
        justify-content: space-around !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    
    /* Styling link tab dasar - PAKSA HITAM GELAP SEBELUM DI-HOVER */
    .capsule-tab-item {{
        flex: 1 !important;
        text-align: center !important;
        padding: 8px 20px !important;
        border-radius: 30px !important;
        color: #4A4A4A !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        transition: all 0.2s ease-in-out !important;
        display: block !important;
    }}
    
    /* Efek ketika HOVER -> Berubah warna tipis biar interaktif */
    .capsule-tab-item:hover {{
        color: #000000 !important;
        background-color: rgba(255, 255, 255, 0.5) !important;
    }}
    
    /* State AKTIF -> Berubah jadi capsule putih bersih, font hitam pekat */
    .capsule-tab-item.active {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700 !important;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08) !important;
    }}

    /* --- FIX KHUSUS FOR BATCH PROCESSING BUTTONS --- */
    /* Paksa tombol PROSES SEMUA agar berwarna putih mentereng dengan outline hitam gelap */
    div.stMainBlockContainer div.stButton > button {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 6px !important;
        border: 1px solid #1B1B1B !important;
        width: auto !important;
        transition: all 0.2s ease !important;
    }}

    div.stMainBlockContainer div.stButton > button:hover {{
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-color: #000000 !important;
    }}

    /* Fix tombol Browse Files */
    div[data-testid="stFileUploader"] button {{
        background-color: #FFFFFF !important;
        color: #1B1B1B !important;
        border: 1px solid #CCCCCC !important;
    }}
    div[data-testid="stFileUploader"] button:hover {{
        background-color: #ECECEC !important;
        color: #000000 !important;
    }}

    /* --- FIX TOMBOL DOWNLOAD HASIL BATCH --- */
    div.stDownloadButton > button {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 6px !important;
        border: 1px solid #1B1B1B !important;
        width: auto !important;
        transition: all 0.2s ease !important;
    }}

    div.stDownloadButton > button:hover {{
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-color: #000000 !important;
    }}
    </style>

    <div class="capsule-nav-container">
        <a href="/?mode=single" target="_self" class="capsule-tab-item {active_single}">Single Client Analysis</a>
        <a href="/?mode=batch" target="_self" class="capsule-tab-item {active_batch}">Batch Processing Pipeline</a>
    </div>
""")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MODE A: SINGLE CLIENT ANALYSIS
# ==========================================
if current_mode == "Single Client Analysis":
    
    # ──────────────────────────────────────────────────────────────
    # KOTAK INFO
    # ──────────────────────────────────────────────────────────────
    with st.expander("📖 PANDUAN PENGISIAN FORM (Klik untuk buka/tutup)", expanded=True):
        
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**👤 DATA DIRI**")
            st.markdown("""
            - **LIMIT_BAL** = Plafon kredit (NT$) - semakin tinggi semakin baik
            - **SEX** = 1 = Laki-laki, 2 = Perempuan
            - **EDUCATION** = 1 = S2/S3, 2 = S1, 3 = SMA, 4 = Lainnya
            - **MARRIAGE** = 1 = Menikah, 2 = Single, 3 = Lainnya
            - **AGE** = Usia nasabah (tahun)
            """)

            st.markdown("**📆 RIWAYAT PEMBAYARAN (PAY_0 - PAY_6)**")
            st.markdown("""
            - **PAY_0** = September (bulan terbaru)
            - **PAY_2** = Agustus
            - **PAY_3** = Juli
            - **PAY_4** = Juni
            - **PAY_5** = Mei
            - **PAY_6** = April
            """)
        
        with col_right:
            st.markdown("**🎯 Arti Nilai PAY:**")
            st.markdown("""
            - ✅ **-2** = Bayar lebih (sangat baik)
            - ✅ **-1** = Bayar tepat waktu (baik)
            - ⚠️ **0** = Telat 1 bulan (cukup)
            - ⚠️ **1** = Telat 2 bulan (buruk)
            - ❌ **2-8** = Telat 3-9 bulan (sangat buruk)
            """)

            st.markdown("**💰 TAGIHAN & PEMBAYARAN**")
            st.markdown("""
            - **BILL_AMT1-6** = Tagihan per bulan (NT$) - yang HARUS dibayar
            - **PAY_AMT1-6** = Pembayaran per bulan (NT$) - yang BENAR-BENAR dibayar
            """)

        
        st.info("💡 **Tips:** Bandingkan PAY_AMT dengan BILL_AMT. Semakin mendekati tagihan, semakin baik.")
        
        st.success("📌 **KESIMPULAN:** Semakin kecil nilai PAY (negatif) dan semakin besar pembayaran dibanding tagihan → semakin BAIK.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    with st.form(key="client_assessment_form", clear_on_submit=False):
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        # Kolom 1: Demographics
        with col1:
            st.markdown("<div class='label-matte-style'>Demographics</div>", unsafe_allow_html=True)
            limit_bal = st.number_input("Limit Balance (NT$)", min_value=0, value=50000, step=10000)
            sex       = st.selectbox("Sex", options=[1, 2], format_func=lambda x: "Male" if x==1 else "Female")
            education = st.selectbox("Education", options=[1, 2, 3, 4], format_func=lambda x: ["Graduate School", "University", "High School", "Other"][x-1])
            marriage  = st.selectbox("Marriage", options=[1, 2, 3], format_func=lambda x: ["Married", "Single", "Other"][x-1])
            age       = st.number_input("Age", min_value=18, max_value=100, value=34)

        # Kolom 2: Repayment Status
        with col2:
            st.markdown("<div class='label-matte-style'>Repayment Status</div>", unsafe_allow_html=True)
            pay_0 = st.slider("PAY_0 (Latest)", -2, 8, 0)
            pay_2 = st.slider("PAY_2", -2, 8, 0)
            pay_3 = st.slider("PAY_3", -2, 8, 1)
            pay_4 = st.slider("PAY_4", -2, 8, 0)
            pay_5 = st.slider("PAY_5", -2, 8, 0)
            pay_6 = st.slider("PAY_6", -2, 8, -1)

        # Kolom 3: Bill Amounts
        with col3:
            st.markdown("<div class='label-matte-style'>Bill Amounts</div>", unsafe_allow_html=True)
            bill_amt1 = st.number_input("BILL_AMT1", value=3913)
            bill_amt2 = st.number_input("BILL_AMT2", value=2682)
            bill_amt3 = st.number_input("BILL_AMT3", value=2355)
            bill_amt4 = st.number_input("BILL_AMT4", value=3572)
            bill_amt5 = st.number_input("BILL_AMT5", value=2000)
            bill_amt6 = st.number_input("BILL_AMT6", value=1850)

        # Kolom 4: Previous Payments
        with col4:
            st.markdown("<div class='label-matte-style'>Previous Payments</div>", unsafe_allow_html=True)
            pay_amt1 = st.number_input("PAY_AMT1", value=0)
            pay_amt2 = st.number_input("PAY_AMT2", value=689)
            pay_amt3 = st.number_input("PAY_AMT3", value=0)
            pay_amt4 = st.number_input("PAY_AMT4", value=0)
            pay_amt5 = st.number_input("PAY_AMT5", value=0)
            pay_amt6 = st.number_input("PAY_AMT6", value=678)

        # Baris tombol tengah
        st.markdown("<br>", unsafe_allow_html=True)
        _, btn_center, _ = st.columns([1.8, 1, 1.8])
        with btn_center:
            submit_clicked = st.form_submit_button(label="PREDIKSI")

    # --- MODEL PROCESSING & INTERACTIVE OUTPUT VIEW ---
    if submit_clicked:
        if model is None:
            st.error("Model engine is currently offline.")
        else:
            raw_input_dict = {
                'LIMIT_BAL': [limit_bal], 'SEX': [sex], 'EDUCATION': [education],
                'MARRIAGE': [marriage], 'AGE': [age],
                'PAY_0': [pay_0], 'PAY_2': [pay_2], 'PAY_3': [pay_3],
                'PAY_4': [pay_4], 'PAY_5': [pay_5], 'PAY_6': [pay_6],
                'BILL_AMT1': [bill_amt1], 'BILL_AMT2': [bill_amt2], 'BILL_AMT3': [bill_amt3],
                'BILL_AMT4': [bill_amt4], 'BILL_AMT5': [bill_amt5], 'BILL_AMT6': [bill_amt6],
                'PAY_AMT1': [pay_amt1], 'PAY_AMT2': [pay_amt2], 'PAY_AMT3': [pay_amt3],
                'PAY_AMT4': [pay_amt4], 'PAY_AMT5': [pay_amt5], 'PAY_AMT6': [pay_amt6]
            }
            df_input = pd.DataFrame(raw_input_dict)

            with st.spinner("Calculating metrics..."):
                # ── BLEND ENSEMBLE PREDICTION ──────────────────────────────
                blend_probs, xgb_probas, anomaly_scores, iso_norms, lof_norms = predict_blend_ensemble(df_input)

                prob_value    = float(blend_probs[0])
                xgb_proba     = float(xgb_probas[0])
                anomaly_score = float(anomaly_scores[0])

                # Debug print ke terminal (tidak tampil di UI)
                print(f"🔍 DEBUG - XGBoost proba    : {xgb_proba:.4f}")
                print(f"🔍 DEBUG - iso_norm         : {float(iso_norms[0]):.4f}")
                print(f"🔍 DEBUG - lof_norm         : {float(lof_norms[0]):.4f}")
                print(f"🔍 DEBUG - Anomaly score    : {anomaly_score:.4f}")
                print(f"🔍 DEBUG - Blend result     : {prob_value:.4f}")
                print(f"🔍 DEBUG - Threshold        : {THRESHOLD:.4f}")

                if prob_value < 0.25:
                    risk_grade  = "LOW RISK"
                    badge_color = "#22C55E"
                elif prob_value < THRESHOLD:
                    risk_grade  = "MEDIUM RISK"
                    badge_color = "#F97316"
                else:
                    risk_grade  = "HIGH RISK"
                    badge_color = "#BA1A1A"

            st.markdown("<br>", unsafe_allow_html=True)
            res_col1, res_col2, res_col3 = st.columns(3, gap="medium")

            decision = "REJECTED" if prob_value >= THRESHOLD else "APPROVED"

            with res_col1:
                st.markdown(f"""
                    <div class='result-card-premium'>
                        <span style='font-size:11px; font-weight:600; text-transform:uppercase; color:#5E5E5E;'>Analysis Verdict</span>
                        <div>
                            <h2 style='font-size: 28px; font-weight: 700; color: #1B1B1B; margin: 0;'>{decision}</h2>
                            <p style='font-size: 12px; color: #5E5E5E; margin-top: 4px;'>The client exhibits {"sustainable" if decision == "APPROVED" else "critical"} behavior metrics.</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with res_col2:
                st.markdown(f"""
                    <div class='result-card-premium'>
                        <span style='font-size:11px; font-weight:600; text-transform:uppercase; color:#5E5E5E;'>Internal Risk Grade</span>
                        <div>
                            <div style='display: flex; align-items: center; gap: 8px;'>
                                <div style='width: 10px; height: 10px; border-radius: 9999px; background-color: {badge_color};'></div>
                                <h2 style='font-size: 28px; font-weight: 700; color: #1B1B1B; margin: 0;'>{risk_grade}</h2>
                            </div>
                            <p style='font-size: 12px; color: #5E5E5E; margin-top: 4px;'>Exposure index: {prob_value:.2f} / 1.00</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with res_col3:
                st.markdown(f"""
<div class='result-card-premium' style='padding-bottom: 24px;'>
<span style='font-size:11px; font-weight:600; text-transform:uppercase; color:#5E5E5E;'>Default Probability</span>
<div style='display: flex; justify-content: space-between; align-items: baseline; margin-top:4px; margin-bottom: 12px;'>
<h2 style='font-size: 28px; font-weight: 700; color: #1B1B1B; margin: 0;'>{prob_value*100:.1f}%</h2>
<span style='font-size: 11px; color: #777777;'>Threshold: {THRESHOLD*100:.0f}%</span>
</div>
<div style='background-color: #EAEAEA; border-radius: 9999px; width: 100%; height: 8px; overflow: hidden;'>
<div style='background-color: #3271D6; width: {min(prob_value*100, 100)}%; height: 100%; border-radius: 9999px;'></div>
</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# MODE B: BATCH PROCESSING PIPELINE
# ==========================================
else:
    st.markdown("<div style='background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px; padding: 2.5rem;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:14px; font-weight:600; color:#1B1B1B; margin-bottom:6px;'>Asynchronous Batch Upload</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px; color:#5E5E5E; margin-bottom:20px;'>Upload file CSV masal untuk memproses evaluasi portofolio kelayakan kredit nasabah sekaligus.</p>", unsafe_allow_html=True)

    csv_file = st.file_uploader("Upload CSV File", type=["csv"], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if csv_file is not None:
        df_batch_raw = pd.read_csv(csv_file)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:11px; font-weight:700; color:#1B1B1B; text-transform:uppercase; margin-bottom:8px;'>Raw Portfolio Preview</div>", unsafe_allow_html=True)
        st.dataframe(df_batch_raw.head(5), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        run_batch = st.button("PROSES SEMUA")

        if run_batch:
            if model is None:
                st.error("Pipeline model artifacts are not loaded correctly.")
            else:
                with st.spinner("Processing continuous data matrices via Blend Ensemble..."):
                    time.sleep(0.5)

                    # ── BLEND ENSEMBLE BATCH ─────────────────────────────────
                    batch_probs, xgb_probs, anomaly_scores, iso_norms, lof_norms = predict_blend_ensemble(df_batch_raw)

                    # Normalisasi anomaly untuk batch: tetap pakai training min/max (sudah di handle di predict_blend_ensemble)
                    # Untuk batch, override: pakai batch-level normalisasi agar distribusi lebih stabil
                    # (sesuai notebook yang pakai batch-level normalisasi untuk test set)
                    iso_raw_batch = -(iso_forest.score_samples(scaler.transform(run_feature_engineering_pipeline(df_batch_raw))))
                    lof_raw_batch = -(lof.score_samples(pca.transform(scaler.transform(run_feature_engineering_pipeline(df_batch_raw)))))

                    # Normalisasi batch pakai training min/max (konsisten dengan single)
                    iso_norm_batch = np.clip((iso_raw_batch - ISO_MIN) / (ISO_MAX - ISO_MIN + 1e-9), 0, 5)
                    lof_norm_batch = np.clip((lof_raw_batch - LOF_MIN) / (LOF_MAX - LOF_MIN + 1e-9), 0, 5)

                    anomaly_scores_batch = 0.05 * iso_norm_batch + 0.95 * lof_norm_batch
                    batch_probs_final    = ALPHA * anomaly_scores_batch + BETA * xgb_probs

                    df_batch_raw['Default_Probability'] = batch_probs_final
                    df_batch_raw['Decision']  = np.where(batch_probs_final >= THRESHOLD, "REJECTED", "APPROVED")
                    df_batch_raw['Risk_Level'] = np.where(
                        batch_probs_final < 0.25, "Low",
                        np.where(batch_probs_final < THRESHOLD, "Medium", "High")
                    )

                    st.markdown("<br><hr><br>", unsafe_allow_html=True)
                    m_col1, m_col2, m_col3 = st.columns(3)

                    total_records  = len(df_batch_raw)
                    total_rejected = len(df_batch_raw[df_batch_raw['Decision'] == 'REJECTED'])
                    total_approved = total_records - total_rejected

                    with m_col1:
                        st.metric("Total Evaluated Records",  f"{total_records} Users")
                    with m_col2:
                        st.metric("Total Approved Portfolio", f"{total_approved} Users")
                    with m_col3:
                        st.metric("Total Rejected Portfolio", f"{total_rejected} Users")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<div style='font-size:11px; font-weight:700; color:#1B1B1B; text-transform:uppercase; margin-bottom:8px;'>Pipeline Output Analytics View</div>", unsafe_allow_html=True)

                    display_cols = ['LIMIT_BAL', 'AGE', 'Default_Probability', 'Decision', 'Risk_Level']
                    avail_cols   = [c for c in display_cols if c in df_batch_raw.columns]
                    st.dataframe(df_batch_raw[avail_cols].head(50), use_container_width=True)

                    final_csv_bytes = df_batch_raw.to_csv(index=False).encode('utf-8')
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.download_button(
                        label="Download Hasil Sebagai CSV",
                        data=final_csv_bytes,
                        file_name="risk_assessment_batch_results.csv",
                        mime="text/csv"
                    )

# ==========================================
# 5. PREMIUM FINTECH FOOTER SECTION
# ==========================================
st.markdown("<br><br><br><hr><br>", unsafe_allow_html=True)
f_left, f_right = st.columns([1, 1])
with f_left:
    st.markdown("<div style='font-size: 11px; font-weight: 700; letter-spacing: 0.1em; color: #1B1B1B;'>RISK ANALYTICS</div>", unsafe_allow_html=True)
with f_right:
    st.markdown("<div style='font-size: 11px; text-align: right; color: #5E5E5E;'>Powered by Blend Ensemble (XGBoost + IF + PCA-LOF). Optimized Threshold 0.57</div>", unsafe_allow_html=True)
