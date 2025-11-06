import mariadb
import csv
import json
import os
from tabulate import tabulate

# Carpeta y archivos
carpeta_csv = "csv_salida"
archivo_json = "datos_comercio_modificado.json"
tablas_dict = {}

# 1. Preguntar al usuario cómo quiere cargar los datos
usar_json = False
if os.path.exists(archivo_json):
    print("🗂 Se encontró un archivo con datos modificados.")
    eleccion = input("¿Querés cargar los datos modificados desde JSON? (s/n): ").lower()
    usar_json = eleccion == "s"

# 2. Cargar los datos según la elección
if usar_json:
    print("🔄 Cargando datos modificados desde JSON...")
    with open(archivo_json, encoding="utf-8") as f:
        tablas_dict = json.load(f)
    nombres_tablas = list(tablas_dict.keys())

else:
    print("🧠 Cargando datos desde la base de datos...")
    conexion = mariadb.connect(
        host="localhost",
        user="root",
        password="",
        database="comercio",
        port=3306
    )
    cursor = conexion.cursor()

    cursor.execute("SHOW TABLES")
    nombres_tablas = [t[0] for t in cursor.fetchall()]
    os.makedirs(carpeta_csv, exist_ok=True)

    for tabla in nombres_tablas:
        cursor.execute(f"SELECT * FROM {tabla}")
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()

        # Guardar CSV original
        with open(f"{carpeta_csv}/{tabla}.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columnas)
            writer.writerows(filas)

        # Cargar como lista de diccionarios
        registros = [dict(zip(columnas, fila)) for fila in filas]
        tablas_dict[tabla] = registros

    cursor.close()
    conexion.close()

# 3. Funciones de interacción
def mostrar_menu():
    print("\n📋 Tablas disponibles:")
    for i, tabla in enumerate(nombres_tablas):
        print(f"{i+1}. {tabla}")
    print("0. Salir")

def mostrar_registros(tabla):
    registros = tablas_dict[tabla]
    if not registros:
        print(f"\n📄 La tabla '{tabla}' está vacía.")
        return
    print(f"\n📄 Registros en '{tabla}':")
    tabla_formateada = []
    for i, fila in enumerate(registros, start=1):
        fila_con_id = {"#": i}
        fila_con_id.update(fila)
        tabla_formateada.append(fila_con_id)
    print(tabulate(tabla_formateada, headers="keys", tablefmt="fancy_grid", stralign="center"))

def agregar_registro(tabla):
    nuevo = {}
    claves = tablas_dict[tabla][0].keys()
    print("🆕 Ingresá los valores:")
    for clave in claves:
        nuevo[clave] = input(f"{clave}: ")
    tablas_dict[tabla].append(nuevo)
    print("✅ Registro agregado.")

def modificar_registro(tabla):
    mostrar_registros(tabla)
    idx = int(input("🔧 Número de registro a modificar: ")) - 1
    if 0 <= idx < len(tablas_dict[tabla]):
        registro = tablas_dict[tabla][idx]
        print("✏️ Ingresá nuevos valores (ENTER para dejar igual):")
        for clave in registro:
            nuevo_valor = input(f"{clave} [{registro[clave]}]: ")
            if nuevo_valor:
                registro[clave] = nuevo_valor
        print("✅ Registro modificado.")
    else:
        print("❌ Índice inválido.")

def eliminar_registro(tabla):
    mostrar_registros(tabla)
    idx = int(input("🗑 Número de registro a eliminar: ")) - 1
    if 0 <= idx < len(tablas_dict[tabla]):
        tablas_dict[tabla].pop(idx)
        print("✅ Registro eliminado.")
    else:
        print("❌ Índice inválido.")

# 4. Menú principal
while True:
    mostrar_menu()
    opcion = input("\n👉 Elegí una tabla (número): ")
    if opcion == "0":
        break
    try:
        tabla = nombres_tablas[int(opcion)-1]
    except:
        print("❌ Opción inválida.")
        continue

    while True:
        print(f"\n📂 Tabla: {tabla}")
        print("1. Ver registros")
        print("2. Agregar registro")
        print("3. Modificar registro")
        print("4. Eliminar registro")
        print("0. Volver")
        accion = input("👉 Elegí una acción: ")

        if accion == "1":
            mostrar_registros(tabla)
        elif accion == "2":
            agregar_registro(tabla)
        elif accion == "3":
            modificar_registro(tabla)
        elif accion == "4":
            eliminar_registro(tabla)
        elif accion == "0":
            break
        else:
            print("❌ Acción inválida.")

# 5. Guardar cambios en CSV y JSON
for tabla, registros in tablas_dict.items():
    campos = set()
    for fila in registros:
        campos.update(fila.keys())
    campos = sorted(campos)
    with open(f"{carpeta_csv}/{tabla}_modificado.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)

with open(archivo_json, "w", encoding="utf-8") as f:
    json.dump(tablas_dict, f, indent=4, ensure_ascii=False)

print("\n✅ Cambios guardados. Proyecto 1 finalizado.")
