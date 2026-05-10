import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re

st.set_page_config(page_title="Last War Pro Analyzer", layout="wide")
st.title("🛡️ Last War Alliance Intelligence Unit")

@st.cache_resource
def load_model():
    return easyocr.Reader(['en'], gpu=False)

reader = load_model()

uploaded_files = st.file_uploader("Ανέβασε τα screenshots της συμμαχίας", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    all_extracted_data = []
    
    if st.button('Έναρξη Ανάλυσης όλων των εικόνων'):
        for uploaded_file in uploaded_files:
            with st.status(f"Ανάλυση εικόνας: {uploaded_file.name}...", expanded=False):
                img = Image.open(uploaded_file)
                img_array = np.array(img)
                results = reader.readtext(img_array)
                
                for (bbox, text, prob) in results:
                    # Φιλτράρισμα: Κράτα μόνο ονόματα και νούμερα Power
                    # Ψάχνουμε για κείμενο που έχει πάνω από 3 χαρακτήρες 
                    # ή νούμερα που μοιάζουν με Power (π.χ. 15.5M)
                    clean_text = text.strip()
                    if len(clean_text) > 2:
                        all_extracted_data.append({
                            "Αρχείο": uploaded_file.name,
                            "Δεδομένο": clean_text,
                            "Πιθανότητα": f"{round(prob*100)}%"
                        })

        # Εμφάνιση αποτελεσμάτων
        if all_extracted_data:
            df = pd.DataFrame(all_extracted_data)
            st.success("Η ανάλυση ολοκληρώθηκε!")
            
            # Διαχωρισμός σε "Πιθανά Ονόματα" και "Πιθανά Power"
            st.subheader("Συγκεντρωτικά Στοιχεία")
            st.dataframe(df, use_container_width=True)
            
            # Κουμπί για Excel
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Κατέβασμα Λίστας για Excel", data=csv, file_name="last_war_data.csv", mime='text/csv')
        else:
            st.error("Δεν μπορέσαμε να διαβάσουμε καθαρά στοιχεία. Δοκίμασε πιο κοντινά screenshots.")

st.info("💡 Tip: Για καλύτερα αποτελέσματα, βγάζε screenshots όπου η λίστα των παικτών φαίνεται καθαρά και δεν είναι ανοιχτό το chat.")
