#CLASES DE VEHICULOS
import math
import pygame
import pathfinding
import map_manager
class Vehiculo:
    """
    Clase base que representa a cualquier vehículo en el simulador.
    Contiene todos los atributos y métodos comunes.
    """ 
    #CONSTRUCTOR DE LA CLASE
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple, posicion_base: tuple):
        # --- Atributos de Identificación ---
        self.id = id
        self.jugador_id = jugador_id
        
        # --- Atributos de Posición y Estado ---
        self.posicion = pygame.math.Vector2(pos_inicial)
        self.posicion_base = posicion_base #posicion de su base para volver
        self.objetivo_actual = None
        self.camino_actual = []
        self.velocidad = 3 # Píxeles por fotograma
        self.estado = "inactivo"  # Posibles estados: inactivo, buscando, volviendo
        
        # --- Atributos de Juego ---
        self.carga_actual = []
        self.viajes_realizados = 0
        
        # --- Atributos a definir por las clases hijas ---
        self.tipo = None
        self.tipo_carga_permitida = []
        self.max_viajes = 0


    def recolectar(self, recurso, map_manager):
        """
        Añade un recurso a la carga si es del tipo permitido.
        """
        print(f"{self.id} ha recolectado {recurso}.")
        self.carga_actual.append(recurso)
        self.viajes_realizados += 1

        # 2. Eliminar el recurso del mapa
        pos_recurso_xy = (recurso.position[1], recurso.position[0])
        map_manager.eliminar_elemento(pos_recurso_xy[0], pos_recurso_xy[1])

    def __repr__(self):
        """
        Representación en string del objeto para facilitar la depuración.
        """
        return f"<{self.jugador_id}-{self.tipo} ({self.id}) en {self.posicion}>"


    def _encontrar_mejor_objetivo(self, map_manager):
        """
        Implementa la ESTRATEGIA de priorización.
        Filtra recursos por tipo  y elige el "mejor".
        
        Retorna: un objeto Recurso o None si no hay objetivos válidos.
        """
        recursos_disponibles = map_manager.resources()
        objetivos_validos = []

        # 1. Filtrar por tipo de carga permitida
        for r in recursos_disponibles:
            if r.type in self.tipo_carga_permitida:
                objetivos_validos.append(r)
        
        if not objetivos_validos:
            return None # No hay nada en el mapa que el vehiculo pueda recoger

        # 2. Elegir el "mejor" (Estrategia simple: el más cercano)
        mejor_objetivo = min(
            objetivos_validos, 
            key=lambda r: self.posicion.distance_to(pygame.math.Vector2(r.position))
        )
        
        return mejor_objetivo

    def _calcular_camino(self, map_manager, destino_yx):
        """
        Función helper para calcular la ruta A* y manejar errores.
        Retorna el camino encontrado o None.
        """
        try:
            mapa_pf = map_manager.generar_mapa_pathfinding()
            pos_inicio_yx = (int(self.posicion.y), int(self.posicion.x))
            
            camino_encontrado = pathfinding.a_star(mapa_pf, pos_inicio_yx, destino_yx)
            
            if camino_encontrado:
                camino_encontrado.pop(0) # Quitamos el primer paso por ser posicion actual
                return camino_encontrado
            else:
                return None
        except Exception as e:
            print(f"Error calculando A* para {self.id}: {e}")
            return None

    def _evaluar_siguiente_paso(self, map_manager):
        """
        Revisa si el siguiente paso en el camino es peligroso (minas G1, vehículos).
        Retorna: (siguiente_pos_yx, peligro_detectado)
        """
        if not self.camino_actual:
            return None, True # No hay camino, se considera "peligro" para no moverse

        siguiente_pos_yx = self.camino_actual[0]
        siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0])

        peligro_detectado = False
        
        # Revisar contra minas móviles
        for mina in map_manager.mines:
            if isinstance(mina, MinaMovil):
                if mina.is_active and mina.is_inside_area(siguiente_pos_xy):
                    peligro_detectado = True
                    print(f"{self.id} FRENANDO: ¡Mina G1 activa en {siguiente_pos_xy}!")
                    break 

        # implementar colision con vehiculos acá
            
        return siguiente_pos_yx, peligro_detectado


    def update(self, map_manager, game_time):
        """
        La lógica principal del vehículo en cada frame, organizada como una Máquina de Estados.
        """
        
        # =======================================================
        # ESTADO 1: INACTIVO (Buscando qué hacer)
        # =======================================================
        if self.estado == "inactivo":
            # Paso 1: Decidir el Objetivo
            self.objetivo_actual = self._encontrar_mejor_objetivo(map_manager)

            if self.objetivo_actual:
                print(f"{self.id} decidió ir a por {self.objetivo_actual.type} en {self.objetivo_actual.position}")
                
                # Paso 2: Calcular la Ruta hacia el objetivo
                self.camino_actual = self._calcular_camino(map_manager, self.objetivo_actual.position)
                
                # Paso 3: Transición de Estado
                if self.camino_actual:
                    self.estado = "buscando" # transicion de estado
                else:
                    # El objetivo es inaccesible, lo olvidamos
                    print(f"{self.id} no encontró camino a {self.objetivo_actual.position}")
                    self.objetivo_actual = None
                    #Se queda 'inactivo' para intentarlo de nuevo en el próximo frame
            
            # else: No hay objetivos en el mapa. El vehículo se queda 'inactivo'.

        # =======================================================
        # ESTADO 2: BUSCANDO (Yendo hacia un recurso)
        # =======================================================
        elif self.estado == "buscando":
            
            if not self.camino_actual:
                # Si el camino desaparece
                print(f"{self.id} perdió su camino, volviendo a inactivo.")
                self.estado = "inactivo"
                return

            # Revisar peligros en el siguiente paso
            siguiente_pos_yx, peligro_detectado = self._evaluar_siguiente_paso(map_manager)
            
            if not peligro_detectado:
                # Es seguro moverse
                siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0])
                self.posicion = pygame.math.Vector2(siguiente_pos_xy)
                self.camino_actual.pop(0) # Del vehiculo avanza un paso en su camino
                
                # --- LÓGICA DE LLEGADA Y RECOLECCIÓN ---
                if not self.camino_actual:
                    print(f"{self.id} llegó al recurso {self.objetivo_actual.type}.")
                    
                    # 1. Recolectar
                    self.recolectar(self.objetivo_actual)
                    self.objetivo_actual = None
                    
                    # 3. DECIDIR QUÉ HACER AHORA
                    if self.viajes_realizados >= self.max_viajes:
                        print(f"{self.id} alcanzó su max_viajes. Volviendo a base.")
                        self.estado = "volviendo" # transicion de estado
                    else:
                        print(f"{self.id} puede seguir recolectando. Buscando nuevo objetivo.")
                        self.estado = "inactivo" # transicion de estado
            
            # else: Peligro detectado. El vehículo no se mueve (no hace pop)
            # y lo re-evaluará en el próximo frame.

        # =======================================================
        # ESTADO 3: VOLVIENDO (Yendo hacia la base)
        # =======================================================
        elif self.estado == "volviendo":
            
            # Paso 1: Calcular el camino a la base (SOLO SI NO LO TIENE)
            if not self.camino_actual:
                print(f"{self.id} está calculando la ruta de regreso a la base.")
                
                # Ojo: A* necesita (y,x) para el destino
                pos_base_yx = (int(self.pos_base[1]), int(self.pos_base[0]))
                self.camino_actual = self._calcular_camino(map_manager, pos_base_yx)
                
                if not self.camino_actual:
                    print(f"{self.id} ¡NO PUEDE ENCONTRAR CAMINO A LA BASE! ATASCADO.")
                    # El vehículo se quedará en este estado, intentando recalcular
                    # cada frame hasta que pueda (p.ej. si una mina G1 se mueve)
                    return

            # Paso 2: Moverse (con la misma lógica de evasión)
            siguiente_pos_yx, peligro_detectado = self._evaluar_siguiente_paso(map_manager)
            
            if not peligro_detectado:
                siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0])
                self.posicion = pygame.math.Vector2(siguiente_pos_xy)
                self.camino_actual.pop(0)

                # --- LÓGICA DE LLEGADA A LA BASE ---
                if not self.camino_actual:
                    print(f"{self.id} llegó a la base y entregó la carga.")
                    
                    # 1. Registrar puntaje (esto se haría en el GameEngine)
                    # game_engine.registrar_entrega(self.jugador_id, self.carga_actual)
                    
                    # 2. Resetear el vehículo
                    self.carga_actual.clear()
                    self.viajes_realizados = 0
                    
                    # 3. Transición de estado
                    self.estado = "inactivo" # transicion de estado
            
            # else: Peligro detectado, espera.
#-----------------------------------------------------------------------------------------------------------   
class Jeep(Vehiculo):
    """
    Representa un vehículo tipo Jeep.
    - Puede recoger todo tipo de carga.
    - Puede realizar hasta 2 viajes antes de volver a base.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple):
        super().__init__(id, jugador_id, pos_inicial)
        self.tipo = "jeep"
        self.max_viajes = 2  # 
        self.tipo_carga_permitida = ["Persona", "Alimentos", "Ropa", "Medicamentos", "Armamentos"]  # 

#------------------------------------------------------------------------------------------------------------
class Moto(Vehiculo):
    """
    Representa un vehículo tipo Moto.
    - Solo puede recoger Personas.
    - Debe volver a la base después de cada viaje.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple):
        super().__init__(id, jugador_id, pos_inicial)
        self.tipo = "moto"
        self.max_viajes = 1  # 
        self.tipo_carga_permitida = ["Persona"]  # 
#-------------------------------------------------------------------------------------------------------------
class Camion(Vehiculo):
    """
    Representa un vehículo tipo Camión.
    - Puede recoger todo tipo de carga.
    - Puede realizar hasta 3 viajes antes de volver a base.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple):
        super().__init__(id, jugador_id, pos_inicial)
        self.tipo = "camion"
        self.max_viajes = 3  # 
        self.tipo_carga_permitida = ["Persona", "Alimentos", "Ropa", "Medicamentos", "Armamentos"] 
#-------------------------------------------------------------------------------------------------------------
class Auto(Vehiculo):
    """
    Representa un vehículo tipo Auto.
    - Puede recoger Personas y cargas.
    - Debe volver a la base después de cada viaje.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple):
        super().__init__(id, jugador_id, pos_inicial)
        self.tipo = "auto"
        self.max_viajes = 1   
        self.tipo_carga_permitida = ["Persona", "Alimentos", "Ropa", "Medicamentos", "Armamentos"]   
