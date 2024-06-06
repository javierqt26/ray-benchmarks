FROM rayproject/ray:2.9.3-py311

RUN pip install pandas==1.5.2 \
tqdm==4.65.0 \
s3fs==2023.10.0 \
pyarrow==13.0.0 \
numpy==1.26.4

ARG BINS_DIR="/bin"
RUN mkdir -p ${BINS_DIR}
COPY torchscript_model_2.1.2.pt ${BINS_DIR}/model.pt

RUN pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu