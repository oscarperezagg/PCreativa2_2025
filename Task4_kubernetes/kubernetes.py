import subprocess
import os
import docker

import subprocess
import time


warning = """
|==========================================================================|
| WARNING: Para que el programa funcione correctamente:                    |
|--------------------------------------------------------------------------|
| 1. Asegúrate de que el ID del proyecto sea válido. En este caso, se ha   |
|    utilizado el ID del alumno. Si necesitas modificarlo, puedes buscar   |
|    la línea 275 en tu código donde se encuentra la referencia a          |
|    'gcloud container clusters' y asegurarte de que el proyecto sea el    |
|    correcto, en este caso 'nomadic-vehicle-369811'.                         |
|                                                                          |
| 1. Debes contar con una cuenta en Docker Hub.                            |
|                                                                          |
| 2. Crea un archivo secret.py que incluya las variables 'username' y      |
|    'password' con las credenciales adecuadas para que el programa pueda  |
|    funcionar correctamente. Asegúrate de mantener este archivo seguro y  |
|    no compartir las credenciales. Debe crearse en la carpeta confing     |
|                                                                          |
| 3. Cuando le salga un cuadro de texto debe pulsar Autorizar              |
|                                                                          |
| ¡Por favor, sigue estas indicaciones para evitar problemas en la         |
| ejecución del programa!                                                  |
|==========================================================================|
"""
print("\033c")

print(warning)
from config import username, password


