import os

from torch.utils.data import Dataset

class FRIEDA(Dataset):
    def __init__(self, root_dir:str='data', 
                 download:bool=False):
        self.root_dir = root_dir

        annotation_file = os.path.join(root_dir, "questions.json")
        image_dir = os.path.join(root_dir, 'imgs')


        if not os.path.exists(image_dir):
            print("[INFO] FRIEDA data directory cannot be found!")

            if download:
                print("[INFO] Downloading FRIEDA images.")
                self.download_image()
            else:
                raise RuntimeError("Please allow downloading the dataset by setting '--download' or specify the correct root directory.")
            
        if not os.path.exists(annotation_file):
            print("[INFO] FRIEDA question file cannot be found")

            if download:
                print("[INFO] Downloading FRIEDA question file.")
                self.download_annotation()

            else:
                raise RuntimeError("Please allow downloading the dataset by setting '--download' or specify the correct root directory.")
    

    def download_image(self):
        import gdown

        return 0
    

    def download_annotation(self):
        import gdown

        return 0
