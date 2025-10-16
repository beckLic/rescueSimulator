 # Inicia el bucle para encontrar una posición segura
                posicion_segura_encontrada = False
                while not posicion_segura_encontrada:
                    
                    # 1. Generamos una posición candidata aleatoria en el mapa
                    x = random.randint(0, self.width - 1)
                    y = random.randint(0, self.height - 1)
                    pos_candidata = (x, y)

                    # 2. Suponemos que la posición es segura por ahora
                    es_posicion_segura = True

                    # 3. Verifica la posición contra TODAS las minas ya colocadas
                    for mina in self.mines: 
                        if mina.is_inside_area(pos_candidata):
                            es_posicion_segura = False # no es segura
                            break # No tiene sentido seguir buscando, probamos otra posición

                    # 4. Si después de revisar todas las minas sigue siendo segura
                    if es_posicion_segura:
                        # Y además nos aseguramos de que la celda de la grilla esté libre
                        if self.grid[x][y] is None:
                            posicion_segura_encontrada = True