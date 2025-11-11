#CLASES DE VEHICULOS
import math
import pygame
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

    def _calcular_camino(self, map_manager, destino_yx):
        """
        Función helper para calcular la ruta A* y manejar errores.
        Retorna el camino encontrado o None.
        """
        try:
            # REVERTIDA: Llama al 'generar_mapa_pathfinding' simple (estático)
            mapa_pf = map_manager.generar_mapa_pathfinding()
            
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
        Revisa si el siguiente paso en el camino es peligroso (minas G1, vehículos).
        Retorna: (siguiente_pos_yx, peligro_detectado (bool))
        """
        if not self.camino_actual:
            return None, True # No hay camino, se considera "peligro"

        siguiente_pos_yx = self.camino_actual[0]
        siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0]) # (x, y)

        peligro_detectado = False
        
        # 1. Revisar contra minas móviles
        for mina in map_manager.mines:
            if isinstance(mina, MinaMovil):
                if mina.is_active and mina.is_inside_area(siguiente_pos_xy):
                    peligro_detectado = True
                    print(f"{self.id} FRENANDO (MINA): ¡Mina G1 activa en {siguiente_pos_xy}!")
                    break 

        if peligro_detectado:
            return siguiente_pos_yx, True # Salir temprano si ya detectamos una mina

        # 2. Revisar contra otros vehículos
        if grupo_vehiculos: 
            for vehiculo_bloqueador in grupo_vehiculos.sprites():
                # Un vehículo no puede bloquearse a sí mismo
                if vehiculo_bloqueador == self:
                    continue
                
                # Posición actual (x,y) del otro vehículo
                vehiculo_pos_xy = (int(vehiculo_bloqueador.posicion.x), int(vehiculo_bloqueador.posicion.y))
                
                # Si el otro vehículo está en nuestro siguiente paso
                if vehiculo_pos_xy == siguiente_pos_xy:
                    
                    # Primero, revisamos si es un compañero
                    if vehiculo_bloqueador.jugador_id == self.jugador_id:
                        # ES UN COMPAÑERO: Siempre esperamos.
                        print(f"{self.id} FRENANDO (COMPAÑERO): {vehiculo_bloqueador.id} está en {siguiente_pos_xy}.")
                        peligro_detectado = True
                    
                    # ES UN ENEMIGO: Ahora aplicamos la lógica de ataque
                    elif vehiculo_bloqueador.carga_actual:
                        # ENEMIGO CON CARGA: ¡Atacar!
                        print(f"{self.id} ¡ATACANDO! {vehiculo_bloqueador.id} (Enemigo) tiene carga en {siguiente_pos_xy}")
                        peligro_detectado = False # Falso = No hay peligro = Avanzar
                    else:
                        # ENEMIGO VACÍO: Esperar.
                        print(f"{self.id} FRENANDO (ENEMIGO VACÍO): {vehiculo_bloqueador.id} está en {siguiente_pos_xy}.")
                        peligro_detectado = True
                    
                    break # Ya encontramos el vehículo que bloquea, no seguimos buscando
            
        return siguiente_pos_yx, peligro_detectado

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
                pos_objetivo_yx = (self.objetivo_actual.position[1], self.objetivo_actual.position[0])
                
                # REVERTIDO: Llama al _calcular_camino simple
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

            # Revisar peligros en el siguiente paso
            # REVERTIDO: 'tipo_peligro' ahora es 'peligro_detectado' (bool)
            siguiente_pos_yx, peligro_detectado = self._evaluar_siguiente_paso(map_manager, grupo_vehiculos)
            
            # --- LÓGICA DE DECISIÓN SIMPLIFICADA ---
            if not peligro_detectado:
                # Es seguro moverse
                siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0])
                pos_anterior = self.posicion.copy()
                self._actualizar_posicion_pixel(siguiente_pos_xy, pos_anterior)
                self.camino_actual.pop(0) 
                
                # --- LÓGICA DE LLEGADA Y RECOLECCIÓN ---
                if not self.camino_actual:
                    self.recolectar(self.objetivo_actual, map_manager)
                    self.objetivo_actual = None
                    if self.viajes_realizados >= self.max_viajes:
                        self.estado = "volviendo"
                    else:
                        self.estado = "inactivo"
            
            else:
                # ¡Peligro! (Mina G1 O Vehículo).
                # La acción es ESPERAR. No hacemos nada (no .pop()).
                # Lo re-evaluará en el próximo frame.
                pass 
            
        # =======================================================
        # ESTADO 3: VOLVIENDO (Yendo hacia la base)
        # =======================================================
        elif self.estado == "volviendo":
            
            # Paso 1: Calcular el camino a la base (SOLO SI NO LO TIENE)
            if not self.camino_actual:
                pos_base_yx = (int(self.posicion_base[1]), int(self.posicion_base[0]))
                
                # REVERTIDO: Llama al _calcular_camino simple
                self.camino_actual = self._calcular_camino(map_manager, pos_base_yx)
                if not self.camino_actual:
                    print(f"{self.id} NO encuentra camino a la base. Esperando...")
                    return
            
            # Paso 2: Moverse (con la misma lógica de evasión)
            siguiente_pos_yx, peligro_detectado = self._evaluar_siguiente_paso(map_manager, grupo_vehiculos)
            
            if not peligro_detectado:
                siguiente_pos_xy = (siguiente_pos_yx[1], siguiente_pos_yx[0])
                pos_anterior = self.posicion.copy()
                self._actualizar_posicion_pixel(siguiente_pos_xy, pos_anterior)
                self.camino_actual.pop(0)

                # --- LÓGICA DE LLEGADA A LA BASE ---
                if not self.camino_actual:
                    # ... (cálculo de puntaje) ...
                    puntaje_obtenido = 0
                    for recurso in self.carga_actual:
                        puntaje_obtenido += recurso.score
                    
                    if self.jugador_id == 1:
                        map_manager.puntaje_j1 += puntaje_obtenido
                    else: 
                        map_manager.puntaje_j2 += puntaje_obtenido
                    
                    print(f"{self.id} llegó a la base y entregó {puntaje_obtenido} puntos.")
                    print(f"== MARCADOR: AZUL ({map_manager.puntaje_j1}) - ROJO ({map_manager.puntaje_j2}) ==")

                    self.carga_actual.clear()
                    self.viajes_realizados = 0
                    self.estado = "inactivo"
            
            else:
                # ¡Peligro! (Mina G1 O Vehículo).
                # La acción es ESPERAR. No hacemos nada.
                pass
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
            
            # Convertimos la posición flotante del vehículo a una tupla de enteros (x, y)
            pos_vehiculo_xy = (int(vehiculo.posicion.x), int(vehiculo.posicion.y))
            
            # ¡Usamos is_inside_area!
            # Para MinaCircular/Lineal, esto chequeará el radio.
            # Para MinaMovil, esta MISMA LLAMADA (self.is_inside_area)
            # revisará internamente si 'is_active' es True.
            if self.is_inside_area(pos_vehiculo_xy):
                
                # ¡Colisión detectada!
                print(f"¡BOOM! Mina en {self.position} explota sobre {vehiculo.id}.")
                
                vehiculo.kill() # Daña/elimina el vehículo
                
                # Las minas móviles (MinaMovil) NO se autodestruyen.
                # Así que solo matamos la mina si NO es una MinaMovil.
                if not isinstance(self, MinaMovil):
                    mapa.eliminar_elemento(self.position[0], self.position[1])
                    self.kill() # La mina estática también se destruye
                    # Como la mina estática se destruyó, no necesitamos
                    # seguir chequeando si choca con otros vehículos.
                    break 
                
                # Si es una MinaMovil, no se destruye y puede
                # seguir explotando en el mismo frame (multikill)
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
    Hereda de CircularMine para reutilizar la lógica de su área de efecto
    """
    #INICIALIZAMOS CON LOS PARAMETROS DE POSICION, RADIO Y TIEMPO DE APARICION
    def __init__(self, position: tuple, radius: int, cycle_duration: int, imagen: pygame.Surface):
        # Nota: Pasamos la imagen al padre (MinaCircular)
        super().__init__(position, radius, imagen)
        self.cycle_duration = cycle_duration
        self.is_active = True

    def update(self, grupo_vehiculos, mapa, game_time):
        """
        Actualiza el estado de la mina (activa/inactiva) basado en el
        tiempo de la simulación, como se especifica en el proyecto.
        """
        # Cada 'cycle_duration' instancias de tiempo, el estado cambia.
        if game_time > 0 and game_time % self.cycle_duration == 0:
            self.is_active = not self.is_active
            # print(f"Mina móvil en {self.position} ahora está {'activa' if self.is_active else 'inactiva'}")
        # 2. Llama al 'update' de la clase Mina (que ahora contiene
        #    la lógica de explosión de área que acabamos de escribir)
        super().update(grupo_vehiculos, mapa, game_time)
    def is_inside_area(self, point: tuple) -> bool:
        # La mina solo puede causar daño si su estado es activo.
        if not self.is_active:
            return False
        
        # Si está activa, utiliza la misma lógica de su clase padre (CircularMine).
        return super().is_inside_area(point)

