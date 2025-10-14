#GESTION DEL MAPA
import random
from classes import *

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

    def _colocar_recursos(self, cantidad, tipo_recurso):
        """Función auxiliar para colocar 'cantidad' de un 'tipo_entidad' en el mapa."""
        #instancio el recurso para poder asignarle la posicion aleatoria despues
        recurso = Recurso(tipo_recurso, RESOURCE_STATS)
        cont = 0
        while cont < (cantidad - 1):
            #coordenadas (x,y) al azar para colocar las entidades
            x = random.randint(0,self.width - 1)
            y = random.randint(0,self.height - 1)

            #checkear que esa coordenada esté libre
            if self.grid[x][y] is None:
                self.grid[x][y] = tipo_recurso
                #seteo la posicion del recurso
                recurso.position = (x,y)
                cont += 1
            

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

