import pygame.sprite
from Visual import CONSTANTES

class Item(pygame.sprite.Sprite):
    
    # El constructor acepta (x, y, imagen, tipo_string,radio)
    def __init__(self, x, y, imagen, tipo_string, radius=None): 
        pygame.sprite.Sprite.__init__(self)
        
        # 'tipo_string' será "mina", "Persona", "Alimentos", etc.
        self.item_type = tipo_string
        self.image = imagen  
        self.radius = radius
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, vehiculo, mapa):
        # Comprobar colisión con el vehículo
        if self.rect.colliderect(vehiculo.shape):
            
            
            if self.item_type == "mina":
                print("¡BOOM! Mina explota.")
                # queda eliminar el vehículo
                
            elif self.item_type == "Persona":
                print("¡Persona rescatada!")
                
            elif self.item_type == "Alimentos":
                print("Comida recolectada.")
                
            elif self.item_type == "Ropa":
                print("Ropa recolectada.")

            elif self.item_type == "Medicamentos":
                print("Medicina recolectada.")
            
            elif self.item_type == "Armamentos":
                print("Armamento recolectado.")
            
            # eliminar el ítem
            
            
            grid_x = int(self.rect.centerx // CONSTANTES.CELDA_ANCHO)
            grid_y = int(self.rect.centery // CONSTANTES.CELDA_ALTO)
            
            # Eliminar el objeto LÓGICO del mapa
            mapa.eliminar_elemento(grid_x, grid_y)
            
            # Eliminar el sprite VISUAL del grupo
            self.kill()
    def draw_radius(self, surface):
        if self.item_type == "mina" and self.radius is not None:
            # Dibujar un círculo rojo 
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA) 
            s.fill((0,0,0,0)) # Rellena con transparente
            
            pygame.draw.circle(s, (255, 0, 0, 100), (self.radius, self.radius), self.radius) # Rojo semitransparente
            
            # círculo centrado en el item
            surface.blit(s, (self.rect.centerx - self.radius, self.rect.centery - self.radius))