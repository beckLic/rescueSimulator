# Archivo: Visual/main.py

import pygame
from Visual import CONSTANTES
from src.map_manager import MapManager
from src.classes import load_resource_config, Jeep, Moto, Camion, Auto
import csv
import os

pygame.init()
fuente_hud = pygame.font.SysFont("Arial", 30)
ventana = pygame.display.set_mode((CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.VENTANA_ALTO_TOTAL))

RUTA_CONFIG = "config/default_config.json"
config = load_resource_config(RUTA_CONFIG)
mapa = MapManager(CONSTANTES.CANTIDAD_I, CONSTANTES.CANTIDAD_J, config)
pygame.display.set_caption("Rescue Simulator")
simulacion_iniciada = False
simulacion_pausada = False
simulacion_finalizada = False
modo_replay = False
modo_record = False
recorder_file = None
replay_desde_grabacion = False

minaLineal=pygame.image.load("imagenes/minaLineal.png") # Corregí la barra \
minaMovil=pygame.image.load("imagenes/minaMovil.png")
img_explosion = pygame.image.load("imagenes/explosion.png").convert_alpha()
grupo_explosiones = pygame.sprite.Group() # Grupo para animaciones
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
# Fila superior
boton_init   = pygame.Rect(50,  CONSTANTES.MAPA_ALTO + 5, 120, 40)
boton_play   = pygame.Rect(190, CONSTANTES.MAPA_ALTO + 5, 120, 40)
boton_stop = pygame.Rect(1000, CONSTANTES.MAPA_ALTO + 55, 100, 40) 
boton_prev = pygame.Rect(900, CONSTANTES.MAPA_ALTO + 55, 40, 40)  # "<<"
boton_next = pygame.Rect(950, CONSTANTES.MAPA_ALTO + 55, 40, 40)  # ">>"
# Fila inferior
boton_replay = pygame.Rect(50, CONSTANTES.MAPA_ALTO + 55, 260, 40)  # Más ancho para texto largo
modo_replay_activado = False  # ← NUEVA variable global para toggle
boton_ver_replay = pygame.Rect(620, CONSTANTES.MAPA_ALTO + 5, 140, 40)


