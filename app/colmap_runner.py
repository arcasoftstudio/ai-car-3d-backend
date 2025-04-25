import os
import subprocess

def run_colmap_pipeline(input_dir, output_dir):
    database_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    model_dir = os.path.join(sparse_dir, "0")
    model_ply = os.path.join(output_dir, "model.ply")

    # ✅ Crea le cartelle necessarie
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(sparse_dir, exist_ok=True)

    # ✅ 1. Estrazione delle feature
    print("\n📦 Estrazione feature...")
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--ImageReader.camera_model", "PINHOLE",
        "--ImageReader.single_camera", "1",
        "--ImageReader.default_focal_length_factor", "1.2"
    ], check=True)

    # ✅ 2. Matching delle immagini
    print("\n🔁 Matching immagini...")
    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path
    ], check=True)

    # ✅ 3. Ricostruzione sparsa (Mapper)
    print("\n🏗️ Ricostruzione sparsa...")
    subprocess.run([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--output_path", sparse_dir,
        "--Mapper.init_min_tri_angle", "4.0",
        "--Mapper.min_num_matches", "15",
        "--Mapper.num_threads", "4"
    ], check=True)

    # ✅ 4. Conversione in PLY
    if os.path.exists(model_dir):
        print("\n🎯 Conversione modello in PLY...")
        subprocess.run([
            "colmap", "model_converter",
            "--input_path", model_dir,
            "--output_path", model_ply,
            "--output_type", "PLY"
        ], check=True)
        print(f"\n✅ Modello PLY salvato: {model_ply}")
    else:
        print("\n⚠️ Errore: nessun modello trovato, qualcosa è andato storto nella ricostruzione.")

    return model_ply

# Esempio di utilizzo
if __name__ == "__main__":
    input_images = "path/alle/immagini"
    output_folder = "path/output"
    run_colmap_pipeline(input_images, output_folder)
