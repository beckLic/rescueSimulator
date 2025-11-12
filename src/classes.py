#CLASES DE VEHICULOS
import math
import pygame
import random
from src.pathfinding import *
from Visual import CONSTANTES
class Vehiculo(pygame.sprite.Sprite):
    """
    Clase base que representa a cualquier vehículo en el simulador.
    Contiene todos los atributos y métodos comunes.
    """ 
    #CONSTRUCTOR DE LA CLASE
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple, posicion_base: tuple):
        pygame.sprite.Sprite.__init__(self)
        # --- Atributos de Identificación ---
        self.id = id
        self.jugador_id = jugador_id
        
        # --- Atributos de Posición y Estado ---
        self.posicion = pygame.math.Vector2(pos_inicial)
        self.posicion_base = posicion_base #posicion de su base para volver
        self.objetivo_actual = None
        self.image = None          
        self.rect = None           
        self.direccion = "derecha"
        self.objetivo_actual = None
        self.camino_actual = []
        self.destruido = False
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
        map_manager.eliminar_elemento(recurso.position[0], recurso.position[1])
        recurso.kill()
        # 3. Eliminar el recurso de la lista de objetivos
        if recurso in map_manager.resources:
            map_manager.resources.remove(recurso)
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
        recursos_disponibles = map_manager.resources
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

    def _calcular_camino(self, map_manager, destino_yx, obstaculos_adicionales=None):
        """
        Función helper para calcular la ruta A* y manejar errores.
        Ahora acepta 'obstaculos_adicionales'.
        Retorna el camino encontrado o None.
        """
        try:

            mapa_pf = map_manager.generar_mapa_pathfinding(obstaculos_adicionales)
            
            pos_inicio_yx = (int(self.posicion.y), int(self.posicion.x))
            
            camino_encontrado = a_star(mapa_pf, pos_inicio_yx, destino_yx)
            
            if camino_encontrado:
                camino_encontrado.pop(0) # Quitamos el primer paso por ser posicion actual
                return camino_encontrado
            else:
                return None
        except Exception as e:
            print(f"Error calculando A* para {self.id}: {e}")
            return None

    def _evaluar_siguiente_paso(self, map_manager, grupo_vehiculos):
        """
        Revisa peligros y devuelve un tipo de peligro específico.
        Retorna: (siguiente_pos_yx, tipo_peligro (str), vehiculo_bloqueador (obj))
        """
        if not self.camino_actual:
            return None, "SIN_CAMINO", None # No hay camino

        siguiente_pos_yx = self.camino_actual[0]
        siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0]) # (x, y)

        # 1. Revisar contra minas móviles
        for mina in map_manager.mines:
            if isinstance(mina, MinaMovil):
                if mina.is_active and mina.is_inside_area(siguiente_pos_xy):
                    print(f"{self.id} FRENANDO (MINA): ¡Mina G1 activa en {siguiente_pos_xy}!")
                    return siguiente_pos_yx, "MINA", None # Peligro de mina, debe esperar

        # 2. Revisar contra otros vehículos
        if grupo_vehiculos: 
            for vehiculo_bloqueador in grupo_vehiculos.sprites():
                if vehiculo_bloqueador == self: continue
                
                vehiculo_pos_xy = (int(vehiculo_bloqueador.posicion.x), int(vehiculo_bloqueador.posicion.y))
                
                if vehiculo_pos_xy == siguiente_pos_xy:
                    
                    # Lógica de ataque (esto ya estaba y es correcto)
                    if self.jugador_id != vehiculo_bloqueador.jugador_id and vehiculo_bloqueador.carga_actual:
                        print(f"{self.id} ¡ATACANDO! {vehiculo_bloqueador.id} (Enemigo) tiene carga en {siguiente_pos_xy}")
                        return siguiente_pos_yx, "SEGURO", None # 'SEGURO' para avanzar y atacar

                    # ¡BLOQUEO! (Compañero O Enemigo vacío)
                    else:
                        print(f"{self.id} BLOQUEADO por {vehiculo_bloqueador.id} en {siguiente_pos_xy}.")
                        return siguiente_pos_yx, "VEHICULO", vehiculo_bloqueador # Peligro de vehículo, debe decidir

        # 3. Si no hay peligros
        return siguiente_pos_yx, "SEGURO", None

    def destruir(self):
    #Marca el vehículo como destruido y lo elimina."""
        if self.destruido: # Evitar destrucción múltiple
            return

        self.destruido = True
        print(f"¡COLISIÓN! {self.id} ha sido destruido.")

        # Pierde toda la carga que llevaba
        self.carga_actual.clear() 

        #Añadir aquí una explosión visual

        # Elimina el sprite de todos los grupos
        self.kill()
    def _resolver_siguiente_paso(self, map_manager, grupo_vehiculos):
        """
        Helper que contiene la lógica de movimiento, evasión y recálculo.
        Es llamado por update() en los estados 'buscando' y 'volviendo'.
        """
        # 1. Evaluar el siguiente paso
        siguiente_pos_yx, tipo_peligro, vehiculo_bloqueador = self._evaluar_siguiente_paso(map_manager, grupo_vehiculos)
        
        # 2. Tomar decisiones basadas en el tipo de peligro
        
        if tipo_peligro == "SEGURO":
            # Es seguro moverse
            siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0])
            pos_anterior = self.posicion.copy()
            self._actualizar_posicion_pixel(siguiente_pos_xy, pos_anterior)
            self.camino_actual.pop(0) 
            
            # --- LÓGICA DE LLEGADA ---
            if not self.camino_actual:
                if self.estado == "buscando":
                    self.recolectar(self.objetivo_actual, map_manager)
                    self.objetivo_actual = None
                    if self.viajes_realizados >= self.max_viajes:
                        self.estado = "volviendo"
                    else:
                        self.estado = "inactivo"
                
                elif self.estado == "volviendo":
                    # ... (cálculo de puntaje) ...
                    puntaje_obtenido = 0
                    for recurso in self.carga_actual:
                        puntaje_obtenido += recurso.score
                        tipo_recurso = recurso.type
                        if self.jugador_id == 1:
                            if tipo_recurso in map_manager.recursos_j1: # Usamos map_manager, no mapa
                                map_manager.recursos_j1[tipo_recurso] += 1
                        else: # jugador_id == 2
                            if tipo_recurso in map_manager.recursos_j2:
                                map_manager.recursos_j2[tipo_recurso] += 1
                    if self.jugador_id == 1:
                        map_manager.puntaje_j1 += puntaje_obtenido
                    else: 
                        map_manager.puntaje_j2 += puntaje_obtenido
                    
                    print(f"{self.id} llegó a la base y entregó {puntaje_obtenido} puntos.")
                    print(f"== MARCADOR: AZUL ({map_manager.puntaje_j1}) - ROJO ({map_manager.puntaje_j2}) ==")

                    self.carga_actual.clear()
                    self.viajes_realizados = 0
                    self.estado = "inactivo"
        
        elif tipo_peligro == "MINA" or tipo_peligro == "SIN_CAMINO":
            # ¡Peligro de Mina G1! o se quedó sin camino.
            # La acción es ESPERAR. No hacemos nada (no .pop()).
            pass 
        
        elif tipo_peligro == "VEHICULO":
            # ¡Bloqueado por un vehículo!
            
            # Aplicar regla de desempate por ID
            # El vehículo con el ID "mayor" (alfabéticamente) es el que cede.
            if self.id > vehiculo_bloqueador.id:
                print(f"{self.id} (cede) recalculando ruta alrededor de {vehiculo_bloqueador.id}")
                
                # Lista de obstáculos para el nuevo cálculo de A*
                obstaculos = [ (vehiculo_bloqueador.posicion.x, vehiculo_bloqueador.posicion.y) ]

                # 1. Obtener destino (depende del estado actual)
                destino_yx = None
                if self.estado == "buscando" and self.objetivo_actual:
                    destino_yx = (self.objetivo_actual.position[1], self.objetivo_actual.position[0])
                elif self.estado == "volviendo":
                    destino_yx = (int(self.posicion_base[1]), int(self.posicion_base[0]))
                
                # 2. Llamar al nuevo _calcular_camino
                if destino_yx:
                    nuevo_camino = self._calcular_camino(map_manager, destino_yx, obstaculos)
                    
                    if nuevo_camino:
                        self.camino_actual = nuevo_camino
                    else:
                        # No hay ruta alternativa, nos quedamos quietos
                        print(f"{self.id} no encontró ruta alternativa. Esperando...")
                        pass 
                else:
                    # No tenía un destino claro, mejor esperar.
                    pass
            else:
                print(f"{self.id} (espera) tiene prioridad sobre {vehiculo_bloqueador.id}")
                pass # Esperamos a que el otro vehículo (con id >) se mueva

    def _actualizar_posicion_pixel(self, nueva_pos_grid: tuple, pos_anterior_grid: pygame.math.Vector2):
        """
        Actualiza el self.rect (píxeles) y la dirección de la imagen
        basado en el cambio de self.posicion (grilla).
        """
        # 1. Actualizar dirección de la imagen (lógica de auto.py)
        delta_x = nueva_pos_grid[0] - pos_anterior_grid.x
        delta_y = nueva_pos_grid[1] - pos_anterior_grid.y

        if delta_x > 0: self.direccion = "derecha"
        elif delta_x < 0: self.direccion = "izquierda"
        elif delta_y < 0: self.direccion = "arriba"
        elif delta_y > 0: self.direccion = "abajo"
        
        self.actualizar_imagen() # Rotar/flipear la imagen
        
        # 2. Actualizar la posición de la grilla
        self.posicion = pygame.math.Vector2(nueva_pos_grid)
        
        # 3. Actualizar la posición del rect en píxeles
        pixel_x = self.posicion.x * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = self.posicion.y * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect.center = (pixel_x, pixel_y)

    def actualizar_imagen(self):
        """
        Gira o voltea la 'image_original' para que coincida con 'self.direccion'.
        (Lógica copiada de Visual/auto.py)
        """
        if self.image_original is None: return # No hacer nada si no hay imagen

        if self.direccion == "derecha":
            self.image = self.image_original
        elif self.direccion == "izquierda":
            self.image = pygame.transform.flip(self.image_original, True, False)
        elif self.direccion == "arriba":
            self.image = pygame.transform.rotate(self.image_original, 90)
        elif self.direccion == "abajo":
            self.image = pygame.transform.rotate(self.image_original, -90)

        # Actualizar el rectángulo para mantener el centro
        centro = self.rect.center
        self.rect = self.image.get_rect(center=centro)
    def update(self, map_manager, game_time, grupo_vehiculos=None):
        
        # =======================================================
        # ESTADO 0: DESTRUIDO (eliminado)
        # =======================================================
        if self.destruido:
            return
        # =======================================================
        # ESTADO 1: INACTIVO (Buscando qué hacer)
        # =======================================================
        if self.estado == "inactivo":
            # Paso 1: Decidir el Objetivo
            self.objetivo_actual = self._encontrar_mejor_objetivo(map_manager)

            if self.objetivo_actual:
                print(f"{self.id} decidió ir a por {self.objetivo_actual.type} en {self.objetivo_actual.position}")
                
                # Paso 2: Calcular la Ruta hacia el objetivo
                pos_objetivo_yx = (self.objetivo_actual.position[1], self.objetivo_actual.position[0])
                
                # (MODIFICADO) Llama al _calcular_camino estándar (sin obstáculos)
                self.camino_actual = self._calcular_camino(map_manager, pos_objetivo_yx)
                
                # Paso 3: Transición de Estado
                if self.camino_actual:
                    self.estado = "buscando" 
                else:
                    print(f"{self.id} no encontró camino a {self.objetivo_actual.position}")
                    self.objetivo_actual = None
            
        # =======================================================
        # ESTADO 2: BUSCANDO (Yendo hacia un recurso)
        # =======================================================
        elif self.estado == "buscando":
            if self.objetivo_actual not in map_manager.resources:
                self.estado = "inactivo"
                self.camino_actual = None
                self.objetivo_actual = None
                return 
            if not self.camino_actual:
                self.estado = "inactivo"
                return

            # (MODIFICADO) Llamar al helper de movimiento
            self._resolver_siguiente_paso(map_manager, grupo_vehiculos)
            
        # =======================================================
        # ESTADO 3: VOLVIENDO (Yendo hacia la base)
        # =======================================================
        elif self.estado == "volviendo":
            
            # Paso 1: Calcular el camino a la base (SOLO SI NO LO TIENE)
            if not self.camino_actual:
                pos_base_yx = (int(self.posicion_base[1]), int(self.posicion_base[0]))
                
                self.camino_actual = self._calcular_camino(map_manager, pos_base_yx)
                if not self.camino_actual:
                    print(f"{self.id} NO encuentra camino a la base. Esperando...")
                    return
            
            # Paso 2: (MODIFICADO) Llamar al helper de movimiento
            self._resolver_siguiente_paso(map_manager, grupo_vehiculos)
