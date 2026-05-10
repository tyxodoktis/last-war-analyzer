import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Last War Alliance Analyzer", layout="wide")
st.title("🛡️ Last War Alliance Intelligence Unit")

# Φόρτωση του AI μοντέλου (EasyOCR)
@st.cache_resource
def load_model():
    return easyocr.Reader(['en'])

reader = load_model()

# Menu στο πλάι
st.sidebar.header("Ρυθμίσεις Αξιολόγησης")
min_power = st.sidebar.number_input("Ελάχιστο Power Growth", value=1000000)

# Κύριο μέρος: Ανέβασμα Εικόνας
uploaded_file = st.file_uploader("Ανέβασε screenshot από το παιχνίδι", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Το Screenshot σου', use_column_width=True)
    
    with st.spinner('Το AI αναλύει τα δεδομένα...'):
        # Μετατροπή εικόνας για το OCR
        img_array = np.array(image)
        results = reader.readtext(img_array)
        
        # Εδώ το AI "καθαρίζει" τα κείμενα
        detected_data = [res[1] for res in results]
        
        # Εμφάνιση αποτελεσμάτων σε πίνακα
        df = pd.DataFrame(detected_data, columns=['Στοιχεία που βρέθηκαν'])
        st.success("Η ανάλυση ολοκληρώθηκε!")
        st.dataframe(df)

        # Κουμπί για κατέβασμα σε Excel
        st.download_button("Κατέβασμα σε Excel", data=df.to_csv(), file_name="alliance_stats.csv")
      