def dibujar_controles(finalizada):
    """
    Dibuja los controles de la UI (botones izquierdos).
    Muestra "Init" siempre.
    Muestra "Play" solo si el juego NO ha terminado.
    """
    
    fuente_botones = pygame.font.SysFont(None, 24)

    # Botón Init (verde)
    pygame.draw.rect(ventana, (0, 200, 0), boton_init)
    texto_init = fuente_botones.render("Init", True, (255, 255, 255))
    ventana.blit(fuente_botones.render("Init", True, (255,255,255)), (85, CONSTANTES.MAPA_ALTO + 20))
    # Botón Play/Pause
    texto_play_str = "Pause" if not simulacion_pausada else "Play"
    if not simulacion_iniciada and not finalizada:
        # ANTES DE INICIAR: Mostrar "Play" y "Replay Toggle"
        
        # Botón Play
        pygame.draw.rect(ventana, (0, 0, 200), boton_play)
        texto_play = fuente_botones.render("Play", True, (0, 0, 0))
        ventana.blit(fuente_botones.render("Play", True, (255,255,255)), (225, CONSTANTES.MAPA_ALTO + 20))
        
        # Botón Replay Toggle
        texto_replay = "REPLAY: SÍ" if modo_replay_activado else "REPLAY: NO"
        color_replay = (0, 150, 0) if modo_replay_activado else (150, 0, 0)
        pygame.draw.rect(ventana, color_replay, boton_replay)
        ventana.blit(fuente_botones.render(texto_replay, True, (255,255,255)), (boton_replay.x + 20, boton_replay.y + 10))
    
    elif simulacion_iniciada and not finalizada:
        # DURANTE LA SIMULACIÓN: Mostrar "Pause" / "Play" (para reanudar)
        
        texto_play_str = "Pause" if not simulacion_pausada else "Play"
        color_boton_play = (255, 165, 0) # Naranja para Pausa
        if simulacion_pausada:
            color_boton_play = (0, 200, 0) # Verde para Reanudar
            
        pygame.draw.rect(ventana, color_boton_play, boton_play)
        ventana.blit(fuente_botones.render(texto_play_str, True, (255,255,255)), (225, CONSTANTES.MAPA_ALTO + 20))

    # --- Mostrar "Ver Replay" solo al final ---
    if finalizada and modo_replay_activado:
        pygame.draw.rect(ventana, (100, 100, 100), boton_ver_replay)
        ventana.blit(fuente_botones.render("Ver Replay", True, (255,255,255)), (boton_ver_replay.x + 10, boton_ver_replay.y + 10))
    
    # --- Estos botones deben estar AFUERA, SIEMPRE VISIBLES ---

    # Botón Stop (Reset)
    pygame.draw.rect(ventana, (200, 0, 0), boton_stop)
    texto_stop = fuente_botones.render("Reset", True, (255, 255, 255))
    ventana.blit(texto_stop, (boton_stop.x + 30, boton_stop.y + 10))

    # Botón Prev "<<"
    pygame.draw.rect(ventana, (0, 100, 200), boton_prev)
    texto_prev = fuente_botones.render("<<", True, (255, 255, 255))
    ventana.blit(texto_prev, (boton_prev.x + 10, boton_prev.y + 10))

    # Botón Next ">>"
    pygame.draw.rect(ventana, (0, 100, 200), boton_next)
    texto_next = fuente_botones.render(">>", True, (255, 255, 255))
    ventana.blit(texto_next, (boton_next.x + 10, boton_next.y + 10))# --- Función para (re)iniciar la simulación ---
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
    
    # 3 Jeeps
    grupo_vehiculos.add(Jeep(id="J1-IA-1", jugador_id=1, pos_inicial=(5, 5), posicion_base=base_jugador_1))
    grupo_vehiculos.add(Jeep(id="J2-IA-1", jugador_id=1, pos_inicial=(5, 6), posicion_base=base_jugador_1))
    grupo_vehiculos.add(Jeep(id="J3-IA-1", jugador_id=1, pos_inicial=(5, 7), posicion_base=base_jugador_1))
    # 2 Motos
    grupo_vehiculos.add(Moto(id="M1-IA-1", jugador_id=1, pos_inicial=(6, 5), posicion_base=base_jugador_1))
    grupo_vehiculos.add(Moto(id="M2-IA-1", jugador_id=1, pos_inicial=(6, 6), posicion_base=base_jugador_1))
    # 2 Camiones
    grupo_vehiculos.add(Camion(id="C1-IA-1", jugador_id=1, pos_inicial=(7, 5), posicion_base=base_jugador_1))
    grupo_vehiculos.add(Camion(id="C2-IA-1", jugador_id=1, pos_inicial=(7, 6), posicion_base=base_jugador_1))
    # 3 Autos
    grupo_vehiculos.add(Auto(id="A1-IA-1", jugador_id=1, pos_inicial=(8, 5), posicion_base=base_jugador_1))
    grupo_vehiculos.add(Auto(id="A2-IA-1", jugador_id=1, pos_inicial=(8, 6), posicion_base=base_jugador_1))
    grupo_vehiculos.add(Auto(id="A3-IA-1", jugador_id=1, pos_inicial=(8, 7), posicion_base=base_jugador_1))
    
    # --- Equipo 2 (Rojo) ---
    base_jugador_2 = (44, 44) # (x, y) en grilla (esquina inferior derecha)
    
    # 3 Jeeps
    grupo_vehiculos.add(Jeep(id="J1-IA-2", jugador_id=2, pos_inicial=(44, 44), posicion_base=base_jugador_2))
    grupo_vehiculos.add(Jeep(id="J2-IA-2", jugador_id=2, pos_inicial=(44, 43), posicion_base=base_jugador_2))
    grupo_vehiculos.add(Jeep(id="J3-IA-2", jugador_id=2, pos_inicial=(44, 42), posicion_base=base_jugador_2))
    # 2 Motos
    grupo_vehiculos.add(Moto(id="M1-IA-2", jugador_id=2, pos_inicial=(43, 44), posicion_base=base_jugador_2))
    grupo_vehiculos.add(Moto(id="M2-IA-2", jugador_id=2, pos_inicial=(43, 43), posicion_base=base_jugador_2))
    # 2 Camiones
    grupo_vehiculos.add(Camion(id="C1-IA-2", jugador_id=2, pos_inicial=(42, 44), posicion_base=base_jugador_2))
    grupo_vehiculos.add(Camion(id="C2-IA-2", jugador_id=2, pos_inicial=(42, 43), posicion_base=base_jugador_2))
    # 3 Autos
    grupo_vehiculos.add(Auto(id="A1-IA-2", jugador_id=2, pos_inicial=(41, 44), posicion_base=base_jugador_2))
    grupo_vehiculos.add(Auto(id="A2-IA-2", jugador_id=2, pos_inicial=(41, 43), posicion_base=base_jugador_2))
    grupo_vehiculos.add(Auto(id="A3-IA-2", jugador_id=2, pos_inicial=(41, 42), posicion_base=base_jugador_2))
  
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

