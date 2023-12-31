<h1>This is an audiobook creator using Tortoise TTS</h1>
<h2>With this repo you will be able to generate super high quality audio books using ai models locally on your computer for absolutely FREE. (No internet connection is needed)</h2>

## Sample Audio

Click below to listen to the audio sample:

[![Audio Sample](https://img.shields.io/badge/Play-AudioSample-blue.svg)](https://raw.githubusercontent.com/georgecsaszargit/tortoise_audio_book_creator/master/demo.mp3)

This repo is a fork of the tortoise-fast repo: https://github.com/152334H/tortoise-tts-fast.git
which was created from the repo: https://github.com/neonbjb/tortoise-tts.git

<h2>BIG THANKS TO THE ORIGINAL CREATOR OF TORTOISE AND THE CREATOR OF TORTOISE FAST!!!</h2>

I changed quite a few things:
- How text is split into chunks
- Added the ability to add pauses to generation. Single or double line breaks create short pause and more than 2 lines breaks a long pause that can be configured from streamlit gui
- Changed the UI quite a bit to optimize it for audio book creation
- Ability to load in a file
- Added self correction feature that tries to fix issues with generation automatically
- Finetuned tortoise settings
- Change terminal logs to show generation details more clearly
- Saves each generated file as mp3 and preserves them upon new generation
- Changed the way as audio files were saved avoiding any quality loss
- Save/reset settings

---------------------------------------------------
Hardware used for testing
---------------------------------------------------
Nvidia RTX 3090 (with Cuda 11.7)
Nvidia RTX 4090 (with Cuda 11.8)

---------------------------------------------------
Installation
---------------------------------------------------
I only have tested it on Linux. I tried it on Ubuntu 22.04, 23.10, and Manjaro Linux

<h2>Here are the steps:</h2>
Download Miniconda from: https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html
Create conda environment: conda create -n [env_name] python==3.9 numba inflect
Activate conda: conda activate [env_name]
Clone this repo: git clone https://github.com/georgecsaszargit/tortoise_audio_book_creator.git
Then install modules:
python -m pip install pyyaml
python -m pip install nltk
python -m pip install pydub
python -m pip install streamlit
python -m pip install librosa
python -m pip install sounddevice
python -m pip install fuzzywuzzy
python -m pip install drawille
python -m pip install pillow
python -m pip install git+https://github.com/openai/whisper.git
python -m pip install -e .
Download finetuned models and place them to ~/.cache/tortoise/models/ folder from:
https://huggingface.co/jbetker/tortoise-tts-finetuned-lj
(These models are better than the original tortoise models)

Instructional video: coming soon...

These are the versions of my python modules for reference:
Package                   Version      Editable project location
------------------------- ------------ -------------------------------------------------------
accelerate                0.20.3
aiohttp                   3.8.3
aiosignal                 1.2.0
altair                    5.0.1
annotated-types           0.5.0
appdirs                   1.4.4
art                       6.1
async-timeout             4.0.2
attrs                     23.1.0
audioread                 3.0.0
auraloss                  0.4.0
beautifulsoup4            4.12.2
BigVGAN                   0.0.1
bleach                    6.1.0
blinker                   1.6.2
boltons                   23.0.0
Bottleneck                1.3.5
brotlipy                  0.7.0
cachetools                5.3.1
certifi                   2023.7.22
cffi                      1.15.1
charset-normalizer        2.0.4
clean-fid                 0.1.35
click                     8.0.4
clip-anytorch             2.5.2
cmake                     3.27.5
contourpy                 1.1.0
cryptography              39.0.1
cycler                    0.11.0
datasets                  2.12.0
decorator                 5.1.1
deepspeed                 0.10.2
dill                      0.3.6
docker-pycreds            0.4.0
docstring-parser          0.15
drawille                  0.1.0
einops                    0.6.1
entrypoints               0.4
fastjsonschema            2.18.1
filelock                  3.9.0
fonttools                 4.40.0
frozenlist                1.3.3
fsspec                    2023.4.0
ftfy                      6.1.1
fuzzywuzzy                0.18.0
gdown                     4.7.1
gitdb                     4.0.10
GitPython                 3.1.31
gmpy2                     2.1.2
hjson                     3.1.0
huggingface-hub           0.15.1
idna                      3.4
imageio                   2.31.1
importlib-metadata        6.8.0
importlib-resources       6.0.0
inflect                   6.2.0
Jinja2                    3.1.2
joblib                    1.2.0
jsonmerge                 1.9.0
jsonschema                4.18.0
jsonschema-specifications 2023.6.1
jupyter_core              5.4.0
k-diffusion               0.0.14
kiwisolver                1.4.4
kornia                    0.6.12
lazy_loader               0.3
Levenshtein               0.22.0
librosa                   0.8.1
lit                       17.0.1
llvmlite                  0.39.1
markdown-it-py            3.0.0
MarkupSafe                2.1.1
matplotlib                3.7.2
mdurl                     0.1.2
mistune                   3.0.2
mkl-fft                   1.3.6
mkl-random                1.2.2
mkl-service               2.4.0
more-itertools            10.1.0
mpmath                    1.2.1
msgpack                   1.0.5
multidict                 6.0.2
multiprocess              0.70.14
nbconvert                 5.3.1
nbformat                  5.9.2
networkx                  2.8.4
ninja                     1.11.1.1
nltk                      3.8.1
numba                     0.56.4
numexpr                   2.8.4
numpy                     1.23.5
nvidia-cublas-cu11        11.10.3.66
nvidia-cuda-nvrtc-cu11    11.7.99
nvidia-cuda-runtime-cu11  11.7.99
nvidia-cudnn-cu11         8.5.0.96
openai-whisper            20230918
packaging                 23.0
pandas                    1.5.3
pandocfilters             1.5.0
pathtools                 0.1.2
pesq                      0.0.4
Pillow                    9.4.0
pip                       23.1.2
platformdirs              3.11.0
pooch                     1.6.0
progressbar               2.5
protobuf                  4.23.4
psutil                    5.9.5
py-cpuinfo                9.0.0
pyarrow                   11.0.0
pycparser                 2.21
pydantic                  1.10.13
pydantic_core             2.1.2
pydeck                    0.8.1b0
pydub                     0.25.1
Pygments                  2.15.1
Pympler                   1.0.1
pyOpenSSL                 23.0.0
pyparsing                 3.0.9
PySocks                   1.7.1
python-dateutil           2.8.2
python-Levenshtein        0.22.0
pytz                      2022.7
pytz-deprecation-shim     0.1.0.post0
PyWavelets                1.4.1
PyYAML                    6.0
rapidfuzz                 3.3.1
referencing               0.29.1
regex                     2022.7.9
requests                  2.29.0
resampy                   0.4.2
resize-right              0.0.2
responses                 0.13.3
rich                      13.4.2
rotary-embedding-torch    0.2.5
rpds-py                   0.8.10
sacremoses                0.0.43
scikit-image              0.21.0
scikit-learn              1.3.0
scipy                     1.11.1
sentry-sdk                1.27.1
setproctitle              1.3.2
setuptools                67.8.0
simple-parsing            0.0.21.post1
six                       1.16.0
smmap                     5.0.0
sounddevice               0.4.6
soundfile                 0.12.1
soupsieve                 2.4.1
soxr                      0.3.5
spicy                     0.16.0
streamlit                 1.24.1
sympy                     1.11.1
tenacity                  8.2.2
testpath                  0.6.0
threadpoolctl             3.1.0
tifffile                  2023.7.4
tiktoken                  0.3.3
tokenizers                0.13.2
toml                      0.10.2
toolz                     0.12.0
torch                     1.13.1
torchaudio                0.13.1
torchdiffeq               0.2.3
torchlibrosa              0.0.7
torchsde                  0.2.5
torchvision               0.15.2
tornado                   6.3.2
tortoise                  3.0.0        ~/Programs/tortoise-fast39/tortoise-tts-fast
tqdm                      4.65.0
traitlets                 5.11.2
trampoline                0.1.2
transformers              4.29.2
triton                    2.0.0
typing_extensions         4.6.3
tzdata                    2023.3
tzlocal                   4.3.1
Unidecode                 1.3.6
urllib3                   1.26.16
validators                0.20.0
voicefixer                0.1.2
wandb                     0.15.5
watchdog                  3.0.0
wcwidth                   0.2.6
webencodings              0.5.1
wheel                     0.38.4
whisper                   1.1.10
xxhash                    2.0.2
yarl                      1.8.1
zipp                      3.15.0