#-----------------------------------------------------------------------------------------------------------   
class Jeep(Vehiculo):
    """
    Representa un vehículo tipo Jeep.
    - Puede recoger todo tipo de carga.
    - Puede realizar hasta 2 viajes antes de volver a base.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple, posicion_base: tuple):
        super().__init__(id, jugador_id, pos_inicial, posicion_base)
        self.tipo = "jeep"
        self.max_viajes = 2  # 
        self.tipo_carga_permitida = ["Personas", "Alimentos", "Ropa", "Medicamentos", "Armamentos"]  # 
        if self.jugador_id == 1:
            ruta_imagen = "imagenes/jeep_A.png"
        else: # Asumimos jugador_id == 2
            ruta_imagen = "imagenes/jeep_R.png"
        self.image_original = pygame.image.load(ruta_imagen).convert_alpha()
        ancho, alto = self.image_original.get_size()
        factor_x = CONSTANTES.CELDA_ANCHO / ancho
        factor_y = CONSTANTES.CELDA_ALTO / alto
        factor = min(factor_x, factor_y)
        self.image_original = pygame.transform.smoothscale(
            self.image_original,
            (int(ancho * factor), int(alto * factor))
        )
        self.image = self.image_original

        # Crear el rect inicial en la posición de píxeles
        pixel_x = pos_inicial[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = pos_inicial[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect = self.image.get_rect(center=(pixel_x, pixel_y))
#------------------------------------------------------------------------------------------------------------
class Moto(Vehiculo):
    """
    Representa un vehículo tipo Moto.
    - Solo puede recoger Personas.
    - Debe volver a la base después de cada viaje.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple, posicion_base: tuple):
        super().__init__(id, jugador_id, pos_inicial, posicion_base) 
        self.tipo = "moto"
        self.max_viajes = 1  # 
        self.tipo_carga_permitida = ["Personas"]  # 
        if self.jugador_id == 1:
            ruta_imagen = "imagenes/moto_A.png"
        else: # Asumimos jugador_id == 2
            ruta_imagen = "imagenes/moto_R.png"
        self.image_original = pygame.image.load(ruta_imagen).convert_alpha()
        ancho, alto = self.image_original.get_size()
        factor_x = CONSTANTES.CELDA_ANCHO / ancho
        factor_y = CONSTANTES.CELDA_ALTO / alto
        factor = min(factor_x, factor_y)
        self.image_original = pygame.transform.smoothscale(
            self.image_original,
            (int(ancho * factor), int(alto * factor))
        )
        self.image = self.image_original

        # Crear el rect inicial en la posición de píxeles
        pixel_x = pos_inicial[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = pos_inicial[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect = self.image.get_rect(center=(pixel_x, pixel_y))
#-------------------------------------------------------------------------------------------------------------
class Camion(Vehiculo):
    """
    Representa un vehículo tipo Camión.
    - Puede recoger todo tipo de carga.
    - Puede realizar hasta 3 viajes antes de volver a base.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple, posicion_base: tuple): 
        super().__init__(id, jugador_id, pos_inicial, posicion_base) 
        self.tipo = "camion"
        self.max_viajes = 3  # 
        self.tipo_carga_permitida = ["Personas", "Alimentos", "Ropa", "Medicamentos", "Armamentos"] 
        if self.jugador_id == 1:
            ruta_imagen = "imagenes/camion_A.png"
        else: # Asumimos jugador_id == 2
            ruta_imagen = "imagenes/camion_R.png"
        self.image_original = pygame.image.load(ruta_imagen).convert_alpha()
        ancho, alto = self.image_original.get_size()
        factor_x = CONSTANTES.CELDA_ANCHO / ancho
        factor_y = CONSTANTES.CELDA_ALTO / alto
        factor = min(factor_x, factor_y)
        self.image_original = pygame.transform.smoothscale(
            self.image_original,
            (int(ancho * factor), int(alto * factor))
        )
        self.image = self.image_original

        # Crear el rect inicial en la posición de píxeles
        pixel_x = pos_inicial[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = pos_inicial[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect = self.image.get_rect(center=(pixel_x, pixel_y))
#-------------------------------------------------------------------------------------------------------------
class Auto(Vehiculo):
    """
    Representa un vehículo tipo Auto.
    - Puede recoger Personas y cargas.
    - Debe volver a la base después de cada viaje.
    """
    def __init__(self, id: str, jugador_id: int, pos_inicial: tuple, posicion_base: tuple): 
        super().__init__(id, jugador_id, pos_inicial, posicion_base) 
        self.tipo = "auto"
        self.max_viajes = 1   
        self.tipo_carga_permitida = ["Personas", "Alimentos", "Ropa", "Medicamentos", "Armamentos"]   
        if self.jugador_id == 1:
            ruta_imagen = "imagenes/Auto_A.png"
        else: # Asumimos jugador_id == 2
            ruta_imagen = "imagenes/Auto_R.png"
        self.image_original = pygame.image.load(ruta_imagen).convert_alpha()
        ancho, alto = self.image_original.get_size()
        factor_x = CONSTANTES.CELDA_ANCHO / ancho
        factor_y = CONSTANTES.CELDA_ALTO / alto
        factor = min(factor_x, factor_y)
        self.image_original = pygame.transform.smoothscale(
            self.image_original,
            (int(ancho * factor), int(alto * factor))
        )
        self.image = self.image_original

        # Crear el rect inicial en la posición de píxeles
        pixel_x = pos_inicial[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = pos_inicial[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect = self.image.get_rect(center=(pixel_x, pixel_y))
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
class Recurso(pygame.sprite.Sprite):
    #PARA INCIALIZAR UN RECURSO SE PASA COMO PARAMETRO EL TIPO DE RECURSO, EL DICCIONARIO Y LA POSICION
    def __init__(self, resource_type: str, stats_config: dict, position: tuple, imagen: pygame.Surface):
        pygame.sprite.Sprite.__init__(self)
        if resource_type not in stats_config:
            raise ValueError(f"El tipo de recurso '{resource_type}' no es válido.")
        
        stats = stats_config[resource_type]
        
        self.type = resource_type
        self.score = stats['score']
        self.position = position
        self.item_type = resource_type
        self.image = imagen
        # Convierte la posición de grilla a píxeles para el sprite
        pixel_x = position[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = position[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect = self.image.get_rect(center=(pixel_x, pixel_y))
    #queda comentado por superpocición con el update de recurso
    def update(self, grupo_vehiculos, mapa, game_time):

    #     # Comprobar colisión con el vehículo
    #     vehiculo_colisionado = pygame.sprite.spritecollideany(self, grupo_vehiculos)
    #     if self.rect.colliderect(vehiculo.shape):
            
            
    #         if self.item_type == "mina":
    #             print("¡BOOM! Mina explota.")
    #             # queda eliminar el vehículo
                
    #         elif self.item_type == "Persona":
    #             print("¡Persona rescatada!")
                
    #         elif self.item_type == "Alimentos":
    #             print("Comida recolectada.")
                
    #         elif self.item_type == "Ropa":
    #             print("Ropa recolectada.")

    #         elif self.item_type == "Medicamentos":
    #             print("Medicina recolectada.")
            
    #         elif self.item_type == "Armamentos":
    #             print("Armamento recolectado.")
            
    #         # eliminar el ítem
            
            
    #         grid_x = int(self.rect.centerx // CONSTANTES.CELDA_ANCHO)
    #         grid_y = int(self.rect.centery // CONSTANTES.CELDA_ALTO)
            
    #         # Eliminar el objeto LÓGICO del mapa
    #         mapa.eliminar_elemento(grid_x, grid_y)
            
    #         # Eliminar el sprite VISUAL del grupo
    #         self.kill()
        pass
#-------------------------------------------------------------------------------------------------------
#CLASE DE MINAS

class Mina(pygame.sprite.Sprite):
    def __init__(self, position: tuple):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.item_type = "mina"
    def update(self, grupo_vehiculos, mapa, game_time):
        
        # Iteramos sobre una copia .sprites() para poder modificar el grupo
        for vehiculo in grupo_vehiculos.sprites():
            pos_vehiculo_xy = (int(vehiculo.posicion.x), int(vehiculo.posicion.y))
            # ... (lógica de is_inside_area) ...
            if self.is_inside_area(pos_vehiculo_xy):
                
                # ¡Colisión detectada!
                print(f"¡BOOM! Mina en {self.position} explota sobre {vehiculo.id}.")

                # (NUEVO) Registrar destrucción del vehículo
                if vehiculo.jugador_id == 1:
                    mapa.vehiculos_destruidos_j1 += 1
                else:
                    mapa.vehiculos_destruidos_j2 += 1
                
                vehiculo.kill() # Daña/elimina el vehículo
    def draw_radius(self, surface):
        """
        Dibuja el área de efecto LÓGICA de la mina, celda por celda.
        Esto es visualmente preciso con la lógica de colisión.
        """
        # Para MinaMovil, si no está activa, no dibuja nada.
        if isinstance(self, MinaMovil) and not self.is_active:
            return

        color_area = (255, 0, 0, 100) # Rojo semitransparente

        # Radio máximo de celdas a chequear (optimización)
        # Basado en el radio/largo más grande de tu config (que es 10)
        max_check_radius = 15 
        
        # Iteramos en un cuadrado de celdas alrededor de la mina
        for x in range(self.position[0] - max_check_radius, self.position[0] + max_check_radius + 1):
            for y in range(self.position[1] - max_check_radius, self.position[1] + max_check_radius + 1):
                
                # Nos aseguramos de no chequear celdas fuera del mapa
                # (Asumiendo un mapa de 50x50 de CONSTANTES)
                if not (0 <= x < CONSTANTES.CANTIDAD_I and 0 <= y < CONSTANTES.CANTIDAD_J):
                    continue

                # Preguntamos a la lógica si esta celda (x,y) es peligrosa
                if self.is_inside_area((x, y)):
                    
                    # Si es peligrosa, dibujamos un RECTÁNGULO en esa celda
                    pixel_x = x * CONSTANTES.CELDA_ANCHO
                    pixel_y = y * CONSTANTES.CELDA_ALTO
                    
                    # Creamos una superficie para la celda (para la transparencia)
                    s = pygame.Surface((CONSTANTES.CELDA_ANCHO, CONSTANTES.CELDA_ALTO), pygame.SRCALPHA)
                    pygame.draw.rect(s, color_area, (0, 0, CONSTANTES.CELDA_ANCHO, CONSTANTES.CELDA_ALTO))
                    
                    # Dibujamos esa celda en la ventana
                    surface.blit(s, (pixel_x, pixel_y))
#-------------------------------------------------------------------------------------------------------------
class MinaCircular(Mina):
    """
    Representa una mina estática con un área de efecto circular.
    Corresponde a las minas O1 y O2 del proyecto.
    """
    #PARA INCIALIZARLA LE PASAMOS COMO PARAMETRO LA POSICION Y SU RADIO
    def __init__(self, position: tuple, radius: int, imagen: pygame.Surface):
        super().__init__(position)
        self.radius = radius
        self.image = imagen
        pixel_x = position[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = position[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect = self.image.get_rect(center=(pixel_x, pixel_y))

    def is_inside_area(self, point: tuple) -> bool:
        # Calcula la distancia euclidiana entre el punto y el centro de la mina
        distance = math.sqrt((point[0] - self.position[0])**2 + (point[1] - self.position[1])**2)
        # Devuelve True si la distancia es menor o igual al radio
        return distance <= self.radius
        
        
#-------------------------------------------------------------------------------------------------------------
class MinaLineal(Mina):
    """
    Representa una mina estática con un área de efecto lineal.
    Corresponde a las minas T1 y T2 del proyecto.
    """
    #PARA INCIALIZARLA LE PASAMOS COMO PARAMETRO LA POSICION, LONGITUD DE SU RADIO Y SU ORIENTACION
    def __init__(self, position: tuple, length: int, orientation: str, imagen: pygame.Surface):
        super().__init__(position)
        self.image = imagen
        pixel_x = position[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
        pixel_y = position[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
        self.rect = self.image.get_rect(center=(pixel_x, pixel_y))
        if orientation not in ['Horizontal', 'Vertical']:
            raise ValueError("La orientación debe ser 'Horizontal' o 'Vertical'.")
        self.length = length
        self.orientation = orientation

    def is_inside_area(self, point: tuple) -> bool:
        px, py = point #coordenadas del vehiculo
        mx, my = self.position #coordenadas del centro de la mina
        offset = (self.length - 1) / 2 #segmento para dividir el radio en dos partes iguales para los costados de la mina

        if self.orientation == 'Horizontal':
            y_match = abs(py - my) < 1 # Para una línea horizontal, la coordenada 'y' debe ser la misma,
            x_in_range = (mx - offset) <= px <= (mx + offset) # y la 'x' debe estar dentro del segmento de la línea.
            #OPERADOR AND PARA RETURNAR TRUE O FALSE
            return y_match and x_in_range
        else: # 'vertical'
            x_match = abs(px - mx) < 1 # Para una línea vertical, la coordenada 'x' debe ser la misma,
            y_in_range = (my - offset) <= py <= (my + offset) # y la 'y' debe estar dentro del segmento de la línea.
            #OPERADOR AND PARA RETURNAR TRUE O FALSE
            return x_match and y_in_range
    

class MinaMovil(MinaCircular):
    """
    Representa la Mina G1, que es circular pero aparece y desaparece.
    También cambia de posición cada vez que se activa (reaparece).
    """
    def __init__(self, position: tuple, radius: int, cycle_duration: int, imagen: pygame.Surface):
        super().__init__(position, radius, imagen)
        self.cycle_duration = cycle_duration
        self.is_active = True
        
        # Márgenes de seguridad para el reposicionamiento
        self.MARGEN_LATERAL_BASES = 10 
        self.MARGEN_SUPERIOR_INFERIOR = 5

    def _cambiar_posicion(self, mapa):
        """
        Busca una nueva posición aleatoria y segura en el mapa y
        actualiza su propia posición y la grilla del map_manager.
        
        'mapa' es la instancia de MapManager.
        """
        print(f"Mina G1 en {self.position} buscando nueva posición...")
        
        # 1. Definir la zona segura para 'aparecer'
        x_min_seguro = self.MARGEN_LATERAL_BASES
        x_max_seguro = mapa.width - 1 - self.MARGEN_LATERAL_BASES
        y_min_seguro = self.MARGEN_SUPERIOR_INFERIOR
        y_max_seguro = mapa.height - 1 - self.MARGEN_SUPERIOR_INFERIOR

        # 2. Buscar una nueva posición
        posicion_encontrada = False
        intentos = 0 # Para evitar un bucle infinito si el mapa está lleno
        
        while not posicion_encontrada and intentos < 100:
            intentos += 1
            x_candidato = random.randint(x_min_seguro, x_max_seguro)
            y_candidato = random.randint(y_min_seguro, y_max_seguro)
            
            # Usamos el helper del map_manager para ver si la celda está vacía
            if mapa.posicion_libre(x_candidato, y_candidato):
                
                # 3. ¡Posición encontrada! Actualizar todo.
                
                # 3a. Borrarse de la grilla vieja (importante)
                mapa.eliminar_elemento(self.position[0], self.position[1])

                # 3b. Actualizar su propia posición (lógica)
                self.position = (x_candidato, y_candidato)
                
                # 3c. Inscribirse en la grilla nueva (importante)
                mapa.grid[y_candidato][x_candidato] = self
                
                # 3d. Actualizar el 'rect' (visual)
                pixel_x = self.position[0] * CONSTANTES.CELDA_ANCHO + (CONSTANTES.CELDA_ANCHO / 2)
                pixel_y = self.position[1] * CONSTANTES.CELDA_ALTO + (CONSTANTES.CELDA_ALTO / 2)
                self.rect.center = (pixel_x, pixel_y)
                
                print(f"Mina G1 reubicada en {self.position}.")
                posicion_encontrada = True
                
        if not posicion_encontrada:
             print(f"ADVERTENCIA: Mina G1 no pudo encontrar nueva posición. Se queda en {self.position}.")


    def update(self, grupo_vehiculos, mapa, game_time):
        """
        Actualiza el estado de la mina (activa/inactiva) basado en el
        tiempo de la simulación (game_time).
        Si ACABA de aparecer (transición a activa), cambia de posición.
        """
        
        # 1. Chequear si el ciclo se cumplió
        if game_time > 0 and game_time % self.cycle_duration == 0:
            # 1a. Invertir estado
            self.is_active = not self.is_active
            # print(f"Mina móvil en {self.position} ahora está {'activa' if self.is_active else 'inactiva'}")

            # 1b. Si ahora está ACTIVA (acaba de aparecer), cambiar de posición
            if self.is_active:
                self._cambiar_posicion(mapa) # 'mapa' es el map_manager
        
        # 2. Llama al 'update' de la clase Mina (que contiene
        #    la lógica de explosión si está activa)
        super().update(grupo_vehiculos, mapa, game_time)

    def is_inside_area(self, point: tuple) -> bool:
        """
        La mina solo puede causar daño si su estado es activo.
        """
        if not self.is_active:
            return False
        
        # Si está activa, utiliza la misma lógica de su clase padre (MinaCircular).
        return super().is_inside_area(point)
