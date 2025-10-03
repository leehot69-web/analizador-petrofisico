import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from funciones_las import cargar_las_streamlit, resumen_las, analizar_intervalos, obtener_info_pozo

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from funciones_las import cargar_las_streamlit, resumen_las, analizar_intervalos

st.set_page_config(page_title="Petrofísica Avanzada", layout="wide")
st.title("🛢️ Análisis Petrofísico Avanzado - Visualización Completa")

archivo = st.file_uploader("Sube tu archivo LAS", type=["las"])

if archivo is not None:
    st.success(f"✅ Archivo cargado: {archivo.name}")
    
    try:
        with st.spinner("Cargando y procesando el archivo LAS..."):
            las = cargar_las_streamlit(archivo)
        
        st.success("¡Archivo LAS cargado exitosamente!")
        
        # SECCIÓN NUEVA: INFORMACIÓN DEL POZO
        st.header("🏭 Información del Pozo")
        
        info_pozo = obtener_info_pozo(las)
        
        # Mostrar en columnas organizadas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Identificación")
            st.metric("Nombre del Pozo", info_pozo['Nombre del Pozo'])
            st.metric("UWI/API", info_pozo['UWI/API'])
            st.metric("Compañía", info_pozo['Compañía'])
            
        with col2:
            st.subheader("Ubicación y Datos")
            st.metric("Campo", info_pozo['Campo'])
            st.metric("Ubicación", info_pozo['Ubicación'])
            st.metric("Fecha", info_pozo['Fecha'])
        
        # Información de profundidad
        st.subheader("Rango de Profundidad")
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Profundidad Mínima", f"{info_pozo['Profundidad Mínima']} m")
        with col4:
            st.metric("Profundidad Máxima", f"{info_pozo['Profundidad Máxima']} m")
        # Obtener DataFrame
        df = las.df()
        
        # Mostrar información básica
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Curvas disponibles", len(df.columns))
        with col2:
            st.metric("Puntos de profundidad", len(df))
        with col3:
            st.metric("Profundidad mínima", f"{df.index.min():.1f}")
        with col4:
            st.metric("Profundidad máxima", f"{df.index.max():.1f}")
        
        # SECCIÓN 1: GRÁFICOS DE CURVAS ESTÁNDAR
        st.header("📈 Curvas de Perfilamiento")
        
        if not df.empty:
            # Detectar automáticamente tipos de curvas comunes
            curvas_gr = [c for c in df.columns if any(x in c.upper() for x in ['GR', 'GAMMA', 'GAMMA_RAY'])]
            curvas_resistividad = [c for c in df.columns if any(x in c.upper() for x in ['RT', 'RES', 'RESISTIVITY', 'ILD'])]
            curvas_porosidad = [c for c in df.columns if any(x in c.upper() for x in ['PHI', 'POR', 'POROSITY', 'NEUT', 'DPHI'])]
            curvas_densidad = [c for c in df.columns if any(x in c.upper() for x in ['RHOB', 'DEN', 'DENSITY'])]
            
            # Crear pistas múltiples como en software petrofísico
            fig = make_subplots(
                rows=1, cols=4,
                subplot_titles=('Rayos Gamma', 'Resistividad', 'Porosidad', 'Densidad'),
                shared_yaxes=True,
                horizontal_spacing=0.02
            )
            
            # Pista 1: Rayos Gamma
            if curvas_gr:
                for curva in curvas_gr[:2]:  # Máximo 2 curvas de GR
                    fig.add_trace(
                        go.Scatter(x=df[curva], y=df.index, name=curva, line=dict(color='green')),
                        row=1, col=1
                    )
            else:
                fig.add_annotation(row=1, col=1, text="No hay datos GR", showarrow=False)
            
            # Pista 2: Resistividad
            if curvas_resistividad:
                for i, curva in enumerate(curvas_resistividad[:3]):  # Máximo 3 curvas de resistividad
                    colors = ['red', 'blue', 'orange']
                    fig.add_trace(
                        go.Scatter(x=df[curva], y=df.index, name=curva, line=dict(color=colors[i % len(colors)])),
                        row=1, col=2
                    )
            else:
                fig.add_annotation(row=1, col=2, text="No hay datos RES", showarrow=False)
            
            # Pista 3: Porosidad
            if curvas_porosidad:
                for i, curva in enumerate(curvas_porosidad[:3]):
                    colors = ['blue', 'lightblue', 'darkblue']
                    fig.add_trace(
                        go.Scatter(x=df[curva], y=df.index, name=curva, line=dict(color=colors[i % len(colors)])),
                        row=1, col=3
                    )
            else:
                fig.add_annotation(row=1, col=3, text="No hay datos POR", showarrow=False)
            
            # Pista 4: Densidad
            if curvas_densidad:
                for curva in curvas_densidad[:2]:
                    fig.add_trace(
                        go.Scatter(x=df[curva], y=df.index, name=curva, line=dict(color='brown')),
                        row=1, col=4
                    )
            else:
                fig.add_annotation(row=1, col=4, text="No hay datos DEN", showarrow=False)
            
            # Configurar layout
            fig.update_yaxes(autorange="reversed", title="Profundidad (m)")
            fig.update_layout(height=800, showlegend=True, title_text="Perfilamiento Completo")
            st.plotly_chart(fig, use_container_width=True)
        
        # SECCIÓN 2: ANÁLISIS DE LITOLOGÍAS Y ARENAS
        st.header("🪨 Análisis de Litologías")
        
        # Buscar curvas que indiquen litología o arena
        curvas_litologia = [c for c in df.columns if any(x in c.upper() for x in 
                        ['LITH', 'LITOLOGY', 'SAND', 'ARENA', 'SHALE', 'LUTITA', 'CALIZA', 'DOLOMITE'])]
        
        if curvas_litologia:
            st.info(f"**Curvas de litología detectadas:** {', '.join(curvas_litologia)}")
            
            # Gráfico de litologías
            fig_litho = go.Figure()
            
            for curva in curvas_litologia:
                # Normalizar datos para visualización
                data = df[curva].dropna()
                if not data.empty:
                    normalized_data = (data - data.min()) / (data.max() - data.min()) * 100
                    fig_litho.add_trace(
                        go.Scatter(
                            x=normalized_data, 
                            y=data.index, 
                            mode='lines',
                            name=curva,
                            line=dict(width=3)
                        )
                    )
            
            fig_litho.update_yaxes(autorange="reversed", title="Profundidad (m)")
            fig_litho.update_layout(
                title="Análisis de Litologías",
                xaxis_title="Valor Normalizado (%)",
                height=600
            )
            st.plotly_chart(fig_litho, use_container_width=True)
            
            # Mostrar estadísticas de litología
            with st.expander("📊 Estadísticas de Litología"):
                for curva in curvas_litologia:
                    if curva in df.columns:
                        st.write(f"**{curva}:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Valor promedio", f"{df[curva].mean():.2f}")
                        with col2:
                            st.metric("Desviación std", f"{df[curva].std():.2f}")
                        with col3:
                            # Clasificación básica
                            avg = df[curva].mean()
                            if avg > 50:
                                clasif = "Posible arena"
                            else:
                                clasif = "Otra litología"
                            st.metric("Clasificación", clasif)
        else:
            st.warning("No se detectaron curvas específicas de litología. Mostrando análisis basado en GR...")
            
            # Análisis básico de arena/lutita basado en GR
            if curvas_gr:
                gr_curve = curvas_gr[0]
                gr_data = df[gr_curve].dropna()
                
                if not gr_data.empty:
                    # Calcular límites para arena/lutita (valores típicos)
                    gr_min, gr_max = gr_data.min(), gr_data.max()
                    limite_arena = gr_min + (gr_max - gr_min) * 0.3  # 30% del rango
                    
                    # Crear clasificación
                    clasificacion = []
                    for valor in gr_data:
                        if valor <= limite_arena:
                            clasificacion.append('Arena')
                        else:
                            clasificacion.append('Lutita')
                    
                    # Gráfico de clasificación
                    fig_class = make_subplots(rows=1, cols=2, shared_yaxes=True,
                                            subplot_titles=('Curva GR', 'Clasificación Arena/Lutita'))
                    
                    # Curva GR
                    fig_class.add_trace(
                        go.Scatter(x=gr_data, y=gr_data.index, name='GR', line=dict(color='green')),
                        row=1, col=1
                    )
                    
                    # Clasificación
                    for lith in ['Arena', 'Lutita']:
                        mask = [l == lith for l in clasificacion]
                        if any(mask):
                            y_values = gr_data.index[mask]
                            x_values = [1 if lith == 'Arena' else 0] * len(y_values)
                            fig_class.add_trace(
                                go.Scatter(x=x_values, y=y_values, mode='markers', 
                                         name=lith, marker=dict(size=5)),
                                row=1, col=2
                            )
                    
                    fig_class.update_yaxes(autorange="reversed", title="Profundidad (m)")
                    fig_class.update_layout(height=600, showlegend=True)
                    st.plotly_chart(fig_class, use_container_width=True)
        
        # SECCIÓN 3: DETALLES TÉCNICOS
        with st.expander("🔍 Detalles Técnicos del Archivo"):
            st.subheader("Información del Header")
            resumen = resumen_las(las)
            st.dataframe(resumen["header_df"], use_container_width=True)
            
            st.subheader("Todas las Curvas Disponibles")
            st.dataframe(resumen["curvas_df"], use_container_width=True)
            
            st.subheader("Vista previa de Datos")
            st.dataframe(df.head(20), use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {str(e)}")
        st.info("""
        **Si los gráficos no se muestran como esperas:**
        1. Verifica que el archivo tenga las curvas esperadas
        2. Revisa los nombres de las curvas en la sección de detalles técnicos
        3. El archivo podría usar nombres no estándar para las curvas
        """)

else:
    st.info("👆 Por favor, sube un archivo LAS para comenzar el análisis")

# Información de ayuda
with st.expander("💡 Cómo interpretar los gráficos"):
    st.markdown("""
    **Gráficos de Perfilamiento:**
    - **Rayos Gamma (GR)**: Identifica lutitas (valores altos) vs arenas (valores bajos)
    - **Resistividad (RT)**: Detecta presencia de hidrocarburos (valores altos)
    - **Porosidad (PHI)**: Indica capacidad de almacenamiento
    - **Densidad (RHOB)**: Ayuda a identificar litologías
    
    **Análisis de Litologías:**
    - Las curvas específicas de litología muestran la interpretación de rocas
    - **Arena**: Generalmente buena porosidad para almacenar fluidos
    - **Lutita**: Baja permeabilidad, actúa como sello
    """)