import os
import subprocess
from PIL import Image

def resize_images_in_dir(directory, max_size=2000):
    print(f"🔧 Riduzione immagini in {directory} a max {max_size}px...")
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            try:
                img = Image.open(path)
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size))
                    img.save(path)
                    print(f"📉 Ridotta: {filename} → {img.size}")
                else:
                    print(f"👌 Ok: {filename} ({img.size})")
            except Exception as e:
                print(f"⚠️ Impossibile processare {filename}: {e}")

def run_colmap_pipeline(input_dir, output_dir):
    sparse_dir = os.path.join(output_dir, "sparse")
    dense_dir = os.path.join(output_dir, "dense")
    meshed_model = os.path.join(output_dir, "final_model.ply")
    database_path = os.path.join(output_dir, "database.db")
    fused_path = os.path.join(dense_dir, "fused.ply")

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    def run_cmd(cmd, desc):
        print(f"\n🚀 {desc}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("✔️ Comando:", ' '.join(cmd))
        print("📤 STDOUT:\n", result.stdout)
        print("⚠️ STDERR:\n", result.stderr)
        result.check_returncode()

    # 🔧 Resize immagini grandi
    resize_images_in_dir(input_dir)

    # 1. Feature extraction
    run_cmd([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", input_dir
    ], "Estrazione feature")

    # 2. Feature matching
    run_cmd([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path
    ], "Matching immagini")

    # 3. Sparse reconstruction
    run_cmd([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--output_path", sparse_dir,
        "--Mapper.init_min_tri_angle", "4.0",
        "--Mapper.min_num_matches", "15"
    ], "Ricostruzione sparsa")

    sparse_model_dir = os.path.join(sparse_dir, "0")
    if not os.path.exists(sparse_model_dir):
        raise RuntimeError("❌ Ricostruzione sparsa fallita: 'sparse/0' non esiste")

    print("🔍 Controllo sparse model...")
    num_files = len(os.listdir(sparse_model_dir))
    print(f"📂 File trovati in sparse/0: {num_files}")
    if num_files < 3:
        raise RuntimeError("⚠️ Sparse model incompleto, forse troppe poche immagini matchate.")

    # 4. Undistort images
    run_cmd([
        "colmap", "image_undistorter",
        "--image_path", input_dir,
        "--input_path", sparse_model_dir,
        "--output_path", dense_dir,
        "--output_type", "COLMAP"
    ], "Undistort immagini per dense")

    # 5. Dense stereo
    run_cmd([
        "colmap", "patch_match_stereo",
        "--workspace_path", dense_dir,
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.geom_consistency", "true"
    ], "Ricostruzione densa")

    # 6. Fusion
    run_cmd([
        "colmap", "stereo_fusion",
        "--workspace_path", dense_dir,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", fused_path
    ], "Fusione nuvola densa")

    if not os.path.exists(fused_path):
        raise RuntimeError("❌ 'fused.ply' non trovato — fusione fallita.")

    # 🔍 Controllo punti della nuvola
    num_points = int(os.popen(f"grep -c '^v ' {fused_path}").read().strip() or 0)
    print(f"🔎 Punti nella nuvola fusa: {num_points}")
    if num_points < 1000:
        raise RuntimeError(f"❌ Solo {num_points} punti nella nuvola — impossibile creare una mesh utile.")

    # 7. Meshing
    run_cmd([
        "colmap", "poisson_mesher",
        "--input_path", fused_path,
        "--output_path", meshed_model
    ], "Generazione mesh finale")

    print(f"✅ Modello 3D completo generato: {meshed_model}")
    return meshed_model
