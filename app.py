import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="Validador de Organigramas", layout="wide")

st.title("🌳 Generador de Organigramas")

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # Limpieza básica
        df = df.dropna(how='all')
        col_id = df.columns[0]
        col_jefe = df.columns[1]

        # Configuración del Gráfico
        # 'dot' es mejor para organigramas (jerarquía de arriba abajo)
        dot = graphviz.Digraph(format='png') 
        dot.attr(rankdir='TB', size='30,30')
        dot.attr('node', shape='rectangle', style='filled,rounded', 
                 color='#2E86C1', fontcolor='white', fontname='Arial')

        for _, row in df.iterrows():
            emp = str(row[col_id]).strip()
            jefe = str(row[col_jefe]).strip()

            if emp != 'nan' and emp != '':
                dot.node(emp, emp)
                if jefe != 'nan' and jefe != '' and jefe != 'None':
                    dot.edge(jefe, emp)

        st.subheader("Visualización del Mapa:")
        
        # Intentar mostrarlo
        st.graphviz_chart(dot)

        # BOTÓN DE RESPALDO: Descarga el diagrama como imagen si no se ve arriba
        st.divider()
        st.write("¿No puedes ver el mapa arriba? Descárgalo aquí:")
        
        # Generar los datos de la imagen para descargar
        png_data = dot.pipe(format='png')
        st.download_button(
            label="📥 Descargar Organigrama (PNG)",
            data=png_data,
            file_name="organigrama.png",
            mime="image/png"
        )

        st.success("✅ Procesado correctamente.")

    except Exception as e:
        st.error(f"Error al procesar: {e}")
