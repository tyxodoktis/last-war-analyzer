import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re
import time

st.set_page_config(page_title="Last War Alliance Analyzer Pro", layout="wide")
st.title("🛡️ Last War Alliance Intelligence Unit")

@st.cache_resource
def load_model():
    # Φόρτωση του μοντέλου AI (English)
    return easyocr.Reader(['en'], gpu=False)

reader = load_model()

# Επιλογή πολλαπλών αρχείων
uploaded_files = st.file_uploader("Ανέβασε τα screenshots (υποστηρίζει 13+ αρχεία)", 
                                  type=['png', 'jpg', 'jpeg'], 
                                  accept_multiple_files=True)

if uploaded_files:
    st.write(f"📊 Έχουν ανέβει **{len(uploaded_files)}** εικόνες.")
    
    if st.button('Έναρξη Μαζικής Ανάλυσης'):
        final_data = []
        seen_players = set()
        
        # Μπάρα προόδου
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Λίστα για να βλέπουμε ποια φωτό διαβάζει
        log_container = st.expander("📝 Logs Ανάλυσης (Δες ποια φωτό διαβάζεται)", expanded=True)

        for i, uploaded_file in enumerate(uploaded_files):
            # Ενημέρωση UI
            current_progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(current_progress)
            status_text.text(f"Επεξεργασία {i+1} από {len(uploaded_files)}: {uploaded_file.name}")
            log_container.write(f"✔️ Διαβάζω την εικόνα: **{uploaded_file.name}**")

            # Ανάλυση Εικόνας
            try:
                img = Image.open(uploaded_file)
                img_array = np.array(img)
                results = reader.readtext(img_array)
                
                ignore_list = ['power', 'kills', 'donation', 'ranking', 'commander', 'strength', 'back', 'alliance', 'merit', 'total']
                
                temp_name = None
                temp_r_level = "R?"
                
                for (bbox, text, prob) in results:
                    txt = text.strip()
                    low_txt = txt.lower()
                    
                    # Ανίχνευση R-Level (R1-R5)
                    r_match = re.search(r'R[1-5]', txt.upper())
                    if r_match:
                        temp_r_level = r_match.group()
                        continue

                    if any(word in low_txt for word in ignore_list) or len(txt) < 2:
                        continue
                    
                    # Ανίχνευση Power (Αριθμοί > 100.000)
                    num_only = re.sub(r'[^0-9]', '', txt)
                    if num_only.isdigit() and int(num_only) > 100000:
                        if temp_name and temp_name not in seen_players:
                            final_data.append({
                                "Position": len(final_data) + 1,
                                "Player": temp_name,
                                "Rank": temp_r_level,
                                "Power": f"{int(num_only):,}"
                            })
                            seen_players.add(temp_name)
                            temp_name = None
                            temp_r_level = "R?"
                    else:
                        if not txt.isdigit():
                            temp_name = txt
                
                # Μικρή παύση για να μην "μπουκώνει" ο browser
                time.sleep(0.1)

            except Exception as e:
                log_container.error(f"❌ Σφάλμα στην εικόνα {uploaded_file.name}: {e}")

        # Τελικά Αποτελέσματα
        if final_data:
            st.success(f"✅ Η ανάλυση ολοκληρώθηκε! Βρέθηκαν {len(final_data)} μοναδικοί παίκτες.")
            df = pd.DataFrame(final_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Κατέβασμα Excel (CSV)", data=csv, file_name="alliance_full_report.csv")
        else:
            st.warning("⚠️ Δεν βρέθηκαν δεδομένα. Βεβαιώσου ότι οι εικόνες είναι καθαρές.")

st.divider()
st.caption("Last War Intelligence Tool v2.0 | Multi-upload & Deduplication enabled")
