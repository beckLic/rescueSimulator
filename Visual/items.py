import pygame.sprite
import CONSTANTES
class Item(pygame.sprite.Sprite):
    def __init__(self, x,y, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.item_type= item_type#0 recurso   1  mina
        self.image = self.item_type
                        
        # Toma los tamaños de la imagen
        ancho, alto = self.image.get_size()
        
        # Calcular factor de escala para que entre en una celda
        factor_x = CONSTANTES.CELDA_ANCHO / ancho
        factor_y = CONSTANTES.CELDA_ALTO / alto
        factor = min(factor_x, factor_y)

        self.image = pygame.transform.smoothscale(
            self.image,
            (int(ancho * factor), int(alto * factor))
        )
        self.rect=self.image.get_rect()
        self.rect=(x,y)