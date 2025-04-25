import os
import subprocess

def run_colmap_pipeline(input_dir, output_dir):
    database_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    model_dir = os.path.join(sparse_dir, "0")
    model_ply = os.path.join(output_dir, "model.ply")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(sparse_dir, exist_ok=True)

    print("📦 Estrazione feature...")
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--ImageReader.camera_model", "PINHOLE",
        "--ImageReader.single_camera", "1",
        "--ImageReader.default_focal_length_factor", "1.2"
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

        # Parametri General
        "--Mapper.multiple_models", "1",
        "--Mapper.max_num_models", "50",
        "--Mapper.max_model_overlap", "20",
        "--Mapper.min_model_size", "10",
        "--Mapper.extract_colors", "1",
        "--Mapper.num_threads", "-1",
        "--Mapper.min_num_matches", "15",
        "--Mapper.snapshot_images_freq", "0",

        # Parametri Init
        "--Mapper.init_image_id1", "-1",
        "--Mapper.init_image_id2", "-1",
        "--Mapper.init_num_trials", "200",
        "--Mapper.init_min_num_inliers", "100",
        "--Mapper.init_max_error", "4.0",
        "--Mapper.init_max_forward_motion", "0.95",
        "--Mapper.init_min_tri_angle", "16.0",
        "--Mapper.init_max_reg_trials", "2",

        # Parametri Registration
        "--Mapper.abs_pose_max_error", "12.0",
        "--Mapper.abs_pose_min_num_inliers", "30",
        "--Mapper.abs_pose_min_inlier_ratio", "0.25",
        "--Mapper.max_reg_trials", "3",

        # Parametri Filter (solo quelli supportati da CLI)
        "--Mapper.min_focal_length_ratio", "0.1",
        "--Mapper.max_focal_length_ratio", "10.0",
        "--Mapper.max_extra_param", "1.0",
        "--Mapper.filter_max_reproj_error", "4.0",
        "--Mapper.filter_min_tri_angle", "1.5"
    ], check=True)

    if os.path.exists(model_dir):
        print("🎯 Conversione modello in PLY...")
        subprocess.run([
            "colmap", "model_converter",
            "--input_path", model_dir,
            "--output_path", model_ply,
            "--output_type", "PLY"
        ], check=True)
        print(f"✅ Modello salvato: {model_ply}")
    else:
        print("⚠️ Nessun modello trovato. La ricostruzione potrebbe essere fallita.")

    return model_ply