def run_command(command):
    """Ejecuta un comando en la terminal y devuelve su salida y un booleano indicando el éxito."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        return result.stdout, None, True
    except subprocess.CalledProcessError as e:
        return None, e.stderr, False


################ CHECKS ################


def is_docker_installed():
    """Verifica si Docker está instalado."""
    output, error, success = run_command("docker --version")
    return success


def is_kubernetes_installed():
    """Verifica si Kubernetes está instalado."""
    output, error, success = run_command("kubectl version --client")
    return success


################ SETUP ################


def setup_docker():
    """Configura Docker en un sistema basado en Debian."""
    print("\n|   Añadiendo la clave GPG oficial de Docker...")
    run_command(
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
    )

    print("\n|   Añadiendo el repositorio de Docker...")
    run_command(
        "echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable' | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null"
    )

    print("\n|   Actualizando paquetes...")
    run_command("sudo apt update")

    print("\n|   Instalando Docker...")
    run_command(
        "sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y"
    )

    print("\nVerificando la versión de Docker...")
    version, error, success = run_command("docker --version")
    print(version)


def setup_kubernetes():
    """Configura Kubernetes en un sistema basado en Debian."""
    print("\n|   Actualizando paquetes...")
    run_command("sudo apt update")

    print("\n|   Añadiendo la clave GPG de Kubernetes...")
    run_command(
        "curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes.gpg"
    )

    print("\n|   Añadiendo el repositorio de Kubernetes...")
    run_command(
        "echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/kubernetes.gpg] http://apt.kubernetes.io/ kubernetes-xenial main' | sudo tee -a /etc/apt/sources.list"
    )

    print(
        "\n|   Actualizando paquetes después de añadir el repositorio de Kubernetes..."
    )
    run_command("sudo apt update")

    print("\n|   Instalando kubeadm, kubelet y kubectl...")
    run_command("sudo apt install kubeadm kubelet kubectl -y")

    print("\n|   Marcando paquetes para que no se actualicen automáticamente...")
    run_command("sudo apt-mark hold kubeadm kubelet kubectl")

    print("\nVerificando la versión de kubeadm...")
    version, error, success = run_command("kubeadm version")
    print(version)


def setup_images():
    """Configura y construye imágenes Docker para el proyecto."""

    # Guardar el directorio actual
    original_directory = os.getcwd()

    # Clonar el repositorio de GitHub
    print("\nClonando el repositorio de GitHub...")
    output, error, success = run_command("sudo rm -rf practica_creativa2")
    if not success:
        print("\n[ERROR]  Algo fue mal! Error: \n" + (error or "Desconocido"))
        return
    output, error, success = run_command(
        "git clone https://github.com/CDPS-ETSIT/practica_creativa2.git"
    )
    if not success:
        print("\n[ERROR]  Algo fue mal! Error: \n" + (error or "Desconocido"))
        return

    # Cambiar al directorio específico
    try:
        print("\nCambiando al directorio del proyecto...")
        os.chdir("practica_creativa2/bookinfo/src/reviews")
    except Exception as e:
        print(f"Error al cambiar de directorio: {e}")
        return

    # Construir el proyecto con Docker y Gradle
    print("\nConstruyendo el proyecto con Docker y Gradle...")
    output, error, success = run_command(
        'sudo docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build'
    )
    if not success:
        print("\n[ERROR]  Algo fue mal! Error: \n" + (error or "Desconocido"))
        return

    # Cambiar al directorio específico
    try:
        print("\nCambiando al directorio del proyecto...")
        os.chdir("reviews-wlpcfg")
    except Exception as e:
        print(f"Error al cambiar de directorio: {e}")
        return

    gradle_image = ("sudo docker build -t reviews .",)
    print(f"\nConstruyendo imagen Docker con el comando: {gradle_image}")
    output, error, success = run_command(gradle_image)
    if not success:
        print("\n[ERROR]  Algo fue mal! Error: \n" + (error or "Desconocido"))
        return

    # Volver al directorio original
    os.chdir(original_directory)

    # Comandos para construir imágenes Docker
    docker_build_commands = [
        "sudo docker build -t productpage -f dockerfiles/productpage .",
        "sudo docker build -t details -f dockerfiles/details .",
        "sudo docker build -t ratings -f dockerfiles/ratings .",
    ]

    for command in docker_build_commands:
        print(f"\nConstruyendo imagen Docker con el comando: {command}")
        output, error, success = run_command(command)
        if not success:
            print("\n[ERROR]  Algo fue mal! Error: \n" + (error or "Desconocido"))
            return


def upload_images():
    """Instala Docker usando pip3."""
    command = "pip3 install docker"
    stdout, stderr, success = run_command(command)

    if success:
        print("\nDocker se ha instalado correctamente.\n")
    else:
        print(f"\nError al instalar Docker: {stderr}\n")
    # Configura el cliente de Docker
    client = docker.from_env()

    # Obtiene la lista de todas las imágenes
    images = client.images.list()

    # Crea un diccionario para almacenar los nombres y los IDs de las imágenes
    image_info_dict = {}

    # Itera sobre las imágenes y guarda el nombre y el Image ID en el diccionario
    for image in images:
        image_info = image.attrs
        image_name = image_info["RepoTags"][0] if image_info["RepoTags"] else ""
        image_id = image_info["Id"].split(":")[-1]
        image_info_dict[image_name] = image_id

    # Log in to Docker Hub
    login_command = f"docker login --username {username} --password {password}"
    subprocess.run(login_command, shell=True, check=True)
    # Imprime el diccionario con la información
    # Itera sobre la lista y ejecuta el comando docker tag para cada imagen
    for new_name, image_id in image_info_dict.items():
        image_name = f"{username}/{new_name}"
        print(f"\nEjecutando:", "docker", "tag", image_id, image_name)

        subprocess.run(["docker", "tag", image_id, image_name])

        # Push the Docker image to Docker Hub
        print(f"\ndocker push {image_name}")

        push_command = f"docker push {image_name}"
        subprocess.run(push_command, shell=True, check=True)


def apply_kubectl():
    # Obtén el directorio del archivo en ejecución
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Lista para almacenar los nombres de los archivos YAML y YML
    yaml_files = []

    # Recorre todos los archivos en el directorio
    for filename in os.listdir(current_directory):
        if filename.endswith((".yaml", ".yml")):
            yaml_files.append(filename)

    for file in yaml_files:
        print(f"\nkubectl apply -f {file}\n")

        subprocess.run(["kubectl", "apply", "-f", file])

    # Wait for one second
    print("\nEsperando 10 segundos a que todo se despliegue correctamente\n")
    time.sleep(10)
    print("\nServices:\n")
    subprocess.run(["kubectl", "get", "services"])
    print("\nDeployments:\n")
    subprocess.run(["kubectl", "get", "deployments"])
    print("\nPods:\n")
    subprocess.run(["kubectl", "get", "pods"])
    print("\nEsperando otros 30 segundos para obtener a dirección publica\n")
    time.sleep(30)
    subprocess.run(["kubectl", "get", "services", "productpage"])


################ PROGRAM ################


if not is_docker_installed():
    print("\nDocker no está instalado. Ejecutando el proceso de configuración...")
    setup_docker()
else:
    print("\nDocker ya está instalado.")

if not is_kubernetes_installed():
    print("\nKubernetes no está instalado. Ejecutando el proceso de configuración...")
    setup_kubernetes()
else:
    print("\nKubernetes ya está instalado. No es necesario volver a configurarlo.")


create = input("\nQuiere crear el contenedor (y/n):")
if create.lower() == "y":
    create = True
else:
    create = False
if create:
    resultado = subprocess.run(
        "gcloud container clusters create creativa2 --num-nodes=3 --no-enable-autoscaling --zone europe-west1-d --project nomadic-vehicle-369811",
        shell=True,
        check=True,
    )

print("\nAccediendo al cluster que hemos creado: \n")
subprocess.run(
    "gcloud container clusters get-credentials creativa2 --zone europe-west1-d --project nomadic-vehicle-369811",
    shell=True,
    check=True,
)


try:
    # Eliminar todos los contenedores detenidos
    subprocess.run("docker container prune -f", shell=True, check=True)

    # Eliminar todas las imágenes no utilizadas
    subprocess.run("docker image prune -a -f", shell=True, check=True)

    print("\nLa limpieza de Docker se completó correctamente.")

except subprocess.CalledProcessError as e:
    print(f"Ocurrió un error: {e}")

setup_images()

upload_images()

try:
    print("\nEliminando servicios existentes\n")
    # Eliminar todos los contenedores detenidos
    subprocess.run("kubectl delete services --all", shell=True, check=True)
    print("\nEliminando desployments existentes\n")

    # Eliminar todas las imágenes no utilizadas
    subprocess.run("kubectl delete deployments --all", shell=True, check=True)
    print("\nEliminando pods existentes\n")
    subprocess.run("kubectl delete pods --all", shell=True, check=True)

    print("La limpieza del cluster se completó correctamente.")

except subprocess.CalledProcessError as e:
    print(f"Ocurrió un error: {e}")


apply_kubectl()
