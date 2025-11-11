# Archivo: Visual/main.py

import pygame
from Visual import CONSTANTES
from src.map_manager import MapManager
from src.classes import load_resource_config, Jeep, Moto, Camion, Auto
import csv, json, gzip, random, argparse, os

CSV_PATH = CONSTANTES.REPLAY_DEFAULT_PATH 
MODO = "run"          # "run" | "record" | "replay"

pygame.init()
fuente_hud = pygame.font.SysFont("Arial", 30)
fuente_titulo_final = pygame.font.SysFont("Arial", 60)
fuente_stats = pygame.font.SysFont("Arial", 28)
ventana = pygame.display.set_mode((CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.VENTANA_ALTO_TOTAL))

RUTA_CONFIG = "config/default_config.json"
config = load_resource_config(RUTA_CONFIG)
mapa = MapManager(CONSTANTES.CANTIDAD_I, CONSTANTES.CANTIDAD_J, config)
pygame.display.set_caption("Rescue Simulator")

simulacion_finalizada = False

minaLineal=pygame.image.load("imagenes/minaLineal.png") # Corregí la barra \
minaMovil=pygame.image.load("imagenes/minaMovil.png")

game_time = 0 #tiempo del algoritmo
recorder = None
replayer = None

# ---------- Grabador de estados por frame ----------
class Recorder:
    def __init__(self, path, fps, seed):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.fps = fps
        self.seed = seed
        self.f = gzip.open(path, "wt", newline="", encoding="utf-8") if path.endswith(".gz") else open(path, "w", newline="", encoding="utf-8")
        self.w = csv.writer(self.f)
        self.w.writerow(["meta", json.dumps({"version": FORMAT_VERSION, "fps": fps, "seed": seed})])

    def log_frame(self, frame, mapa, vehiculos):
        veh_states = []
        for v in vehiculos.sprites():
            veh_states.append({
                "id": getattr(v, "id", "?"),
                "jug": getattr(v, "jugador_id", None),
                "x": int(getattr(v, "posicion").x),
                "y": int(getattr(v, "posicion").y),
                "alive": True
            })
        row = {
            "t": frame,
            "puntajes": {"j1": mapa.puntaje_j1, "j2": mapa.puntaje_j2},
            "vehiculos": veh_states
        }
        self.w.writerow(["frame", json.dumps(row)])

    def log_event(self, frame, kind, data):
        self.w.writerow(["event", json.dumps({"t": frame, "kind": kind, "data": data})])

    def close(self):
        self.f.close()

# ---------- Reproductor ----------
class Replayer:
    def __init__(self, path):
        f = gzip.open(path, "rt", newline="", encoding="utf-8") if path.endswith(".gz") else open(path, "r", newline="", encoding="utf-8")
        r = csv.reader(f)
        self.meta = None
        self.frames = {}  # t -> snapshot
        for typ, payload in r:
            if typ == "meta":
                self.meta = json.loads(payload)
            elif typ == "frame":
                row = json.loads(payload)
                self.frames[row["t"]] = row
            elif typ == "event":
                pass
        f.close()
        if not self.meta:
            raise ValueError("CSV de replay inválido: falta meta")
        self.max_t = max(self.frames.keys()) if self.frames else 0

    def get_state(self, frame):
        return self.frames.get(frame)
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

