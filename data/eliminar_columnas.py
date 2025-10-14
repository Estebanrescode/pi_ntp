import pandas as pd

df = pd.read_csv('data\MEN_MATRICULA_ESTADISTICA_ES_20250916.csv') 

print("Columnas originales:")
print(df.columns.tolist()) 
columnas_a_eliminar = ["Código de la Institución","IES PADRE","Id_Sector","Id_Caracter","Código del departamento(IES)","Código del Municipio(IES)","Código SNIES delprograma","Id_Nivel","Id_Nivel_Formacion","Id_Metodologia","Id_Area","Id_Nucleo","Código del Departamento(Programa)","Código del Municipio(Programa)"]  # Lista con los nombres exactos (sensible a mayúsculas)
df_limpio = df.drop(columns=columnas_a_eliminar) 

print("\nColumnas después de eliminar:")
print(df_limpio.columns.tolist())  

print("\nPrimeras 5 filas del CSV limpio:")
print(df_limpio.head())

df_limpio.to_csv('datos_limpio.csv', index=False)

print("\n¡Archivo guardado como 'datos_limpio.csv'! Revisa la carpeta.")