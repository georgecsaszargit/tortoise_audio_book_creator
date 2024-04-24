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
<p>I only tested it on Ubuntu 22.04 Linux.</p>
<p>Here are the steps:</p>
<ol>
    <li>Install latest proprietary nvidia driver</li>
    <li>Install Ubuntu packages<br>sudo apt install git git-lfs perl make ffmpeg nvidia-cuda-toolkit nvidia-cudnn libportaudio2</li>
    <li>Download Miniconda from: <a target="_blank" rel="noopener noreferrer" href="https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html">https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html</a></li>
    <li>Install it without sudo rights for current user</li>
    <li>Restart computer</li>
    <li>Clone this repo<br>git clone <a target="_blank" rel="noopener noreferrer" href="https://github.com/georgecsaszargit/tortoise_audio_book_creator.git">https://github.com/georgecsaszargit/tortoise_audio_book_creator.git</a></li>
    <li>CD into the repo folder where you can see the requirements-new.txt</li>
    <li>Create conda env:<br>conda env create -f environment-new.yml</li>
    <li>Activate conda:&nbsp;<br>conda activate tortoiseaudiobook</li>
    <li>Install python packages using pip:<br>python -m pip install -r requirements-rtx3090.txt</li>
    <li>Install tortoise module:<br>python -m pip install -e .</li>
    <li>ONLY ON RTX4090 do this 1 following line:
    <br>pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118</li>
    <li>Download finetuned models and place them to ~/.cache/tortoise/models/ folder from: <a target="_blank" rel="noopener noreferrer" href="https://huggingface.co/csdzs/tortoise-audio-book-creator">https://huggingface.co/csdzs/tortoise-audiobook-creator-finetuned-models</a>(These models are better than the original tortoise models)<br>git clone <a target="_blank" rel="noopener noreferrer" href="https://huggingface.co/csdzs/tortoise-audio-book-creator">https://huggingface.co/csdzs/tortoise-audiobook-creator-finetuned-models</a><br>cd tortoise-audiobook-creator-finetuned-models<br>git lfs fetch --all<br>git lfs checkout<br>mkdir -p ~/.cache/tortoise/models<br>cp * ~/.cache/tortoise/models</li>
    <li>cd 1 level up and run tortoise:<br>cd ..<br>streamlit run scripts/app.py</li>
</ol>
<p>Instructional video: https://youtu.be/BCCMB0p4fC8?si=5pHqHb8nZCSa_ExO</p>
