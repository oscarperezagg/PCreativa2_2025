# Comprobar si está instalado pip

import subprocess
import logging
import os


# Configuración del logging
logging.basicConfig(
    level=logging.INFO,  # Nivel de logging
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    handlers=[
        logging.FileHandler("script.log"),  # Archivo donde se guarda el log
        logging.StreamHandler(),  # Mostrar en consola
    ],
)

# Si realizáis esa parte en el laboratorio, utilizad la imagen de Ubuntu 20.04 de la práctica 2 
# Para poder acceder a la aplicación en Google Cloud, tendréis que abrir el puerto 9080 en el firewall 
# (opción Red de VPC->Firewall). Además, si os conectáis a Google Cloud desde vuestros portatiles utilizando 
# eduroam, tened en cuenta que el puerto 9080 está filtrado. Conectaros mejor a través del móvil o desde 
# los ordenadores del laboratorio.

# Para usarlo hay que instalar python3 con "sudo apt-get install python3"

def check_and_install_pip():
    """
    Comprueba si `pip3` está instalado en el sistema y lo instala si no lo está.

    1. Verifica si `pip3` está instalado ejecutando el comando `pip3 --version`.
    2. Si no está instalado, actualiza los repositorios (`apt update`) e instala `pip3` usando `apt install`.
    3. Maneja errores durante el proceso de instalación.

    Logging:
        - Registra si `pip3` ya está instalado.
        - Registra si se ha iniciado y completado la instalación, o si ocurrió un error.

    Returns:
        None
    """
    try:
        # Verificar si pip3 está instalado
        subprocess.check_output(["pip3", "--version"])
        logging.info("pip3 ya está instalado en el sistema.")
    except Exception:
        # Si pip3 no está instalado, actualizar e intentar instalarlo
        logging.info("pip3 no está instalado en el sistema. Se procederá a instalarlo.")
        try:
            # Actualizar los repositorios del sistema
            logging.info("Actualizando los repositorios del sistema...")
            subprocess.check_call(["sudo", "apt", "update"])

            # Instalar pip3
            logging.info("Instalando pip3...")
            subprocess.check_call(["sudo", "apt", "install", "python3-pip", "-y"])

            logging.info("pip3 se ha instalado correctamente.")
        except Exception as e:
            logging.error("Hubo un error al intentar instalar pip3: %s", str(e))


if __name__ == "__main__":
    # Comprobar e instalar pip3

    check_and_install_pip()

    # Descargar el repositorio de Git
    subprocess.check_call(
        [
            "git",
            "clone",
            "https://github.com/CDPS-ETSIT/practica_creativa2.git",
        ]
    )

    # Obtén el path absoluto del archivo en ejecución
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    # Concatena las partes para obtener la ubicación completa del archivo
    ruta_del_archivo = os.path.join(
        directorio_actual,
        "practica_creativa2",
        "bookinfo",
        "src",
        "productpage",
        "requirements.txt",
    )

    # Instalar las dependencias desde el archivo requirements.txt
    logging.info(
        "####################### Ejecutando: pip3 install -r requirements.txt #######################"
    )

    subprocess.check_call(["sudo", "pip3", "install", "-r", ruta_del_archivo])

    # Actualizar la biblioteca requests
    logging.info(
        "####################### Ejecutando: pip3 install --upgrade requests #######################"
    )
    subprocess.check_call(["sudo", "pip3", "install", "--upgrade", "requests"])

    # Instalar la biblioteca testresources
    logging.info(
        "####################### Ejecutando: pip3 install testresources #######################"
    )

    subprocess.check_call(["sudo", "pip3", "install", "testresources"])

    # Actualizar la biblioteca json2html
    logging.info(
        "####################### Ejecutando: pip3 install --upgrade json2html #######################"
    )

    subprocess.check_call(["sudo", "pip3", "install", "--upgrade", "json2html"])

    # Concatena las partes para obtener la ubicación completa del archivo
    ruta_del_archivo = os.path.join(
        directorio_actual,
        "practica_creativa2",
        "bookinfo",
        "src",
        "productpage",
        "productpage_monolith.py",
    )
    logging.info(
        f"####################### Ejecutando el script: {ruta_del_archivo} en el puerto 9080 #######################"
    )

    # Ejecutar el script productpage_monolith.py en el puerto 80
    subprocess.check_call(["sudo", "python3", ruta_del_archivo, "9080"])
