import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re

st.set_page_config(page_title="Last War Alliance Intelligence", layout="wide")
st.title("🛡️ Last War Alliance Analyzer Pro")

@st.cache_resource
def load_model():
    return easyocr.Reader(['en'], gpu=False)

reader = load_model()

uploaded_files = st.file_uploader("Ανέβασε screenshots", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button('Ανάλυση & Κατάταξη'):
        final_data = []
        seen_players = set() 
        
        for uploaded_file in uploaded_files:
            img = Image.open(uploaded_file)
            img_array = np.array(img)
            results = reader.readtext(img_array)
            
            # Λέξεις που θέλουμε να αγνοήσουμε
            ignore_list = ['power', 'kills', 'donation', 'ranking', 'commander', 'strength', 'back', 'alliance', 'merit']
            
            temp_name = None
            temp_r_level = "R?" 
            
            for (bbox, text, prob) in results:
                txt = text.strip()
                # Καθαρισμός κειμένου από περίεργα σύμβολα
                txt_clean = re.sub(r'[^a-zA-Z0-9]', '', txt)
                low_txt = txt.lower()
                
                # 1. Ανίχνευση R-Level (Πλέον και R5!)
                # Ψάχνουμε για R1, R2, R3, R4, R5
                r_match = re.search(r'R[1-5]', txt.upper())
                if r_match:
                    temp_r_level = r_match.group()
                    continue

                # 2. Αγνοούμε άχρηστες λέξεις
                if any(word in low_txt for word in ignore_list) or len(txt) < 2:
                    continue
                
                # 3. Αν είναι αριθμός πάνω από 100k, είναι Power
                # Χρησιμοποιούμε regex για να βρούμε αριθμούς ακόμα κι αν έχουν τελεία ή κόμμα (π.χ. 31.874.618)
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
                    # Αν είναι κείμενο και δεν είναι στην ignore list, είναι όνομα
                    if not txt.isdigit():
                        temp_name = txt

        if final_data:
            df = pd.DataFrame(final_data)
            st.success(f"Η ανάλυση ολοκληρώθηκε! Βρέθηκαν {len(df)} μοναδικοί παίκτες.")
            
            # Εμφάνιση του πίνακα
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Κατέβασμα Λίστας (Excel)", data=csv, file_name="alliance_report.csv")
        else:
            st.warning("Δεν βρέθηκαν επαρκή στοιχεία. Δοκίμασε screenshots με καλύτερη εστίαση στα ονόματα.")

st.divider()
st.info("💡 **R5 Update:** Ο κώδικας πλέον αναγνωρίζει και τον Leader (R5). Αν κάποιος παίκτης εμφανίζεται ως R?, σημαίνει ότι το AI δεν διάβασε καθαρά το γράμμα R δίπλα στο όνομά του.")
