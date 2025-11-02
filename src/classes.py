#CLASES DE VEHICULOS
import math
import pygame

class Vehiculo:
    """
    Clase base que representa a cualquier vehículo en el simulador.
    Contiene todos los atributos y métodos comunes.
    """ 
    #CONSTRUCTOR DE LA CLASE
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple):
        # --- Atributos de Identificación ---
        self.id = id
        self.jugador_id = jugador_id
        
        # --- Atributos de Posición y Estado ---
        self.posicion = pygame.math.Vector2(pos_inicial)
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

    def mover(self):
        """
        Lógica de movimiento del vehículo para seguir un camino.
        (A implementar)
        """
        if self.camino_actual:
            print(f"{self.id} se está moviendo a {self.camino_actual[0]}...")
        pass

    def recolectar(self, recurso):
        """
        Añade un recurso a la carga si es del tipo permitido.
        (A implementar)
        """
        print(f"{self.id} ha recolectado {recurso}.")
        self.carga_actual.append(recurso)
        self.viajes_realizados += 1

    def __repr__(self):
        """
        Representación en string del objeto para facilitar la depuración.
        """
        return f"<{self.jugador_id}-{self.tipo} ({self.id}) en {self.posicion}>"


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