<h2>This is an audiobook creator using Tortoise TTS</h2>
<h6>With this repo you will be able to generate super high quality audio books using ai models locally on your computer. (No internet connection is needed)</h6>

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

Instructions are coming soon on how to install it and what to pay attention to

Instructional video:
