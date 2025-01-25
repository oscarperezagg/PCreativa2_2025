import subprocess
import logging

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,  # Nivel de logging
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    handlers=[
        logging.StreamHandler(),  # Mostrar en consola
    ],
)


def run_docker_commands():
    try:
        # Construir la imagen Docker
        build_command = "sudo docker build -t product-page/g23 ."
        subprocess.run(build_command, shell=True, check=True)

        # Ejecutar el contenedor Docker
        run_command = "sudo docker run --name product-page-g23 -p 9080:5080 -e GROUP_NUM=g23 -d product-page/g23"
        subprocess.run(run_command, shell=True, check=True)

        logging.info("Comandos Docker ejecutados correctamente.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ocurrió un error al ejecutar los comandos: {e}")


if __name__ == "__main__":
    run_docker_commands()


# Stop all running containers
# sudo docker stop $(sudo docker ps -q)
# Remove all containers
# sudo docker rm -f $(sudo docker ps -aq)
# Delete all images
# sudo docker rmi -f $(sudo docker images -q)