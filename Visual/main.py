import pygame
from auto import Jeep
import CONSTANTES
from items import Item
pygame.init()

ventana = pygame.display.set_mode((CONSTANTES.ANCHO_VENTANA, CONSTANTES.ALTO_VENTANA))
pygame.display.set_caption("Rescue Simulator")

#imagen minas(fañta colocar una función que las escale)
minaCircular=pygame.image.load("rescueSimulator\imagenes\minaCircular.png")
minaLineal=pygame.image.load("rescueSimulator\imagenes\minaLineal.png")
minaMovil=pygame.image.load("rescueSimulator\imagenes\minaMovil.png")

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

#items creados
minaC = Item(250,200, minaCircular)
minaL = Item(100,20, minaLineal)
minaM= Item(500,500, minaMovil)

#añadir al grupo los items
grupo_items.add(minaC)
grupo_items.add(minaL)
grupo_items.add(minaM)
while run:
    reloj.tick(60)
    ventana.fill(CONSTANTES.COLOR_NEGRO)
    dibujar_grid()
    jeep1.dibujar(ventana)
    #dibujar items
    grupo_items.draw(ventana)
    # Obtener todas las teclas presionadas
    keys = pygame.key.get_pressed()

    # Reiniciar delta
    delta_x = 0
    delta_y = 0

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

    # Eventos (cerrar ventana)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

    #update de sprite de items
    grupo_items.update()