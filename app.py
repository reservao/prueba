import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="Generador de Organigramas", layout="wide")

st.title("🌳 Generador Automático de Organigramas")
st.write("Sube tu archivo Excel con las columnas: **ID Trabajador** e **ID Jefatura**.")

# 1. Subida de archivo
uploaded_file = st.file_uploader("Elige tu archivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Limpiar espacios en blanco por si acaso
        df.columns = [c.strip() for c in df.columns]
        col_id = df.columns[0] # Columna A
        col_jefe = df.columns[1] # Columna B

        # 2. Crear el gráfico
        dot = graphviz.Digraph(comment='Organigrama')
        dot.attr(rankdir='TB', size='10')

        # Estilo de los nodos
        dot.attr('node', shape='box', style='filled', color='lightblue', fontname='Arial')

        for index, row in df.iterrows():
            emp = str(row[col_id])
            jefe = str(row[col_jefe])

            # Agregar el trabajador
            dot.node(emp, emp)

            # Si tiene jefe y no es un valor vacío, crear la conexión
            if jefe and jefe.lower() != 'nan' and jefe != 'None' and jefe != '':
                dot.edge(jefe, emp)

        # 3. Mostrar resultados
        st.subheader("Visualización del Mapa:")
        st.graphviz_chart(dot)
        
        st.success("✅ Organigrama generado con éxito.")

    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")
        st.info("Asegúrate de que la Columna A sea el ID y la Columna B el ID del Jefe.")