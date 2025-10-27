import pygame
import CONSTANTES
class Jeep():#hay que hacer una general de vehículo y luego uno particular por tipo de auto
    def __init__(self, x, y):
        # Cargar imagen base mirando a la derecha
        self.image_original = pygame.image.load("rescueSimulator\imagenes\jeep.png").convert_alpha()
        
        # Toma los tamaños de la imagen
        ancho, alto = self.image_original.get_size()
        
        # Calcular factor de escala para que entre en una celda
        factor_x = CONSTANTES.CELDA_ANCHO / ancho
        factor_y = CONSTANTES.CELDA_ALTO / alto
        factor = min(factor_x, factor_y)

        self.image_original = pygame.transform.smoothscale(
            self.image_original,
            (int(ancho * factor), int(alto * factor))
        )

        # Imagen actual (la que se dibuja)
        self.image = self.image_original

        # Rectángulo de posición
        self.shape = self.image.get_rect(center=(x, y))

        # Dirección actual del vehículo
        self.direccion = "derecha"

    def movimiento(self, delta_x, delta_y):
        self.shape.x += delta_x
        self.shape.y += delta_y

        # Cambiar dirección según el movimiento
        if delta_x > 0:
            self.direccion = "derecha"
        elif delta_x < 0:
            self.direccion = "izquierda"
        elif delta_y < 0:
            self.direccion = "arriba"
        elif delta_y > 0:
            self.direccion = "abajo"

        # Actualizar imagen según la dirección
        self.actualizar_imagen()

    def actualizar_imagen(self):
        if self.direccion == "derecha":
            self.image = self.image_original
        elif self.direccion == "izquierda":
            self.image = pygame.transform.flip(self.image_original, True, False)
        elif self.direccion == "arriba":
            self.image = pygame.transform.rotate(self.image_original, 90)
        elif self.direccion == "abajo":
            self.image = pygame.transform.rotate(self.image_original, -90)

        # Actualizar el rectángulo para mantener el centro
        centro = self.shape.center
        self.shape = self.image.get_rect(center=centro)

    def dibujar(self, interfaz):
        interfaz.blit(self.image, self.shape)
        pygame.draw.rect(interfaz,CONSTANTES.COLOR_VERDE,self.shape,1)
