# Archivo: Visual/main.py

import pygame
from Visual import CONSTANTES
from src.map_manager import MapManager
from src.classes import load_resource_config, Jeep, Moto, Camion, Auto


pygame.init()
fuente_hud = pygame.font.SysFont("Arial", 30)
ventana = pygame.display.set_mode((CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.VENTANA_ALTO_TOTAL))

RUTA_CONFIG = "config/default_config.json"
config = load_resource_config(RUTA_CONFIG)
mapa = MapManager(CONSTANTES.CANTIDAD_I, CONSTANTES.CANTIDAD_J, config)
pygame.display.set_caption("Rescue Simulator")

simulacion_finalizada = False

minaLineal=pygame.image.load("imagenes/minaLineal.png") # Corregí la barra \
minaMovil=pygame.image.load("imagenes/minaMovil.png")

game_time = 0 #tiempo del algoritmo
def dibujar_grid():
    # El grid solo se dibuja hasta el alto del MAPA
    for x in range(51):
        pygame.draw.line(ventana,CONSTANTES.COLOR_ROJO, (x*CONSTANTES.CELDA_ANCHO, 0), (x*CONSTANTES.CELDA_ANCHO, CONSTANTES.MAPA_ALTO))
    for y in range(51):
        pygame.draw.line(ventana, CONSTANTES.COLOR_ROJO, (0, y*CONSTANTES.CELDA_ALTO), (CONSTANTES.MAPA_ANCHO, y*CONSTANTES.CELDA_ALTO))


reloj = pygame.time.Clock()
run = True
#grupo de items
grupo_items = pygame.sprite.Group() 
grupo_vehiculos = pygame.sprite.Group()
# Cargar minas en el mapa y en el grupo
mapa.colocar_minas(grupo_items)
mapa._colocar_recursos(grupo_items)
# Botones: Movemos la coordenada Y al panel de UI (MAPA_ALTO + offset)
boton_init = pygame.Rect(50, CONSTANTES.MAPA_ALTO + 30, 120, 40)
boton_play = pygame.Rect(200, CONSTANTES.MAPA_ALTO + 30, 120, 40)
simulacion_iniciada = False
def dibujar_controles(finalizada):
    """
    Dibuja los controles de la UI (botones izquierdos).
    Muestra "Init" siempre.
    Muestra "Play" solo si el juego NO ha terminado.
    """
    fuente_botones = pygame.font.SysFont(None, 24)
    
    # Botón Init (siempre se dibuja)
    pygame.draw.rect(ventana, (0, 200, 0), boton_init)
    ventana.blit(fuente_botones.render("Init", True, (255,255,255)), (85, CONSTANTES.MAPA_ALTO + 40))

    # Botón Play (solo si el juego no ha terminado)
    if not finalizada:
        pygame.draw.rect(ventana, (0, 0, 200), boton_play)
        ventana.blit(fuente_botones.render("Play", True, (255,255,255)), (235, CONSTANTES.MAPA_ALTO + 40))
