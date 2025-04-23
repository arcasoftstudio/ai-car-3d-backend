import os
import subprocess

def run_colmap_pipeline(input_dir, output_dir):
    database_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    model_path = os.path.join(output_dir, "model.ply")

    # Step 1: Feature extraction
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", input_dir
    ], check=True)

    # Step 2: Feature matching
    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path
    ], check=True)

    # Step 3: Sparse reconstruction
    os.makedirs(sparse_dir, exist_ok=True)
    subprocess.run([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", input_dir,
        "--output_path", sparse_dir
    ], check=True)

    # Step 4: Convert model to PLY
    subprocess.run([
        "colmap", "model_converter",
        "--input_path", os.path.join(sparse_dir, "0"),
        "--output_path", model_path,
        "--output_type", "PLY"
    ], check=True)

    return model_path