#---------------------------------------------------------------------------------------------------------
#CLASES DE RECURSOS

import json

#FUNCION PARA TRAER LOS DATOS DE LOS RECURSOS DEL JSON
def load_resource_config(filepath: str) -> dict:

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración en {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo JSON en {filepath} está mal formateado.")
        return {}


#SE CARGA LA CONFIGURACION UNA VEZ CUANDO EMPIEZA EL SIMULADOR
RESOURCE_STATS = load_resource_config('config/default_config.json')
#-------------------------------------------------------------------------------------------------------------
class Recurso:
    #PARA INCIALIZAR UN RECURSO SE PASA COMO PARAMETRO EL TIPO DE RECURSO, EL DICCIONARIO Y LA POSICION
    def __init__(self, resource_type: str, stats_config: dict, position: tuple):
        if resource_type not in stats_config:
            raise ValueError(f"El tipo de recurso '{resource_type}' no es válido.")
        
        stats = stats_config[resource_type]
        
        self.type = resource_type
        self.score = stats['score']
        self.position = position
#-------------------------------------------------------------------------------------------------------
#CLASE DE MINAS

class Mina:
    def __init__(self, position: tuple):
        self.position = position
#-------------------------------------------------------------------------------------------------------------
class MinaCircular(Mina):
    """
    Representa una mina estática con un área de efecto circular.
    Corresponde a las minas O1 y O2 del proyecto.
    """
    #PARA INCIALIZARLA LE PASAMOS COMO PARAMETRO LA POSICION Y SU RADIO
    def __init__(self, position: tuple, radius: int):
        super().__init__(position)
        self.radius = radius

    def is_inside_area(self, point: tuple) -> bool:
        # Calcula la distancia euclidiana entre el punto y el centro de la mina
        distance = math.sqrt((point[0] - self.position[0])**2 + (point[1] - self.position[1])**2)
        # Devuelve True si la distancia es menor o igual al radio
        if distance <= self.radius:
            return True
        else:
            return False
#-------------------------------------------------------------------------------------------------------------
class MinaLineal(Mina):
    """
    Representa una mina estática con un área de efecto lineal.
    Corresponde a las minas T1 y T2 del proyecto.
    """
    #PARA INCIALIZARLA LE PASAMOS COMO PARAMETRO LA POSICION, LONGITUD DE SU RADIO Y SU ORIENTACION
    def __init__(self, position: tuple, length: int, orientation: str):
        super().__init__(position)
        if orientation not in ['Horizontal', 'Vertical']:
            raise ValueError("La orientación debe ser 'Horizontal' o 'Vertical'.")
        self.length = length
        self.orientation = orientation

    def is_inside_area(self, point: tuple) -> bool:
        px, py = point #coordenadas del vehiculo
        mx, my = self.position #coordenadas del centro de la mina
        half_len = self.length / 2 #segmento para dividir el radio en dos partes iguales para los costados de la mina

        if self.orientation == 'Horizontal':
            y_match = abs(py - my) < 1 # Para una línea horizontal, la coordenada 'y' debe ser la misma,
            x_in_range = (mx - half_len) <= px <= (mx + half_len) # y la 'x' debe estar dentro del segmento de la línea.
            #OPERADOR AND PARA RETURNAR TRUE O FALSE
            return y_match and x_in_range
        else: # 'vertical'
            x_match = abs(px - mx) < 1 # Para una línea vertical, la coordenada 'x' debe ser la misma,
            y_in_range = (my - half_len) <= py <= (my + half_len) # y la 'y' debe estar dentro del segmento de la línea.
            #OPERADOR AND PARA RETURNAR TRUE O FALSE
            return x_match and y_in_range
#-------------------------------------------------------------------------------------------------------------
class MinaMovil(MinaCircular):
    """
    Representa la Mina G1, que es circular pero aparece y desaparece.
    Hereda de CircularMine para reutilizar la lógica de su área de efecto
    """
    #INICIALIZAMOS CON LOS PARAMETROS DE POSICION, RADIO Y TIEMPO DE APARICION
    def __init__(self, position: tuple, radius: int, cycle_duration: int = 5):
        super().__init__(position, radius)
        self.cycle_duration = cycle_duration
        self.is_active = True

    def update(self, game_time: int):
        """
        Actualiza el estado de la mina (activa/inactiva) basado en el
        tiempo de la simulación, como se especifica en el proyecto.
        """
        # Cada 'cycle_duration' instancias de tiempo, el estado cambia.
        if game_time > 0 and game_time % self.cycle_duration == 0:
            self.is_active = not self.is_active
            # print(f"Mina móvil en {self.position} ahora está {'activa' if self.is_active else 'inactiva'}")

    def is_inside_area(self, point: tuple) -> bool:
        # La mina solo puede causar daño si su estado es activo.
        if not self.is_active:
            return False
        
        # Si está activa, utiliza la misma lógica de su clase padre (CircularMine).
        return super().is_inside_area(point)
    

