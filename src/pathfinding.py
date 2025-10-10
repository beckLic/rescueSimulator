#ALGORITMOS DE NAVEGACION

import heapq

class Nodo:
    """
    Una clase para representar un nodo en la cuadrícula de búsqueda.
    Contiene la posición, el nodo padre (para reconstruir el camino) y los costos A*.
    """
    def __init__(self, posicion=None, padre=None):
        self.posicion = posicion
        self.padre = padre
        
        # Costos del algoritmo A*
        self.g = 0  # Costo desde el inicio hasta el nodo actual
        self.h = 0  # Costo heurístico estimado desde el nodo actual hasta el final
        self.f = 0  # Costo total (g + h)

    def __eq__(self, otro):
        # Compara dos nodos por su posición
        return self.posicion == otro.posicion

    def __lt__(self, otro):
        # Permite que el heap de prioridad ordene los nodos por su costo f
        return self.f < otro.f


def a_star(mapa, inicio, fin):
    """
    Encuentra el camino más corto desde un punto de inicio a un punto final usando A*.
    :param mapa: Una lista de listas (cuadrícula 2D) donde 0 es caminable y 1 es obstáculo.
    :param inicio: Una tupla (fila, columna) para el punto de partida.
    :param fin: Una tupla (fila, columna) para el punto de destino.
    :return: Una lista de tuplas que representa el camino, o None si no se encuentra.
    """
    
    # 1. Inicialización
    nodo_inicio = Nodo(inicio, None)
    nodo_fin = Nodo(fin, None)
    
    lista_abierta = []  # Un heap de prioridad para los nodos por visitar
    lista_cerrada = set() # Un conjunto para las posiciones ya visitadas
    
    # Añadimos el nodo inicial al heap
    heapq.heappush(lista_abierta, nodo_inicio)
    
    # 2. Bucle principal del algoritmo
    while lista_abierta:
        
        # Obtenemos el nodo con el menor costo f del heap
        nodo_actual = heapq.heappop(lista_abierta)
        lista_cerrada.add(nodo_actual.posicion)
        
        # 3. Comprobación de si hemos llegado al destino
        if nodo_actual == nodo_fin:
            camino = []
            actual = nodo_actual
            while actual is not None:
                camino.append(actual.posicion)
                actual = actual.padre
            return camino[::-1]  # Devolvemos el camino invertido (de inicio a fin)
            
        # 4. Generación de nodos vecinos
        (fila, col) = nodo_actual.posicion
        vecinos = [(fila-1, col), (fila+1, col), (fila, col-1), (fila, col+1)]
        
        for siguiente_pos in vecinos:
            (vecino_fila, vecino_col) = siguiente_pos
            
            # Asegurarse de que el vecino está dentro de los límites del mapa
            if not (0 <= vecino_fila < len(mapa) and 0 <= vecino_col < len(mapa[0])):
                continue
            
            # Asegurarse de que el vecino es un terreno caminable
            if mapa[vecino_fila][vecino_col] != 0:
                continue
            
            # Si el vecino ya está en la lista cerrada, lo ignoramos
            if siguiente_pos in lista_cerrada:
                continue
            
            # Creamos el nodo vecino
            vecino = Nodo(siguiente_pos, nodo_actual)
            
            # 5. Cálculo de costos
            vecino.g = nodo_actual.g + 1
            # Heurística: Distancia Manhattan
            vecino.h = abs(vecino.posicion[0] - nodo_fin.posicion[0]) + abs(vecino.posicion[1] - nodo_fin.posicion[1])
            vecino.f = vecino.g + vecino.h
            
            # Si el vecino ya está en la lista abierta con un costo g mayor, lo ignoramos
            if any(n for n in lista_abierta if n == vecino and vecino.g > n.g):
                continue

            # Añadimos el vecino al heap de prioridad
            heapq.heappush(lista_abierta, vecino)
            
    return None # Si el bucle termina, no se encontró un camino

# --- Ejemplo de Uso ---
if __name__ == '__main__':
    # Definimos un mapa: 0 = caminable, 1 = obstáculo (pared)
    mapa = [
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    inicio = (0, 0)
    fin = (9,5 )

    camino = a_star(mapa, inicio, fin)

    if camino:
        print(f"Se encontró un camino de {inicio} a {fin}:")
        print(camino)
    else:
        print(f"No se pudo encontrar un camino de {inicio} a {fin}.")