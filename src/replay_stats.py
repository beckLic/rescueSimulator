import csv, gzip, json
from collections import defaultdict

def analizar_replay(path_replay, path_salida="data/statistics/resumen.csv"):
    resumen_vehiculos = defaultdict(lambda: {
        "jugador": None,
        "frames_vivo": 0,
        "destruido": False,
        "inicio_x": None,
        "inicio_y": None
    })

    # Para entregas/puntajes
    puntajes_j1 = []
    puntajes_j2 = []

    with (gzip.open(path_replay, "rt", encoding="utf-8") if path_replay.endswith(".gz")
          else open(path_replay, "r", encoding="utf-8")) as f:
        reader = csv.reader(f)
        for tipo, payload in reader:
            if tipo == "frame":
                frame = json.loads(payload)

                # Puntajes por frame
                puntajes_j1.append(frame["puntajes"]["j1"])
                puntajes_j2.append(frame["puntajes"]["j2"])

                for v in frame["vehiculos"]:
                    vid = v["id"]
                    r = resumen_vehiculos[vid]
                    r["jugador"] = v["jug"]
                    r["frames_vivo"] += int(v["alive"])
                    if r["inicio_x"] is None:
                        r["inicio_x"] = v["x"]
                        r["inicio_y"] = v["y"]
                    if not v["alive"]:
                        r["destruido"] = True

    # Detectar entregas como cambios de puntaje
    entregas_j1 = sum(1 for i in range(1, len(puntajes_j1)) if puntajes_j1[i] > puntajes_j1[i - 1])
    entregas_j2 = sum(1 for i in range(1, len(puntajes_j2)) if puntajes_j2[i] > puntajes_j2[i - 1])

    with open(path_salida, "w", newline='', encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow([
            "vehiculo", "jugador", "frames_vivo", "destruido", "inicio_x", "inicio_y"
        ])
        for vid, r in resumen_vehiculos.items():
            writer.writerow([
                vid, r["jugador"], r["frames_vivo"],
                "Sí" if r["destruido"] else "No",
                r["inicio_x"], r["inicio_y"]
            ])
        writer.writerow([])
        writer.writerow(["Jugador", "Entregas", "Puntaje Final"])
        writer.writerow(["Jugador 1 (Azul)", entregas_j1, puntajes_j1[-1] if puntajes_j1 else 0])
        writer.writerow(["Jugador 2 (Rojo)", entregas_j2, puntajes_j2[-1] if puntajes_j2 else 0])

    print(f"[✔] Estadísticas guardadas en: {path_salida}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python -m src.replay_stats <archivo_replay.csv.gz>")
    else:
        path = sys.argv[1]
        analizar_replay(path)