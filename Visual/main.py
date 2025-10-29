import pygame
from Visual.auto import Jeep
from Visual.items import Item
from Visual import CONSTANTES
from src.map_manager import MapManager
from src.classes import load_resource_config


pygame.init()

ventana = pygame.display.set_mode((CONSTANTES.ANCHO_VENTANA, CONSTANTES.ALTO_VENTANA))
from src.classes import load_resource_config

RUTA_CONFIG = "config/default_config.json"
config = load_resource_config(RUTA_CONFIG)
mapa = MapManager(CONSTANTES.CANTIDAD_I, CONSTANTES.CANTIDAD_J, config)
pygame.display.set_caption("Rescue Simulator")

#imagen minas(fañta colocar una función que las escale)

minaLineal=pygame.image.load("imagenes\minaLineal.png")
minaMovil=pygame.image.load("imagenes\minaMovil.png")

def dibujar_grid():
    for x in range(51):
        pygame.draw.line(ventana,CONSTANTES.COLOR_ROJO, (x*CONSTANTES.CELDA_ANCHO, 0), (x*CONSTANTES.CELDA_ANCHO, CONSTANTES.ALTO_VENTANA))
    for y in range(51):
        pygame.draw.line(ventana, CONSTANTES.COLOR_ROJO, (0, y*CONSTANTES.CELDA_ALTO), (CONSTANTES.ANCHO_VENTANA, y*CONSTANTES.CELDA_ALTO))

jeep1 = Jeep(500, 300)

reloj = pygame.time.Clock()
run = True
#grupo de items
grupo_items= pygame.sprite.Group()
# Cargar minas en el mapa y en el grupo
mapa.colocar_minas(grupo_items)

# --- Botones ---
boton_init = pygame.Rect(50, 30, 120, 40)
boton_play = pygame.Rect(200, 30, 120, 40)
simulacion_iniciada = False
def dibujar_botones():
    pygame.draw.rect(ventana, (0, 200, 0), boton_init)
    pygame.draw.rect(ventana, (0, 0, 200), boton_play)
    fuente = pygame.font.SysFont(None, 24)
    ventana.blit(fuente.render("Init", True, (255,255,255)), (85, 40))
    ventana.blit(fuente.render("Play", True, (255,255,255)), (235, 40))

while run:
    reloj.tick(60)
    ventana.fill(CONSTANTES.COLOR_NEGRO)
    dibujar_grid()
    # Mostrar minas y recursos en la grilla (debug visual)
    mapa.dibujar_mapa_debug(ventana)
    jeep1.dibujar(ventana)
    #dibujar items
    grupo_items.draw(ventana)
    # Obtener todas las teclas presionadas
    keys = pygame.key.get_pressed()

    # Reiniciar delta
    delta_x = 0
    delta_y = 0



    

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
    # Mover solo en una dirección a la vez
    if keys[pygame.K_a]:
        delta_x = -5
    elif keys[pygame.K_d]:
        delta_x = 5
    elif keys[pygame.K_w]:
        delta_y = -5
    elif keys[pygame.K_s]:
        delta_y = 5    
    # Aplicar movimiento
    jeep1.movimiento(delta_x, delta_y)
    dibujar_botones()

    #update de sprite de items
    
    grupo_items.update(jeep1, mapa)



    pygame.display.update()

    #Debuggin