def dibujar_pantalla_final():
    """
    Dibuja la pantalla de estadísticas de fin de juego.
    """
    # Fondo semitransparente
    s = pygame.Surface((CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.VENTANA_ALTO_TOTAL), pygame.SRCALPHA)
    s.fill((0, 0, 0, 210)) # Negro con 210 de alfa (bastante opaco)
    ventana.blit(s, (0, 0))
    
    # 1. Título
    titulo = fuente_titulo_final.render("Simulación Finalizada", True, (255, 255, 255))
    rect_titulo = titulo.get_rect(centerx=CONSTANTES.VENTANA_ANCHO_TOTAL / 2, y=50)
    ventana.blit(titulo, rect_titulo)

    # 2. Posiciones de columnas
    x_col_1 = CONSTANTES.VENTANA_ANCHO_TOTAL * 0.25
    x_col_2 = CONSTANTES.VENTANA_ANCHO_TOTAL * 0.75
    y_inicio = 150

    # --- COLUMNA 1: EQUIPO AZUL ---
    titulo_j1 = fuente_hud.render("Equipo Azul", True, (100, 150, 255))
    ventana.blit(titulo_j1, titulo_j1.get_rect(centerx=x_col_1, y=y_inicio))
    
    # Puntaje Total
    score_j1 = fuente_stats.render(f"Puntaje Total: {mapa.puntaje_j1}", True, (255, 255, 255))
    ventana.blit(score_j1, score_j1.get_rect(centerx=x_col_1, y=y_inicio + 60))
    
    # Vehículos Destruidos
    muertes_j1 = fuente_stats.render(f"Vehículos Destruidos: {mapa.vehiculos_destruidos_j1}", True, (255, 255, 255))
    ventana.blit(muertes_j1, muertes_j1.get_rect(centerx=x_col_1, y=y_inicio + 100))
    
    # Recursos
    recursos_titulo_j1 = fuente_stats.render("Recursos Recolectados:", True, (200, 200, 200))
    ventana.blit(recursos_titulo_j1, recursos_titulo_j1.get_rect(centerx=x_col_1, y=y_inicio + 160))
    
    y_recurso = y_inicio + 200
    for tipo, cantidad in mapa.recursos_j1.items():
        if cantidad > 0: # Solo mostrar si recolectó al menos uno
            texto = fuente_stats.render(f"{tipo}: {cantidad}", True, (255, 255, 255))
            ventana.blit(texto, texto.get_rect(centerx=x_col_1, y=y_recurso))
            y_recurso += 40

    # --- COLUMNA 2: EQUIPO ROJO ---
    titulo_j2 = fuente_hud.render("Equipo Rojo", True, (255, 100, 100))
    ventana.blit(titulo_j2, titulo_j2.get_rect(centerx=x_col_2, y=y_inicio))
    
    # Puntaje Total
    score_j2 = fuente_stats.render(f"Puntaje Total: {mapa.puntaje_j2}", True, (255, 255, 255))
    ventana.blit(score_j2, score_j2.get_rect(centerx=x_col_2, y=y_inicio + 60))
    
    # Vehículos Destruidos
    muertes_j2 = fuente_stats.render(f"Vehículos Destruidos: {mapa.vehiculos_destruidos_j2}", True, (255, 255, 255))
    ventana.blit(muertes_j2, muertes_j2.get_rect(centerx=x_col_2, y=y_inicio + 100))
    
    # Recursos
    recursos_titulo_j2 = fuente_stats.render("Recursos Recolectados:", True, (200, 200, 200))
    ventana.blit(recursos_titulo_j2, recursos_titulo_j2.get_rect(centerx=x_col_2, y=y_inicio + 160))
    
    y_recurso = y_inicio + 200
    for tipo, cantidad in mapa.recursos_j2.items():
        if cantidad > 0: # Solo mostrar si recolectó al menos uno
            texto = fuente_stats.render(f"{tipo}: {cantidad}", True, (255, 255, 255))
            ventana.blit(texto, texto.get_rect(centerx=x_col_2, y=y_recurso))
            y_recurso += 40

    # 3. Ganador
    texto_str = ""
    color_texto = (255, 255, 255)
    if mapa.puntaje_j1 > mapa.puntaje_j2:
        texto_str = "¡Gana Equipo Azul!"
        color_texto = (100, 150, 255)
    elif mapa.puntaje_j2 > mapa.puntaje_j1:
        texto_str = "¡Gana Equipo Rojo!"
        color_texto = (255, 100, 100)
    else:
        texto_str = "¡Empate!"
    
    ganador = fuente_titulo_final.render(texto_str, True, color_texto)
    rect_ganador = ganador.get_rect(centerx=CONSTANTES.VENTANA_ANCHO_TOTAL / 2, y=CONSTANTES.ALTO_VENTANA - 150)
    ventana.blit(ganador, rect_ganador)
    
    


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

    global game_time, simulacion_finalizada, recorder, replayer

    game_time = 0
    simulacion_finalizada = False
    print("Iniciando simulación...")
<<<<<<< HEAD
    mapa.reiniciar_estadisticas()
=======

    # 0) Determinismo: fijamos semilla ANTES de generar mapa o crear unidades
    import random
    random.seed(CONSTANTES.GLOBAL_SEED)


>>>>>>> 068fa64 (Resolviendo conflictos)
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

    # 5) Inicializar recorder/replayer según el modo
    if MODO == "record":
        recorder = Recorder(
            CSV_PATH,
            fps=CONSTANTES.FPS,
            seed=CONSTANTES.GLOBAL_SEED
        )
        replayer = None
        print(f"[REC] Guardando en: {CSV_PATH}")
    elif MODO == "replay":
        replayer = Replayer(CSV_PATH)
        recorder = None
        print(f"[REPLAY] Cargando de: {CSV_PATH} (frames: {replayer.max_t + 1})")
    else:
        recorder = None
        replayer = None

    print(f"Simulación inicializada con {len(grupo_vehiculos)} vehículos.")

