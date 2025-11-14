import streamlit as st
import json
import pandas as pd
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Lector Medidor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 500;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .result-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'prompt' not in st.session_state:
    st.session_state.prompt = """You are an expert in infrastructure inspection. 
Analyze the provided image of a water, electrical, or gas meter.

Your tasks:
1. Detect and extract the numeric reading shown on the meter display (in kWh).
2. Evaluate the readability of each digit and provide an overall reading quality score (0–100), where 100 = perfectly clear.
3. Assess the condition of the meter and its immediate surroundings based on visual cues:
   - Dirt, rust, cracks, or damage.
   - Vegetation, moisture, or obstructions.
   - Visibility of labels and seals.
   - General maintenance state (good / moderate / poor).
4. Provide a short human-readable summary describing your assessment in plain language.

Do not include any explanation or formatting other than the requested JSON output. 
Attached is an example for you to replace with the current, correct data.

If the image does not show a water, electrical, or gas meter meter, just return the same JSON with zeros and in the summary add a text saying that what the photo is, if recognizable.

All answers on the returning JSON must be in SPANISH."""

if 'json_structure' not in st.session_state:
    st.session_state.json_structure = """{
  "meter_reading": "078254",
  "reading_quality": 92,
  "digit_confidence": [
    {"digito": "0", "confianza": 0.98},
    {"digito": "7", "confianza": 0.95},
    {"digito": "8", "confianza": 0.94},
    {"digito": "2", "confianza": 0.90},
    {"digito": "5", "confianza": 0.88},
    {"digito": "4", "confianza": 0.92}
  ],
  "condition_assessment": {
    "physical_state": "Intacto pero sucio",
    "environment": "Vegetacion presente, expuesto a la lluvia",
    "label_visibility": "Limpio y claro",
    "overall_condition": "Moderado"
  },
  "summary": "El medidor aparece funcional y legible con una pantalla clara. Se observan algunos residuos y cerca de la vegetación; se recomienda limpiar para evitar la degradación futura."
}"""

if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'processing_result' not in st.session_state:
    st.session_state.processing_result = None


def encode_image_to_base64(image):
    """Convert PIL Image or uploaded file to base64 string"""
    buffered = BytesIO()
    if isinstance(image, Image.Image):
        image.save(buffered, format="PNG")
    else:
        image.seek(0)
        buffered = BytesIO(image.read())
    
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def process_image_with_openai(image, api_key, prompt, json_example):
    """Send image to OpenAI Vision API and get JSON response"""
    try:
        client = OpenAI(api_key=api_key)
        
        # Encode image to base64
        base64_image = encode_image_to_base64(image)
        
        # Prepare the full prompt with JSON example
        full_prompt = f"{prompt}\n\nExpected JSON format:\n{json_example}"
        
        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Extract JSON from response
        json_response = json.loads(response.choices[0].message.content)
        return json_response, None
        
    except Exception as e:
        return None, str(e)


