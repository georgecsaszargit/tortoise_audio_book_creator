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
