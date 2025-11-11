#GESTION DEL MAPA
import random
from src.classes import *

# Importar tu sprite visual

from Visual.CONSTANTES import *

# Importar constantes (si las necesitás)
from Visual import CONSTANTES
# CLASE PARA INICIALIZAR EL MAPA
class MapManager:
    #SE VA A INSTANCIAR EN EL game_engine.py
    def __init__(self, width, height,config):
        self.mine_config = config.get("Minas", {})
        self.resources_config = config.get("Recursos",{})
        self.width = width
        self.height = height
        # Atributo para guardar los objetos de las minas
        self.mines = []
        # Atributo para guardar los objetos de los recursos
        self.resources = []
        # atributo para guardar los objetos de los vehiculos
        self.vehiculos = []
        # Creamos una matriz para representar el mapa, inicialmente vacía (con None)
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        print(f"Mapa de {width}x{height} creado.")

        #puntajes
        self.puntaje_j1 = 0
        self.puntaje_j2 = 0

    def get_recursos(self):
        """Devuelve la lista de objetos de recursos."""
        return self.resources

    def __str__(self):
        """
        Devuelve una representación en string detallada del mapa.
        O: Recurso
        C: Mina Circular
        T1: Mina Lineal Horizontal
        T2: Mina Lineal Vertical
        G1: Mina Móvil
        .: Vacío
        """
        map_lines = []
        for row in self.grid:
            line_parts = []
            for cell in row:
                if isinstance(cell, Recurso):
                    line_parts.append("R")
                # revisamos la clase más específica (hija) primero.
                elif isinstance(cell, MinaMovil):
                    line_parts.append("G1")
                elif isinstance(cell, MinaLineal):
                    # Revisamos el atributo 'orientation' para diferenciar T1 de T2.
                    if cell.orientation == 'Horizontal':
                        line_parts.append("T1")
                    else: # 'Vertical'
                        line_parts.append("T2")
                # Revisamos la clase padre después de la hija.
                elif isinstance(cell, MinaCircular):
                    line_parts.append("C")
                else: # La celda está vacía (None)
                    line_parts.append("-")
            map_lines.append(" ".join(line_parts))
        
        # Une todas las líneas para formar el mapa completo
        return "\n".join(map_lines)

    def _colocar_recursos(self,grupo_items):
        """
        Coloca todos los recursos del JSON en el mapa, asegurándose de que
        no se generen dentro del área de efecto de ninguna mina.
        """
        # Itera sobre cada tipo de recurso definido en el JSON
        resources = self.resources_config
        for resource_type, stats in resources.items():
            
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
                        if self.grid[y][x] is None:
                            posicion_segura_encontrada = True
                
                # 5. Cuando el bucle 'while' termina, tenemos una posición segura garantizada
                # Instanciamos el recurso y lo colocamos en el mapa
                pos_candidata = (x, y)
                imagen = pygame.image.load(f"imagenes/{resource_type}.png")
                imagen_escalada = pygame.transform.smoothscale(
                    imagen,
                    (int(CONSTANTES.CELDA_ANCHO), int(CONSTANTES.CELDA_ALTO))
                )
                recurso = Recurso(resource_type, resources, pos_candidata, imagen_escalada)
                self.grid[y][x] = recurso
                self.resources.append(recurso)
                
                  
                # Y añadimos ESE MISMO objeto al grupo de sprites
                grupo_items.add(recurso)
                
        print(f"Se han distribuido los recursos de forma segura.")

    def colocar_minas(self,grupo_items):
        """
        Coloca las minas del JSON en el mapa, asegurándose de que
        la posición de su centro esté libre antes de crearla.
        """
        minas_config = self.mine_config.items()

        MARGEN_LATERAL_BASES = 10 
        MARGEN_SUPERIOR_INFERIOR = 5
        
        # Calcula la zona segura para generar minas
        x_min_seguro = MARGEN_LATERAL_BASES
        x_max_seguro = self.width - 1 - MARGEN_LATERAL_BASES
        
        y_min_seguro = MARGEN_SUPERIOR_INFERIOR
        y_max_seguro = self.height - 1 - MARGEN_SUPERIOR_INFERIOR

        imagen = None
        for mina_nombre, valores in minas_config:
            class_name = valores.get("class")
            
            # Inicia el bucle para encontrar una posición válida
            posicion_encontrada = False
            while not posicion_encontrada:
                
                # 1. Genera una posición candidata DENTRO de la zona segura
                x_candidato = random.randint(x_min_seguro, x_max_seguro)
                y_candidato = random.randint(y_min_seguro, y_max_seguro)
                pos = (x_candidato, y_candidato)

                # 2. Chequea si la posición está libre usando la función posicion_libre
                if self.posicion_libre(pos[0], pos[1]):
                    
                    new_mine = None
                    imagen = None
                    # 3. Usa if/elif para crear la mina correcta
                    if class_name == "MinaCircular":
                        imagen = pygame.image.load("imagenes/minaCircular.png")
                        radius = valores.get("radius")
                        # Escalar imagen
                        imagen_escalada = pygame.transform.smoothscale(imagen, (int(CONSTANTES.CELDA_ANCHO), int(CONSTANTES.CELDA_ALTO)))
                        new_mine = MinaCircular(position=pos, radius=radius, imagen=imagen_escalada)
                        
                        
                    elif class_name == "MinaLineal":
                        imagen = pygame.image.load("imagenes/minaLineal.png")
                        length = valores.get("length")
                        orientation = valores.get("orientation")
                        imagen_escalada = pygame.transform.smoothscale(imagen, (int(CONSTANTES.CELDA_ANCHO), int(CONSTANTES.CELDA_ALTO)))
                        new_mine = MinaLineal(position=pos, length=length, orientation=orientation, imagen=imagen_escalada)
                        
                    elif class_name == "MinaMovil":
                        imagen = pygame.image.load("imagenes/minaMovil.png")
                        radius = valores.get("radius")
                        cycle = valores.get("cycle_duration")
                        imagen_escalada = pygame.transform.smoothscale(imagen, (int(CONSTANTES.CELDA_ANCHO), int(CONSTANTES.CELDA_ALTO)))
                        new_mine = MinaMovil(position=pos, radius=radius, cycle_duration=cycle, imagen=imagen_escalada)
                        
                        
                    # 4. Si se creó la mina, la colocamos en la grilla
                    if new_mine:
                        self.grid[pos[1]][pos[0]] = new_mine
                        posicion_encontrada = True 
                        self.mines.append(new_mine)
                        grupo_items.add(new_mine)

    def posicion_libre(self, x, y):
        """Devuelve True si la celda (x, y) está vacía (None)."""
        return self.grid[y][x] is None        
       
    def generar_mapa_aleatorio(self, grupo_items):
        """
        Limpia completamente el mapa y distribuye de nuevo todos los
        recursos y minas de forma aleatoria.
        """
        # 1. Limpiar las listas de objetos existentes.
        self.mines.clear()
        self.resources.clear()

        # 2. Reiniciar la matriz (grid) a su estado inicial (todo None).
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

        
        self.colocar_minas(grupo_items)

        
        self._colocar_recursos(grupo_items)       
  
    def generar_mapa_pathfinding(self, obstaculos_temporales=None):
        """
        Crea y devuelve un mapa de pathfinding
        basada en el radio de acción de las minas estaticas Y obstáculos temporales.

        Devuelve:
            list[list[int]]: Una grilla donde:
                - 0: La celda es segura (caminable).
                - 1: La celda es un obstáculo (mina estática o vehículo bloqueador).
        """
        
        # 1. Creamos un mapa nuevo, asumiendo que todo es caminable (0)
        mapa_pf = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # 2. Iteramos por CADA celda (x, y) del mapa
        for y in range(self.height):
            for x in range(self.width):
                pos_actual = (x, y)
                
                # 3. Comprobamos esta celda contra la lista de minas estáticas
                for mina in self.mines:
                    if isinstance(mina, MinaMovil):
                        continue 
                    if mina.is_inside_area(pos_actual):
                        mapa_pf[y][x] = 1
                        break 
        
        if obstaculos_temporales:
            for pos_xy in obstaculos_temporales:
                # La posición viene como (x, y)
                x_obst, y_obst = int(pos_xy[0]), int(pos_xy[1])
                # Validar que esté en el mapa
                if 0 <= y_obst < self.height and 0 <= x_obst < self.width:
                    mapa_pf[y_obst][x_obst] = 1 # Marcar como obstáculo

        # 5. Devolvemos el mapa de 0s y 1s
        return mapa_pf
    
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
if __name__ == "__main__": 
    import pygame
    from src.classes import load_resource_config

    RUTA_CONFIG = "config/default_config.json"
    config = load_resource_config(RUTA_CONFIG)

    mapa = MapManager(50,50,config)

    listaRecursos = mapa.get_recursos()

    print(len(listaRecursos))
    grupo_items_debug = pygame.sprite.Group()

    mapa.colocar_minas(grupo_items_debug)
    mapa._colocar_recursos(grupo_items_debug)
    print(len(listaRecursos))
    recurso = listaRecursos[0]
    print(recurso.type)


