import os
from huggingface_hub import hf_hub_download
import logging

logger = logging.getLogger(__name__)

def download_hinval_dataset(cache_dir: str = "data/raw") -> str:
    """
    Downloads hinval.parquet from huggingface if it doesn't exist locally.
    """
    os.makedirs(cache_dir, exist_ok=True)
    file_path = os.path.join(cache_dir, "hinval.parquet")
    
    # We use existence check as a simple cache verification
    if os.path.exists(file_path):
        logger.info(f"Dataset already cached at {file_path}. Skipping download.")
        return file_path
        
    logger.info("Downloading dataset from HuggingFace...")
    # hf_hub_download caches internally, but we'll specify local_dir for explicit control
    downloaded_path = hf_hub_download(
        repo_id="ai4bharat/MSMARCO-XI",
        repo_type="dataset",
        filename="validation/hinval.parquet",
        local_dir=cache_dir,
        local_dir_use_symlinks=False
    )
    
    logger.info(f"Dataset downloaded to {downloaded_path}")
    return downloaded_path

if __name__ == "__main__":
    download_hinval_dataset()
