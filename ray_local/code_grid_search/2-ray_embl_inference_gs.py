import os
import ray
import torch
from torchvision import transforms
import time
from PIL import Image
import torch.nn.functional as F
import itertools
import pandas as pd
import s3fs


cwd = os.getcwd()

ds_name = 'dataset'

n_repetitions = 3

param_grid_inference = {
    'dataset_size': [2954],
    'parallelism_read': [-1, 25, 50],
    'num_cpus': [1, 2],
    'batch_size_map_batches': [64, 128, 256],
    'concurrency': [1, 2, 3],
    'preserve_order': [False]
}

# Create all possible parameter combinations
configurations = list(itertools.product(*param_grid_inference.values()))


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


def save_metrics_locally(metrics_to_csv, file_name):
    try:
        # Try to load existing CSV file and concatenate new metrics
        existing_df = pd.read_csv(file_name)
        new_df = pd.concat([existing_df, pd.DataFrame(metrics_to_csv, index=[0])])
        new_df.to_csv(file_name, index=False)
        print("Updated metrics have been saved to", file_name)
    except FileNotFoundError:
        # If the file doesn't exist, create a new one with the metrics
        df = pd.DataFrame(metrics_to_csv, index=[0])
        df.to_csv(file_name, index=False)
        print("A new file", file_name, "has been created with metrics")


def evaluate(params):
    dataset_size, parallelism_read, num_cpus, batch_size_map_batches, concurrency, preserve_order = params

    if ray.is_initialized:
        ray.shutdown()

    ray.init()

    ctx = ray.data.DataContext.get_current()
    ctx.execution_options.verbose_progress = True
    ctx.execution_options.preserve_order = preserve_order

    job_id = ray.get_runtime_context().get_job_id()

    image_directory = f"{cwd}/../../embl/{ds_name}/"
    image_files = [os.path.join(image_directory, file) for file in os.listdir(image_directory)]
    image_files = image_files[:dataset_size]

    start_time = time.time()

    ds = ray.data.read_images(paths=image_files, include_paths=True, mode="RGB", file_extensions=None, parallelism=parallelism_read, ray_remote_args={"num_cpus": num_cpus})

    # fs = s3fs.S3FileSystem(anon=False, key='minioadmin', secret='minioadmin', client_kwargs={'endpoint_url': 'http://localhost:9000'})
    # ds = ray.data.read_images(filesystem=fs, paths="s3://bucket/dataset/", include_paths=True, mode="RGB", file_extensions=None, parallelism=parallelism_read, ray_remote_args={"num_cpus": num_cpus})

    start_time_without_metadata_fetching = time.time()

    ds = ds.map_batches(preprocess, batch_format="numpy", batch_size=batch_size_map_batches, num_cpus=num_cpus)
    ds = ds.map_batches(Actor, batch_format="numpy", batch_size=batch_size_map_batches, num_cpus=num_cpus, concurrency=concurrency)

    for _ in ds.iter_batches(batch_format="numpy", batch_size=None):
        pass

    end_time = time.time()

    num_records = ds.count()
    total_time = end_time - start_time
    throughput = num_records / total_time
    total_time_without_metadata_fetching = end_time - start_time_without_metadata_fetching
    throughput_without_metadata_fetching = num_records / total_time_without_metadata_fetching

    metrics = {
        "Job ID": job_id,
        "Dataset": ds_name,
        "Preserve order": preserve_order,
        "Parallelism": parallelism_read,
        "Num cpus": num_cpus,
        "Batch size map_batches()": batch_size_map_batches,
        "Concurrency": concurrency,
        "Dataset size (bytes)": ds.size_bytes(),
        "Num records dataset": num_records,
        "Num blocks dataset": ds.num_blocks(),
        "Total time": total_time,
        "Throughput (img/sec)": throughput,
        "Total time w/o metadata fetching": total_time_without_metadata_fetching,
        "Throughput w/o metadata fetching (img/sec)": throughput_without_metadata_fetching
    }

    save_metrics_locally(metrics, "metrics_embl_inference_local.csv")

    return metrics


best_throughput = -1
best_params = None
for config in configurations:
    iteration_metrics = []
    job_ids = []
    sum_metrics = {
        "Total time": 0,
        "Throughput (img/sec)": 0,
        "Total time w/o metadata fetching": 0,
        "Throughput w/o metadata fetching (img/sec)": 0
    }

    for _ in range(n_repetitions):
        iteration_metrics = evaluate(config)

        job_ids.append(iteration_metrics["Job ID"])

        for key in sum_metrics.keys():
            if key in iteration_metrics:
                sum_metrics[key] += iteration_metrics[key]

    avg_metrics = iteration_metrics

    avg_metrics["Job ID"] = ', '.join(map(str, job_ids))

    avg_metrics.update({key: value / n_repetitions for key, value in sum_metrics.items()})

    save_metrics_locally(avg_metrics, f"avg_metrics_{n_repetitions}_repetitions_embl_inference.csv")

    if avg_metrics["Throughput (img/sec)"] > best_throughput:
        best_throughput = avg_metrics["Throughput (img/sec)"]
        best_params = config

print("Best throughput:", best_throughput)
print("Best parameters:", best_params)