def chequear_colisiones_vehiculos(grupo_vehiculos):
    """
    Revisa si dos vehículos ocupan la misma celda de la grilla y 
    los elimina si eso ocurre.
    Ahora reporta las muertes al mapa.
    """
    posiciones_ocupadas = {} 
    vehiculos_a_eliminar = set() 

    for vehiculo in grupo_vehiculos.sprites():
        pos_tuple = (int(vehiculo.posicion.x), int(vehiculo.posicion.y))

        if pos_tuple in posiciones_ocupadas:
            otro_vehiculo = posiciones_ocupadas[pos_tuple]
            print(f"¡COLISIÓN en {pos_tuple} entre {vehiculo.id} y {otro_vehiculo.id}!")
            
            vehiculos_a_eliminar.add(vehiculo)
            vehiculos_a_eliminar.add(otro_vehiculo)
        else:
            posiciones_ocupadas[pos_tuple] = vehiculo
    
    # Eliminar todos los vehículos que colisionaron
    for vehiculo in vehiculos_a_eliminar:
        # Registrar destrucción
        if vehiculo.jugador_id == 1:
            mapa.vehiculos_destruidos_j1 += 1
        else:
            mapa.vehiculos_destruidos_j2 += 1
        
        vehiculo.kill() # .kill() los elimina de CUALQUIER grupo


# --- INICIO DEL BUCLE PRINCIPAL ---
run = True
simulacion_iniciada = False

# --- CLI para elegir run/record/replay ---
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", nargs="?", const=CSV_PATH, help="Graba la simulación en CSV(.gz)")
    ap.add_argument("--replay", nargs="?", const=CSV_PATH, help="Reproduce desde CSV(.gz)")
    args, unknown = ap.parse_known_args()
    if args.record:
        MODO = "record"; CSV_PATH = args.record
    elif args.replay:
        MODO = "replay"; CSV_PATH = args.replay

inicializar_simulacion()
while run:
    reloj.tick(10)#FPS
    game_time += 1
    
    # Lógica de dibujado
    if simulacion_finalizada:
        # --- PANTALLA FINAL ---
        # 1. Fondo de la simulación (detrás de la superposición)
        ventana.fill(CONSTANTES.COLOR_NEGRO)
        color_panel_ui = (30, 30, 30)
        pygame.draw.rect(ventana, color_panel_ui, (0, CONSTANTES.MAPA_ALTO, CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.UI_ALTO))
        dibujar_grid()
        grupo_items.draw(ventana)
        grupo_vehiculos.draw(ventana)
        
        # 2. Superponer la pantalla de estadísticas
        dibujar_pantalla_final() 
        
    else:
        # --- SIMULACIÓN ACTIVA O EN PAUSA ---
        # 1. Fondo
        ventana.fill(CONSTANTES.COLOR_NEGRO)
        color_panel_ui = (30, 30, 30)
        pygame.draw.rect(ventana, color_panel_ui, (0, CONSTANTES.MAPA_ALTO, CONSTANTES.VENTANA_ANCHO_TOTAL, CONSTANTES.UI_ALTO))
        dibujar_grid()
        
        # 2. Sprites
        grupo_items.draw(ventana)
        grupo_vehiculos.draw(ventana)
        for item in grupo_items:
            if hasattr(item, 'draw_radius'):
                item.draw_radius(ventana)
        
        # 3. HUD (Puntajes)
        texto_j1 = fuente_hud.render(f"Equipo Azul: {mapa.puntaje_j1}", True, (100, 150, 255))
        texto_j2 = fuente_hud.render(f"Equipo Rojo: {mapa.puntaje_j2}", True, (255, 100, 100))
        pygame.draw.rect(ventana, (0,0,0), (345, CONSTANTES.MAPA_ALTO + 20, 250, 65))
        ventana.blit(texto_j1, (350, CONSTANTES.MAPA_ALTO + 25))
        ventana.blit(texto_j2, (350, CONSTANTES.MAPA_ALTO + 55))
        
        # 4. Botón "Play" (Solo si no ha empezado y no ha terminado)
        if not simulacion_iniciada:
             fuente_botones = pygame.font.SysFont(None, 24)
             pygame.draw.rect(ventana, (0, 0, 200), boton_play)
             ventana.blit(fuente_botones.render("Play", True, (255,255,255)), (235, CONSTANTES.MAPA_ALTO + 40))


    # --- Botón "Init" (Reset) ---
    fuente_botones = pygame.font.SysFont(None, 24)
    pygame.draw.rect(ventana, (0, 200, 0), boton_init)
    ventana.blit(fuente_botones.render("Init", True, (255,255,255)), (85, CONSTANTES.MAPA_ALTO + 40))


    # --- Eventos (Se manejan siempre) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if boton_init.collidepoint(event.pos):
                inicializar_simulacion() # ¡Esto resetea todo, incluida la pantalla final!
            elif boton_play.collidepoint(event.pos) and not simulacion_iniciada and not simulacion_finalizada:
                simulacion_iniciada = True
                print("Simulación iniciada")
    
    # --- Lógica de Simulación (Solo si está iniciada) ---
    if simulacion_iniciada:
