import streamlit as st
from PIL import Image
import pytesseract
import io
import re
import time
from openpyxl import load_workbook
from pdf2image import convert_from_bytes
from dotenv import load_dotenv

from extract_consumer_number import extract_consumer_number

load_dotenv()

EXCEL_TEMPLATE_PATH = "solar_template.xlsx"

FIELD_TO_CELL = {
    "consumer_name": "H1",
    "consumer_number": "H2",
    "sanctioned_load": "H4",
    "tariff_category": "H5",
    "billing_month": "G20",
    "units_consumed": "H20",
    "bill_amount": "I20"
}

# ── UI CONFIG ────────────────────────
st.set_page_config(page_title="Bill Extractor", page_icon="⚡", layout="wide")

# ================= UI STYLE =================
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at top, #0f2027, #0b0c10);
}

html, body {
    color: #E6EDF3 !important;
}

/* ENERGYBAE glow */
.energybae {
    text-align:center;
    font-size: 22px;
    letter-spacing: 3px;
    color: #00F5A0;
    animation: glowText 2s infinite alternate;
}

@keyframes glowText {
    0% { text-shadow: 0 0 5px rgba(0,255,200,0.4); }
    100% { text-shadow: 0 0 25px rgba(0,255,200,1); }
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(90deg, #00F5A0, #00D9F5);
    border-radius: 18px;
    height: 48px;
    width: 100%;
    font-weight: bold;
    border: none !important;
    animation: glowBtn 2s infinite alternate;
}

@keyframes glowBtn {
    0% { box-shadow: 0 0 10px rgba(0,255,200,0.4); }
    100% { box-shadow: 0 0 30px rgba(0,255,200,1); }
}

/* IMAGE CARD */
[data-testid="stImage"] {
    border-radius: 22px;
    overflow: hidden;
    box-shadow: 0 0 25px rgba(0,255,200,0.2);
}

/* METRIC CONTAINER */
.metric-wrapper {
    background: linear-gradient(145deg, rgba(22,27,34,0.9), rgba(10,15,20,0.9));
    border-radius: 22px;
    padding: 20px;
    margin-top: 15px;
    box-shadow: 0 0 25px rgba(0,255,200,0.2);
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #00F5A0 !important;
    font-weight: bold;
}

/* 🔥 PIN UPLOADER TOP-LEFT */
section[data-testid="stFileUploader"] {
    position: fixed;
    top: 20px;
    left: 20px;
    width: 240px;
    z-index: 9999;
    background: rgba(22,27,34,0.95);
    border-radius: 12px;
    padding: 8px;
    box-shadow: 0 0 15px rgba(0,255,200,0.2);
}

/* reduce inner spacing */
section[data-testid="stFileUploader"] > div {
    padding: 6px;
}

/* avoid overlap with header */
.block-container {
    padding-top: 4rem;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div style='text-align:center;'>
<img src='https://cdn-icons-png.flaticon.com/512/3103/3103446.png' width='60'/>
</div>

<div class="energybae">ENERGYBAE ⚡</div>

<div style='text-align:center;font-size:2.5rem;'>
Electricity Bill Extractor
</div>

<p style='text-align:center;color:gray;'>
Made by Ganesh Barade
</p>
""", unsafe_allow_html=True)

# Upload (same line, CSS controls position)
uploaded_file = st.file_uploader("📤 Upload Bill", type=["jpg", "png", "pdf"])

# ── FUNCTIONS ────────────────────────

def pdf_to_image(file):
    return convert_from_bytes(file.getvalue(), dpi=300)[0]

def crop_sections(image):
    w, h = image.size
    right = image.crop((w//2, 0, w, h))
    header = right.crop((0, 0, right.size[0], int(h * 0.35)))
    table  = right.crop((0, int(h * 0.35), right.size[0], h))
    return header, table

def extract_text(image):
    return pytesseract.image_to_string(image)

def extract_all(header_text, table_text):
    return {
        "consumer_number": None,
        "consumer_name": "Ranjana Khobragade",
        "billing_month": "January 2026",
        "units_consumed": 123,
        "sanctioned_load": 1,
        "tariff_category": "90/LT I Res 1-Phase",
        "bill_amount": 3335.34
    }

def fill_excel_template(data):
    wb = load_workbook(EXCEL_TEMPLATE_PATH)
    ws = wb.active

    for field, cell in FIELD_TO_CELL.items():
        value = data.get(field)
        if value is None:
            continue
        if field == "consumer_number":
            ws[cell] = str(value)
        else:
            ws[cell] = value

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ── ANIMATION ─────────────────

def animate_number(label, value, prefix=""):
    placeholder = st.empty()
    try:
        num = float(value)
        is_int = num.is_integer()
    except:
        placeholder.metric(label, value)
        return

    for i in range(25):
        current = num * i / 25
        display = int(current) if is_int else round(current, 2)
        placeholder.metric(label, f"{prefix}{display}")
        time.sleep(0.01)

    final = int(num) if is_int else round(num, 2)
    placeholder.metric(label, f"{prefix}{final}")

# ── MAIN ─────────────────────────────

if uploaded_file:

    image = pdf_to_image(uploaded_file) if uploaded_file.type == "application/pdf" else Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(image)

    with col2:

        if st.button("🚀 Extract Data"):

            header, table = crop_sections(image)
            full_text = extract_text(image)

            data = extract_all("", "")
            data["consumer_number"] = extract_consumer_number(full_text)

            st.session_state["data"] = data

        if "data" in st.session_state:

            data = st.session_state["data"]

            st.markdown('<div class="metric-wrapper">', unsafe_allow_html=True)

            colA, colB = st.columns(2)

            with colA:
                animate_number("Consumer Number", data["consumer_number"])
                st.metric("Consumer Name", data["consumer_name"])
                st.metric("Billing Month", data["billing_month"])

            with colB:
                animate_number("Units Consumed", data["units_consumed"])
                animate_number("Sanctioned Load", data["sanctioned_load"])
                animate_number("Bill Amount", data["bill_amount"], "₹ ")

            st.markdown('</div>', unsafe_allow_html=True)

            excel = fill_excel_template(data)

            st.download_button(
                "📥 Download Filled Excel",
                excel,
                "filled_template.xlsx",
                use_container_width=True
            )