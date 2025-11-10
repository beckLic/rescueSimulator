# Archivo: Visual/main.py

import pygame
from Visual import CONSTANTES
from src.map_manager import MapManager
from src.classes import load_resource_config, Jeep, Moto, Camion, Auto


pygame.init()
fuente_hud = pygame.font.SysFont("Arial", 30)
ventana = pygame.display.set_mode((CONSTANTES.ANCHO_VENTANA, CONSTANTES.ALTO_VENTANA))


RUTA_CONFIG = "config/default_config.json"
config = load_resource_config(RUTA_CONFIG)
mapa = MapManager(CONSTANTES.CANTIDAD_I, CONSTANTES.CANTIDAD_J, config)
pygame.display.set_caption("Rescue Simulator")



minaLineal=pygame.image.load("imagenes/minaLineal.png") # Corregí la barra \
minaMovil=pygame.image.load("imagenes/minaMovil.png")

game_time = 0 #tiempo del algoritmo
def dibujar_grid():
    for x in range(51):
        pygame.draw.line(ventana,CONSTANTES.COLOR_ROJO, (x*CONSTANTES.CELDA_ANCHO, 0), (x*CONSTANTES.CELDA_ANCHO, CONSTANTES.ALTO_VENTANA))
    for y in range(51):
        pygame.draw.line(ventana, CONSTANTES.COLOR_ROJO, (0, y*CONSTANTES.CELDA_ALTO), (CONSTANTES.ANCHO_VENTANA, y*CONSTANTES.CELDA_ALTO))



reloj = pygame.time.Clock()
run = True
#grupo de items
grupo_items = pygame.sprite.Group() 
grupo_vehiculos = pygame.sprite.Group()
# Cargar minas en el mapa y en el grupo
mapa.colocar_minas(grupo_items)
mapa._colocar_recursos(grupo_items)
#Botones
boton_init = pygame.Rect(50, 30, 120, 40)
boton_play = pygame.Rect(200, 30, 120, 40)
simulacion_iniciada = False
def dibujar_botones():
    pygame.draw.rect(ventana, (0, 200, 0), boton_init)
    pygame.draw.rect(ventana, (0, 0, 200), boton_play)
    fuente = pygame.font.SysFont(None, 24)
    ventana.blit(fuente.render("Init", True, (255,255,255)), (85, 40))
    ventana.blit(fuente.render("Play", True, (255,255,255)), (235, 40))
# --- Función para (re)iniciar la simulación ---
def inicializar_simulacion():
    global game_time
    game_time = 0
    print("Iniciando simulación...")
    mapa.puntaje_j1 = 0
    mapa.puntaje_j2 = 0
    # 1. Limpiar grupos
    grupo_items.empty()
    grupo_vehiculos.empty()
    
    
    mapa.generar_mapa_aleatorio(grupo_items)
    
    
    # --- Equipo 1 (Azul) ---
    base_jugador_1 = (5, 5) # (x, y) en grilla (esquina superior izquierda)
    
    jeep_ia_1 = Jeep(id="J-IA-1", jugador_id=1, pos_inicial=(0, 0), posicion_base=(0,0))
    moto_ia_1 = Moto(id="M-IA-1", jugador_id=1, pos_inicial=(0, 5), posicion_base=(0,5))
    camion_ia_1 = Camion(id="C-IA-1", jugador_id=1, pos_inicial=(0, 10), posicion_base=(0,10))
    auto_ia_1 = Auto(id="A-IA-1", jugador_id=1, pos_inicial=(0, 15), posicion_base=(0,15))

    # --- Equipo 2 (Rojo) ---
    # (El mapa es 50x50, así que usamos coordenadas opuestas)
    base_jugador_2 = (44, 44) # (x, y) en grilla (esquina inferior derecha)

    jeep_ia_2 = Jeep(id="J-IA-2", jugador_id=2, pos_inicial=(49, 0), posicion_base=base_jugador_2)
    moto_ia_2 = Moto(id="M-IA-2", jugador_id=2, pos_inicial=(49, 5), posicion_base=base_jugador_2)
    camion_ia_2 = Camion(id="C-IA-2", jugador_id=2, pos_inicial=(49, 10), posicion_base=base_jugador_2)
    auto_ia_2 = Auto(id="A-IA-2", jugador_id=2, pos_inicial=(49, 15), posicion_base=base_jugador_2)

    # 4. Añadirlos TODOS al grupo de vehículos
    grupo_vehiculos.add(
        jeep_ia_1, moto_ia_1, camion_ia_1, auto_ia_1,
        jeep_ia_2, moto_ia_2, camion_ia_2, auto_ia_2
    )

    print(f"Simulación inicializada con {len(grupo_vehiculos)} vehículos.")

