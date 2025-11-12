# Proyecto: Simulador de Rescate (Algoritmos II)

Este proyecto es un simulador de estrategia en 2D desarrollado en Python y Pygame para la materia Algoritmos y Estructuras de Datos II. Dos equipos de vehículos autónomos (IA) compiten para recolectar recursos en un mapa dinámico lleno de minas.

El proyecto implementa algoritmos de pathfinding (A*), evasión de obstáculos en tiempo real y una arquitectura modular orientada a objetos.

## Instrucciones de Instalación

Para correr el simulador, necesitarás Python 3 y las dependencias del proyecto.

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/beckLic/rescueSimulator.git
    cd rescueSimulator
    ```

2.  **(Recomendado) Crear un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    Usa el archivo `requirements.txt` para instalar Pygame:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Cómo Usar (Ejecutar)

El punto de entrada principal del proyecto es el archivo `rescue_simulator.py`.

**Para ejecutar el simulador:**

Asegúrate de estar en la carpeta raíz del proyecto (`rescueSimulator/`) y ejecuta:

```bash
python rescue_simulator.py

