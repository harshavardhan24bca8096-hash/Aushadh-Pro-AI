import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import uuid

# --- 1. CONFIG ---
# Replace with your actual Gemini 3 key
genai.configure(api_key="AIzaSyCFHgZcLbhjcfMuIHYWTBc3Sje-xhWDbWc")
model = genai.GenerativeModel('gemini-3-flash-preview')

st.set_page_config(page_title="Aushadh Pro AI", layout="wide", page_icon="💊")

# --- 2. PROFESSIONAL UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Report Cards - High Contrast for Readability */
    .report-box { 
        background: #ffffff !important; 
        color: #1a1c24 !important; 
        padding: 25px; 
        border-radius: 12px; 
        border-top: 6px solid #007bff;
        min-height: 480px;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .report-box h1, .report-box h2, .report-box h3 { color: #007bff !important; }
    
    /* Action Button Styling */
    div.stButton > button:first-child {
        background-color: #007bff;
        color: white;
        font-size: 18px;
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Aushadh Pro")
    st.info("Medical Safety Verification Agent")
    st.markdown("---")
    st.write("**Features:**")
    st.write("✅ Prescription Decoding")
    st.write("✅ Tablet Strip Analysis")
    st.write("✅ Multi-Language Audio")
    st.write("✅ Visual Cross-Match")
    st.markdown("---")
    st.caption("Solution Challenge 2026")

# --- 4. INPUT SECTION ---
st.title("💊 Aushadh Pro: Smart Medical Agent")
col_in1, col_in2 = st.columns(2)

with col_in1:
    st.subheader("📝 Upload Files")
    input_file = st.file_uploader("Drop Prescription or Strip Image/PDF", type=['png', 'jpg', 'jpeg', 'pdf'])

with col_in2:
    st.subheader("📷 Live Scan")
    cam_file = st.camera_input("Scan your medicine")

active_file = input_file if input_file else cam_file

# --- 5. EXECUTION & LOGIC ---
if active_file:
    if st.button("🚀 ANALYZE & VERIFY"):
        img = Image.open(active_file)
        
        with st.spinner("🤖 Agent is reasoning over documents..."):
            # Prompt for Dual Content Analysis
            main_prompt = """
            Analyze this image. If it's a prescription, extract medicine names and usage. 
            If it's a strip, check expiry and purpose. 
            Return the response in this EXACT format:
            [ENGLISH_REPORT]
            (Analysis in English)
            
            [HINDI_REPORT]
            (Analysis in simple Hindi)
            """
            
            response_text = model.generate_content([main_prompt, img]).text
            
            # Extract medicine names for specific Google Search
            search_prompt = "Based on this image, list only the names of the medicines found, separated by commas. If none found, say 'General Medicine'."
            med_names = model.generate_content([search_prompt, img]).text.strip()
            
            # Split reports for UI
            try:
                eng_report = response_text.split("[HINDI_REPORT]")[0].replace("[ENGLISH_REPORT]", "").strip()
                hin_report = response_text.split("[HINDI_REPORT]")[1].strip()
            except:
                eng_report = response_text
                hin_report = "हिंदी अनुवाद उपलब्ध नहीं है।"

            # --- DISPLAY SIDE-BY-SIDE REPORTS ---
            col_text1, col_text2 = st.columns(2)
            run_id = str(uuid.uuid4())[:8]

            with col_text1:
                st.subheader("🇬🇧 English Analysis")
                st.markdown(f'<div class="report-box">{eng_report}</div>', unsafe_allow_html=True)
                
                # English Audio Logic
                e_path = f"en_{run_id}.mp3"
                tts_e = gTTS(text=eng_report.replace('*',''), lang='en')
                tts_e.save(e_path)
                with open(e_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

            with col_text2:
                st.subheader("🇮🇳 Hindi Analysis (हिंदी)")
                st.markdown(f'<div class="report-box">{hin_report}</div>', unsafe_allow_html=True)
                
                # Hindi Audio Logic
                h_path = f"hi_{run_id}.mp3"
                tts_h = gTTS(text=hin_report.replace('*',''), lang='hi')
                tts_h.save(h_path)
                with open(h_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

            # --- VISUAL VERIFICATION SECTION ---
            st.markdown("---")
            st.subheader("🖼️ Visual Verification Hub")
            col_v1, col_v2 = st.columns(2)
            
            with col_v1:
                st.write("**Your Scanned Input:**")
                st.image(img, use_container_width=True)
            
            with col_v2:
                st.write("**AI-Targeted Reference:**")
                st.info(f"Detected Medicines: **{med_names}**")
                
                # Generate clean Google Image search for the specific TABLETS
                search_query = f"{med_names} tablet strip appearance".replace(" ", "+")
                search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
                
                st.write("Click below to verify if your tablets look like the official versions:")
                st.link_button(f"👁️ View {med_names} Tablet Images", search_url)
                
                st.markdown("""
                **Safety Checklist:**
                * Match the Color and Shape.
                * Check for the manufacturer's logo.
                * Ensure the 'Red Line' is present if it's a Schedule H drug.
                """)
else:
    st.warning("Awaiting medical document or medicine scan...")