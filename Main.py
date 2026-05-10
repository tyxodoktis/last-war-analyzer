import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re
import gc

st.set_page_config(page_title="Last War Intelligence", layout="wide")
st.title("🛡️ Last War Alliance Analyzer")

# Φόρτωση μοντέλου με βελτιστοποίηση μνήμης
@st.cache_resource
def load_model():
    return easyocr.Reader(['en'], gpu=False, model_storage_directory='.')

reader = load_model()

# Πολλαπλά αρχεία
uploaded_files = st.file_uploader("Ανέβασε όλα τα screenshots (13+)", 
                                  type=['png', 'jpg', 'jpeg'], 
                                  accept_multiple_files=True)

if uploaded_files:
    st.info(f"📊 Έτοιμος για ανάλυση {len(uploaded_files)} εικόνων.")
    
    if st.button('Έναρξη Σταθερής Ανάλυσης'):
        final_data = []
        seen_players = set()
        
        # UI Προόδου
        progress_bar = st.progress(0)
        status_txt = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Ενημέρωση προόδου
            current_pct = (i + 1) / len(uploaded_files)
            progress_bar.progress(current_pct)
            status_txt.markdown(f"**Επεξεργασία:** `{uploaded_file.name}` ({i+1}/{len(uploaded_files)})")
            
            try:
                # Άνοιγμα και σμίκρυνση εικόνας για εξοικονόμηση RAM
                img = Image.open(uploaded_file).convert('L') # Μετατροπή σε ασπρόμαυρο για ταχύτητα
                img.thumbnail((1000, 1000)) # Σμίκρυνση αν είναι τεράστια
                img_array = np.array(img)
                
                results = reader.readtext(img_array)
                
                temp_name = None
                temp_r_level = "R?"
                
                for (bbox, text, prob) in results:
                    txt = text.strip()
                    
                    # 1. R1-R5
                    r_match = re.search(r'R[1-5]', txt.upper())
                    if r_match:
                        temp_r_level = r_match.group()
                        continue
                    
                    # 2. Power
                    num_only = re.sub(r'[^0-9]', '', txt)
                    if num_only.isdigit() and int(num_only) > 100000:
                        if temp_name and temp_name not in seen_players:
                            final_data.append({
                                "Player": temp_name,
                                "Rank": temp_r_level,
                                "Power": int(num_only)
                            })
                            seen_players.add(temp_name)
                            temp_name = None
                            temp_r_level = "R?"
                    else:
                        ignore = ['power', 'kills', 'donation', 'ranking', 'commander', 'back', 'total', 'alliance']
                        if len(txt) > 2 and txt.lower() not in ignore:
                            temp_name = txt

                # Καθαρισμός μνήμης αμέσως
                del img
                del img_array
                gc.collect()

            except Exception as e:
                st.warning(f"Παράλειψη αρχείου {uploaded_file.name} λόγω σφάλματος.")

        status_txt.empty()

        if final_data:
            df = pd.DataFrame(final_data)
            df = df.sort_values(by="Power", ascending=False).reset_index(drop=True)
            df.index += 1
            st.success(f"✅ Ολοκληρώθηκε! Βρέθηκαν {len(df)} παίκτες.")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=True).encode('utf-8')
            st.download_button("📥 Λήψη Excel", data=csv, file_name="alliance_stats.csv")

st.divider()
st.caption("Stable v2.5 | Optimized for Fair-Use Limits")