def cargar_datos_replay(path="replay.csv"):
    datos = {}
    try:
        with open(path, newline='') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                frame = int(fila["frame"])
                id_vehiculo = fila["id"]
                x = int(fila["x"])
                y = int(fila["y"])
                if frame not in datos:
                    datos[frame] = []
                datos[frame].append((id_vehiculo, x, y))
        print(f"[DEBUG] Replay cargado con {len(datos)} frames.")
    except Exception as e:
        print(f"[ERROR] al leer replay.csv: {e}")
        return None
    return datos

def inicializar_replay(datos_replay):
    grupo_vehiculos.empty()
    
    if not datos_replay:
        print("[ERROR] Replay está vacío. No se puede inicializar.")
        return False  # <- IMPORTANTE

    frame_inicial = min(datos_replay.keys())

    for id_vehiculo, x, y in datos_replay[frame_inicial]:
        if id_vehiculo.startswith("J"):
            v = Jeep(id=id_vehiculo, jugador_id=1 if "1" in id_vehiculo else 2, pos_inicial=(x, y), posicion_base=(x, y))
        elif id_vehiculo.startswith("M"):
            v = Moto(id=id_vehiculo, jugador_id=1 if "1" in id_vehiculo else 2, pos_inicial=(x, y), posicion_base=(x, y))
        elif id_vehiculo.startswith("C"):
            v = Camion(id=id_vehiculo, jugador_id=1 if "1" in id_vehiculo else 2, pos_inicial=(x, y), posicion_base=(x, y))
        elif id_vehiculo.startswith("A"):
            v = Auto(id=id_vehiculo, jugador_id=1 if "1" in id_vehiculo else 2, pos_inicial=(x, y), posicion_base=(x, y))
        else:
            continue
        grupo_vehiculos.add(v)

    return True  # <- Indica que sí se pudo cargar correctamente

