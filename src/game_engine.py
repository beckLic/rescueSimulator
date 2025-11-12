#MOTOR DEL JUEGO
import random
from .classes import *
import pygame
class GameEngine:
    def __init__(self):
        self.vehiculos_j1 = []
        self.vehiculos_j2 = []
        self.puntaje_j1 = 0
        self.puntaje_j2 = 0

    
    def _crear_vehiculos(self):
        """
        Modifica self.vehiculos_j1 y self.vehiculos_j2
        llenándolas con las flotas de cada jugador.
        """
        grupo_vehiculos_creados = pygame.sprite.Group()
        pos = (4, 4); grupo_vehiculos_creados.add(Jeep(id="J1-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        pos = (4, 8); grupo_vehiculos_creados.add(Jeep(id="J2-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        pos = (4, 12); grupo_vehiculos_creados.add(Jeep(id="J3-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        # 2 Motos
        pos = (4, 15); grupo_vehiculos_creados.add(Moto(id="M1-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        pos = (4, 20); grupo_vehiculos_creados.add(Moto(id="M2-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        # 2 Camiones
        pos = (4, 27); grupo_vehiculos_creados.add(Camion(id="C1-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        pos = (4, 32); grupo_vehiculos_creados.add(Camion(id="C2-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        # 3 Autos
        pos = (4, 39); grupo_vehiculos_creados.add(Auto(id="A1-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        pos = (4, 43); grupo_vehiculos_creados.add(Auto(id="A2-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        pos = (4, 47); grupo_vehiculos_creados.add(Auto(id="A3-IA-1", jugador_id=1, pos_inicial=pos, posicion_base=pos))
        
        # --- Equipo 2 (Rojo) ---
        
        # (posicion_base ahora es igual a pos_inicial)
        
        # 3 Jeeps
        pos = (46, 4); grupo_vehiculos_creados.add(Jeep(id="J1-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        pos = (46, 8); grupo_vehiculos_creados.add(Jeep(id="J2-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        pos = (46, 12); grupo_vehiculos_creados.add(Jeep(id="J3-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        # 2 Motos
        pos = (46, 15); grupo_vehiculos_creados.add(Moto(id="M1-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        pos = (46, 20); grupo_vehiculos_creados.add(Moto(id="M2-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        # 2 Camiones
        pos = (46, 27); grupo_vehiculos_creados.add(Camion(id="C1-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        pos = (46, 32); grupo_vehiculos_creados.add(Camion(id="C2-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        # 3 Autos
        pos = (46, 39); grupo_vehiculos_creados.add(Auto(id="A1-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        pos = (46, 43); grupo_vehiculos_creados.add(Auto(id="A2-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
        pos = (46, 47); grupo_vehiculos_creados.add(Auto(id="A3-IA-2", jugador_id=2, pos_inicial=pos, posicion_base=pos))
            
        # Llenamos las listas internas del engine (como estaba en tu original)
        self.vehiculos_j1 = [v for v in grupo_vehiculos_creados if v.jugador_id == 1]
        self.vehiculos_j2 = [v for v in grupo_vehiculos_creados if v.jugador_id == 2]

        print(f"Flota J1 (self) llenada con {len(self.vehiculos_j1)} vehículos.")
        print(f"Flota J2 (self) llenada con {len(self.vehiculos_j2)} vehículos.")
        
        # Devolvemos el grupo que main.py usará
        return grupo_vehiculos_creados