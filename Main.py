import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re

st.set_page_config(page_title="Last War 100-Member Analyzer", layout="wide")
st.title("🛡️ Last War Alliance Intelligence (Full 100 Support)")

@st.cache_resource
def load_model():
    return easyocr.Reader(['en'], gpu=False)

reader = load_model()

uploaded_files = st.file_uploader("Ανέβασε τα screenshots (κατά προτίμηση με τη σειρά)", 
                                  type=['png', 'jpg', 'jpeg'], 
                                  accept_multiple_files=True)

if uploaded_files:
    if st.button('Έναρξη Πλήρους Ανάλυσης'):
        final_data = []
        seen_players = set()
        
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            img = Image.open(uploaded_file)
            img_array = np.array(img)
            # Αυξάνουμε το contrast εσωτερικά για να διαβάζει καλύτερα τα R
            results = reader.readtext(img_array, paragraph=False)
            
            temp_name = None
            temp_r_level = "R?"
            
            for (bbox, text, prob) in results:
                txt = text.strip()
                
                # 1. Βελτιωμένο R-Detection (πιάνει R1, R2, R3, R4, R5 ακόμα και μέσα σε λέξεις)
                r_match = re.search(r'R[1-5]', txt.upper())
                if r_match:
                    temp_r_level = r_match.group()
                
                # 2. Καθαρισμός ονόματος (αφαιρούμε σύμβολα που μπερδεύουν το AI)
                clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', txt)
                
                # 3. Ανίχνευση Power (οποιοσδήποτε αριθμός > 100.000)
                num_only = re.sub(r'[^0-9]', '', txt)
                
                if num_only.isdigit() and int(num_only) > 100000:
                    power_val = int(num_only)
                    # Αν έχουμε όνομα, το "παντρεύουμε" με το Power
                    if temp_name and temp_name not in seen_players:
                        final_data.append({
                            "Player": temp_name,
                            "Rank": temp_r_level,
                            "Power": power_val
                        })
                        seen_players.add(temp_name)
                        temp_name = None
                        temp_r_level = "R?"
                else:
                    # Αν δεν είναι αριθμός, Power ή λέξη-μενού, είναι όνομα
                    ignore = ['power', 'kills', 'donation', 'ranking', 'commander', 'back', 'total']
                    if len(clean_name) > 2 and clean_name.lower() not in ignore and not r_match:
                        temp_name = clean_name

            progress_bar.progress((i + 1) / len(uploaded_files))

        if final_data:
            df = pd.DataFrame(final_data)
            # Ταξινόμηση αυτόματη από το μεγαλύτερο Power στο μικρότερο
            df = df.sort_values(by="Power", ascending=False).reset_index(drop=True)
            df.index += 1 # Position 1, 2, 3...
            
            st.success(f"✅ Βρέθηκαν {len(df)} παίκτες!")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=True).encode('utf-8')
            st.download_button("📥 Download Excel File", data=csv, file_name="alliance_full_100.csv")
        else:
            st.error("Δεν βρέθηκαν παίκτες. Δοκίμασε πιο καθαρά screenshots.")

st.divider()
st.info("💡 **Για να πιάσεις και τους 100:**\n1. Βγάζε screenshots που να αλληλοκαλύπτονται λίγο (να φαίνεται ο τελευταίος παίκτης της προηγούμενης φωτό).\n2. Μην κουνάς την οθόνη την ώρα που βγάζεις screenshot.")