def chequear_colisiones_vehiculos(grupo_vehiculos):
    """
    Revisa si dos vehículos ocupan la misma celda de la grilla y 
    los elimina si eso ocurre.
    """
    posiciones_ocupadas = {} # Almacena { (x,y) : vehiculo }
    vehiculos_a_eliminar = set() # Usamos un set para evitar duplicados

    # Iteramos sobre una copia .sprites() para poder modificar el grupo
    for vehiculo in grupo_vehiculos.sprites():
        # La posición es un Vector2, la convertimos en tupla para usarla como clave
        pos_tuple = (int(vehiculo.posicion.x), int(vehiculo.posicion.y))

        if pos_tuple in posiciones_ocupadas:
            # ¡Colisión detectada!
            otro_vehiculo = posiciones_ocupadas[pos_tuple]
            print(f"¡COLISIÓN en {pos_tuple} entre {vehiculo.id} y {otro_vehiculo.id}!")
            
            # Añadir ambos vehículos al set de eliminación
            vehiculos_a_eliminar.add(vehiculo)
            vehiculos_a_eliminar.add(otro_vehiculo)
        else:
            # Esta celda ahora está ocupada por este vehículo
            posiciones_ocupadas[pos_tuple] = vehiculo
    
    # Eliminar todos los vehículos que colisionaron
    for vehiculo in vehiculos_a_eliminar:
        vehiculo.kill() # .kill() los elimina de CUALQUIER grupo al que pertenezcan


# --- INICIO DEL BUCLE PRINCIPAL ---
run = True
simulacion_iniciada = False
inicializar_simulacion()
while run:
    reloj.tick(20)#FPS
    game_time += 1
    ventana.fill(CONSTANTES.COLOR_NEGRO)
    dibujar_grid()

    
    grupo_items.draw(ventana)
    grupo_vehiculos.draw(ventana)
    for item in grupo_items:
        if hasattr(item, 'draw_radius'):
            item.draw_radius(ventana)

   

    # Eventos (cerrar ventana)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not simulacion_iniciada:
                if boton_init.collidepoint(event.pos):
                    # Cuando se hace clic en Init
                    inicializar_simulacion() # Usamos la función para reiniciar todo
                    
                elif boton_play.collidepoint(event.pos):
                    simulacion_iniciada = True
                    print("Simulación iniciada")
    
    if simulacion_iniciada:
            
            # 1. Actualiza la IA de los vehículos (aquí cambian su self.posicion)
            grupo_vehiculos.update(mapa, game_time,grupo_vehiculos)
            
            # 2. Chequear colisiones entre vehículos DESPUÉS de que se movieron
            chequear_colisiones_vehiculos(grupo_vehiculos)
            
            # 3. Actualiza los items (para colisiones con minas/recursos)
            #    Los vehículos destruidos en el paso 2 ya no existen en
            #    grupo_vehiculos, así que no chocarán con minas.
            grupo_items.update(grupo_vehiculos, mapa, game_time)
            
    # Dibujar HUD de Puntajes
    texto_j1 = fuente_hud.render(f"Equipo Azul: {mapa.puntaje_j1}", True, (100, 150, 255)) # Azul
    texto_j2 = fuente_hud.render(f"Equipo Rojo: {mapa.puntaje_j2}", True, (255, 100, 100)) # Rojo
    
    # Dibujamos un fondo oscuro para el HUD
    pygame.draw.rect(ventana, (0,0,0), (345, 20, 250, 65))
    
    ventana.blit(texto_j1, (350, 25))
    ventana.blit(texto_j2, (350, 55))
    dibujar_botones()
    pygame.display.update()

pygame.quit()

    #Debuggin
