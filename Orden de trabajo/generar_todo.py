import subprocess
import os

def run_script(script_name):
    print(f"--- Ejecutando {script_name} ---")
    try:
        result = subprocess.run(["python", script_name], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_name}:")
        print(e.stderr)

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)
    
    run_script("generar_desazolves.py")
    run_script("generar_trampas.py")
    
    print("Proceso finalizado. Las órdenes de trabajo se encuentran en la carpeta 'Documentos_generados'.")
