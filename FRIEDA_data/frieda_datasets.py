import os

from torch.utils.data import Dataset

class FRIEDA(Dataset):
    def __init__(self, root_dir:str='data', 
                 download:bool=False):
        self.root_dir = root_dir

        annotation_file = os.path.join(root_dir, "questions.json")
        image_dir = os.path.join(root_dir, 'imgs')


        if not os.path.exists(image_dir):
            print("FRIEDA data directory cannot be found!")

            if download:
                print("Downloading FRIEDA images.")
                self.download_image()
            else:
                raise RuntimeError("Please allow downloading the dataset by setting '--download' for specify the correct directory.")
    
    def download_image(self):
        import gdown

        return 0
