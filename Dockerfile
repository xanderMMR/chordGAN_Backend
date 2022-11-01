FROM python:3.10.4-slim

RUN apt-get update \
     && apt-get install -y \
        libgl1-mesa-glx \
        libx11-xcb1 \
        libsndfile1 \
     && apt-get clean all \
     && rm -r /var/lib/apt/lists/*

RUN pip install torch
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

COPY model/ ./model/
COPY data/ ./data/
COPY resources/ ./resources/

COPY IsParsed.txt .
COPY  DidGenerate.txt .
EXPOSE 5000
CMD ["python", "api.py"]












# FROM nvidia/cuda:11.1.1-base-ubuntu20.04
# RUN apt-get update
# RUN apt-get install -y python3    python3-pip
# RUN pip3 install torch torchvision


# RUN apt-get update \
#      && apt-get install -y \
#         libgl1-mesa-glx \
#         libx11-xcb1 \
#         libsndfile1 \
#      && apt-get clean all \
#      && rm -r /var/lib/apt/lists/*

# # RUN apt-get --yes install libsndfile1
# # SUDO groupadd docker
# # RUN pip install torch
# COPY requirements.txt .
# RUN python3 -m pip install -r requirements.txt

# WORKDIR /app
# COPY . /app


# COPY model/ ./model/
# COPY data/ ./data/
# COPY  utils.py ./utils.py
# CMD ["python3", "api.py"]
