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
        # Intentar leer el archivo Excel
        st.write("Intentando leer el archivo Excel...")
        data = pd.read_excel(excel_file, sheet_name=None)
        st.write("Archivo Excel leído correctamente.")
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None

    result = {}
    try:
        for sheet_name, df in data.items():
            st.write(f"Procesando hoja: {sheet_name}")
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
        st.write("Modificaciones aplicadas exitosamente.")
    except Exception as e:
        st.error(f"Error al procesar las hojas de Excel: {e}")
        return None

    try:
        json_result = json.dumps(result, ensure_ascii=False, indent=4)
        st.write("Conversión a JSON completada.")
        return json_result
    except Exception as e:
        st.error(f"Error al convertir los datos a JSON: {e}")
        return None

def obtener_recomendaciones(prompt):
    """Obtiene recomendaciones basadas en un prompt usando OpenAI."""
    try:
        st.write("Enviando solicitud a OpenAI...")
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Cambiar por "gpt-3.5-turbo" si no tienes acceso a "gpt-4"
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": prompt}
            ]
        )
        st.write("Respuesta recibida de OpenAI.")
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error al obtener recomendaciones: {e}")
        return None

def main():
    st.title("Conversor de Excel a JSON con OpenAI")

    # Validar la clave API
    if not openai.api_key:
        st.error("La clave API de OpenAI no está configurada. Verifica el archivo .env.")
        return

    # Subida de archivo Excel
    excel_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])
    if excel_file:
        try:
            modifications = {
                'add_field': {'field_name': 'createdAt', 'value': datetime.now().isoformat()},
                'combine_fields': {'field1': 'Nombre', 'field2': 'Apellido', 'new_field': 'NombreCompleto'}
            }

            json_result = excel_to_json_with_modifications(excel_file, modifications)
            if json_result:
                st.json(json_result)
                st.download_button("Descargar JSON", json_result, file_name="resultado.json", mime="application/json")
        except Exception as e:
            st.error(f"Error al procesar el archivo Excel: {e}")

    # Entrada para el prompt
    prompt = st.text_input("Ingresa tu prompt para recomendaciones:")
    if st.button("Obtener Recomendaciones"):
        if prompt:
            try:
                recomendaciones = obtener_recomendaciones(prompt)
                if recomendaciones:
                    st.write(recomendaciones)
                else:
                    st.error("No se recibieron recomendaciones.")
            except Exception as e:
                st.error(f"Error al procesar el prompt: {e}")

if __name__ == "__main__":
    main()