# --- INICIO DEL BUCLE PRINCIPAL ---
run = True
simulacion_iniciada = False
inicializar_simulacion()
while run:
    reloj.tick(10)#FPS
    
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
            if not simulacion_iniciada:
                if boton_init.collidepoint(event.pos):
                    inicializar_simulacion() # Resetea todo
                
                elif boton_replay.collidepoint(event.pos):
                    modo_replay_activado = not modo_replay_activado
                    print(f"[DEBUG] Modo REPLAY {'activado' if modo_replay_activado else 'desactivado'}")
                elif boton_play.collidepoint(event.pos) and not simulacion_iniciada and not simulacion_finalizada:
                    if not simulacion_iniciada and not simulacion_finalizada:
                        # Iniciar simulación
                        simulacion_iniciada = True
                        simulacion_pausada = False
                        print("Simulación iniciada")

                        if modo_replay_activado:
                            try:
                                recorder_file = open("replay.csv", "w")
                                recorder_file.write("frame,id,x,y\n")
                                modo_record = True
                                replay_desde_grabacion = True
                                print("[DEBUG] Grabación iniciada")
                            except Exception as e:
                                print(f"[ERROR] No se pudo iniciar el archivo de replay: {e}")
                                recorder_file = None
                                modo_record = False
                    elif simulacion_iniciada and not simulacion_finalizada:
                        # Pausar o reanudar
                        simulacion_pausada = not simulacion_pausada
                        print(f"Simulación {'pausada' if simulacion_pausada else 'reanudada'}")

                      
                # El botón 'Play' solo funciona si el juego NO ha iniciado Y NO ha finalizado
                
                elif boton_ver_replay.collidepoint(event.pos) and not simulacion_iniciada and simulacion_finalizada and modo_replay_activado:
                    try:
                        datos_replay = cargar_datos_replay("replay.csv")
                        if datos_replay:
                            inicializar_replay(datos_replay)
                            simulacion_iniciada = True
                            modo_replay = True
                            frame_actual = 1
                            print("[DEBUG] Reproducción de Replay iniciada")
                        else:
                            print("[ERROR] Replay vacío, no se puede reproducir.")
                    except Exception as e:
                        print(f"[ERROR] No se pudo cargar el replay: {e}")
            else: # Si la simulación YA está iniciada
                if boton_play.collidepoint(event.pos):
                    simulacion_pausada = not simulacion_pausada # Toggle pausa
                    print(f"Simulación {'pausada' if simulacion_pausada else 'reanudada'}")
            if boton_stop.collidepoint(event.pos):
                    print("Simulación detenida y reseteada.")
                    simulacion_iniciada = False
                    simulacion_pausada = False
                    modo_replay = False # Asegúrate de resetear esto también
                    modo_record = False
                    if recorder_file:
                        recorder_file.close()
                        recorder_file = None
                    inicializar_simulacion() # Resetea todo

            if boton_prev.collidepoint(event.pos):
                    print("Botón '<<' (Frame Anterior) presionado. Lógica no implementada.")

            if boton_next.collidepoint(event.pos):
                    print("Botón '>>' (Frame Siguiente) presionado. Lógica no implementada.")
                                        
    


    
    # --- Lógica de Simulación ---
    if simulacion_iniciada:
            if not simulacion_pausada:
                game_time += 1
                # 1. Actualiza la IA de los vehículos
                grupo_vehiculos.update(mapa, game_time,grupo_vehiculos)

                # Guardar frame actual si está activado el modo_record
                if modo_record and recorder_file:
                    for vehiculo in grupo_vehiculos:
                        x = int(vehiculo.posicion.x)
                        y = int(vehiculo.posicion.y)
                        recorder_file.write(f"{game_time},{vehiculo.id},{x},{y}\n")

                if modo_replay:
                    if frame_actual in datos_replay:
                        # Limpiar posiciones actuales
                        for vehiculo in grupo_vehiculos:
                            vehiculo.posicion.x = -1
                            vehiculo.posicion.y = -1

                        # Actualizar posiciones desde el frame actual
                        for id, x, y in datos_replay[frame_actual]:
                            for vehiculo in grupo_vehiculos:
                                if vehiculo.id == id:
                                    vehiculo.posicion.x = x
                                    vehiculo.posicion.y = y
                                    vehiculo._actualizar_posicion_pixel((x, y), (x, y))  # <- ESTA LÍNEA AGREGA
                                    break
                        frame_actual += 1

                # 2. Chequear colisiones entre vehículos
                chequear_colisiones_vehiculos(grupo_vehiculos)
                
                # 3. Actualiza los items (para colisiones con minas/recursos)
                grupo_items.update(grupo_vehiculos, mapa, game_time)
                colisiones_vehiculos = pygame.sprite.groupcollide(grupo_vehiculos, grupo_vehiculos, False, False)

                vehiculos_a_destruir = set()

                for v1, lista_colisiones in colisiones_vehiculos.items():
                    for v2 in lista_colisiones:
                        # Evitar colisión consigo mismo
                        if v1 != v2: 
                            # Registrar ambos para destrucción
                            vehiculos_a_destruir.add(v1)
                            vehiculos_a_destruir.add(v2)

                # Destruir vehículos (fuera del bucle de detección)
                for v in vehiculos_a_destruir:
                    if not v.destruido:
                        v.destruir()
                        # (Aquí es donde mostrarías la imagen de explosión)
                        # p.ej: explosion_sprite = Explosion(v.rect.center, img_explosion)
                        #      grupo_explosiones.add(explosion_sprite)
                # 4.Chequear condiciones de fin de juego
                # Un grupo de sprites vacío evalúa como False
                if not mapa.resources or not grupo_vehiculos:
                    simulacion_iniciada = False
                    simulacion_finalizada = True
                    print(f"¡Simulación finalizada! Recursos: {len(mapa.resources)}, Vehículos: {len(grupo_vehiculos)}")
                    if recorder_file:
                        if replay_desde_grabacion:
                            if os.path.exists("replay.csv"):
                                with open("replay.csv", "r") as f:
                                    lines = f.readlines()
                                if len(lines) <= 1:
                                    os.remove("replay.csv")
                                    print("[DEBUG] Replay vacío eliminado.")
                            recorder_file.close()
                            print("[DEBUG] Archivo replay.csv guardado y cerrado.")
                        recorder_file = None
                        modo_record = False

            
    # Archivo: Visual/main.py

