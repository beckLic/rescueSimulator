#GESTION DEL MAPA
import random

# CLASE PARA INICIALIZAR EL MAPA
class MapManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Creamos una matriz para representar el mapa, inicialmente vacía (con None)
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        print(f"Mapa de {width}x{height} creado.")

    def __str__(self):
        # Un método para imprimir el mapa en la consola(para debugear)
        map_str = ""
        for row in self.grid:
            for cell in row:
                if cell is None:
                    map_str += ". " # Espacio vacío
                else:
                    map_str += "X " # Hay algo aquí
            map_str += "\n"
        return map_str
    
# ... (init y otros métodos)

    def _colocar_entidades(self, cantidad, tipo_entidad):
        """Función auxiliar para colocar 'cantidad' de un 'tipo_entidad' en el mapa."""
        for _ in range(cantidad):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                
                # Si la celda está vacía, colocamos la entidad y salimos del bucle.
                if self.grid[y][x] is None:
                    # Cuando las clases estén listas, crearás instancias:
                    # self.grid[y][x] = Recurso(tipo=tipo_entidad, x=x, y=y)
                    
                    # Por ahora, usamos un placeholder (string):
                    self.grid[y][x] = tipo_entidad
                    break

    def generar_mapa_aleatorio(self):
        """
        Limpia el mapa y distribuye todos los recursos y minas de forma aleatoria.
        """
        # Limpiamos el grid
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        # Colocamos recursos
        self._colocar_entidades(10, "persona")
        self._colocar_entidades(10, "alimentos") # La especificación no detalla la cantidad de cada mercancía, asumimos una distribución
        self._colocar_entidades(15, "ropa")
        self._colocar_entidades(10, "medicamentos")
        self._colocar_entidades(15, "armamentos")

        # Colocamos minas
        self._colocar_entidades(1, "mina_01")
        self._colocar_entidades(1, "mina_O2")
        self._colocar_entidades(1, "mina_T1")
        self._colocar_entidades(1, "mina_T2")
        self._colocar_entidades(1, "mina_G1")
        
        print("Recursos y minas distribuidos aleatoriamente.")

# ... (otros métodos)

    def es_posicion_valida(self, x, y):
        """Devuelve True si la coordenada (x, y) está dentro del mapa."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_elemento_en(self, x, y):
        """Devuelve el objeto en la coordenada (x, y) o None si está vacía o fuera de los límites."""
        if not self.es_posicion_valida(x, y):
            return None
        return self.grid[y][x]

    def eliminar_elemento(self, x, y):
        """Elimina un elemento del mapa (por ejemplo, al ser recogido)."""
        if self.es_posicion_valida(x, y):
            elemento = self.grid[y][x]
            self.grid[y][x] = None
            return elemento
        return None

#------------------------------------------------------------------------------------------
#DEBUGGING

def run_debug():
    """
    Esta función ejecuta una serie de pruebas para la clase MapManager.
    """
    print("--- INICIANDO DEBUG DE MAPMANAGER ---")

    # --- 1. Prueba de inicialización ---
    print("\n[Paso 1] Creando una instancia de MapManager (15x10)...")
    try:
        # Usamos un tamaño pequeño para que sea fácil de ver en la consola.
        map_manager = MapManager(width=15, height=10)
        print("-> Éxito: MapManager creado.")
    except Exception as e:
        print(f"-> Error al inicializar MapManager: {e}")
        return # Si falla aquí, no podemos continuar.

    # --- 2. Prueba de generación del mapa ---
    print("\n[Paso 2] Generando mapa con recursos y minas...")
    try:
        map_manager.generar_mapa_aleatorio()
        print("-> Éxito: El método generar_mapa_aleatorio() se ejecutó.")
    except Exception as e:
        print(f"-> Error al generar el mapa: {e}")
        return

    # --- 3. Prueba de visualización (método __str__) ---
    print("\n[Paso 3] Mostrando el mapa generado en la consola:")
    print("-------------------------------------------")
    # Usamos 'X' para entidades y '.' para celdas vacías.
    print(map_manager)
    print("-------------------------------------------")

    # --- 4. Prueba de métodos de consulta ---
    print("\n[Paso 4] Probando los métodos de consulta en 3 coordenadas aleatorias...")
    for i in range(3):
        x, y = random.randint(0, map_manager.width - 1), random.randint(0, map_manager.height - 1)
        elemento = map_manager.get_elemento_en(x, y)
        if elemento:
            print(f"-> Coordenada ({x},{y}): Encontrado '{elemento}'")
        else:
            print(f"-> Coordenada ({x},{y}): Celda vacía (None)")

    # --- 5. Prueba de límites del mapa ---
    print("\n[Paso 5] Verificando los límites del mapa...")
    coord_valida = (5, 5)
    coord_invalida = (20, 20)
    print(f"-> ¿Es ({coord_valida[0]},{coord_valida[1]}) una posición válida? {map_manager.es_posicion_valida(coord_valida[0], coord_valida[1])}")
    print(f"-> ¿Es ({coord_invalida[0]},{coord_invalida[1]}) una posición válida? {map_manager.es_posicion_valida(coord_invalida[0], coord_invalida[1])}")

    # --- 6. Prueba de eliminación de elementos ---
    print("\n[Paso 6] Buscando y eliminando el primer recurso encontrado...")
    elemento_eliminado = None
    coords_eliminadas = None
    for y in range(map_manager.height):
        for x in range(map_manager.width):
            if map_manager.get_elemento_en(x, y) is not None:
                print(f"-> Encontrada una entidad en ({x},{y}). Intentando eliminarla.")
                elemento_eliminado = map_manager.eliminar_elemento(x, y)
                coords_eliminadas = (x, y)
                break
        if elemento_eliminado:
            break
    
    if elemento_eliminado:
        print(f"-> Éxito: Se eliminó '{elemento_eliminado}' de las coordenadas {coords_eliminadas}.")
        print("-> Mapa después de la eliminación:")
        print("-------------------------------------------")
        print(map_manager)
        print("-------------------------------------------")
    else:
        print("-> No se encontró ninguna entidad para eliminar (¿mapa vacío?).")

    print("\n--- DEBUG DE MAPMANAGER FINALIZADO ---")


if __name__ == "__main__":
    # Esta línea asegura que el código de debug solo se ejecute
    # cuando corres este archivo directamente.
    run_debug()