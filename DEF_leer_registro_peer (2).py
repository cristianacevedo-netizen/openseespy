import numpy as np

def leer_registro_peer(ruta_archivo):
    """
    Lee un archivo de registro PEER NGA con formato:

    Línea 1: PEER NGA STRONG MOTION DATABASE RECORD
    Línea 2: Info del evento
    Línea 3: ACCELERATION TIME SERIES...
    Línea 4: NPTS= xxxx, DT= xxxx SEC, ...
    Líneas siguientes: serie de aceleraciones (en G).

    Devuelve:
        npts : int
        dt   : float
        acc  : np.ndarray de forma (npts,) con los datos en orden.
    """
    with open(ruta_archivo, 'r') as f:
        # Saltar las tres primeras líneas
        f.readline()  # línea 1
        f.readline()  # línea 2
        f.readline()  # línea 3
        linea4 = f.readline()  # línea 4 con NPTS y DT

        # --- Extraer NPTS y DT sin regex ---
        # Dividimos por comas: típicamente algo como
        # ["NPTS=  14000", " DT=   .0100 SEC", "   ..."]
        partes = linea4.split(',')

        npts = None
        dt = None

        for parte in partes:
            texto = parte.strip()
            if 'NPTS' in texto:
                # Ej: "NPTS=  14000"
                trozos = texto.split('=')
                npts_str = trozos[1].strip()
                npts = int(npts_str)
            elif 'DT' in texto:
                # Ej: "DT=   .0100 SEC"
                trozos = texto.split('=')
                dt_str = trozos[1].strip().split()[0]  # nos quedamos con ".0100"
                dt = float(dt_str)

        if npts is None or dt is None:
            raise ValueError("No se han podido encontrar NPTS y/o DT en la cabecera.")

        # --- Leer el resto del archivo como números ---
        # Se leen en el orden en que aparecen: izq→dcha, arriba→abajo
        resto = f.read().split()
        acc = np.array(resto, dtype=float)

    # Comprobación de consistencia
    if acc.size != npts:
        raise ValueError(
            f"NPTS indica {npts} puntos, pero se han leído {acc.size} valores."
        )

    return npts, dt, acc