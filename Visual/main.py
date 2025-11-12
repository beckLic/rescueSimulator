# Archivo: Visual/main.py

import pygame
from Visual import CONSTANTES
from src.map_manager import MapManager
from src.game_engine import GameEngine
from src.classes import load_resource_config,Vehiculo, Jeep, Moto, Camion, Auto, Explosion, Recurso
import csv
import os
import gzip
import random

pygame.init()
fuente_hud = pygame.font.SysFont("Arial", 30)
ventana = pygame.display.set_mode((CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.VENTANA_ALTO_TOTAL))

RUTA_CONFIG = "config/default_config.json"
config = load_resource_config(RUTA_CONFIG)
mapa = MapManager(CONSTANTES.CANTIDAD_I, CONSTANTES.CANTIDAD_J, config)
pygame.display.set_caption("Rescue Simulator")
engine = GameEngine()
simulacion_iniciada = False
simulacion_pausada = False
simulacion_finalizada = False
modo_replay = False
modo_record = False
recorder_file = None
replay_desde_grabacion = False
datos_replay = {}
frame_actual = 0
max_frame = 0
replay_pausado = False
semilla_actual = None
frames_todos_inactivos = 0
minaLineal=pygame.image.load("imagenes/minaLineal.png") # Corregí la barra \
minaMovil=pygame.image.load("imagenes/minaMovil.png")
img_explosion = pygame.image.load("imagenes/explosion.png").convert_alpha()
img_explosion = pygame.transform.scale(img_explosion, (CONSTANTES.CELDA_ANCHO, CONSTANTES.CELDA_ALTO))
grupo_explosiones = pygame.sprite.Group() # Grupo para animaciones
Vehiculo.set_assets_explosiones(img_explosion, grupo_explosiones)
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
frame_step_live = False

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
    # Botón Play/Pausa
    texto_play_str = "Pausa" if not simulacion_pausada else "Play"
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
        # DURANTE LA SIMULACIÓN: Mostrar "Pausa" / "Play" (para reanudar)
        
        texto_play_str = "Pausa" if not simulacion_pausada else "Renaudar"
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
def inicializar_simulacion(semilla=None):
    global game_time, simulacion_finalizada, grupo_vehiculos, engine,semilla_actual
    if semilla is None:
        semilla_actual = random.randint(0, 999999) # Crea una nueva semilla
        print(f"Generando NUEVA simulación con semilla: {semilla_actual}")
    else:
        semilla_actual = semilla # Reutiliza la semilla anterior
        print(f"Cargando simulación con semilla: {semilla_actual}")
    
    random.seed(semilla_actual)
    game_time = 0
    simulacion_finalizada = False
    print("Iniciando simulación...")
    
    mapa.puntaje_j1 = 0
    mapa.puntaje_j2 = 0
    # 1. Limpiar grupos
    grupo_items.empty()
    
    
    
    mapa.generar_mapa_aleatorio(grupo_items)
    grupo_vehiculos = engine._crear_vehiculos()
    
   
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
        vehiculo.destruir() # .kill() los elimina de CUALQUIER grupo al que pertenezcan

def cargar_datos_replay(path="replay.csv"):
    datos = {}
    try:
        with gzip.open(path, "rt", encoding="utf-8", newline='') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                frame = int(fila["frame"])
                if frame not in datos:
                    datos[frame] = {'vehiculos': [], 'score': (0, 0)}
                id_vehiculo = fila["id"]
                jugador_id = int(fila["jugador"])
                x = int(fila["x"])
                y = int(fila["y"])
                if frame not in datos:
                    datos[frame] = []
                datos[frame]['vehiculos'].append((id_vehiculo, jugador_id, x, y))
                score_j1 = int(fila["score_j1"])
                score_j2 = int(fila["score_j2"])
                datos[frame]['score'] = (score_j1, score_j2)
        print(f"[DEBUG] Replay cargado con {len(datos)} frames.")
    except Exception as e:
        print(f"[ERROR] al leer replay.csv: {e}")
        return None
    return datos

def inicializar_replay(datos_replay):
    inicializar_simulacion(semilla=semilla_actual) 
    grupo_vehiculos.empty()
    
    if not datos_replay:
        print("[ERROR] Replay está vacío. No se puede inicializar.")
        return False  # <- IMPORTANTE

    frame_inicial = min(datos_replay.keys())

    for id_vehiculo, jugador_id, x, y in datos_replay[frame_inicial]['vehiculos']:
        if id_vehiculo.startswith("J"):
            v = Jeep(id=id_vehiculo, jugador_id=jugador_id, pos_inicial=(x, y), posicion_base=(x, y))
        elif id_vehiculo.startswith("M"):
            v = Moto(id=id_vehiculo, jugador_id=jugador_id, pos_inicial=(x, y), posicion_base=(x, y))
        elif id_vehiculo.startswith("C"):
            v = Camion(id=id_vehiculo, jugador_id=jugador_id, pos_inicial=(x, y), posicion_base=(x, y))
        elif id_vehiculo.startswith("A"):
            v = Auto(id=id_vehiculo, jugador_id=jugador_id, pos_inicial=(x, y), posicion_base=(x, y))
        else:
            continue
        grupo_vehiculos.add(v)

    return True  # <- Indica que sí se pudo cargar correctamente


