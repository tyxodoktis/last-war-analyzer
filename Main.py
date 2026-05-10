import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np

st.set_page_config(page_title="Last War Smart Analyzer", layout="wide")
st.title("🛡️ Last War Alliance Intelligence")

@st.cache_resource
def load_model():
    return easyocr.Reader(['en'], gpu=False)

reader = load_model()

uploaded_files = st.file_uploader("Ανέβασε screenshots", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button('Επεξεργασία & Ταξινόμηση'):
        final_list = []
        
        for uploaded_file in uploaded_files:
            img = Image.open(uploaded_file)
            img_array = np.array(img)
            results = reader.readtext(img_array)
            
            # Φιλτράρουμε τα "άχρηστα" (Power, Kills, Ranking κλπ)
            garbage_words = ['power', 'kills', 'donation', 'ranking', 'commander', 'strength', 'back']
            
            current_player = None
            
            for (bbox, text, prob) in results:
                txt = text.strip()
                low_txt = txt.lower()
                
                # Αγνοούμε τις λέξεις-μενού
                if any(word in low_txt for word in garbage_words) or len(txt) < 2:
                    continue
                
                # Αν είναι καθαρός αριθμός (πάνω από 1 εκατομμύριο), είναι το Power
                if txt.isdigit() and int(txt) > 100000:
                    if current_player:
                        final_list.append({"Player": current_player, "Stats": txt})
                        current_player = None
                else:
                    # Αν δεν είναι αριθμός, λογικά είναι όνομα
                    current_player = txt

        if final_list:
            df = pd.DataFrame(final_list)
            st.success("Βρέθηκαν οι παρακάτω παίκτες!")
            st.table(df) # Εμφάνιση καθαρού πίνακα
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Excel Ready File", data=csv, file_name="alliance_eval.csv")
        else:
            st.warning("Δεν μπορέσαμε να ταιριάξουμε ονόματα με νούμερα. Δοκίμασε πιο καθαρά screenshots.")

st.divider()
st.info("💡 **Πώς να βοηθήσεις το AI:** Προσπάθησε στα screenshots να μην φαίνονται τα κουμπιά του κινητού ή το chat, γιατί μπερδεύουν την ανάγνωση.")
