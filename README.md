# 📊 Dashboard: Hurto de Vehículos en Colombia
Este repositorio presenta un análisis detallado del hurto de automotores y motocicletas en Colombia entre los años 2003 y 2024, basado en datos recopilados y procesados en el proyecto [Hurto_Vehiculos_Colombia](https://github.com/olancheros/Hurto_Vehiculos_Colombia).

## 🚀 ¿Qué encontrarás en este dashboard?
El dashboard ha sido desarrollado con [Streamlit](https://streamlit.io/), proporcionando una interfaz interactiva que permite explorar los datos de manera intuitiva.

### 🔹 Características principales
El diseño del dashboard se compone de:

#### ✅ Un Sidebar Interactivo:

Tres selectores permiten elegir tipo de vehículo, año y paleta de color para personalizar la visualización de datos.

#### ✅ Panel Principal:
##### 📌 Tendencias temporales:
Gráficos de líneas (line plots) muestran la cantidad de hurtos y su acumulado a lo largo del periodo de estudio, diferenciados por tipo de vehículo.
##### 📌 Análisis geográfico y comparativo:

- **Variación anual por departamento**:
  - Destaca qué departamentos tuvieron el mayor incremento y disminución de hurtos en comparación con el año anterior.
  - Incluye la variación porcentual del hurto a nivel nacional.

- **Mapa de coropletas**:
  - Representa la variación geográfica del hurto en los diferentes departamentos del país para el año seleccionado.

- **Mapa de calor**:
  - Muestra la evolución del hurto en todo el periodo de estudio.
  - Se aplicó una transformación logarítmica $(log(x+1))$ a la variable de color (num_hurtos) para mejorar el contraste visual.

##### 📌 Análisis mensual y ranking de departamentos:
- Gráficos de líneas (line plots) ilustran la evolución mensual del hurto y su acumulado.
- Un gráfico de barras muestra el Top 10 de departamentos con más hurtos en el país.

--------------------------------
Este dashboard proporciona una visión clara y dinámica del hurto de vehículos en Colombia, facilitando la identificación de patrones y tendencias clave. 🔍🚗📉

¡Explora el dashboard y descubre los insights más relevantes sobre el fenómeno del hurto de vehículos en el país [aquí](https://dashboardhurtovehiculos-olancheros.streamlit.app/)! 🎯📈