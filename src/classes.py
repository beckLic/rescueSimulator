#CLASES DE VEHICULOS

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
        self.tipo_carga_permitida = ["persona", "alimentos", "ropa", "medicamentos", "armamentos"]  # 


class Moto(Vehiculo):
    """
    Representa un vehículo tipo Moto.
    - Solo puede recoger personas.
    - Debe volver a la base después de cada viaje.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple):
        super().__init__(id, jugador_id, pos_inicial)
        self.tipo = "moto"
        self.max_viajes = 1  # 
        self.tipo_carga_permitida = ["persona"]  # 


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
        self.tipo_carga_permitida = ["persona", "alimentos", "ropa", "medicamentos", "armamentos"] 


class Auto(Vehiculo):
    """
    Representa un vehículo tipo Auto.
    - Puede recoger personas y cargas.
    - Debe volver a la base después de cada viaje.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple):
        super().__init__(id, jugador_id, pos_inicial)
        self.tipo = "auto"
        self.max_viajes = 1   
        self.tipo_carga_permitida = ["persona", "alimentos", "ropa", "medicamentos", "armamentos"]   

# --- Ejemplo de Uso ---
if __name__ == "__main__":
    # Creamos una instancia de cada tipo de vehículo para el jugador 1
    jeep_j1 = Jeep(id="jeep_01", jugador_id=1, pos_inicial=(100, 50))
    moto_j1 = Moto(id="moto_01", jugador_id=1, pos_inicial=(100, 80))
    
    print(jeep_j1)
    print(f"Viajes máximos del Jeep: {jeep_j1.max_viajes}")  
    print(f"Cargas permitidas para la Moto: {moto_j1.tipo_carga_permitida}") 
    # Simulamos una recolección
    moto_j1.recolectar("persona_rescatada_01")
    print(f"Carga actual de la moto: {moto_j1.carga_actual}")
    print(f"Viajes realizados por la moto: {moto_j1.viajes_realizados}")

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
    #PARA INCIALIZAR UN RECURSO SE PASA COMO PARAMETRO EL TIPO DE RECURSO Y EL DICCIONARIO
    def __init__(self, resource_type: str, stats_config: dict):
        if resource_type not in stats_config:
            raise ValueError(f"El tipo de recurso '{resource_type}' no es válido.")
        
        stats = stats_config[resource_type]
        
        self.type = resource_type
        self.score = stats['score']
        self.position = None