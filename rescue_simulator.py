#ARCHIVO PRINCIPAL 
import runpy
import os
import sys

try:
    #Arreglar el Directorio de Trabajo (para las imágenes y configs)
    #Obtiene la ruta absoluta de la carpeta donde está ESTE script (la raíz del proyecto)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Le dice a Python: "Ejecuta todo desde esta carpeta"
    os.chdir(script_dir) 

    # Arreglar la ruta de importación (para 'src' y 'Visual')
    # Añade la raíz del proyecto al path de Python 
    sys.path.insert(0, script_dir)

    # 3. Ejecutar el módulo
    runpy.run_module('Visual.main', run_name='__main__')

except Exception as e:
    print(f"Ocurrió un error al ejecutar el simulador:")
    print(e)
    input("Presiona Enter para salir...") 