import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="Auditor Maestro de Organigramas", layout="wide")

st.title("🌳 Auditor de Organigramas con Alerta de Errores")

with st.expander("📌 REQUISITOS DEL ARCHIVO EXCEL", expanded=False):
    st.markdown("""
    * **Columna A:** ID del Trabajador.
    * **Columna B:** ID de la Jefatura.
    * **Verde:** Relación correcta.
    * **Rojo:** El ID del jefe NO existe en la lista de trabajadores (error de referencia).
    """)

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(how='all')
        
        col_id = df.columns[0]
        col_jefe = df.columns[1]

        # Limpieza y creación de lista de IDs válidos
        df[col_id] = df[col_id].astype(str).str.strip()
        df[col_jefe] = df[col_jefe].astype(str).str.strip()
        
        # Lista de todos los trabajadores existentes para validar jefes
        todos_los_ids = set(df[col_id].unique())

        dot = graphviz.Digraph(format='svg')
        dot.attr(rankdir='TB', splines='ortho', nodesep='0.4', ranksep='0.6')

        for _, row in df.iterrows():
            emp = row[col_id]
            jefe = row[col_jefe]

            if emp != 'nan' and emp != '':
                # Lógica de Color
                # Si es el jefe máximo (sin jefe arriba), azul oscuro
                if jefe == 'nan' or jefe == '' or jefe == 'None':
                    color_nodo = '#2E4053' # Gris azulado (Jefe Supremo)
                    texto_color = 'white'
                # Si el jefe existe en la lista de trabajadores, verde
                elif jefe in todos_los_ids:
                    color_nodo = '#27AE60' # Verde (Correcto)
                    texto_color = 'white'
                # Si el jefe NO existe, rojo
                else:
                    color_nodo = '#C0392B' # Rojo (Error de Jefatura)
                    texto_color = 'white'

                dot.node(emp, emp, style='filled,rounded', 
                         fillcolor=color_nodo, fontcolor=texto_color, 
                         fontname='Arial', fontsize='10')
                
                if jefe != 'nan' and jefe != '' and jefe != 'None':
                    dot.edge(jefe, emp)

        st.subheader("Visualización con Semáforo de Errores")
        st.graphviz_chart(dot, use_container_width=True)

        st.divider()
        st.subheader("📥 Exportar Resultados")
        st.download_button(
            label="Descargar PDF de Auditoría (Zoom Infinito)",
            data=dot.pipe(format='pdf'),
            file_name="auditoria_organigrama.pdf",
            mime="application/pdf"
        )

        # Tabla resumen de errores para copiar rápido
        errores = df[~df[col_jefe].isin(todos_los_ids) & (df[col_jefe] != 'nan') & (df[col_jefe] != '')]
        if not errores.empty:
            st.warning(f"⚠️ Se detectaron {len(errores)} trabajadores con jefaturas inexistentes:")
            st.dataframe(errores)
        else:
            st.success("✅ No se detectaron errores de referencia en las jefaturas.")

    except Exception as e:
        st.error(f"Error: {e}")
