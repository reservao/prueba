import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="Auditor Maestro de Organigramas", layout="wide")

# --- SECCIÓN 1: INSTRUCCIONES DE ESTRUCTURA ---
st.title("🌳 Generador de Organigramas Masivos")
with st.expander("📌 REQUISITOS DEL ARCHIVO EXCEL (Haz clic para ver)", expanded=True):
    st.markdown("""
    Para que el sistema funcione, tu archivo debe tener esta estructura exacta:
    * **Columna A:** ID o Nombre del Trabajador (único).
    * **Columna B:** ID o Nombre de la Jefatura a la que reporta.
    * **El Jefe Máximo:** La celda de su jefatura (Columna B) debe estar **vacía**.
    * **Formato:** Archivo `.xlsx` sin filas vacías al inicio.
    """)

# --- SECCIÓN 2: CARGA Y PROCESAMIENTO ---
uploaded_file = st.file_uploader("Sube tu archivo Excel aquí", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(how='all') # Eliminar filas vacías
        
        col_id = df.columns[0]
        col_jefe = df.columns[1]

        # Configuración del motor gráfico para alta densidad
        dot = graphviz.Digraph(format='svg') 
        dot.attr(rankdir='TB', splines='ortho', nodesep='0.4', ranksep='0.6')
        
        # Estilo de los nodos para que no ocupen tanto espacio
        dot.attr('node', shape='box', style='filled,rounded', 
                 color='#2E86C1', fontcolor='white', fontname='Arial', fontsize='10')

        # Construcción del árbol completo
        for _, row in df.iterrows():
            emp = str(row[col_id]).strip()
            jefe = str(row[col_jefe]).strip()

            if emp != 'nan' and emp != '':
                dot.node(emp, emp)
                if jefe != 'nan' and jefe != '' and jefe != 'None':
                    dot.edge(jefe, emp)

        # --- SECCIÓN 3: VISUALIZACIÓN Y DESCARGA ---
        st.divider()
        st.subheader("Visualización del Árbol Completo")
        st.info("💡 Tip: Si el gráfico es muy grande, usa el botón de la esquina superior derecha del mapa para ampliar, o descarga el PDF para hacer zoom.")

        # Mostramos en SVG (esto permite que el texto sea nítido en la web)
        st.graphviz_chart(dot, use_container_width=True)

        st.divider()
        st.subheader("📥 Descarga para Auditoría Detallada")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="Descargar PDF (Zoom Infinito - Recomendado)",
                data=dot.pipe(format='pdf'),
                file_name="organigrama_completo.pdf",
                mime="application/pdf"
            )
        
        with col2:
            st.write("El PDF te permitirá buscar nombres con `Ctrl + F` y ver detalles sin pixeles.")

        st.success(f"✅ Se han procesado {len(df)} registros.")

    except Exception as e:
        st.error(f"Error en el procesamiento: {e}")
