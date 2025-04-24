import os
import subprocess

def run_colmap_pipeline(input_dir, output_dir):
    sparse_dir = os.path.join(output_dir, "sparse")
    dense_dir = os.path.join(output_dir, "dense")
    meshed_model = os.path.join(output_dir, "final_model.ply")
    database_path = os.path.join(output_dir, "database.db")

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    print("📦 Estrazione feature...")
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", input_dir
    ], check=True)

    print("🔁 Matching immagini...")
    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path
    ], check=True)

    print("🏗️ Ricostruzione sparsa...")
    subprocess.run([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--output_path", sparse_dir,
        "--Mapper.init_min_tri_angle", "4.0",
        "--Mapper.min_num_matches", "15"
    ], check=True)

    print("📷 Undistort immagini per ricostruzione densa...")
    subprocess.run([
        "colmap", "image_undistorter",
        "--image_path", input_dir,
        "--input_path", sparse_dir,
        "--output_path", dense_dir,
        "--output_type", "COLMAP"
    ], check=True)

    print("🧠 Dense stereo matching...")
    subprocess.run([
        "colmap", "patch_match_stereo",
        "--workspace_path", dense_dir,
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.geom_consistency", "true"
    ], check=True)

    print("🌩️ Fusione nuvola di punti...")
    subprocess.run([
        "colmap", "stereo_fusion",
        "--workspace_path", dense_dir,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", os.path.join(dense_dir, "fused.ply")
    ], check=True)

    print("🔷 Generazione mesh finale...")
    subprocess.run([
        "colmap", "poisson_mesher",
        "--input_path", os.path.join(dense_dir, "fused.ply"),
        "--output_path", meshed_model
    ], check=True)

    return meshed_model