def dibujar_bases(surface, vehiculos):
    """
    Dibuja un cuadrado blanco en la celda base de cada vehículo.
    """
    COLOR_BASE = (255, 255, 255) # Blanco
    
    for v in vehiculos:
        # 1. Obtener la celda base (x, y) del vehículo
        base_x_grid, base_y_grid = v.posicion_base
        
        # 2. Convertir celda a píxeles
        pixel_x = base_x_grid * CONSTANTES.CELDA_ANCHO
        pixel_y = base_y_grid * CONSTANTES.CELDA_ALTO
        
        # 3. Crear el rectángulo para esa celda
        base_rect = pygame.Rect(pixel_x, pixel_y, CONSTANTES.CELDA_ANCHO, CONSTANTES.CELDA_ALTO)
        
        # 4. Dibujar el rectángulo
        pygame.draw.rect(surface, COLOR_BASE, base_rect)


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
    dibujar_bases(ventana, grupo_vehiculos)

    
    grupo_items.draw(ventana)
    grupo_vehiculos.draw(ventana)
    grupo_explosiones.draw(ventana)
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
                                # --- MODIFICADO: Usamos 'replay.csv.gz' ---
                                # (Asegúrate de importar 'gzip' al inicio de tu main.py)
                                # import gzip 
                                recorder_file = gzip.open("replay.csv.gz", "wt", encoding="utf-8")
                                # Escribimos el encabezado del CSV 
                                recorder_file.write("frame,id,jugador,x,y,score_j1,score_j2\n")
                                modo_record = True
                                print("[DEBUG] Grabación iniciada en 'replay.csv.gz'")
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
                        datos_replay = cargar_datos_replay("replay.csv.gz") 
                        if datos_replay:
                            if inicializar_replay(datos_replay): # Comprueba si la inicialización fue exitosa
                                simulacion_iniciada = True
                                modo_replay = True
                                frame_actual = min(datos_replay.keys())
                                max_frame = max(datos_replay.keys())
                                replay_pausado = True
                                print(f"[DEBUG] Reproducción de Replay iniciada. Frames: {frame_actual} a {max_frame}")
                            else:
                                print("[ERROR] Replay vacío o corrupto, no se puede reproducir.")
                        else:
                            print("[ERROR] No se pudo cargar el replay (vacío).")
                    except Exception as e:
                        print(f"[ERROR] No se pudo cargar el replay: {e}")
            else: # Si la simulación YA está iniciada
                if boton_play.collidepoint(event.pos):
                    if modo_replay:
                        # En modo replay, 'Play' controla la reproducción automática
                        replay_pausado = not replay_pausado
                        print(f"Replay {'pausado' if replay_pausado else 'reanudado'}")
                    else:
                        # En simulación normal, controla la pausa del motor
                        simulacion_pausada = not simulacion_pausada 
                        print(f"Simulación {'pausada' if simulacion_pausada else 'reanudada'}")
                if modo_replay: # Estos botones SOLO funcionan en modo replay
                    if boton_prev.collidepoint(event.pos):
                        frame_actual = max(0, frame_actual - 1)
                        print(f"Replay: Viendo frame {frame_actual}")

                    if boton_next.collidepoint(event.pos):
                        frame_actual = min(frame_actual + 1, max_frame)
                        print(f"Replay: Viendo frame {frame_actual}")
            if boton_stop.collidepoint(event.pos):
                    print("Simulación detenida y reseteada.")
                    simulacion_iniciada = False
                    simulacion_pausada = False
                    simulacion_finalizada = False # Resetea esto también
                    modo_replay = False
                    modo_record = False
                    if recorder_file:
                        recorder_file.close()
                        recorder_file = None
                    inicializar_simulacion() # Resetea todo

            
                                        
    


    
    # --- Lógica de Simulación ---
    if simulacion_iniciada:
        
        # --- (CAMBIO) Lógica de REPLAY ---
        # Esta lógica AHORA está separada de la simulación en vivo.
        if modo_replay:
            
            # 1. Aplicar el estado del frame actual (SIEMPRE)
            #    Esto hace que '<<' y '>>' funcionen al instante, 
            #    incluso si 'replay_pausado' es True.
            if frame_actual in datos_replay:
                score_j1, score_j2 = datos_replay[frame_actual]['score']
                mapa.puntaje_j1 = score_j1
                mapa.puntaje_j2 = score_j2
                # Guardar las posiciones del frame
                posiciones_frame = {}
                for id, _, x, y in datos_replay[frame_actual]['vehiculos']: 
                    posiciones_frame[id] = (x, y) # (Tupla)

                # Iterar sobre los vehículos y actualizarlos
                for vehiculo in grupo_vehiculos:
                    if vehiculo.id in posiciones_frame:
                        # Guardar la posición ANTERIOR (Vector2)
                        pos_anterior_vec = vehiculo.posicion.copy()
                        
                        # Obtener la posición NUEVA (Tupla)
                        pos_nueva_tuple = posiciones_frame[vehiculo.id]
                        
                        # Llamar a la función de actualización
                        vehiculo._actualizar_posicion_pixel(pos_nueva_tuple, pos_anterior_vec)
                    
                    else:
                        # Si el vehículo no está en el frame (ej. destruido), 
                        # moverlo fuera de la pantalla (como en tu código original)
                        pos_fuera = -100
                        vehiculo.posicion.x = pos_fuera
                        vehiculo.posicion.y = pos_fuera
                        vehiculo.rect.center = (
                            pos_fuera * CONSTANTES.CELDA_ANCHO,
                            pos_fuera * CONSTANTES.CELDA_ALTO
                        )
            grupo_items.update(grupo_vehiculos, mapa, frame_actual)
            grupo_explosiones.update()
            for vehiculo in grupo_vehiculos:
                # Comprueba si este vehículo está chocando con algún item
                items_colisionados = pygame.sprite.spritecollide(vehiculo, grupo_items, False)
                
                for item in items_colisionados:
                    
                    if isinstance(item, Recurso):
                        item.kill() # Elimina el sprite de 'grupo_items'
            # 2. Avanzar el frame SÓLO SI no está pausado
            if not replay_pausado:
                frame_actual += 1
            
            # 3. (NUEVO) Chequear fin del replay
            if frame_actual > max_frame and max_frame > 0:
                frame_actual = max_frame # Asegura que no se pase
                replay_pausado = True
                simulacion_finalizada = True
                simulacion_iniciada = False # Detiene la lógica
                # (CAMBIO) NO salimos de modo_replay aquí, 
                # para que el HUD siga mostrando "REPLAY FINALIZADO"
                # modo_replay = False 
                
                # (NUEVO) Aplicar el puntaje final una última vez
                if max_frame in datos_replay:
                    mapa.puntaje_j1, mapa.puntaje_j2 = datos_replay[max_frame]['score']

                print("Replay finalizado.")

        # --- (CAMBIO) Lógica de SIMULACIÓN EN VIVO ---
        # Se usa 'elif' para que NO se ejecute si estamos en modo_replay
        elif not simulacion_pausada:
            game_time += 1
            
            # 1. Actualiza la IA de los vehículos
            grupo_vehiculos.update(mapa, game_time,grupo_vehiculos)

            # Guardar frame actual si está activado el modo_record
            if modo_record and recorder_file:
                for vehiculo in grupo_vehiculos:
                    x = int(vehiculo.posicion.x)
                    y = int(vehiculo.posicion.y)
                    recorder_file.write(f"{game_time},{vehiculo.id},{vehiculo.jugador_id},{x},{y},{mapa.puntaje_j1},{mapa.puntaje_j2}\n")

            # (El bloque 'if modo_replay' que estaba aquí fue movido arriba)

            # 2. Chequear colisiones entre vehículos
            chequear_colisiones_vehiculos(grupo_vehiculos)
            
            # 3. Actualiza los items (para colisiones con minas/recursos)
            grupo_items.update(grupo_vehiculos, mapa, game_time)
            grupo_explosiones.update()
            
            # 4. Lógica de colisión (la mantengo como la tenías)
            colisiones_vehiculos = pygame.sprite.groupcollide(grupo_vehiculos, grupo_vehiculos, False, False)
            vehiculos_a_destruir = set()
            for v1, lista_colisiones in colisiones_vehiculos.items():
                for v2 in lista_colisiones:
                    if v1 != v2: 
                        vehiculos_a_destruir.add(v1)
                        vehiculos_a_destruir.add(v2)
            for v in vehiculos_a_destruir:
                if not v.destruido:
                    v.destruir()

            # 5.Chequear condiciones de fin de juego
            if grupo_vehiculos: # Solo si hay vehículos vivos
                todos_inactivos = True
                for v in grupo_vehiculos:
                    if v.estado != "inactivo":
                        todos_inactivos = False
                        break

                if todos_inactivos:
                    frames_todos_inactivos += 1
                else:
                    frames_todos_inactivos = 0 # Alguien se movió, resetea
            else:
                frames_todos_inactivos = 0 # No hay vehículos, no aplica


            # Condición 1: No quedan recursos
            if not mapa.resources:
                simulacion_iniciada = False
                simulacion_finalizada = True
                print(f"¡Simulación finalizada! Recursos recolectados.")

            # Condición 2: No quedan vehículos
            elif not grupo_vehiculos:
                simulacion_iniciada = False
                simulacion_finalizada = True
                print(f"¡Simulación finalizada! Vehículos destruidos.")

            # Condición 3 (NUEVA): Todos inactivos por más de 10 frames
            elif frames_todos_inactivos > 10: # (10 frames = 1 segundo en tu sim)
                simulacion_iniciada = False
                simulacion_finalizada = True
                print(f"¡Simulación finalizada! No hay más movimientos/viajes posibles.")


            # Si el juego terminó, cerrar el archivo de replay
            if simulacion_finalizada and modo_record:
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
