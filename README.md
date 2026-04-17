![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

# 🌱 Clima Intelligence

### 🔗 Acceso Directo a la Aplicación
Puedes interactuar con la plataforma aquí:
👉 **[https://app-mi-proyecto-clima.streamlit.app/](https://mi-proyecto-clima.streamlit.app/)**

---

📋 **Descripción del Proyecto**

Esta plataforma es una herramienta avanzada de Business Intelligence aplicada al sector agrícola y climático. El sistema integra múltiples fuentes de datos para analizar la relación entre las variables meteorológicas y el rendimiento de las cosechas en diferentes municipios de la región.

La aplicación permite la ingesta de datos desde archivos Excel (.xlsx), CSV y bases de datos SQL (SQLite) de manera automática y centralizada, ofreciendo un dashboard interactivo para la toma de decisiones.

🎯 Objetivos del Análisis

El proyecto busca responder a preguntas críticas para la planificación agrícola mediante el uso de analítica descriptiva y exploratoria:

Identificación de Patrones Climáticos: Determinar periodos críticos de precipitación y temperatura que afectan directamente a los cultivos.

Correlación Clima-Producción: Analizar cómo el brillo solar y la lluvia influyen en el rendimiento por hectárea.

Optimización Regional: Identificar los municipios con mejor desempeño agrícola bajo condiciones climáticas específicas.

Mitigación de Riesgos: Proporcionar una base de datos histórica para predecir posibles caídas en la producción ante eventos climáticos adversos.

📊 Estructura de la Base de Datos

El proyecto procesa la información organizada en los siguientes módulos (basados en el archivo Datos Base de Datos.xlsx):

🌡️ Temperatura: Análisis de máximas y mínimas diarias (en degC) por región.

🌧️ Precipitación: Monitoreo mensual de lluvias acumuladas (en mm).

☀️ Brillo Solar: Registro de horas de sol efectivas diarias.

🌾 Producción: Datos críticos de áreas sembradas, áreas cosechadas, producción total y rendimiento por producto.

🚀 Características Principales

Carga Multi-formato: Motor de detección inteligente que busca fuentes en SQL, CSV y hojas de Excel simultáneamente.

Normalización de Datos: Limpieza automática de cabeceras y conversión robusta de tipos numéricos (manejo de separadores de miles y decimales).

Visualización Avanzada: Implementación de gráficos estadísticos con Seaborn y Matplotlib para análisis de densidad y comparativas regionales.

Seguridad y UX: Interfaz con control de sesión, diseño responsivo y navegación por pestañas profesionales.

🛠️ Instalación y Uso

Clonar el repositorio:

git clone [https://github.com/grupoproyectoanalisisdatos-bot/Simulacion_-IA-cosechas_-repo-prueba-streamlit.git](https://github.com/grupoproyectoanalisisdatos-bot/Simulacion_-IA-cosechas_-repo-prueba-streamlit.git)


Instalar dependencias:

pip install -r requirements.txt


Ejecutar la aplicación:

streamlit run streamlit_app.py


📦 Dependencias Técnicas

Pandas: Manipulación y limpieza de dataframes.

Seaborn & Matplotlib: Visualización científica de datos.

Openpyxl: Librería necesaria para la lectura de archivos Excel (.xlsx).

Sqlite3: Integración de base de datos relacional para persistencia local.

[!IMPORTANT]
Nota de Configuración: Asegúrese de que el archivo Datos Base de Datos.xlsx o sus equivalentes en .csv se encuentren en la raíz del proyecto para que el motor de carga pueda indexar la información correctamente.
