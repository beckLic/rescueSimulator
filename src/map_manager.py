#GESTION DEL MAPA
import random
from classes import *

# CLASE PARA INICIALIZAR EL MAPA
class MapManager:
    #SE VA A INSTANCIAR EN EL game_engine.py
    def __init__(self, width, height,config):
        self.mine_config = config.get("Mines", {})
        self.width = width
        self.height = height
        # Atributo para guardar los objetos de las minas
        self.mines = []
        
        # Atributo para guardar los objetos de los recursos
        self.resources = []
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

    # Asumiendo que esta función está dentro de la clase MapManager

def _colocar_recursos(self, resource_config):
    """
    Coloca todos los recursos del JSON en el mapa, asegurándose de que
    no se generen dentro del área de efecto de ninguna mina.
    """
    # Itera sobre cada tipo de recurso definido en el JSON
    for resource_type, stats in resource_config.items():
        
        # Bucle para crear la cantidad ('count') de recursos de este tipo
        for _ in range(stats.get("count", 0)):
            
            # Inicia el bucle para encontrar una posición segura
            posicion_segura_encontrada = False
            while not posicion_segura_encontrada:
                
                # 1. Generamos una posición candidata aleatoria en el mapa
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                pos_candidata = (x, y)

                # 2. Suponemos que la posición es segura por ahora
                es_posicion_segura = True

                # 3. Verifica la posición contra TODAS las minas ya colocadas
                for mina in self.mines: 
                    if mina.is_inside_area(pos_candidata):
                        es_posicion_segura = False # no es segura
                        break # No tiene sentido seguir buscando, probamos otra posición

                # 4. Si después de revisar todas las minas sigue siendo segura
                if es_posicion_segura:
                    # Y además nos aseguramos de que la celda de la grilla esté libre
                    if self.grid[x][y] is None:
                        posicion_segura_encontrada = True
            
            # 5. Cuando el bucle 'while' termina, tenemos una posición segura garantizada
            # Instanciamos el recurso y lo colocamos en la grilla
            recurso = Recurso(resource_type, pos_candidata, resource_config)
            self.grid[x][y] = recurso

    print(f"Se han distribuido los recursos de forma segura.")

    #FUNCION PARA COLOCAR LAS MINAS EN EL MAPA QUE SE EJECUTA PRIMERO QUE LA DE COLOCAR RECURSOS
    def colocar_minas(self):
        """
        Coloca las minas del JSON en el mapa, asegurándose de que
        la posición de su centro esté libre antes de crearla.
        """
        minas_config = self.mine_config.items()

        for mina_nombre, valores in minas_config:
            class_name = valores.get("class")
            
            # Inicia el bucle para encontrar una posición válida
            posicion_encontrada = False
            while not posicion_encontrada:
                
                # 1. Genera una posición candidata UNA SOLA VEZ por intento
                pos = (random.randint(50, self.width - 50), random.randint(50, self.height - 50))

                # 2. Chequea si la posición está libre usando la función posicion_libre
                if self.posicion_libre(pos[0], pos[1]):
                    
                    new_mine = None
                    # 3. Usa if/elif para crear la mina correcta
                    if class_name == "MinaCircular":
                        radius = valores.get("radius")
                        new_mine = MinaCircular(position=pos, radius=radius)
                        
                    elif class_name == "MinaLineal":
                        length = valores.get("length")
                        orientation = valores.get("orientation")
                        # Corregido: Ahora crea una MinaLineal
                        new_mine = MinaLineal(position=pos, length=length, orientation=orientation)
                        
                    elif class_name == "MinaMovil":
                        radius = valores.get("radius")
                        cycle = valores.get("cycle_duration")
                        # Corregido: Ahora crea una MinaMovil
                        new_mine = MinaMovil(position=pos, radius=radius, cycle_duration=cycle)

                    # 4. Si se creó la mina, la colocamos en la grilla
                    if new_mine:
                        self.grid[pos[0]][pos[1]] = new_mine
                        posicion_encontrada = True # Esto hará que el 'while' termine

        

    def posicion_libre(self, x, y):
        """Devuelve True si la celda (x, y) está vacía (None)."""
        return self.grid[x][y] is None        
        


    def generar_mapa_aleatorio(self):
        """
        Limpia el mapa y distribuye todos los recursos y minas de forma aleatoria.
        """

  

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

#-----------------------------------------------------------------------------------------
#DEBUGGING

