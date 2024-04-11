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
- Added self correction feature that tries to fix issues with generation automatically (word, char differences, and pitch control)
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
I only tested it on Ubuntu 22.04 Linux.

<h2>Here are the steps:</h2>
Install latest proprietary nvidia driver<br>
sudo apt install git git-lfs perl make ffmpeg nvidia-cuda-toolkit nvidia-cudnn libportaudio2<br>
Download Miniconda from: https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html<br>
Install it without sudo rights for current user<br>
Restart computer<br>
Create conda env: conda env create -f environment-new.yml<br>
Activate conda: conda activate tortoiseaudiobook<br>
python -m pip install -r requirements-new.txt<br>
Download finetuned models and place them to ~/.cache/tortoise/models/ folder from:<br>
https://huggingface.co/jbetker/tortoise-tts-finetuned-lj<br>
(These models are better than the original tortoise models)<br>
git clone https://huggingface.co/jbetker/tortoise-tts-finetuned-lj<br>
cd tortoise-tts-finetuned-lj<br>
git lfs fetch --all<br>
git lfs checkout<br>
mkdir -p tortoise/models<br>
cp * ~/.cache/tortoise/models<br>
<br>
Instructional video: coming soon...<br>
<br><br>
These are the versions of my python modules for reference:<br>
Package                   Version      Editable project location<br>
------------------------- ------------ -------------------------------------------------------<br>
accelerate                0.20.3<br>
aiohttp                   3.8.3<br>
aiosignal                 1.2.0<br>
altair                    5.0.1<br>
annotated-types           0.5.0<br>
appdirs                   1.4.4<br>
art                       6.1<br>
async-timeout             4.0.2<br>
attrs                     23.1.0<br>
audioread                 3.0.0<br>
auraloss                  0.4.0<br>
beautifulsoup4            4.12.2<br>
BigVGAN                   0.0.1<br>
bleach                    6.1.0<br>
blinker                   1.6.2<br>
boltons                   23.0.0<br>
Bottleneck                1.3.5<br>
brotlipy                  0.7.0<br>
cachetools                5.3.1<br>
certifi                   2023.7.22<br>
cffi                      1.15.1<br>
charset-normalizer        2.0.4<br>
clean-fid                 0.1.35<br>
click                     8.0.4<br>
clip-anytorch             2.5.2<br>
cmake                     3.27.5<br>
contourpy                 1.1.0<br>
cryptography              39.0.1<br>
cycler                    0.11.0<br>
datasets                  2.12.0<br>
decorator                 5.1.1<br>
deepspeed                 0.10.2<br>
dill                      0.3.6<br>
docker-pycreds            0.4.0<br>
docstring-parser          0.15<br>
drawille                  0.1.0<br>
einops                    0.6.1<br>
entrypoints               0.4<br>
fastjsonschema            2.18.1<br>
filelock                  3.9.0<br>
fonttools                 4.40.0<br>
frozenlist                1.3.3<br>
fsspec                    2023.4.0<br>
ftfy                      6.1.1<br>
fuzzywuzzy                0.18.0<br>
gdown                     4.7.1<br>
gitdb                     4.0.10<br>
GitPython                 3.1.31<br>
gmpy2                     2.1.2<br>
hjson                     3.1.0<br>
huggingface-hub           0.15.1<br>
idna                      3.4<br>
imageio                   2.31.1<br>
importlib-metadata        6.8.0<br>
importlib-resources       6.0.0<br>
inflect                   6.2.0<br>
Jinja2                    3.1.2<br>
joblib                    1.2.0<br>
jsonmerge                 1.9.0<br>
jsonschema                4.18.0<br>
jsonschema-specifications 2023.6.1<br>
jupyter_core              5.4.0<br>
k-diffusion               0.0.14<br>
kiwisolver                1.4.4<br>
kornia                    0.6.12<br>
lazy_loader               0.3<br>
Levenshtein               0.22.0<br>
librosa                   0.8.1<br>
lit                       17.0.1<br>
llvmlite                  0.39.1<br>
markdown-it-py            3.0.0<br>
MarkupSafe                2.1.1<br>
matplotlib                3.7.2<br>
mdurl                     0.1.2<br>
mistune                   3.0.2<br>
mkl-fft                   1.3.6<br>
mkl-random                1.2.2<br>
mkl-service               2.4.0<br>
more-itertools            10.1.0<br>
mpmath                    1.2.1<br>
msgpack                   1.0.5<br>
multidict                 6.0.2<br>
multiprocess              0.70.14<br>
nbconvert                 5.3.1<br>
nbformat                  5.9.2<br>
networkx                  2.8.4<br>
ninja                     1.11.1.1<br>
nltk                      3.8.1<br>
numba                     0.56.4<br>
numexpr                   2.8.4<br>
numpy                     1.23.5<br>
nvidia-cublas-cu11        11.10.3.66<br>
nvidia-cuda-nvrtc-cu11    11.7.99<br>
nvidia-cuda-runtime-cu11  11.7.99<br>
nvidia-cudnn-cu11         8.5.0.96<br>
openai-whisper            20230918<br>
packaging                 23.0<br>
pandas                    1.5.3<br>
pandocfilters             1.5.0<br>
pathtools                 0.1.2<br>
pesq                      0.0.4<br>
Pillow                    9.4.0<br>
pip                       23.1.2<br>
platformdirs              3.11.0<br>
pooch                     1.6.0<br>
progressbar               2.5<br>
protobuf                  4.23.4<br>
psutil                    5.9.5<br>
py-cpuinfo                9.0.0<br>
pyarrow                   11.0.0<br>
pycparser                 2.21<br>
pydantic                  1.10.13<br>
pydantic_core             2.1.2<br>
pydeck                    0.8.1b0<br>
pydub                     0.25.1<br>
Pygments                  2.15.1<br>
Pympler                   1.0.1<br>
pyOpenSSL                 23.0.0<br>
pyparsing                 3.0.9<br>
PySocks                   1.7.1<br>
python-dateutil           2.8.2<br>
python-Levenshtein        0.22.0<br>
pytz                      2022.7<br>
pytz-deprecation-shim     0.1.0.post0<br>
PyWavelets                1.4.1<br>
PyYAML                    6.0<br>
rapidfuzz                 3.3.1<br>
referencing               0.29.1<br>
regex                     2022.7.9<br>
requests                  2.29.0<br>
resampy                   0.4.2<br>
resize-right              0.0.2<br>
responses                 0.13.3<br>
rich                      13.4.2<br>
rotary-embedding-torch    0.2.5<br>
rpds-py                   0.8.10<br>
sacremoses                0.0.43<br>
scikit-image              0.21.0<br>
scikit-learn              1.3.0<br>
scipy                     1.11.1<br>
sentry-sdk                1.27.1<br>
setproctitle              1.3.2<br>
setuptools                67.8.0<br>
simple-parsing            0.0.21.post1<br>
six                       1.16.0<br>
smmap                     5.0.0<br>
sounddevice               0.4.6<br>
soundfile                 0.12.1<br>
soupsieve                 2.4.1<br>
soxr                      0.3.5<br>
spicy                     0.16.0<br>
streamlit                 1.24.1<br>
sympy                     1.11.1<br>
tenacity                  8.2.2<br>
testpath                  0.6.0<br>
threadpoolctl             3.1.0<br>
tifffile                  2023.7.4<br>
tiktoken                  0.3.3<br>
tokenizers                0.13.2<br>
toml                      0.10.2<br>
toolz                     0.12.0<br>
torch                     1.13.1<br>
torchaudio                0.13.1<br>
torchdiffeq               0.2.3<br>
torchlibrosa              0.0.7<br>
torchsde                  0.2.5<br>
torchvision               0.15.2<br>
tornado                   6.3.2<br>
tortoise                  3.0.0        ~/Programs/tortoise-fast39/tortoise-tts-fast<br>
tqdm                      4.65.0<br>
traitlets                 5.11.2<br>
trampoline                0.1.2<br>
transformers              4.29.2<br>
triton                    2.0.0<br>
typing_extensions         4.6.3<br>
tzdata                    2023.3<br>
tzlocal                   4.3.1<br>
Unidecode                 1.3.6<br>
urllib3                   1.26.16<br>
validators                0.20.0<br>
voicefixer                0.1.2<br>
wandb                     0.15.5<br>
watchdog                  3.0.0<br>
wcwidth                   0.2.6<br>
webencodings              0.5.1<br>
wheel                     0.38.4<br>
whisper                   1.1.10<br>
xxhash                    2.0.2<br>
yarl                      1.8.1<br>
zipp                      3.15.0<br>
