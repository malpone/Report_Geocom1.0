import streamlit as st
import os
import json
from google import genai
from google.genai import types
from docxtpl import DocxTemplate
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Generatore Report (Gemini New SDK)", page_icon="⚡")

st.title("⚡ Generatore Report Aziendale")
st.write("Motore: Google Gemini 1.5 Flash (Nuovo SDK)")

# --- CONFIGURAZIONE API KEY ---
# Incolla la tua chiave qui sotto tra le virgolette se non vuoi inserirla ogni volta
API_KEY_FISSA = "" 

if API_KEY_FISSA:
    api_key = API_KEY_FISSA
else:
    api_key = st.sidebar.text_input("Google AI Studio Key", type="password")
    st.sidebar.info("Richiedi la chiave su aistudio.google.com")

# --- INPUT UTENTE ---
testo_grezzo = st.text_area("Incolla qui il testo del report:", height=300)

# --- FUNZIONI ---
def get_gemini_data(text, key):
    # 1. Inizializza il Client
    client = genai.Client(api_key=key)
    
def get_gemini_data(text, key):
    # 1. Inizializza il nuovo Client
    client = genai.Client(api_key=key)
    
    # 2. Prompt
    prompt = f"""
    Sei un assistente data-entry. Estrai i dati dal testo seguente in formato JSON rigoroso.
    Struttura richiesta:
    {{
        "titolo_report": "...",
        "sottotitolo_report": "...",
        "data_odierna": "DD MMMM YYYY",
        "lista_sezioni": [
            {{ "titolo": "...", "testo": "..." }}
        ]
    }}
    
    TESTO:
    {text}
    """

    # 3. Chiamata al modello (Alias Stabile Gratuito)
    response = client.models.generate_content(
        model='gemini-flash-latest', # <--- QUESTA È LA MODIFICA SICURA
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json'
        )
    )
    
    # 4. Parsing
    return json.loads(response.text)

def generate_doc(data):
    if not os.path.exists("template_aziendale.docx"):
        st.error("ERRORE: Manca il file 'template_aziendale.docx' nella cartella!")
        return None

    doc = DocxTemplate("template_aziendale.docx")
    doc.render(data)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- LOGICA APPLICAZIONE ---
if st.button("🚀 Genera Report"):
    if not api_key:
        st.error("Manca la API Key!")
    elif not testo_grezzo:
        st.warning("Inserisci il testo prima di generare.")
    else:
        with st.spinner("Elaborazione con Gemini in corso..."):
            try:
                # 1. Chiama AI
                dati = get_gemini_data(testo_grezzo, api_key)
                st.success("Dati estratti!")
                
                with st.expander("Vedi JSON grezzo"):
                    st.json(dati)

                # 2. Crea DOCX
                file_docx = generate_doc(dati)

                if file_docx:
                    # 3. Download
                    st.download_button(
                        label="📥 Scarica Report (.docx)",
                        data=file_docx,
                        file_name="Report_Finale.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
                
                ## per runnarlo ---> python -m streamlit run formattazione2.py