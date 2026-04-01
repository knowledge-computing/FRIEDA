import pickle
from pathlib import Path
from typing import Union

from datasets import load_dataset, Image, Sequence

def download(root_dir: str = None,
             bool_return_snap: bool=False) -> Union[str, None]:
    
    from huggingface_hub import snapshot_download

    snap_dir = snapshot_download(
        repo_id="knowledge-computing/FRIEDA",
        repo_type="dataset",
        allow_patterns=["images/**", "instruction.pkl"],
        local_dir=root_dir
    )

    print(f"[INFO] Downloaded FRIEDA to {snap_dir} through HuggingFace")

    if bool_return_snap:
        return snap_dir

# def load()

# def archive() -> None:
#     REPO_ID = "knowledge-computing/FRIEDA"

#     ds = load_dataset(REPO_ID, split="data")

#     snap_dir = snapshot_download(
#         repo_id=REPO_ID,
#         repo_type="dataset",
#         allow_patterns=["images/**", "instruction.pkl"],
#     )
#     snap_dir = Path(snap_dir)

#     # Load instruction.pkl
#     with (snap_dir / "instruction.pkl").open("rb") as f:
#         instruction = pickle.load(f)

#     def to_local_paths(ex):
#         ex["images"] = [str(snap_dir / p) for p in ex["images"]]
#         ex["context_images"] = [str(snap_dir / p) for p in ex["context_images"]]
#         return ex

#     ds = ds.map(to_local_paths)
#     ds = ds.cast_column("images", Sequence(Image()))
#     ds = ds.cast_column("context_images", Sequence(Image()))

#     print("instruction type:", type(instruction))
#     print(type(ds[0]["images"][0]), ds[0]["images"][0].size)


#     import pickle

#     instr_path = snap_dir / "instruction.pkl"
#     with instr_path.open("rb") as f:
#         instruction = pickle.load(f)

#     print(type(instruction))