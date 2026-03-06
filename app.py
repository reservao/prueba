import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="Auditor de Organigramas", layout="wide")

st.title("🌳 Auditor Inteligente de Organigramas")
st.markdown("""
Esta herramienta te permite auditar tramos de control específicos.  
Sube tu Excel y luego **selecciona una jefatura** para ver su equipo.
""")

# --- FUNCIONES DE AYUDA (Para no saturar el código principal) ---
def obtener_subordinados(df, jefe_id, niveles=2):
    """Busca recursivamente los subordinados de un jefe hasta N niveles."""
    col_id = df.columns[0]
    col_jefe = df.columns[1]
    
    subordinados = []
    # Nivel 1: Directos
    directos = df[df[col_jefe].astype(str).str.strip() == str(jefe_id).strip()][col_id].tolist()
    subordinados.extend(directos)
    
    # Niveles siguientes
    if niveles > 1:
        for sub in directos:
            subordinados.extend(obtener_subordinados(df, sub, niveles - 1))
            
    return list(set(subordinados)) # Evitar duplicados

# --- APLICACIÓN PRINCIPAL ---
uploaded_file = st.file_uploader("1. Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Cargar y limpiar datos
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(how='all')
        
        # Asegurar que las columnas sean strings y no tengan espacios extra
        col_id = df.columns[0]
        col_jefe = df.columns[1]
        df[col_id] = df[col_id].astype(str).str.strip()
        df[col_jefe] = df[col_jefe].astype(str).str.strip()

        # 2. Selección de Jefatura
        st.divider()
        st.subheader("2. Selecciona la Jefatura a auditar:")
        
        # Crear lista única de jefes (excluyendo 'nan')
        lista_jefes = df[col_jefe].unique().tolist()
        lista_jefes = [j for j in lista_jefes if j.lower() != 'nan' and j != '']
        lista_jefes.sort()
        
        jefe_seleccionado = st.selectbox("Elige un ID de Jefe:", ["-- Selecciona --"] + lista_jefes)

        if jefe_seleccionado != "-- Selecciona --":
            # 3. Filtrar datos para el gráfico
            st.divider()
            st.subheader(f"Vista para la Jefatura: {jefe_seleccionado}")
            
            # Obtener subordinados hasta 3 niveles (suficiente para auditar)
            ids_a_mostrar = obtener_subordinados(df, jefe_seleccionado, niveles=3)
            ids_a_mostrar.append(jefe_seleccionado) # Incluir al jefe elegido
            
            # Filtrar el DataFrame original
            df_filtrado = df[df[col_id].isin(ids_a_mostrar)]
            
            # 4. Generar el Gráfico Filtrado
            dot = graphviz.Digraph(format='png')
            dot.attr(rankdir='TB', nodesep='0.4', ranksep='0.6')
            
            # Estilo de los nodos (cuadros)
            dot.attr('node', shape='rectangle', style='filled,rounded', 
                     color='#2E86C1', fontcolor='white', fontname='Arial', fontsize='11')
            
            # Resaltar al jefe seleccionado
            dot.node(jefe_seleccionado, jefe_seleccionado, color='#F39C12', fontcolor='black')

            for _, row in df_filtrado.iterrows():
                emp = str(row[col_id])
                jefe = str(row[col_jefe])

                # No volver a dibujar el nodo del jefe seleccionado
                if emp != jefe_seleccionado:
                    dot.node(emp, emp)
                
                # Crear conexión si ambos están en la lista a mostrar
                if jefe in ids_a_mostrar and emp in ids_a_mostrar:
                    if jefe != 'nan' and jefe != '':
                        dot.edge(jefe, emp)

            # 5. Mostrar y Descargar
            st.image(dot.pipe(format='png'), use_container_width=False)
            
            with st.expander("📥 Opciones de descarga de alta calidad"):
                st.write("Si el gráfico sigue siendo grande, descarga el PDF. Los PDFs no se pixelan.")
                
                # Descarga PNG (Imagen estándar)
                st.download_button(
                    label="Descargar esta vista (PNG)",
                    data=dot.pipe(format='png'),
                    file_name=f"equipo_{jefe_seleccionado}.png",
                    mime="image/png"
        )
                # Descarga PDF (Lo mejor para imprimir o auditar con zoom)
                st.download_button(
                    label="Descargar esta vista (PDF - Alta Calidad)",
                    data=dot.pipe(format='pdf'),
                    file_name=f"equipo_{jefe_seleccionado}.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"Hubo un error técnico. Revisa que tu Excel tenga los datos en las dos primeras columnas. Error: {e}")
