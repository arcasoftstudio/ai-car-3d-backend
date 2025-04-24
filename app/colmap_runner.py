import os
import subprocess

def run_colmap_pipeline(input_dir, output_dir):
    sparse_dir = os.path.join(output_dir, "sparse")
    dense_dir = os.path.join(output_dir, "dense")
    meshed_model = os.path.join(output_dir, "final_model.ply")
    database_path = os.path.join(output_dir, "database.db")

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    def run_cmd(cmd, desc):
        print(f"\n🚀 {desc}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("✔️ Comando:", ' '.join(cmd))
        print("📤 STDOUT:\n", result.stdout)
        print("⚠️ STDERR:\n", result.stderr)
        result.check_returncode()

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
    fused_path = os.path.join(dense_dir, "fused.ply")
    run_cmd([
        "colmap", "stereo_fusion",
        "--workspace_path", dense_dir,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", fused_path
    ], "Fusione nuvola densa")

    # 7. Meshing
    run_cmd([
        "colmap", "poisson_mesher",
        "--input_path", fused_path,
        "--output_path", meshed_model
    ], "Generazione mesh finale")

    print(f"✅ Modello 3D completo generato: {meshed_model}")
    return meshed_model
