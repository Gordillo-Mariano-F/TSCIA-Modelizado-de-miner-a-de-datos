import streamlit as st
import mariadb
import pandas as pd
import json
import os

# Configuración inicial
st.set_page_config(page_title="Proyecto N°4", layout="wide")
st.title("📊 Proyecto N°4 – Dashboard de Gestión de Datos")

# Archivos y carpetas
carpeta_csv = "csv_salida"
archivo_json = "datos_comercio_modificado.json"
os.makedirs(carpeta_csv, exist_ok=True)

# Estado de sesión
if "tablas_dict" not in st.session_state:
    st.session_state.tablas_dict = {}
if "nombres_tablas" not in st.session_state:
    st.session_state.nombres_tablas = []

# 🔌 Conexión a base de datos
def conectar_db(host, user, password, database, port):
    try:
        conn = mariadb.connect(
            host=host,
            user=user,
            password=password if password else None,
            database=database,
            port=port
        )
        return conn
    except Exception as e:
        st.sidebar.error(f"❌ Error de conexión: {e}")
        return None

# 📥 Cargar datos desde DB
def cargar_desde_db(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tablas = [t[0] for t in cursor.fetchall()]
    tablas_dict = {}
    for tabla in tablas:
        cursor.execute(f"SELECT * FROM {tabla}")
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        df = pd.DataFrame(filas, columns=columnas)
        df.to_csv(f"{carpeta_csv}/{tabla}.csv", index=False, encoding="utf-8")
        tablas_dict[tabla] = df
    cursor.close()
    conn.close()
    return tablas, tablas_dict

# 📤 Guardar datos modificados
def guardar_modificados(tablas_dict):
    for tabla, df in tablas_dict.items():
        df.to_csv(f"{carpeta_csv}/{tabla}_modificado.csv", index=False, encoding="utf-8")
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump({k: df.to_dict(orient="records") for k, df in tablas_dict.items()}, f, indent=4, ensure_ascii=False)

# 🧠 Cargar datos modificados desde JSON
def cargar_desde_json():
    with open(archivo_json, encoding="utf-8") as f:
        data = json.load(f)
    tablas_dict = {k: pd.DataFrame(v) for k, v in data.items()}
    return list(tablas_dict.keys()), tablas_dict

# 📁 Cargar CSV desde carpeta
def cargar_csv_desde_carpeta(ruta):
    archivos = [f for f in os.listdir(ruta) if f.endswith(".csv")]
    tablas_dict = {}
    for archivo in archivos:
        nombre_tabla = archivo.replace(".csv", "")
        df = pd.read_csv(os.path.join(ruta, archivo), encoding="utf-8")
        tablas_dict[nombre_tabla] = df
    return list(tablas_dict.keys()), tablas_dict

# 📤 Opciones en la barra lateral
st.sidebar.header("📥 Cargar datos")

with st.sidebar.expander("🔐 Conectar a la base de datos"):
    host = st.text_input("Host", value="localhost")
    user = st.text_input("Usuario", value="root")
    password = st.text_input("Contraseña", type="password")
    database = st.text_input("Base de datos", value="comercio")
    port = st.number_input("Puerto", value=3306, step=1)
    if st.button("Conectar y cargar"):
        conn = conectar_db(host, user, password, database, port)
        if conn:
            st.session_state.nombres_tablas, st.session_state.tablas_dict = cargar_desde_db(conn)
            st.sidebar.success("✅ Datos cargados desde la base.")

if os.path.exists(archivo_json):
    if st.sidebar.button("📂 Cargar datos modificados desde JSON"):
        st.session_state.nombres_tablas, st.session_state.tablas_dict = cargar_desde_json()
        st.sidebar.success("✅ Datos cargados desde JSON.")

with st.sidebar.expander("📁 Cargar CSV desde carpeta"):
    carpeta = st.text_input("Ruta carpeta CSV", value="csv_salida")
    if st.button("📥 Cargar carpeta CSV"):
        try:
            nombres, tablas = cargar_csv_desde_carpeta(carpeta)
            st.session_state.tablas_dict = tablas
            st.session_state.nombres_tablas = nombres
            st.sidebar.success(f"✅ {len(nombres)} archivos CSV cargados.")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")

with st.sidebar.expander("📄 Cargar archivo CSV individual"):
    archivo_csv = st.file_uploader("Subí un archivo CSV", type=["csv"])
    if archivo_csv:
        nombre_tabla = st.text_input("Nombre para esta tabla", value="tabla_csv")
        df = pd.read_csv(archivo_csv)
        st.session_state.tablas_dict[nombre_tabla] = df
        if nombre_tabla not in st.session_state.nombres_tablas:
            st.session_state.nombres_tablas.append(nombre_tabla)
        st.sidebar.success(f"✅ Archivo '{archivo_csv.name}' cargado como '{nombre_tabla}'.")

st.sidebar.header("📤 Exportar datos")
if st.sidebar.button("Exportar CSV modificados"):
    guardar_modificados(st.session_state.tablas_dict)
    st.sidebar.success("✅ CSV exportados.")

if st.sidebar.button("Exportar JSON completo"):
    guardar_modificados(st.session_state.tablas_dict)
    st.sidebar.success("✅ JSON exportado.")

# 🧭 Interfaz principal organizada en tabs
tab1, tab2 = st.tabs(["📋 Visualización y Edición", "🆕 Crear Tablas"])

with tab1:
    st.subheader("📋 Visualización y Edición de Tablas")
    if st.session_state.nombres_tablas:
        tabla_seleccionada = st.selectbox("Elegí una tabla", st.session_state.nombres_tablas)
        df_original = st.session_state.tablas_dict[tabla_seleccionada]

        st.markdown("### 👁️ Vista previa")
        st.dataframe(df_original, use_container_width=True)

        st.markdown("### ✏️ Editor de registros (modificá y luego guardá)")
        df_editado = st.data_editor(df_original.copy(), num_rows="dynamic", use_container_width=True)

        if st.button("💾 Guardar cambios manualmente"):
            st.session_state.tablas_dict[tabla_seleccionada] = df_editado
            guardar_modificados(st.session_state.tablas_dict)
            st.success("✅ Cambios guardados.")

with tab2:
    st.subheader("🆕 Crear nueva tabla")

    nueva_tabla = st.text_input("Nombre de la nueva tabla")
    st.markdown("### ➕ Definir columnas")

    if "columnas_temp" not in st.session_state:
        st.session_state.columnas_temp = []

    with st.form("form_columnas"):
        col1, col2 = st.columns([2, 2])
        nombre_columna = col1.text_input("Nombre de la columna")
        tipo_columna = col2.selectbox("Tipo de dato", ["Texto", "Número", "Fecha"])
        agregar = st.form_submit_button("Agregar columna")

        if agregar and nombre_columna:
            st.session_state.columnas_temp.append((nombre_columna, tipo_columna))

    if st.session_state.columnas_temp:
        st.markdown("### 🧱 Columnas definidas:")
        for i, (nombre, tipo) in enumerate(st.session_state.columnas_temp):
            st.write(f"{i+1}. {nombre} ({tipo})")

        if st.button("Crear tabla"):
            if nueva_tabla in st.session_state.nombres_tablas:
                st.error(f"❌ La tabla '{nueva_tabla}' ya existe.")
            else:
                columnas = [col[0] for col in st.session_state.columnas_temp]
                df_nueva = pd.DataFrame(columns=columnas)
                st.session_state.tablas_dict[nueva_tabla] = df_nueva
                st.session_state.nombres_tablas.append(nueva_tabla)
                st.session_state.columnas_temp = []
                st.success(f"✅ Tabla '{nueva_tabla}' creada.")

    if nueva_tabla in st.session_state.tablas_dict:
        st.subheader(f"✏️ Editar datos de '{nueva_tabla}'")
        df_nueva = st.session_state.tablas_dict[nueva_tabla]
        edit_df = st.data_editor(df_nueva, num_rows="dynamic", use_container_width=True)
        st.session_state.tablas_dict[nueva_tabla] = edit_df

        if st.button("💾 Guardar cambios en esta tabla nueva"):
            guardar_modificados(st.session_state.tablas_dict)
            st.success("✅ Cambios guardados.")
