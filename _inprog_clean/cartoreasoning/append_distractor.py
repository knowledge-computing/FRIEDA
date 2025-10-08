import argparse
import polars as pl

import os
from glob import glob

from PIL import Image
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import matplotlib.pyplot as plt

model = SentenceTransformer('clip-ViT-B-32')

def generate_clip_embeddings(images_path, model):

    image_paths = glob(os.path.join(images_path, '**/*.png'), recursive=True) \
                + glob(os.path.join(images_path, '**/*.jpg'), recursive=True) \
                + glob(os.path.join(images_path, '**/*.jpeg'), recursive=True)
    
    embeddings = []
    for img_path in image_paths:
        image = Image.open(img_path)
        embedding = model.encode(image)
        embeddings.append(embedding)
    
    return embeddings, image_paths

def create_faiss_index(embeddings, output_path):

    dimension = len(embeddings[0])
    index = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIDMap(index)
    
    vectors = np.array(embeddings).astype(np.float32)

    # Add vectors to the index with IDs
    index.add_with_ids(vectors, np.array(range(len(embeddings))))
    
    # Save the index
    faiss.write_index(index, output_path)
    print(f"Index created and saved to {output_path}")
    
    return index

# def load_faiss_index(index_path):
#     index = faiss.read_index(index_path)
#     with open(index_path + '.paths', 'r') as f:
#         image_paths = [line.strip() for line in f]
#     print(f"Index loaded from {index_path}")
#     return index, image_paths

# index, image_paths = load_faiss_index(OUTPUT_INDEX_PATH)

def retrieve_similar_images(query, model, index, image_paths, top_k=3):
    
    # query preprocess:
    if query.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        query = Image.open(query)

    query_features = model.encode(query)
    query_features = query_features.astype(np.float32).reshape(1, -1)

    distances, indices = index.search(query_features, top_k)

    retrieved_images = [image_paths[int(idx)] for idx in indices[0]]

    return query, retrieved_images

def get_contextual(dir_image, image_urls, contextual_size):
    sub_path, img_name = image_urls[0].rsplit('/', 1)
    IMAGES_PATH = os.path.join(dir_image, sub_path)

    for i in image_urls:
        full_img_path = os.path.join(dir_image, i)
        if not os.path.exists(full_img_path):
            return ["CANNOT FIND IMAGE"]

    total_img_length = len(os.listdir(IMAGES_PATH))
    if total_img_length <= contextual_size:
        return [os.path.join(sub_path, i) for i in os.listdir(IMAGES_PATH)]

    embeddings, image_paths = generate_clip_embeddings(IMAGES_PATH, model)

    OUTPUT_INDEX_PATH = f"./vector.index"
    index = create_faiss_index(embeddings, OUTPUT_INDEX_PATH)

    full_img_path = os.path.join(IMAGES_PATH, img_name)

    tmp_contextuals = []
    contextuals = set()
    for i in image_urls:
        query = os.path.join(dir_image, i)
        query, retrieved_images = retrieve_similar_images(query, model, index, image_paths, top_k=contextual_size)

        list_tmp = [r.split(dir_image)[1] for r in retrieved_images]
        tmp_contextuals.append(list_tmp)

    idx = 0
    while True:
        try:
            for j in tmp_contextuals:
                contextuals.add(j[idx])
        except:
            pass
        if len(contextuals) >= contextual_size:
            contextuals = list(contextuals)
            contextuals = contextuals[:contextual_size]
            break
        idx += 1

    return contextuals

def append_contextual_info(file_name, dir_image, contextual_size,
                           start_idx, last_idx, ):
    pl_data = pl.read_json(file_name)
    
    if last_idx:
        pl_data = pl_data[start_idx:last_idx]

    pl_data = pl_data.with_columns(
        contextual_urls = pl.struct(pl.all()).map_elements(lambda x: get_contextual(dir_image, x['image_urls'], contextual_size))
    )

    pd_data = pl_data.to_pandas()

    new_file_name = f"{file_name.split('.json')[0]}_contextual{start_idx}_{contextual_size}.json"

    pd_data.to_json(new_file_name, orient='records', indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Contextual Image Append Tool')

    parser.add_argument('--file_data', type=str, required=True)
    parser.add_argument('--image_dir', type=str, required=True)
    parser.add_argument('--context_size', type=int, required=True)

    parser.add_argument('--start_index', type=int, default=0)
    parser.add_argument('--last_index', type=int, default=None)
    

    args = parser.parse_args()

    append_contextual_info(file_name=args.file_data, 
                           dir_image=args.image_dir,
                           contextual_size=args.context_size,
                           start_idx=args.start_index,
                           last_idx=args.last_index)