import os
import subprocess
import shutil

def run_colmap_pipeline(input_dir, output_dir):
    database_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    dense_dir = os.path.join(output_dir, "dense")
    stereo_dir = os.path.join(dense_dir, "stereo")
    fused_ply = os.path.join(dense_dir, "fused.ply")
    mesh_ply = os.path.join(dense_dir, "mesh.ply")
    final_sparse_ply = os.path.join(output_dir, "sparse_model.ply")

    # Creazione delle cartelle di output
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    # Estrazione delle feature
    print("\n📦 Estrazione feature...")
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--ImageReader.camera_model", "PINHOLE",
        "--ImageReader.single_camera", "1",
        "--ImageReader.default_focal_length_factor", "1.2"
    ], check=True)

    # Matching delle immagini
    print("\n🔁 Matching immagini...")
    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path
    ], check=True)

    # Ricostruzione sparsa
    print("\n🏗️ Ricostruzione sparsa...")
    subprocess.run([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--output_path", sparse_dir,

        "--Mapper.multiple_models", "1",
        "--Mapper.max_num_models", "50",
        "--Mapper.max_model_overlap", "20",
        "--Mapper.min_model_size", "10",
        "--Mapper.extract_colors", "1",
        "--Mapper.num_threads", "-1",
        "--Mapper.min_num_matches", "15",
        "--Mapper.snapshot_images_freq", "0",

        "--Mapper.init_image_id1", "-1",
        "--Mapper.init_image_id2", "-1",
        "--Mapper.init_num_trials", "200",
        "--Mapper.init_min_num_inliers", "100",
        "--Mapper.init_max_error", "4.0",  # Non rimuovere questa parte
        "--Mapper.init_max_forward_motion", "0.95",
        "--Mapper.init_min_tri_angle", "16.0",
        "--Mapper.init_max_reg_trials", "2",

        "--Mapper.abs_pose_max_error", "12.0",
        "--Mapper.abs_pose_min_num_inliers", "30",
        "--Mapper.abs_pose_min_inlier_ratio", "0.25",
        "--Mapper.max_reg_trials", "3",

        "--Mapper.min_focal_length_ratio", "0.1",
        "--Mapper.max_focal_length_ratio", "10.0",
        "--Mapper.max_extra_param", "1.0",
        "--Mapper.filter_max_reproj_error", "4.0",
        "--Mapper.filter_min_tri_angle", "1.5"
    ], check=True)

    # Verifica la presenza del modello sparso
    model_dir = os.path.join(sparse_dir, "0")
    if os.path.exists(model_dir):
        print("\n🎯 Conversione modello sparso in PLY...")
        subprocess.run([
            "colmap", "model_converter",
            "--input_path", model_dir,
            "--output_path", final_sparse_ply,
            "--output_type", "PLY"
        ], check=True)

        # Ricostruzione densa con PatchMatch Stereo
        print("\n🔍 Ricostruzione densa: PatchMatch stereo...")
        subprocess.run([
            "colmap", "patch_match_stereo",
            "--workspace_path", output_dir,
            "--workspace_format", "COLMAP",
            "--PatchMatchStereo.geom_consistency", "true"
        ], check=True)

        # Fusione delle mappe di profondità
        print("\n🌩️ Fusione mappe di profondità...")
        subprocess.run([
            "colmap", "stereo_fusion",
            "--workspace_path", output_dir,
            "--workspace_format", "COLMAP",
            "--input_type", "geometric",
            "--output_path", fused_ply
        ], check=True)

        # Generazione della mesh finale
        print("\n🧱 Generazione mesh...")
        subprocess.run([
            "colmap", "poisson_mesher",
            "--input_path", fused_ply,
            "--output_path", mesh_ply
        ], check=True)

        # Salva la mesh finale nella cartella di output
        shutil.copy(mesh_ply, final_sparse_ply)  # Salvataggio diretto del modello mesh

        print(f"\n✅ Mesh finale salvata in: {final_sparse_ply}")
    else:
        print("⚠️ Errore: nessun modello sparso trovato.")

    return final_sparse_ply
