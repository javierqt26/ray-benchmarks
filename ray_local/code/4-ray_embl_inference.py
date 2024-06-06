import os
import ray
import torch
from torchvision import transforms
import time
from PIL import Image
import torch.nn.functional as F
import s3fs

DATASET_SIZE = 14
BATCH_SIZE = 2

cwd = os.getcwd()

ray.init()

image_directory = f"{cwd}/../../embl/dataset/"
image_files = [os.path.join(image_directory, file) for file in os.listdir(image_directory)]
image_files = image_files[:DATASET_SIZE]

start_time = time.time()

# fs = s3fs.S3FileSystem(anon=False, key='minioadmin', secret='minioadmin', client_kwargs={'endpoint_url': 'http://localhost:9000'})
# ds = ray.data.read_images(filesystem=fs, paths="s3://bucket/dataset/", include_paths=True, mode="RGB", file_extensions=None, ray_remote_args={"num_cpus": 1})

ds = ray.data.read_images(paths=image_files, include_paths=True, mode="RGB", file_extensions=None, ray_remote_args={"num_cpus": 1})

def preprocess(image_batch):
    composed_transforms = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: F.grid_sample(x.unsqueeze(0), torch.nn.functional.affine_grid(
            torch.eye(2, 3, dtype=torch.float32).unsqueeze(0), [1, 3, 224, 224], True), mode='bilinear',
                                                  padding_mode='reflection', align_corners=True)),
        transforms.Lambda(lambda x: x.squeeze(0)),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    preprocessed_images = []
    for img in image_batch["image"]:
        img_pil = Image.fromarray(img)
        preprocessed_img = composed_transforms(img_pil)
        preprocessed_images.append(preprocessed_img.numpy())
    return {"image": preprocessed_images, "path": image_batch["path"]}

class Actor:
    def __init__(self):
        self.model = torch.jit.load(f"{cwd}/../../embl/torchscript_model_2.1.2.pt",torch.device('cpu'))

    def __call__(self, batch):
        inputs = torch.as_tensor(batch["image"], device="cpu")
        with torch.no_grad():
            output_batch = self.model.forward(inputs)
            predictions_batch = torch.softmax(output_batch, dim=1)
            pred_probs = predictions_batch.numpy()
            preds = pred_probs.argmax(axis=1)
            labels = []
            probabilities = []
            for i in range(len(pred_probs)):
                probabilities.append(pred_probs[i][0])
                if preds[i] == 0:
                    labels.append('off')
                else:
                    labels.append('on')
            return {"path": batch["path"], "label": labels, "prob": probabilities}


start_time_without_metadata_fetching = time.time()
ds = ds.map_batches(preprocess, batch_format="numpy", num_cpus=1)
ds = ds.map_batches(Actor, batch_format="numpy", batch_size=BATCH_SIZE, num_cpus=1, concurrency=2)

for _ in ds.iter_batches(batch_format="numpy", batch_size=None):
    pass

end_time = time.time()

num_records = ds.count()
print("Total time: ", end_time - start_time)
print("Throughput (img/sec): ", num_records / (end_time - start_time))
print("Total time w/o metadata fetching (img/sec): ", end_time - start_time_without_metadata_fetching)
print("Throughput w/o metadata fetching (img/sec): ", num_records / (end_time - start_time_without_metadata_fetching))

print(ds.schema())
ds.show() # By default, it only shows 20 records