def display_results_table(result_json):
    """Display the JSON results in a structured table format"""
    st.markdown("### Resultados del Análisis")
    
    # Meter Reading Section
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Lectura del Medidor (kWh)", result_json.get("meter_reading", "N/A"))
    with col2:
        st.metric("Calidad de Lectura", f"{result_json.get('reading_quality', 0)}%")
    
    st.markdown("---")
    
    # Digit Confidence Table
    st.markdown("#### Confianza por Dígito")
    digit_data = result_json.get("digit_confidence", [])
    if digit_data:
        df_digits = pd.DataFrame(digit_data)
        
        # Handle both Spanish and English field names
        confidence_col = None
        if 'confianza' in df_digits.columns:
            confidence_col = 'confianza'
        elif 'Confianza' in df_digits.columns:
            confidence_col = 'Confianza'
        elif 'confidence' in df_digits.columns:
            confidence_col = 'confidence'
        
        if confidence_col:
            df_digits[confidence_col] = df_digits[confidence_col].apply(lambda x: f"{x*100:.1f}%")
        
        # Rename columns to Spanish for display
        column_map = {
            'digit': 'Dígito',
            'digito': 'Dígito', 
            'dígito': 'Dígito',
            'confidence': 'Confianza',
            'confianza': 'Confianza',
            'Confianza': 'Confianza'
        }
        df_digits = df_digits.rename(columns=column_map)
        st.dataframe(df_digits, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Condition Assessment
    st.markdown("#### Evaluación de Condición")
    condition = result_json.get("condition_assessment", {})
    if condition:
        df_condition = pd.DataFrame([
            {"Aspecto": "Estado Físico", "Estado": condition.get("physical_state", "N/A")},
            {"Aspecto": "Ambiente", "Estado": condition.get("environment", "N/A")},
            {"Aspecto": "Visibilidad de Etiquetas", "Estado": condition.get("label_visibility", "N/A")},
            {"Aspecto": "Condición General", "Estado": condition.get("overall_condition", "N/A")}
        ])
        st.dataframe(df_condition, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Summary
    st.markdown("#### Resumen")
    summary = result_json.get("summary", "No hay resumen disponible.")
    st.info(summary)


# Create tabs
tab1, tab2 = st.tabs(["Lector de Medidor", "Configuración"])

# MAIN TAB
with tab1:
    st.markdown('<div class="main-header">Lector de Medidor Eléctrico</div>', unsafe_allow_html=True)
    #st.markdown('<div class="sub-header">Capture an image of a meter for automated analysis</div>', unsafe_allow_html=True)
    
    # Camera capture section
    #st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    st.markdown("#### Capturar desde Cámara")
    camera_photo = st.camera_input("Tomar foto", label_visibility="collapsed")
    if camera_photo:
        st.session_state.uploaded_image = camera_photo
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process button
    if st.session_state.uploaded_image:
        if st.button("Procesar Imagen", type="primary", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Por favor ingrese su clave API de OpenAI en la pestaña de Configuración.")
            else:
                with st.spinner("Analizando imagen del medidor..."):
                    result, error = process_image_with_openai(
                        st.session_state.uploaded_image,
                        st.session_state.api_key,
                        st.session_state.prompt,
                        st.session_state.json_structure
                    )
                    
                    if error:
                        st.error(f"Error al procesar la imagen: {error}")
                    else:
                        st.session_state.processing_result = result
                        st.success("¡Análisis completado!")
    
    # Display results
    if st.session_state.processing_result:
        st.markdown("---")
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        display_results_table(st.session_state.processing_result)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Option to download results
        st.download_button(
            label="Descargar Resultados (JSON)",
            data=json.dumps(st.session_state.processing_result, indent=2, ensure_ascii=False),
            file_name="analisis_medidor.json",
            mime="application/json"
        )

# CONFIGURATION TAB
with tab2:
    st.markdown("### Configuración")
    st.markdown("Configure su clave API de OpenAI y personalice los parámetros de análisis.")
    
    st.markdown("---")
    
    # API Key input
    st.markdown("#### Clave API de OpenAI")
    api_key_input = st.text_input(
        "Ingrese su clave API de OpenAI",
        type="password",
        value=st.session_state.api_key,
        help="Su clave API se almacenará solo para esta sesión y nunca se guardará permanentemente."
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.success("¡Clave API actualizada!")
    
    st.markdown("---")
    
    # Prompt customization
    st.markdown("#### Prompt de Análisis")
    prompt_input = st.text_area(
        "Personalice el prompt de análisis",
        value=st.session_state.prompt,
        height=300,
        help="Este prompt guía a la IA en el análisis de la imagen del medidor."
    )
    if prompt_input != st.session_state.prompt:
        st.session_state.prompt = prompt_input
    
    st.markdown("---")
    
    # JSON structure customization
    st.markdown("#### Estructura JSON Esperada")
    json_input = st.text_area(
        "Defina el formato de salida JSON esperado",
        value=st.session_state.json_structure,
        height=400,
        help="Este ejemplo JSON muestra a la IA qué formato devolver."
    )
    
    # Validate JSON
    try:
        json.loads(json_input)
        if json_input != st.session_state.json_structure:
            st.session_state.json_structure = json_input
        st.success("La estructura JSON es válida")
    except json.JSONDecodeError as e:
        st.error(f"Formato JSON inválido: {e}")
    
    st.markdown("---")
    
    # Save button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Restaurar Valores Predeterminados", use_container_width=True):
            st.session_state.prompt = """You are an expert in infrastructure inspection. 
Analyze the provided image of an electric, gas or water meter.

Your tasks:
1. Detect and extract the numeric reading shown on the meter display.
2. Evaluate the readability of each digit and provide an overall reading quality score (0–100), where 100 = perfectly clear.
3. Assess the condition of the meter and its immediate surroundings based on visual cues:
   - Dirt, rust, cracks, or damage.
   - Vegetation, moisture, or obstructions.
   - Visibility of labels and seals.
   - General maintenance state (good / moderate / poor).
4. Provide a short human-readable summary describing your assessment in plain language.

Do not include any explanation or formatting other than the requested JSON output. Attached is an example for you to replace with the current, correct data. All answers on the returning JSON must be in SPANISH."""
            
            st.session_state.json_structure = """{
  "meter_reading": "078254",
  "reading_quality": 92,
  "digit_confidence": [
    {"dígito": "0", "Confianza": 0.98},
    {"dígito": "7", "Confianza": 0.95},
    {"dígito": "8", "Confianza": 0.94},
    {"dígito": "2", "Confianza": 0.90},
    {"dígito": "5", "Confianza": 0.88},
    {"dígito": "4", "Confianza": 0.92}
  ],
  "condition_assessment": {
    "physical_state": "Intacto pero sucio",
    "environment": "Vegetacion presente, expuesto a la lluvia",
    "label_visibility": "Limpio y claro",
    "overall_condition": "Moderado"
  },
  "summary": "El medidor aparece funcional y legible con una pantalla clara. Se observan algunos residuos y cerca de la vegetación; se recomienda limpiar para evitar la degradación futura."
}"""
            st.rerun()

