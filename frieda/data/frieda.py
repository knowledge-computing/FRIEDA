import os
import tarfile

from torch.utils.data import Dataset

class FRIEDA(Dataset):
    def __init__(self, root_dir:str, 
                 download:bool=False):
        self.root_dir = root_dir

        img_dir = os.path.join(root_dir, 'images')
        annotation_file = os.path.join(root_dir, "frieda_q_bank.json")
        instruction_file = os.path.join(root_dir, "instruction.pkl")

        # Download image directory
        if not os.path.exists(img_dir):
            print("[INFO] FRIEDA data directory cannot be found.")

            if download:
                print("[INFO] Downloading FRIEDA images.")
                self.download_image(root_dir)
            else:
                raise RuntimeError("Please allow downloading the dataset by setting '--download' or specify the correct root directory.")
            
        # Download anntoation file
        if not os.path.exists(annotation_file):
            print("[INFO] FRIEDA question file cannot be found.")

            if download:
                print("[INFO] Downloading FRIEDA question file.")
                self.download_annotation(root_dir)

            else:
                raise RuntimeError("Please allow downloading the dataset by setting '--download' or specify the correct root directory.")
        
        # Download instruction file needed for system instruction
        if not os.path.exists(instruction_file):
            print("[INFO] FRIEDA instruction file cannot be found.")

            if download:
                print("[INFO] Downloading FRIEDA instruction file.")
                self.download_instruction(root_dir)

            else:
                raise RuntimeError("Please allow downloading the dataset by setting '--download' or specify the correct root directory.")
    

    def download_image(self, data_dir:str):
        import gdown

        gdown.download(id='1ULDAt9EdMs0oFYqm7t4hLPlgI8TxM9uR',
                       output=f"{data_dir}/")
        
        print("[INFO] Extracting image tar file.")
        with tarfile.open(f"{data_dir}/images.tar") as tar:
            tar.extractall(path=f"{data_dir}/")
    
    def download_annotation(self, data_dir:str):
        import gdown

        gdown.download(id='1ZMxqgQiywKzhqgSN_mw6wlb-RrCOG8MS',
                       output=f"{data_dir}/")
        
    def download_instruction(self, data_dir:str):
        import gdown

        gdown.download(id='1CeDcV2pgM3eoWevpX151QII6aw1ZU9ju',
                       output=f"{data_dir}/")