import os
import subprocess
import shutil
import logging

# Impostazione dei log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_colmap_pipeline(input_dir, output_dir):
    if not os.path.exists(input_dir):
        logger.error(f"❌ La directory di input non esiste: {input_dir}")
        return None
    
    if len([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]) == 0:
        logger.error("❌ Nessuna immagine trovata nella directory di input!")
        return None
    
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
    logger.info("\n📦 Estrazione feature...")
    try:
        subprocess.run([
            "colmap", "feature_extractor",
            "--database_path", database_path,
            "--image_path", input_dir,
            "--ImageReader.camera_model", "PINHOLE",
            "--ImageReader.single_camera", "1",
            "--ImageReader.default_focal_length_factor", "1.2"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Errore durante l'estrazione delle feature: {e}")
        return None

    # Matching delle immagini
    logger.info("\n🔁 Matching immagini...")
    try:
        subprocess.run([
            "colmap", "exhaustive_matcher",
            "--database_path", database_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Errore durante il matching delle immagini: {e}")
        return None

    # Ricostruzione sparsa
    logger.info("\n🏗️ Ricostruzione sparsa...")
    try:
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
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Errore durante la ricostruzione sparsa: {e}")
        return None

    # Verifica la presenza del modello sparso
    model_dir = os.path.join(sparse_dir, "0")
    if not os.path.exists(model_dir):
        logger.error(f"❌ Nessun modello sparso trovato nella cartella {model_dir}")
        return None

    # Conversione del modello sparso in PLY
    logger.info("\n🎯 Conversione modello sparso in PLY...")
    try:
        subprocess.run([
            "colmap", "model_converter",
            "--input_path", model_dir,
            "--output_path", final_sparse_ply,
            "--output_type", "PLY"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Errore durante la conversione del modello sparso in PLY: {e}")
        return None

    # Ricostruzione densa con PatchMatch Stereo
    logger.info("\n🔍 Ricostruzione densa: PatchMatch stereo...")
    try:
        subprocess.run([
            "colmap", "patch_match_stereo",
            "--workspace_path", output_dir,
            "--workspace_format", "COLMAP",
            "--PatchMatchStereo.geom_consistency", "true"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Errore durante la ricostruzione densa con PatchMatch stereo: {e}")
        return None

    # Fusione delle mappe di profondità
    logger.info("\n🌩️ Fusione mappe di profondità...")
    try:
        subprocess.run([
            "colmap", "stereo_fusion",
            "--workspace_path", output_dir,
            "--workspace_format", "COLMAP",
            "--input_type", "geometric",
            "--output_path", fused_ply
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Errore durante la fusione delle mappe di profondità: {e}")
        return None

    # Generazione della mesh finale
    logger.info("\n🧱 Generazione mesh...")
    try:
        subprocess.run([
            "colmap", "poisson_mesher",
            "--input_path", fused_ply,
            "--output_path", mesh_ply
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Errore durante la generazione della mesh finale: {e}")
        return None

    # Salva la mesh finale nella cartella di output
    shutil.copy(mesh_ply, final_sparse_ply)  # Salvataggio diretto del modello mesh

    logger.info(f"\n✅ Mesh finale salvata in: {final_sparse_ply}")
    return final_sparse_ply