<<<<<<< HEAD
=======

            
            # 1. Actualiza la IA de los vehículos
            grupo_vehiculos.update(mapa, game_time,grupo_vehiculos)
            
            # 2. Chequear colisiones entre vehículos

        if MODO in ("run", "record"):
            # 1. Actualiza la IA de los vehículos (aquí cambian su self.posicion)
            grupo_vehiculos.update(mapa, game_time,grupo_vehiculos)

            # 2. Chequear colisiones entre vehículos DESPUÉS de que se movieron

            chequear_colisiones_vehiculos(grupo_vehiculos)
            
            # 3. Actualiza los items (para colisiones con minas/recursos)
            grupo_items.update(grupo_vehiculos, mapa, game_time)

        # Guardar snapshot del frame si estamos grabando
        if recorder:
            recorder.log_frame(game_time, mapa, grupo_vehiculos)

    elif MODO == "replay":
        state = replayer.get_state(game_time)
        if state:
            # Puntajes
            mapa.puntaje_j1 = state["puntajes"]["j1"]
            mapa.puntaje_j2 = state["puntajes"]["j2"]

            # Sin IA: sólo sincronizamos sprites con la foto del frame
            vivos_set = set()
            by_id = {v.id: v for v in grupo_vehiculos.sprites()}

            for vs in state["vehiculos"]:
                vivos_set.add(vs["id"])
                v = by_id.get(vs["id"])
                if v and vs["alive"]:
                    v.posicion.x = vs["x"]
                    v.posicion.y = vs["y"]
                elif v and not vs["alive"]:
                    v.kill()

            # Si quedó algún sprite no listado como vivo, lo eliminamos
            for v in list(grupo_vehiculos.sprites()):
                if v.id not in vivos_set:
                    v.kill()
        else:
            # Fin del replay
            simulacion_iniciada = False
            
            
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
>>>>>>> 068fa64 (Resolviendo conflictos)
        
        # 1. Actualiza IA
        grupo_vehiculos.update(mapa, game_time, grupo_vehiculos)
        
        # 2. Chequear colisiones
        chequear_colisiones_vehiculos(grupo_vehiculos)
        
        # 3. Actualiza items (minas)
        grupo_items.update(grupo_vehiculos, mapa, game_time)
        
        # 4. Chequear fin de juego
        fin_juego = False
        if not mapa.resources or not grupo_vehiculos:
            fin_juego = True
            print(f"¡Simulación finalizada! (Causa: Sin recursos o sin vehículos)")
        else:
            personas_restantes = False
            for recurso in mapa.resources:
                if recurso.type == "Personas":
                    personas_restantes = True
                    break
            if not personas_restantes:
                otros_vehiculos_activos = False
                for vehiculo in grupo_vehiculos.sprites():
                    if vehiculo.tipo != "moto":
                        otros_vehiculos_activos = True
                        break
                if not otros_vehiculos_activos:
                    fin_juego = True
                    print(f"¡Simulación finalizada! (Causa: Solo quedan Motos y no hay Personas)")
        
        if fin_juego:
            simulacion_iniciada = False
            simulacion_finalizada = True
            print(f"Estadísticas finales: Recursos: {len(mapa.resources)}, Vehículos: {len(grupo_vehiculos)}")

    pygame.display.update()

<<<<<<< HEAD
pygame.quit()
=======
if recorder:
    recorder.close()
pygame.quit()
    #Debuggin
>>>>>>> 068fa64 (Resolviendo conflictos)
