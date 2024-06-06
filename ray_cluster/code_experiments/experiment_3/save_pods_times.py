import subprocess
import json
import csv

csv_file = "pods_times.csv"

pods = subprocess.run(["kubectl", "get", "pods", "-l=ray.io/is-ray-node=yes", "-o", "json"], capture_output=True, text=True)
pods_json = json.loads(pods.stdout)

with open(csv_file, mode='w') as file:
    writer = csv.writer(file)
    writer.writerow(["Pod", "Initialized", "Ready"])

for pod in pods_json['items']:
    pod_name = pod['metadata']['name']
    print(pod)
    initialized_time = None
    ready_time = None

    for condition in pod['status']['conditions']:
        if condition['type'] == 'PodScheduled':
            initialized_time = condition['lastTransitionTime']
        elif condition['type'] == 'Ready':
            ready_time = condition['lastTransitionTime']

    with open(csv_file, mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([pod_name, initialized_time, ready_time])

print("The data has been saved in", csv_file)