import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Last War Analyzer", layout="centered")
st.title("🛡️ Last War Alliance Intelligence")

# Φόρτωση του AI - Πιο ελαφριά έκδοση
@st.cache_resource
def load_model():
    # Το gpu=False βοηθάει να μην κρασάρει ο server
    return easyocr.Reader(['en'], gpu=False)

try:
    reader = load_model()
except Exception as e:
    st.error("Το AI μοντέλο δυσκολεύεται να φορτώσει. Δοκίμασε πάλι σε λίγο.")

# Ανέβασμα Εικόνας
uploaded_file = st.file_uploader("Ανέβασε screenshot (Power/Kills)", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Screenshot', use_container_width=True)
    
    if st.button('Έναρξη Ανάλυσης'):
        with st.spinner('Παρακαλώ περιμένετε, το AI διαβάζει τα στοιχεία...'):
            try:
                img_array = np.array(image)
                # Ανάλυση
                results = reader.readtext(img_array)
                
                # Καθαρισμός δεδομένων
                data_found = [res[1] for res in results]
                
                if data_found:
                    df = pd.DataFrame(data_found, columns=['Στοιχεία'])
                    st.success("Η ανάλυση ολοκληρώθηκε!")
                    st.table(df) # Το table είναι πιο ελαφρύ από το dataframe
                else:
                    st.warning("Δεν βρέθηκε κείμενο. Δοκίμασε πιο καθαρό screenshot.")
            except Exception as e:
                st.error(f"Παρουσιάστηκε σφάλμα: {e}")

st.info("Σημείωση: Η πρώτη ανάλυση μπορεί να καθυστερήσει λίγο.")
