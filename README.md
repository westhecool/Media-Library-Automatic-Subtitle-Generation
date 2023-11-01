# Media Library Automatic Subtitle Generation
Automatic subtitle generation using OpenAI's Whisper for jellyfin.

## Install
Using a venv:
```sh
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Run (on cpu)
```sh
./venv/bin/python3 main.py [input file or directory]
```

## GPU
GPU support is kind of finicky because you need the cublas and cudnn libraries. If you do already have them installed you can just run the program with the flag `--gpu` to use the gpu. You can also see a fix below for Linux.

## GPU fix (Linux only)
You can actually download the libraries with `pip` if you are on Linux.
```sh
./venv/bin/pip install -r requirements.gpu.txt
```
Then you can start the program using:
```sh
bash gpurun.sh [input file or directory]
```