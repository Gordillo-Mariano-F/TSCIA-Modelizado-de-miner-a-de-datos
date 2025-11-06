# ============================================================
# ANEXO 1: GENERACIÓN DEL ARCHIVO EXCEL SIMULADO
# ============================================================
import pandas as pd

data = {
    "Cliente_ID": range(1, 21),
    "Genero": ["F", "M"] * 10,
    "Edad": [23, 34, 45, 29, 31, 38, 27, 50, 40, 36, 25, 33, 46, 28, 39, 42, 30, 48, 35, 37],
    "Recibio_Promo": ["Sí", "No", "Sí", "Sí", "No", "Sí", "No", "Sí", "No", "Sí",
                      "No", "Sí", "Sí", "No", "No", "Sí", "No", "Sí", "No", "Sí"],
    "Monto_Promocion": [500, 0, 700, 300, 0, 600, 0, 800, 0, 450,
                        0, 620, 710, 0, 0, 480, 0, 750, 0, 520],
    "Recompra": ["Sí", "No", "Sí", "No", "No", "Sí", "No", "Sí", "No", "Sí",
                 "No", "No", "Sí", "No", "No", "Sí", "No", "Sí", "No", "Sí"],
    "Total_Compras": [2, 1, 3, 1, 1, 4, 1, 5, 1, 3, 1, 2, 4, 1, 1, 3, 1, 5, 1, 3],
    "Ingreso_Mensual": [30000, 45000, 40000, 28000, 32000, 50000, 31000, 60000,
                        29000, 37000, 31000, 34000, 47000, 30000, 29000, 43000,
                        33000, 55000, 30000, 41000]
}

df_excel = pd.DataFrame(data)
df_excel.to_excel("Mini_Proyecto_Clientes_Promociones.xlsx", index=False)
print("✅ Archivo Excel generado correctamente.")

# ============================================================
# EJERCICIO 1: COMPRENSIÓN DEL PROBLEMA
# ============================================================
print("\n--- EJERCICIO 1: COMPRENSIÓN DEL PROBLEMA ---")
print("Objetivo: Predecir si los clientes que reciben promociones recompran.")
print("Preguntas guía:")
print("- ¿Recibir una promoción influye en la recompra?")
print("- ¿Importa el monto de la promoción?")
print("- ¿Influye la edad o el ingreso mensual?")

# ============================================================
# EJERCICIO 2: CARGA Y EXPLORACIÓN DEL DATASET
# ============================================================
print("\n--- EJERCICIO 2: CARGA Y EXPLORACIÓN DEL DATASET ---")
df = pd.read_excel("Mini_Proyecto_Clientes_Promociones.xlsx")
print("\nInformación general del dataset:")
print(df.info())
print("\nEstadísticas descriptivas:")
print(df.describe())
print("\nValores nulos por columna:")
print(df.isnull().sum())

# ============================================================
# EJERCICIO 3: TRANSFORMACIÓN Y CODIFICACIÓN
# ============================================================
print("\n--- EJERCICIO 3: TRANSFORMACIÓN Y CODIFICACIÓN ---")
df['Genero'] = df['Genero'].map({'F': 0, 'M': 1})
df['Recibio_Promo'] = df['Recibio_Promo'].map({'Sí': 1, 'No': 0})
df['Recompra'] = df['Recompra'].map({'Sí': 1, 'No': 0})
print("Variables categóricas codificadas correctamente.")

# ============================================================
# EJERCICIO 4: VISUALIZACIÓN DE RELACIONES CLAVE
# ============================================================
print("\n--- EJERCICIO 4: VISUALIZACIÓN DE RELACIONES CLAVE ---")
import seaborn as sns
import matplotlib.pyplot as plt

sns.boxplot(x="Recompra", y="Monto_Promocion", data=df)
plt.title("Recompra según el Monto Promocional")
plt.show()

sns.boxplot(x="Recompra", y="Ingreso_Mensual", data=df)
plt.title("Recompra según el Ingreso Mensual")
plt.show()

sns.histplot(data=df, x="Edad", hue="Genero", multiple="stack")
plt.title("Distribución de Edad por Género")
plt.show()

# ============================================================
# EJERCICIO 5: MODELADO PREDICTIVO
# ============================================================
print("\n--- EJERCICIO 5: MODELADO PREDICTIVO ---")
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

X = df.drop(['Cliente_ID', 'Recompra'], axis=1)
y = df['Recompra']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = DecisionTreeClassifier()
modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)

print("\nMatriz de confusión:")
print(confusion_matrix(y_test, y_pred))
print("\nReporte de clasificación:")
print(classification_report(y_test, y_pred))

# ============================================================
# EJERCICIO 6: TOMA DE DECISIONES BASADA EN VISUALIZACIÓN
# ============================================================
print("\n--- EJERCICIO 6: TOMA DE DECISIONES BASADA EN VISUALIZACIÓN ---")
sns.barplot(x="Edad", y="Recompra", data=df)
plt.title("Probabilidad de Recompra según Edad")
plt.show()

sns.barplot(x="Recibio_Promo", y="Recompra", data=df)
plt.title("Impacto de recibir promoción en la recompra")
plt.show()

# ============================================================
# EJERCICIO 7: DISCUSIÓN E INFORME
# ============================================================
print("\n--- EJERCICIO 7: DISCUSIÓN E INFORME ---")
print("Variables más importantes: Edad, Monto_Promocion, Ingreso_Mensual.")
print("¿Conviene invertir más en promociones para ciertos grupos? Depende del perfil de recompra.")
print("¿Cómo mejorar el modelo? Probar otros algoritmos y más datos.")
print("Visualización más útil: Boxplot y barplot segmentados por recompra.")