# --- Función para (re)iniciar la simulación ---
def inicializar_simulacion():
    global game_time, simulacion_finalizada
    game_time = 0
    simulacion_finalizada = False
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

    jeep_ia_2 = Jeep(id="J-IA-2", jugador_id=2, pos_inicial=(0, 30), posicion_base=(0, 30))
    moto_ia_2 = Moto(id="M-IA-2", jugador_id=2, pos_inicial=(0, 35), posicion_base=(0, 35))
    camion_ia_2 = Camion(id="C-IA-2", jugador_id=2, pos_inicial=(0, 40), posicion_base=(0, 40))
    auto_ia_2 = Auto(id="A-IA-2", jugador_id=2, pos_inicial=(0, 45), posicion_base=(0, 45))

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
    reloj.tick(5)#FPS
    game_time += 1
    ventana.fill(CONSTANTES.COLOR_NEGRO)
    # Dibujamos el fondo del panel de UI
    # (Un gris oscuro, por ejemplo)
    color_panel_ui = (30, 30, 30)
    pygame.draw.rect(ventana, color_panel_ui, (0, CONSTANTES.MAPA_ALTO, CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.UI_ALTO))
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
            # El botón 'Init' funciona siempre y resetea el juego
            if boton_init.collidepoint(event.pos):
                inicializar_simulacion() # Resetea todo, incl. simulacion_finalizada
                    
            # El botón 'Play' solo funciona si el juego NO ha iniciado Y NO ha finalizado
            elif boton_play.collidepoint(event.pos) and not simulacion_iniciada and not simulacion_finalizada:
                simulacion_iniciada = True
                print("Simulación iniciada")
    
    # --- Lógica de Simulación ---
    if simulacion_iniciada:
            
            # 1. Actualiza la IA de los vehículos
            grupo_vehiculos.update(mapa, game_time,grupo_vehiculos)
            
            # 2. Chequear colisiones entre vehículos
            chequear_colisiones_vehiculos(grupo_vehiculos)
            
            # 3. Actualiza los items (para colisiones con minas/recursos)
            grupo_items.update(grupo_vehiculos, mapa, game_time)
            
            # 4.Chequear condiciones de fin de juego
            # Un grupo de sprites vacío evalúa como False
            if not mapa.resources or not grupo_vehiculos:
                simulacion_iniciada = False
                simulacion_finalizada = True
                print(f"¡Simulación finalizada! Recursos: {len(mapa.resources)}, Vehículos: {len(grupo_vehiculos)}")

            
    # Archivo: Visual/main.py


    # --- Dibujar HUD ---
    
    # Puntajes (lado izquierdo/centro)
    texto_j1 = fuente_hud.render(f"Equipo Azul: {mapa.puntaje_j1}", True, (100, 150, 255))
    texto_j2 = fuente_hud.render(f"Equipo Rojo: {mapa.puntaje_j2}", True, (255, 100, 100))
    
    pygame.draw.rect(ventana, (0,0,0), (345, CONSTANTES.MAPA_ALTO + 20, 250, 65))
    
    ventana.blit(texto_j1, (350, CONSTANTES.MAPA_ALTO + 25))
    ventana.blit(texto_j2, (350, CONSTANTES.MAPA_ALTO + 55))
    
    # Controles
    dibujar_controles(simulacion_finalizada)

    # --- Dibujar Ganador ---
    if simulacion_finalizada:
        texto_str = ""
        color_texto = (255, 255, 255) # Blanco por defecto
        
        if mapa.puntaje_j1 > mapa.puntaje_j2:
            texto_str = "¡Gana Equipo Azul!"
            color_texto = (100, 150, 255) # Azul
        elif mapa.puntaje_j2 > mapa.puntaje_j1:
            texto_str = "¡Gana Equipo Rojo!"
            color_texto = (255, 100, 100) # Rojo
        else:
            texto_str = "¡Empate!"
            color_texto = (255, 255, 255) # Blanco

        # Renderizar texto del ganador
        texto_ganador = fuente_hud.render(texto_str, True, color_texto)
        
        # Posición X: El ancho total de la ventana menos un margen de 50px
        pos_x_derecha = CONSTANTES.VENTANA_ANCHO_TOTAL - 50 
        
        # Posición Y: Centrado verticalmente en el panel del HUD
        pos_y_centro_hud = CONSTANTES.MAPA_ALTO + (CONSTANTES.UI_ALTO / 2)
        
        # Crear el rectángulo del texto y posicionarlo
        rect_ganador = texto_ganador.get_rect(centery=pos_y_centro_hud, right=pos_x_derecha)
        
        # Dibujar el texto en la ventana
        ventana.blit(texto_ganador, rect_ganador)

    
    pygame.display.update()

pygame.quit()
    #Debuggin
