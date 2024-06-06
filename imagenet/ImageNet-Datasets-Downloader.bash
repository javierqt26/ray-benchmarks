git clone https://github.com/mf1024/ImageNet-Datasets-Downloader.git
cd ImageNet-Datasets-Downloader/
# Download images
python downloader.py -data_root "$(pwd)" -number_of_classes 10 -images_per_class 20
parent_dir="$(pwd)"/imagenet_images
# Join all subdirectories into the parent directory
find "$parent_dir" -mindepth 2 -type f -exec mv -t "$parent_dir" '{}' +
# Remove all subdirectories
find "$parent_dir" -mindepth 1 -type d -exec rm -rf '{}' +

