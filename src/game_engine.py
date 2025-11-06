#MOTOR DEL JUEGO
import random
from classes import *
class GameEngine:
    def __init__(self):
        self.vehiculos_j1 = []
        self.vehiculos_j2 = []
        self.puntaje_j1 = 0
        self.puntaje_j2 = 0

    
    def _crear_vehiculos(self, map_width, map_height):
        """
        Modifica self.vehiculos_j1 y self.vehiculos_j2
        llenándolas con las flotas de cada jugador.
        """
        
        # --- 1. Definir Posiciones de Bases ---
        base_j1_y = random.randint(0, map_height - 1)
        BASE_J1_POS = (0, base_j1_y)
        
        base_j2_y = random.randint(0, map_height - 1)
        BASE_J2_POS = (map_width - 1, base_j2_y)

        print(f"Base Jugador 1 generada en: {BASE_J1_POS}")
        print(f"Base Jugador 2 generada en: {BASE_J2_POS}")

        # --- 2. Crear Flotas  ---
        
        # 3 Jeeps
        for i in range(3):
            self.vehiculos_j1.append(Jeep(f"J1-Jeep-{i+1}", 1, BASE_J1_POS, BASE_J1_POS))
            self.vehiculos_j2.append(Jeep(f"J2-Jeep-{i+1}", 2, BASE_J2_POS, BASE_J2_POS))
            
        # 2 Motos
        for i in range(2):
            self.vehiculos_j1.append(Moto(f"J1-Moto-{i+1}", 1, BASE_J1_POS, BASE_J1_POS))
            self.vehiculos_j2.append(Moto(f"J2-Moto-{i+1}", 2, BASE_J2_POS, BASE_J2_POS))
            
        # 2 Camiones
        for i in range(2):
            self.vehiculos_j1.append(Camion(f"J1-Camion-{i+1}", 1, BASE_J1_POS, BASE_J1_POS))
            self.vehiculos_j2.append(Camion(f"J2-Camion-{i+1}", 2, BASE_J2_POS, BASE_J2_POS))

        # 3 Autos
        for i in range(3):
            self.vehiculos_j1.append(Auto(f"J1-Auto-{i+1}", 1, BASE_J1_POS, BASE_J1_POS))
            self.vehiculos_j2.append(Auto(f"J2-Auto-{i+1}", 2, BASE_J2_POS, BASE_J2_POS))
            
        print(f"Flota J1 (self) llenada con {len(self.vehiculos_j1)} vehículos.")
        print(f"Flota J2 (self) llenada con {len(self.vehiculos_j2)} vehículos.")