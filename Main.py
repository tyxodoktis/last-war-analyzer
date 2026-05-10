import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re
import gc # Garbage Collector για να μην κρασάρει
import time

st.set_page_config(page_title="Last War Multi-Analyzer", layout="wide")
st.title("🛡️ Last War Alliance Intelligence (100 Members Support)")

@st.cache_resource
def load_model():
    return easyocr.Reader(['en'], gpu=False)

reader = load_model()

# Η ΡΥΘΜΙΣΗ ΓΙΑ ΠΟΛΛΕΣ ΦΩΤΟ ΕΙΝΑΙ ΕΔΩ (accept_multiple_files=True)
uploaded_files = st.file_uploader("Επίλεξε όλα τα screenshots (13+)", 
                                  type=['png', 'jpg', 'jpeg'], 
                                  accept_multiple_files=True)

if uploaded_files:
    st.info(f"✅ Φορτώθηκαν {len(uploaded_files)} αρχεία.")
    
    if st.button('Έναρξη Ανάλυσης'):
        final_data = []
        seen_players = set()
        
        # Δείκτες Προόδου
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Ενημέρωση μπάρας προόδου
            percent = (i + 1) / len(uploaded_files)
            progress_bar.progress(percent)
            status_text.markdown(f"**Επεξεργασία:** {i+1} / {len(uploaded_files)} | `{uploaded_file.name}`")
            
            try:
                img = Image.open(uploaded_file)
                img_array = np.array(img)
                results = reader.readtext(img_array)
                
                temp_name = None
                temp_r_level = "R?"
                
                for (bbox, text, prob) in results:
                    txt = text.strip()
                    
                    # Ανίχνευση R1-R5
                    r_match = re.search(r'R[1-5]', txt.upper())
                    if r_match:
                        temp_r_level = r_match.group()
                    
                    # Ανίχνευση Power
                    num_only = re.sub(r'[^0-9]', '', txt)
                    if num_only.isdigit() and int(num_only) > 100000:
                        p_val = int(num_only)
                        if temp_name and temp_name not in seen_players:
                            final_data.append({
                                "Player": temp_name,
                                "Rank": temp_r_level,
                                "Power": p_val
                            })
                            seen_players.add(temp_name)
                            temp_name = None
                            temp_r_level = "R?"
                    else:
                        # Φιλτράρισμα ονόματος
                        ignore = ['power', 'kills', 'donation', 'ranking', 'commander', 'back', 'total', 'alliance']
                        if len(txt) > 2 and txt.lower() not in ignore and not r_match:
                            temp_name = txt

                # ΚΑΘΑΡΙΣΜΟΣ ΜΝΗΜΗΣ ΜΕΤΑ ΑΠΟ ΚΑΘΕ ΦΩΤΟΓΡΑΦΙΑ
                del img
                del img_array
                gc.collect()

            except Exception as e:
                st.error(f"Σφάλμα στο αρχείο {uploaded_file.name}: {e}")

        status_text.empty()

        if final_data:
            df = pd.DataFrame(final_data)
            df = df.sort_values(by="Power", ascending=False).reset_index(drop=True)
            df.index += 1
            
            st.success(f"✅ Η ανάλυση ολοκληρώθηκε! Βρέθηκαν {len(df)} παίκτες.")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=True).encode('utf-8')
            st.download_button("📥 Κατέβασμα Αρχείου Excel", data=csv, file_name="alliance_report.csv")
        else:
            st.warning("Δεν βρέθηκαν δεδομένα.")

st.divider()
st.caption("v2.4 | Multi-Image Stability Enabled")
