import streamlit as st
import pandas as pd
import graphviz
import networkx as nx

# Configuración de la página
st.set_page_config(page_title="Auditor Maestro de Organigramas", layout="wide")

# --- 1. INSTRUCCIONES Y REQUISITOS ---
st.title("🌳 Auditor de Organigramas Inteligente")

with st.expander("📌 REQUISITOS DEL ARCHIVO EXCEL (Estructura)", expanded=True):
    st.markdown("""
    Para que el sistema funcione correctamente, tu archivo debe ser así:
    * **Columna A:** ID del Trabajador (Nombre o Número único).
    * **Columna B:** ID de la Jefatura (A quién reporta).
    * **Jefe Máximo:** Su celda de jefatura en la Columna B debe estar **vacía**.
    
    **Código de Colores:**
    * 🟢 **Verde:** Relación correcta (el jefe existe en la lista).
    * 🔴 **Rojo:** Error (el ID del jefe no existe en la columna A).
    * 🔵 **Azul Oscuro:** Nodo raíz (Jefe máximo).
    """)

# --- 2. CARGA DE ARCHIVO ---
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Cargar datos
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(how='all') # Limpiar filas vacías
        
        # Identificar columnas
        col_id = df.columns[0]
        col_jefe = df.columns[1]

        # Limpiar datos de texto
        df[col_id] = df[col_id].astype(str).str.strip()
        df[col_jefe] = df[col_jefe].astype(str).str.strip().replace('nan', '')

        # Lista de IDs válidos para validar existencia
        todos_los_ids = set(df[col_id].unique())

        # --- 3. GENERACIÓN DEL GRÁFICO ---
        dot = graphviz.Digraph(format='svg')
        dot.attr(rankdir='TB', splines='ortho', nodesep='0.4', ranksep='0.6')
        
        for _, row in df.iterrows():
            emp = row[col_id]
            jefe = row[col_jefe]

            if emp != '' and emp != 'nan':
                # Lógica de colores para auditoría
                if jefe == '':
                    color_nodo = '#2E4053' # Azul Oscuro (Raíz)
                elif jefe in todos_los_ids:
                    color_nodo = '#27AE60' # Verde (OK)
                else:
                    color_nodo = '#C0392B' # Rojo (Error: Jefe no existe)

                dot.node(emp, emp, style='filled,rounded', 
                         fillcolor=color_nodo, fontcolor='white', 
                         fontname='Arial', fontsize='10')
                
                if jefe != '':
                    dot.edge(jefe, emp)

        # Mostrar mapa
        st.subheader("Visualización del Mapa Completo")
        st.graphviz_chart(dot, use_container_width=True)

        # --- 4. BOTONES DE DESCARGA ---
        st.divider()
        st.subheader("📥 Exportar para Revisión")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button("Descargar PDF (Alta Calidad / Zoom)", 
                               data=dot.pipe(format='pdf'), 
                               file_name="organigrama_auditoria.pdf")
        with col_btn2:
            st.info("El PDF permite buscar con Ctrl+F y no se pixela.")

        # --- 5. PANEL DE AUDITORÍA (ERRORES) ---
        st.divider()
        st.subheader("🔍 Informe de Errores Encontrados")
        
        err_col1, err_col2 = st.columns(2)

        with err_col1:
            # Error 1: Jefes que no existen en la columna A
            errores_ref = df[~df[col_jefe].isin(todos_los_ids) & (df[col_jefe] != '')]
            if not errores_ref.empty:
                st.error(f"❌ {len(errores_ref)} empleados reportan a IDs inexistentes")
                st.dataframe(errores_ref)
            else:
                st.success("✅ Todas las jefaturas existen en la lista.")

        with err_col2:
            # Error 2: Referencias Circulares (Bucles)
            G = nx.DiGraph()
            for _, row in df.iterrows():
                if row[col_jefe] != '':
                    G.add_edge(row[col_jefe], row[col_id])
            try:
                ciclo = nx.find_cycle(G, orientation='original')
                st.warning("⚠️ Bucle Infinito detectado:")
                for u, v, _ in ciclo:
                    st.write(f"🔄 {u} <--> {v}")
            except:
                st.success("✅ No hay referencias circulares (bucles).")

    except Exception as e:
        st.error(f"Se produjo un error al procesar el archivo: {e}")