# (Busca y REEMPLAZA la última sección del bucle 'while run:')

    # --- Dibujar HUD (MODIFICADO) ---
    
    # Puntajes (lado izquierdo/centro)
    texto_j1 = fuente_hud.render(f"Equipo Azul: {mapa.puntaje_j1}", True, (100, 150, 255))
    texto_j2 = fuente_hud.render(f"Equipo Rojo: {mapa.puntaje_j2}", True, (255, 100, 100))
    
    pygame.draw.rect(ventana, (0,0,0), (345, CONSTANTES.MAPA_ALTO + 20, 250, 65))
    
    ventana.blit(texto_j1, (350, CONSTANTES.MAPA_ALTO + 25))
    ventana.blit(texto_j2, (350, CONSTANTES.MAPA_ALTO + 55))
    
    # Controles (botones en el lado izquierdo)
    dibujar_controles(simulacion_finalizada)

    # --- (NUEVO) Dibujar Ganador (lado derecho) ---
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
        
        # Calcular posición en la DERECHA del HUD
        # Usamos .get_rect() para alinear el texto a la derecha
        
        # Posición X: El ancho total de la ventana menos un margen de 50px
        pos_x_derecha = CONSTANTES.VENTANA_ANCHO_TOTAL - 50 
        
        # Posición Y: Centrado verticalmente en el panel del HUD
        pos_y_centro_hud = CONSTANTES.MAPA_ALTO + (CONSTANTES.UI_ALTO / 2)
        
        # Crear el rectángulo del texto y posicionarlo
        rect_ganador = texto_ganador.get_rect(centery=pos_y_centro_hud, right=pos_x_derecha)
        
        # Dibujar el texto en la ventana
        ventana.blit(texto_ganador, rect_ganador)

        # Dibujar control de ver replay
        dibujar_controles(simulacion_finalizada)

    
    if modo_replay and simulacion_iniciada:
        total_frames = max(datos_replay.keys())
        texto_replay = fuente_hud.render(f"REPLAY EN CURSO... Frame {frame_actual}/{total_frames}", True, (255, 255, 100))
        ventana.blit(texto_replay, (CONSTANTES.VENTANA_ANCHO_TOTAL - 400, 10))
    elif modo_replay and simulacion_finalizada:
        texto_replay = fuente_hud.render("REPLAY FINALIZADO", True, (255, 100, 100))
        ventana.blit(texto_replay, (CONSTANTES.VENTANA_ANCHO_TOTAL - 400, 10))

    pygame.display.update()

pygame.quit()
    #Debuggin
