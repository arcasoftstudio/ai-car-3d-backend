import os
import subprocess
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def run_colmap_pipeline(upload_folder):
    images_path = os.path.join(upload_folder, "images")
    sparse_path = os.path.join(upload_folder, "sparse")
    dense_path = os.path.join(upload_folder, "dense")
    database_path = os.path.join(upload_folder, "database.db")
    final_mesh_path = os.path.join(upload_folder, "final_mesh.ply")

    os.makedirs(images_path, exist_ok=True)
    os.makedirs(sparse_path, exist_ok=True)
    os.makedirs(dense_path, exist_ok=True)

    logger.info("\n🔍 Estrazione feature...")
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", images_path,
        "--ImageReader.single_camera", "1"
    ], check=True)

    logger.info("\n🔍 Matching sequenziale (come nella GUI)...")
    subprocess.run([
        "colmap", "sequential_matcher",
        "--database_path", database_path,
        "--SiftMatching.guided_matching", "1"
    ], check=True)

    logger.info("\n🏗️ Ricostruzione sparsa...")
    subprocess.run([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", images_path,
        "--output_path", sparse_path,
        "--Mapper.extract_colors", "1"
    ], check=True)

    # Verifica sparse
    sparse_model_dir = os.path.join(sparse_path, "0")
    if not os.path.exists(os.path.join(sparse_model_dir, "cameras.bin")):
        raise Exception("❌ Errore: ricostruzione sparsa fallita, sparse/0 mancante o incompleto.")
    else:
        logger.info(f"📸 Ricostruzione sparsa completata. File presenti: {os.listdir(sparse_model_dir)}")

    logger.info("\n🖼️ Undistort immagini...")
    subprocess.run([
        "colmap", "image_undistorter",
        "--image_path", images_path,
        "--input_path", sparse_model_dir,
        "--output_path", dense_path,
        "--output_type", "COLMAP",
        "--max_image_size", "4096"
    ], check=True)

    logger.info("\n🧩 Ricostruzione densa ottimizzata...")
    subprocess.run([
        "colmap", "patch_match_stereo",
        "--workspace_path", dense_path,
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.geom_consistency", "1",
        "--PatchMatchStereo.window_radius", "7",
        "--PatchMatchStereo.num_samples", "20",
        "--PatchMatchStereo.max_image_size", "4096",
        "--PatchMatchStereo.cache_size", "64",
        "--PatchMatchStereo.filter", "1"
    ], check=True)

    # Verifica depth maps
    depth_map_dir = os.path.join(dense_path, "stereo", "depth_maps")
    if not os.path.exists(depth_map_dir) or len(os.listdir(depth_map_dir)) == 0:
        raise Exception("❌ Errore: patch_match_stereo non ha generato depth maps. La ricostruzione densa è fallita.")
    else:
        logger.info(f"✅ Depth maps generate: {len(os.listdir(depth_map_dir))}")

    logger.info("\n🔗 Fusione stereo migliorata...")
    subprocess.run([
        "colmap", "stereo_fusion",
        "--workspace_path", dense_path,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", os.path.join(dense_path, "fused.ply"),
        "--StereoFusion.min_num_pixels", "5",
        "--StereoFusion.max_image_size", "4096"
    ], check=True)

    logger.info("\n🛠️ Creazione mesh con pulizia...")
    subprocess.run([
        "colmap", "poisson_mesher",
        "--input_path", os.path.join(dense_path, "fused.ply"),
        "--output_path", final_mesh_path,
        "--PoissonMeshing.trim", "10"
    ], check=True)

    # Controllo finale: il file finale esiste davvero?
    if
