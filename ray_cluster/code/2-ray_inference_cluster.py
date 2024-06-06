import os
import ray
import torch
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights
import time
import s3fs

BATCH_SIZE = 8

ray.init()

model = resnet50(weights=ResNet50_Weights.DEFAULT)
model_ref = ray.put(model)

start_time = time.time()

fs = s3fs.S3FileSystem(anon=False, key='minioadmin', secret='minioadmin', client_kwargs={'endpoint_url': 'http://localhost:9000'})
ds = ray.data.read_images(filesystem=fs, paths="s3://bucket/dataset/", size=(224, 224), mode='RGB', ray_remote_args={"num_cpus": 1})


def preprocess(image_batch):
    preprocess = transforms.Compose(
        [
            transforms.Resize(256, antialias=None),
            transforms.CenterCrop(224),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    torch_tensor = torch.Tensor(image_batch["image"].transpose(0, 3, 1, 2))
    preprocessed_images = preprocess(torch_tensor).numpy()
    return {"image": preprocessed_images}


class Actor:
    def __init__(self, model):
        self.model = ray.get(model)
        self.model.eval()
        self.model.to("cpu")

    def __call__(self, batch):
        with torch.inference_mode():
            output = self.model(torch.as_tensor(batch["image"], device="cpu"))
            return {"class": output.cpu().numpy()}


start_time_without_metadata_fetching = time.time()
ds = ds.map_batches(preprocess, batch_format="numpy", num_cpus=1)
ds = ds.map_batches(Actor, batch_format="numpy", batch_size=BATCH_SIZE, num_cpus=1, concurrency=4, fn_constructor_kwargs={"model": model_ref})

for _ in ds.iter_batches(batch_format="numpy", batch_size=None):
    pass

end_time = time.time()

num_records = ds.count()
print("Total time: ", end_time - start_time)
print("Throughput (img/sec): ", num_records / (end_time - start_time))
print("Total time w/o metadata fetching (img/sec): ", end_time - start_time_without_metadata_fetching)
print("Throughput w/o metadata fetching (img/sec): ", num_records / (end_time - start_time_without_metadata_fetching))
