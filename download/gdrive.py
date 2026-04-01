import os
import tarfile

def download(root_dir: str,
             bool_return_snap: bool=False) -> None:
    img_dir = os.path.join(root_dir, 'images')
    annotation_file = os.path.join(root_dir, "frieda_q_bank.json")
    instruction_file = os.path.join(root_dir, "instruction.pkl")

    # Download image directory
    if not os.path.exists(img_dir):
        import gdown

        print("[INFO] FRIEDA data directory cannot be found.")
        print("[INFO] Downloading FRIEDA images.")

        gdown.download(id='1ULDAt9EdMs0oFYqm7t4hLPlgI8TxM9uR',
                       output=f"{root_dir}/")
        
        print("[INFO] Extracting image tar file.")
        with tarfile.open(f"{root_dir}/images.tar") as tar:
            tar.extractall(path=f"{root_dir}/")

    # # Download annotation file
    # if not os.path.exists(annotation_file):
    #     import gdown
    #     print("[INFO] FRIEDA question file cannot be found.")
    #     print("[INFO] Downloading FRIEDA question file.")

    #     gdown.download(id='1ZMxqgQiywKzhqgSN_mw6wlb-RrCOG8MS',
    #                    output=f"{root_dir}/")
        
    # Download instruction file needed for system instruction
    if not os.path.exists(instruction_file):
        import gdown
        print("[INFO] FRIEDA instruction file cannot be found.")
        print("[INFO] Downloading FRIEDA instruction file.")       

        gdown.download(id='1CeDcV2pgM3eoWevpX151QII6aw1ZU9ju',
                       output=f"{root_dir}/")
    
    print(f"[INFO] Downloaded FRIEDA to {root_dir} through Google Drive")

    if bool_return_snap:
        return root_dir