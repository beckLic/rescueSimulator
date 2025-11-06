import pygame
from Visual import CONSTANTES
from src.map_manager import MapManager
from src.classes import load_resource_config, Jeep, Moto, Camion, Auto


pygame.init()

ventana = pygame.display.set_mode((CONSTANTES.ANCHO_VENTANA, CONSTANTES.ALTO_VENTANA))


RUTA_CONFIG = "config/default_config.json"
config = load_resource_config(RUTA_CONFIG)
mapa = MapManager(CONSTANTES.CANTIDAD_I, CONSTANTES.CANTIDAD_J, config)
pygame.display.set_caption("Rescue Simulator")



minaLineal=pygame.image.load("imagenes\minaLineal.png")
minaMovil=pygame.image.load("imagenes\minaMovil.png")

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
    
    # 1. Limpiar grupos
    grupo_items.empty()
    grupo_vehiculos.empty()
    
    # 2. Generar mapa lógico Y sprites de items/minas
    #    (Tu generar_mapa_aleatorio ya hace esto)
    mapa.generar_mapa_aleatorio(grupo_items)
    
    # 3. ¡Crear los vehículos de IA!
    # (Define sus posiciones iniciales y bases en la GRILLA)
    base_jugador_1 = (5, 5) # (x, y) en grilla
    
    jeep_ia_1 = Jeep(id="J-IA-1", jugador_id=1, pos_inicial=(5, 5), posicion_base=base_jugador_1)
    
    # (Puedes añadir más vehículos)
    # moto_ia_1 = Moto(id="M-IA-1", jugador_id=1, pos_inicial=(6, 6), posicion_base=base_jugador_1)
    
    # 4. Añadirlos al grupo de vehículos
    grupo_vehiculos.add(jeep_ia_1)
    # grupo_vehiculos.add(moto_ia_1)
    
    print(f"Simulación inicializada con {len(grupo_vehiculos)} vehículos.")
run = True
simulacion_iniciada = False
inicializar_simulacion()
while run:
    reloj.tick(20)
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
                    grupo_items.empty()
                    mapa.generar_mapa_aleatorio(grupo_items)  # distribuye minas y recursos
                    mapa.colocar_minas(grupo_items)
                elif boton_play.collidepoint(event.pos):
                    simulacion_iniciada = True
                    print("Simulación iniciada")
    
    if simulacion_iniciada:
            
            # 1. ¡Actualiza la IA de los vehículos!
            # (Esto corre la máquina de estados, A*, y mueve los sprites)
            grupo_vehiculos.update(mapa, game_time)
            
            # 2. Actualiza los items (para colisiones)
            # (Les pasamos el grupo de vehículos para que revisen colisiones)
            # (Necesitas arreglar el update de Recurso y Mina, mira abajo)
            grupo_items.update(grupo_vehiculos, mapa, game_time)


    dibujar_botones()
    pygame.display.update()

pygame.quit()

    #Debuggin
