"""
Script to download the dataset from Hugging Face.
In this example, we download the MSMARCO-XI dataset.
"""
from datasets import load_dataset
import os

def download_dataset(dataset_name: str = "ai4bharat/MSMARCO-XI", 
                     split: str = "train", 
                     save_path: str = "./data/raw",
                     limit: int = None):
    """
    Download the dataset and save it to disk.
    For simplicity, we are just loading the dataset and not saving it to disk.
    In a real implementation, we might save it as CSV, JSON, or another format.
    """
    print(f"Downloading dataset {dataset_name} (split: {split})...")
    dataset = load_dataset(dataset_name, split=split)
    if limit:
        dataset = dataset.select(range(limit))
    
    # Print some information about the dataset
    print(f"Dataset loaded with {len(dataset)} examples")
    print(f"Features: {dataset.features}")
    
    # In a real implementation, we would save the dataset to disk
    # For example, as a CSV or JSON file.
    # For now, we just return the dataset object.
    return dataset

if __name__ == "__main__":
    # Example usage
    dataset = download_dataset(limit=1000)  # Limit to 1000 for quick testing
    print("First example:", dataset[0])