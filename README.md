Enfoque para el manejo de las minas y vehiculos: Desde el motor del juego se va a estar chequeando constantemente las posiciones de los vehiculos y las minas para detectar colisiones,
las minas van a tener atributos como posicion, radio(para las circulares), largo y orientacion(para las lineales), la mina movil va a tener su timer junto con su radio para ir cambiando de posicion
cada 5 frames. De esta forma el motor del juego mediante un bucle va llamando a las funciones correspondientes pasando como parametros las posiciones de los vehiculos.

