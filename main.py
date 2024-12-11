import os
import pandas as pd
import json
from datetime import datetime
import streamlit as st
import openai
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Usar la clave API desde el entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

def excel_to_json_with_modifications(excel_file, modifications):
    """Convierte un archivo Excel a JSON con modificaciones."""
    try:
        data = pd.read_excel(excel_file, sheet_name=None)
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None

    result = {}
    for sheet_name, df in data.items():
        records = df.to_dict(orient='records')

        for record in records:
            if 'add_field' in modifications:
                record[modifications['add_field']['field_name']] = modifications['add_field']['value']
            if 'combine_fields' in modifications:
                field1 = modifications['combine_fields']['field1']
                field2 = modifications['combine_fields']['field2']
                new_field = modifications['combine_fields']['new_field']
                record[new_field] = f"{record.get(field1, '')} {record.get(field2, '')}"

        result[sheet_name] = records

    return json.dumps(result, ensure_ascii=False, indent=4)

def obtener_recomendaciones(prompt):
    """Obtiene recomendaciones basadas en un prompt usando OpenAI."""
    try:
        # Cambiado para ser compatible con openai>=1.0.0
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Cambiar por "gpt-3.5-turbo" si no tienes acceso a "gpt-4"
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extraer la respuesta del asistente
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error al obtener recomendaciones: {e}"

def main():
    st.title("Conversor de Excel a JSON")
    
    excel_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])
    if excel_file:
        modifications = {
            'add_field': {'field_name': 'createdAt', 'value': datetime.now().isoformat()},
            'combine_fields': {'field1': 'Nombre', 'field2': 'Apellido', 'new_field': 'NombreCompleto'}
        }

        json_result = excel_to_json_with_modifications(excel_file, modifications)
        if json_result:
            st.json(json_result)
            st.download_button("Descargar JSON", json_result, file_name="resultado.json", mime="application/json")

    prompt = st.text_input("Ingresa tu prompt para recomendaciones:")
    if st.button("Obtener Recomendaciones"):
        if prompt:
            recomendaciones = obtener_recomendaciones(prompt)
            st.write(recomendaciones)

if __name__ == "__main__":
    main()
