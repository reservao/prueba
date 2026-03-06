import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="Validador de Organigramas", layout="wide")

st.title("🌳 Generador Automático de Organigramas")

uploaded_file = st.file_uploader("Elige tu archivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # Limpiamos nombres de columnas y datos
        df.columns = [str(c).strip() for c in df.columns]
        col_id = df.columns[0]
        col_jefe = df.columns[1]

        # Crear el gráfico
        dot = graphviz.Digraph(comment='Organigrama')
        dot.attr(rankdir='TB', size='20,20!') # Aumentamos el límite de tamaño
        dot.attr('node', shape='box', style='filled,rounded', color='#E1F5FE', fontname='Arial')

        for index, row in df.iterrows():
            emp = str(row[col_id]).strip()
            jefe = str(row[col_jefe]).strip()

            if emp != 'nan' and emp != '':
                dot.node(emp, emp)
                if jefe != 'nan' and jefe != '' and jefe != 'None':
                    dot.edge(jefe, emp)

        st.subheader("Visualización del Mapa:")
        
        # Usamos un contenedor para asegurar que se vea
        with st.container():
            st.graphviz_chart(dot, use_container_width=True)
            
        st.success("✅ Organigrama generado. Si no lo ves, intenta con un archivo más pequeño para probar.")

    except Exception as e:
        st.error(f"Error: {e}")
