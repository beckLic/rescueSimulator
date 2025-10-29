#ALGORITMOS DE NAVEGACION
import heapq

class Nodo:
    def __init__(self, posicion=None, padre=None):
        self.posicion = posicion
        self.padre = padre
        self.g = 0
        self.h = 0
        self.f = 0
    
    def __eq__(self, otro):
        return self.posicion == otro.posicion
    
    def __lt__(self, otro):
        return self.f < otro.f


# Definimos un costo "infinito" para los obstáculos
COSTO_OBSTACULO = 100000 

def a_star(mapa_costos, inicio, fin):
    """
    Encuentra el camino de menor costo desde un inicio a un fin usando A*.
    :param mapa_costos: Una lista de listas (cuadrícula 2D) donde cada celda
                         tiene un costo de movimiento (ej. 1, 5, 50).
                         Los obstáculos deben tener un costo muy alto (ej. COSTO_OBSTACULO).
    :param inicio: Una tupla (fila, columna) para el punto de partida.
    :param fin: Una tupla (fila, columna) para el punto de destino.
    :return: Una lista de tuplas que representa el camino, o None si no se encuentra.
    """
    
    # 1. Inicialización
    nodo_inicio = Nodo(inicio, None)
    nodo_fin = Nodo(fin, None)
    
    lista_abierta = []
    lista_cerrada = set() 
    
    heapq.heappush(lista_abierta, nodo_inicio)
    
    # 2. Bucle principal
    while lista_abierta:
        
        nodo_actual = heapq.heappop(lista_abierta)
        lista_cerrada.add(nodo_actual.posicion)
        
        # 3. Comprobación de destino
        if nodo_actual == nodo_fin:
            camino = []
            actual = nodo_actual
            while actual is not None:
                camino.append(actual.posicion)
                actual = actual.padre
            return camino[::-1]
            
        # 4. Generación de vecinos
        (fila, col) = nodo_actual.posicion
        vecinos = [(fila-1, col), (fila+1, col), (fila, col-1), (fila, col+1)]
        
        for siguiente_pos in vecinos:
            (vecino_fila, vecino_col) = siguiente_pos
            
            # Asegurarse de que el vecino está dentro de los límites
            if not (0 <= vecino_fila < len(mapa_costos) and 0 <= vecino_col < len(mapa_costos[0])):
                continue
            
            # --- !!! CAMBIO CLAVE 1 !!! ---
            # Obtener el costo de moverse A ESA celda
            costo_movimiento = mapa_costos[vecino_fila][vecino_col]
            
            # Asegurarse de que el vecino es caminable (costo no es obstáculo)
            if costo_movimiento >= COSTO_OBSTACULO:
                continue
            
            # Si el vecino ya está en la lista cerrada, lo ignoramos
            if siguiente_pos in lista_cerrada:
                continue
            
            # Creamos el nodo vecino
            vecino = Nodo(siguiente_pos, nodo_actual)
            
            # --- !!! CAMBIO CLAVE 2 !!! ---
            # Calculamos el costo g: costo del padre + costo de moverse a esta nueva celda
            vecino.g = nodo_actual.g + costo_movimiento
            
            # Heurística: Distancia Manhattan
            # (La heurística NO debe multiplicarse por el costo, debe ser la distancia "pura")
            vecino.h = abs(vecino.posicion[0] - nodo_fin.posicion[0]) + abs(vecino.posicion[1] - nodo_fin.posicion[1])
            vecino.f = vecino.g + vecino.h
            
            # Si el vecino ya está en la lista abierta con un costo g mayor, lo ignoramos
            # (Este chequeo es importante para encontrar el camino óptimo)
            en_lista_abierta = False
            for n in lista_abierta:
                if n == vecino:
                    en_lista_abierta = True
                    if vecino.g < n.g:
                        n.g = vecino.g # Actualizamos el costo g del nodo en la lista abierta
                        n.f = vecino.f
                        n.padre = nodo_actual # Actualizamos el padre
                    break # Salimos del bucle
            
            if not en_lista_abierta:
                # Añadimos el vecino al heap de prioridad
                heapq.heappush(lista_abierta, vecino)
            
    return None

# --- Ejemplo de Uso con Costos ---
if __name__ == '__main__':
    # Costo 1 = normal
    # Costo 5 = "lodo" o "terreno difícil" (A* lo evitará si puede)
    # COSTO_OBSTACULO = pared
    
    mapa_costos = [
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 5, 5, 5, 5, 5, 5, 1, 1], # Una fila de "lodo"
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, COSTO_OBSTACULO, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    inicio = (0, 0)
    fin = (0, 8)

    camino = a_star(mapa_costos, inicio, fin)

    if camino:
        print(f"Se encontró un camino de {inicio} a {fin}:")
        print(camino)
        # Verás que el camino ahora rodea la fila 5 para evitar el costo '5'
    else:
        print(f"No se pudo encontrar un camino de {inicio} a {fin}.")