import subprocess
import os

def run_meshroom(input_dir: str, output_dir: str):
    print("📸 Avvio ricostruzione Meshroom...")
    try:
        os.makedirs(output_dir, exist_ok=True)
        subprocess.run([
            "meshroom_photogrammetry",
            "--input", input_dir,
            "--output", output_dir
        ], check=True)
        print("✅ Meshroom completato")
    except Exception as e:
        print(f"❌ ERRORE MESHROOM: {e}")
