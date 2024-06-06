import ray
import torch
from torchvision import transforms
import time
from PIL import Image
import torch.nn.functional as F
import s3fs

ray.init()

start_time = time.time()

fs = s3fs.S3FileSystem(anon=False, key='minioadmin', secret='minioadmin', client_kwargs={'endpoint_url': 'http://localhost:9000'})
ds = ray.data.read_images(filesystem=fs, paths="s3://bucket/dataset/", include_paths=True, mode='RGB', file_extensions=None, ray_remote_args={"num_cpus": 1})


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


start_time_without_metadata_fetching = time.time()
ds = ds.map_batches(preprocess, batch_format="numpy", num_cpus=1)

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
