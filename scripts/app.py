# AGPL: a notification must be added stating that changes have been made to that file.

import os
from pathlib import Path
from datetime import datetime
import re
import streamlit as st

from tortoise.api import MODELS_DIR
from tortoise.inference import (
    infer_on_texts,
    run_and_save_tts,
    split_and_recombine_text,
)
from tortoise.utils.diffusion import SAMPLERS
from app_utils.filepicker import st_file_selector
from app_utils.conf import TortoiseConfig
from pydub import AudioSegment
from app_utils.funcs import (
    timeit,
    load_model,
    list_voices,
    load_voice_conditionings,
)
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import time
import shutil
import yaml

LATENT_MODES = [
    "Tortoise original (bad)",
    "average per 4.27s (broken on small files)",
    "average per voice file (broken on small files)",
]

voice_count = 1
loaded_settings = {}

# Function to save settings
def save_settings(text, voice, max_self_correcting_rounds, select_ar_checkpoint, split_length,short_break_val,long_break_val,acceptable_diff,acceptable_char_diff,preset,candidates,latent_averaging_mode,sampler,steps,seed,voice_fixer,output_path,length_penalty_val,repetition_penalty_val,top_p_val,cvvp_amount_val,temperature_val,diffusion_temperature_val,low_vram,max_mel_tokens):
    
    if low_vram == True:
        low_vram = False
    else:
        low_vram = True

    settings = {
        "text": text,
        "voice": voice,
        "max_self_correcting_rounds": max_self_correcting_rounds,
        "select_ar_checkpoint": select_ar_checkpoint, 
        "split_length": split_length,
        "short_break_val": short_break_val,
        "long_break_val": long_break_val,
        "acceptable_diff": acceptable_diff,
        "acceptable_char_diff": acceptable_char_diff,
        "preset": preset,
        "candidates": candidates,
        "latent_averaging_mode": latent_averaging_mode,
        "sampler": sampler,
        "steps": steps,
        "seed": seed,
        "voice_fixer": voice_fixer,
        "output_path": output_path,
        "length_penalty": length_penalty_val,
        "repetition_penalty": repetition_penalty_val,
        "top_p": top_p_val,
        "cvvp_amount": cvvp_amount_val,
        "temperature": temperature_val,
        "diffusion_temperature": diffusion_temperature_val,
        "low_vram": low_vram,
        "max_mel_tokens": max_mel_tokens,
    }
    
    with open("settings.yaml", "w") as f:
        yaml.dump(settings, f)
        
    st.write("Settings saved to settings.yaml")
    
# Function to load settings    
def load_settings():
    global loaded_settings

    if not os.path.exists("settings.yaml"):
        with open("settings.yaml", "w") as f:
            f.write("---\n")  # This writes an empty YAML document.

        st.write("No settings file found. An empty one has been created.")
        return  # Exit the function since the file is empty.

    with open("settings.yaml", "r") as f:
        settings = yaml.safe_load(f) or {}  # If the result is None, default to an empty dictionary.

    loaded_settings['text'] = settings.get("text", None)
    loaded_settings['voice'] = settings.get("voice", None)
    loaded_settings['max_self_correcting_rounds'] = settings.get("max_self_correcting_rounds", None)
    loaded_settings['select_ar_checkpoint'] = settings.get("select_ar_checkpoint", None)
    loaded_settings['split_length'] = settings.get("split_length", None)
    loaded_settings['short_break_val'] = settings.get("short_break_val", None)
    loaded_settings['long_break_val'] = settings.get("long_break_val", None)
    loaded_settings['acceptable_diff'] = settings.get("acceptable_diff", None)
    loaded_settings['acceptable_char_diff'] = settings.get("acceptable_char_diff", None)
    loaded_settings['preset'] = settings.get("preset", None)
    loaded_settings['candidates'] = settings.get("candidates", None)
    loaded_settings['latent_averaging_mode'] = settings.get("latent_averaging_mode", None)
    loaded_settings['sampler'] = settings.get("sampler", None)
    loaded_settings['steps'] = settings.get("steps", None)
    loaded_settings['seed'] = settings.get("seed", None)
    loaded_settings['voice_fixer'] = settings.get("voice_fixer", None)
    loaded_settings['output_path'] = settings.get("output_path", None)
    
    loaded_settings['length_penalty'] = settings.get("length_penalty", None)
    loaded_settings['repetition_penalty'] = settings.get("repetition_penalty", None)
    loaded_settings['top_p'] = settings.get("top_p", None)
    loaded_settings['cvvp_amount'] = settings.get("cvvp_amount", None)
    loaded_settings['temperature'] = settings.get("temperature", None)
    loaded_settings['diffusion_temperature'] = settings.get("diffusion_temperature", None)
    loaded_settings['low_vram'] = settings.get("low_vram", None)
    loaded_settings['max_mel_tokens'] = settings.get("max_mel_tokens", None)
    

    st.write("Settings loaded")

def reset_settings():
    """Remove the file if it exists."""
    if os.path.isfile("settings.yaml"):
        os.remove("settings.yaml")
        print(f"settings.yaml has been removed!")
    else:
        print(f"settings.yaml does not exist!")

load_settings()

def main():
    conf = TortoiseConfig()
    
    def clean_text(text_value):
        # Clean up the content using regex
        text_value = re.sub(r'[^\x00-\x7F]+', ' ', text_value)  # Remove non-ASCII characters
        return text_value

    st.markdown("<h2 style='text-align: center; font-size: 40px; font-weight: bold;'>Tortoise Audiobook Creator</h2>", unsafe_allow_html=True)

    file = st.file_uploader("Select File", type=["txt"])

    # Default text for the text area
    text_value = "Insert your text here for your audio book, or use the file selector option above this field. Many thanks to the original creators of Tortoise text-to-speech and the creators of Tortoise fast repository. My lifelong dream has finally come true in this project!"

    # Check if there's a saved setting for the text
    if loaded_settings.get('text') and loaded_settings['text']:
        text_value = loaded_settings['text']

    # Check if a file has been uploaded and use its content, if present
    if file:
        try:
            # Decode with UTF-8
            text_content = file.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                # If UTF-8 fails, decode with ISO-8859-1 (Latin-1) and convert to UTF-8
                file.seek(0)  # Reset file pointer
                text_content = file.read().decode("ISO-8859-1").encode('utf-8').decode('utf-8')
            except UnicodeDecodeError:
                st.error("Unable to decode the uploaded file. Please ensure it's a valid text file.")
                text_content = None

        if text_content:
            text_value = clean_text(text_content)

    # Create the text_area widget with the determined value
    text = st.text_area(
        "Text",
        help="Text to speak.",
        value=text_value,
        height=200
    )

    # Splitting the layout into 2 columns to place max self-correct and voice side by side
    col_voice,col_ar,col_max_self_correct = st.columns([0.3,0.5,0.2])

    if loaded_settings.get('max_self_correcting_rounds') and loaded_settings['max_self_correcting_rounds'] != None:
        max_self_correcting_rounds_val = loaded_settings['max_self_correcting_rounds']
    else:
        max_self_correcting_rounds_val = 3

    with col_max_self_correct:
        max_self_correcting_rounds = st.number_input(
            "Self correct rounds",
            help="How many times we repeat generation if generation was faulty and extra words were added. (0 = no self correction)",
            value=max_self_correcting_rounds_val,
            min_value=0, 
            max_value=100,
        )
    
    voices, extra_voices_ls = list_voices("")
    
    voice_index = 0
    
    if loaded_settings.get('voice') and loaded_settings['voice'] != None:
        for ind, v in enumerate(voices):
            if v == loaded_settings['voice']:
                voice_index = ind
    
    with col_voice:
        voice = st.selectbox(
            "Voice",
            voices,
            help="Selects the voice to use for generation. See options in voices/ directory (and add your own!) "
            "Use the & character to join two voices together. Use a comma to perform inference on multiple voices.",
            index=voice_index
        )
                       
    directory_path_models = "models/finetuned/"
    
    file_list_models = [f for f in os.listdir(directory_path_models) if os.path.isfile(os.path.join(directory_path_models, f))]
    file_list_models = sorted(file_list_models)
    file_list_models.insert(0,"autoregressive.pth")
    
    ar_index = 0
    if loaded_settings.get('select_ar_checkpoint') and loaded_settings['select_ar_checkpoint'] != None:
        
        for ind, v in enumerate(file_list_models):
            if v == loaded_settings['select_ar_checkpoint']:
                ar_index = ind
    
    with col_ar:
        select_ar_checkpoint = st.selectbox(
            "Model",
            file_list_models,
            help="Selects model in Finetuned directory",
            index=ar_index
        )    

    if "autoregressive.pth" in select_ar_checkpoint:
        ar_checkpoint = MODELS_DIR + "/" + select_ar_checkpoint
    else:
        ar_checkpoint = "models/finetuned/" + select_ar_checkpoint

    print("Model selected: " + ar_checkpoint)

    with st.expander("Settings"):
        col1, col2 = st.columns(2)
        with col1:
            """#### Text Splitting"""
        
            split_options = ('long','medium','short')

            if loaded_settings.get('split_length') and loaded_settings['split_length'] != None:
                for ind, v in enumerate(split_options):
                    if v == loaded_settings['split_length']:
                        split_length_ind = ind
            else:
                split_length_ind = 0
        
            split_length = st.selectbox(
                'Select a length',
                split_options,
                help="Determines chunk size",
                index=split_length_ind
            )
            
            if loaded_settings.get('short_break_val') and loaded_settings['short_break_val'] != None:
                val_0 = loaded_settings['short_break_val']
            else:
                val_0 = 500

            """#### Add Pause """
            short_break_val = st.number_input(
                "Short pause (millisec)",
                help="If a line break is detected a pause will be created with this value in millisec",
                value=val_0,
                min_value=0, 
                max_value=3000,
            )

            if loaded_settings.get('long_break_val') and loaded_settings['long_break_val'] != None:
                val_1 = loaded_settings['long_break_val']
            else:
                val_1 = 3000

            long_break_val = st.number_input(
                "Long pause (millisec)",
                help="If 2 or more line breaks are detected a pause will be created with this value in millisec",
                value=val_1,
                min_value=0, 
                max_value=10000,
            )
    
    with col2:
            
            if loaded_settings.get('acceptable_diff') and loaded_settings['acceptable_diff'] != None:
                acceptable_diff_val = loaded_settings['acceptable_diff']
            else:
                acceptable_diff_val = 0

            """#### Self correction settings"""
            acceptable_diff = st.number_input(
                "Acceptable word diff",
                help="Number of words that is still within acceptable level of generation verification. (0 means even 1 word difference causes self correction round)",
                value=acceptable_diff_val,
                min_value=0, 
                max_value=20,
            )

            if loaded_settings.get('acceptable_char_diff') and loaded_settings['acceptable_char_diff'] != None:
                acceptable_char_diff_val = loaded_settings['acceptable_char_diff']
            else:
                acceptable_char_diff_val = 3

            acceptable_char_diff = st.number_input(
                "Acceptable char diff",
                help="If there is a larger than accapted difference in word count between orig. and generated text, then this char count will be checked. If char diff larger than this value, then self correction round will start.",
                value=acceptable_char_diff_val,
                min_value=0, 
                max_value=100,
            )
            

    with st.expander("Advanced Settings"):
        col1, col2 = st.columns(2)
        with col1:
            
            preset_options = (
                "single_sample",
                "ultra_fast",
                "very_fast",
                "ultra_fast_old",
                "fast",
                "standard",
                "high_quality",
            )

            if loaded_settings.get('preset') and loaded_settings['preset'] != None:
                for ind, v in enumerate(preset_options):
                    if v == loaded_settings['preset']:
                        preset_ind = ind
            else:
                preset_ind = 1
            
            preset = st.selectbox(
                "Preset",
                preset_options,
                help="Which voice preset to use.",
                index=preset_ind,
            )

            diff_checkpoint = st_file_selector(
                st,
                path=conf.DIFF_CHECKPOINT,
                label="Select Diffusion Checkpoint",
                key="pth-diff",
            )

            if loaded_settings.get('candidates') and loaded_settings['candidates'] != None:
                candidates_val = loaded_settings['candidates']
            else:
                candidates_val = 1

            """#### Model parameters"""
            candidates = st.number_input(
                "Candidates",
                help="How many output candidates to produce per-voice.",
                value=candidates_val,
            )

            if loaded_settings.get('latent_averaging_mode') and loaded_settings['latent_averaging_mode'] != None:
                for ind, v in enumerate(LATENT_MODES):
                    if v == loaded_settings['latent_averaging_mode']:
                        latent_averaging_mode_ind = ind
            else:
                latent_averaging_mode_ind = 0

            latent_averaging_mode = st.radio(
                "Latent averaging mode",
                LATENT_MODES,
                help="How voice samples should be averaged together.",
                index=latent_averaging_mode_ind,
            )
            
            sampler_ind = 2
            if loaded_settings.get('sampler') and loaded_settings['sampler'] != None:
                for ind, v in enumerate(SAMPLERS):
                    if v == loaded_settings['sampler']:
                        sampler_ind = ind
            
            sampler = st.radio(
                "Sampler",
                SAMPLERS,
                help="Diffusion sampler. Note that dpm++2m is experimental and typically requires more steps.",
                index=sampler_ind,
            )

            if loaded_settings.get('steps') and loaded_settings['steps'] != None:
                steps_val = loaded_settings['steps']
            else:
                steps_val = 30

            steps = st.number_input(
                "Steps",
                help="Override the steps used for diffusion (default depends on preset)",
                value=steps_val,
            )

            if loaded_settings.get('seed') and loaded_settings['seed'] != None:
                seed_val = loaded_settings['seed']
            else:
                seed_val = 0

            seed = st.number_input(
                "Seed",
                help="Random seed which can be used to reproduce results.",
                value=seed_val,
            )
            if seed == -1:
                seed = None

            if loaded_settings.get('voice_fixer') and loaded_settings['voice_fixer'] != None:
                voice_fixer_val = loaded_settings['voice_fixer']
            else:
                voice_fixer_val = False

            voice_fixer = st.checkbox(
                "Voice fixer",
                help="Use `voicefixer` to improve audio quality. This is a post-processing step which can be applied to any output.",
                value=voice_fixer_val,
            )

            if loaded_settings.get('output_path') and loaded_settings['output_path'] != None:
                output_path_val = loaded_settings['output_path']
            else:
                output_path_val = "results/"

            """#### Directories"""
            output_path = st.text_input(
                "Output Path", 
                help="Where to store outputs.", 
                value=output_path_val
            )

            model_dir = st.text_input(
                "Model Directory",
                help="Where to find pretrained model checkpoints. Tortoise automatically downloads these to .models, so this"
                "should only be specified if you have custom checkpoints.",
                value=MODELS_DIR,
            )

        with col2:

            if loaded_settings.get('low_vram') and loaded_settings['low_vram'] != None:
                low_vram_val = loaded_settings['low_vram']
            else:
                low_vram_val = False

            """#### Optimizations"""
            high_vram = not st.checkbox(
                "Low VRAM",
                help="Re-enable default offloading behaviour of tortoise",
                value=low_vram_val,
            )
            
            if loaded_settings.get('length_penalty') is None:
                loaded_settings['length_penalty'] = 6.0

            if loaded_settings.get('repetition_penalty') is None:
                loaded_settings['repetition_penalty'] = 8.0

            if loaded_settings.get('top_p') is None:
                loaded_settings['top_p'] = 0.8

            if loaded_settings.get('cvvp_amount') is None:
                loaded_settings['cvvp_amount'] = 0.0

            if loaded_settings.get('temperature') is None:
                loaded_settings['temperature'] = 1.0
            
            if loaded_settings.get('diffusion_temperature') is None:
                loaded_settings['diffusion_temperature'] = 1.0

            if loaded_settings.get('max_mel_tokens') is None:
                loaded_settings['max_mel_tokens'] = 500
                        

            """#### Extra Options"""
            length_penalty = st.slider("Length Penalty", 0.1, 8.0, loaded_settings['length_penalty'])
            repetition_penalty = st.slider("Repetition Penalty", 0.1, 8.0, loaded_settings['repetition_penalty'])
            top_p = st.slider("Top p", 0.1, 1.0, loaded_settings['top_p'])
            max_mel_tokens = st.number_input("Max mel tokens", help="Values are valid between 1 to 1000", value=loaded_settings['max_mel_tokens'])
            cvvp_amount = st.slider("CVPP Amount", 0.0, 1.0, loaded_settings['cvvp_amount'])
            temperature = st.slider("Temperature", 0.1, 2.0, loaded_settings['temperature'])
            diffusion_temperature = st.slider("Diffusion Temperature", 0.1, 1.0, loaded_settings['diffusion_temperature'])

            
                
            # Create buttons 
            if st.button("Save Settings"):
                save_settings(text, voice, max_self_correcting_rounds, select_ar_checkpoint, split_length,short_break_val,long_break_val,acceptable_diff,acceptable_char_diff,preset,candidates,latent_averaging_mode,sampler,steps,seed,voice_fixer,output_path,length_penalty,repetition_penalty,top_p,cvvp_amount,temperature,diffusion_temperature,high_vram,max_mel_tokens)

            if st.button("Reset Settings"):
                reset_settings()
                st.warning("You must restart the app to take effect")


    half = False
    kv_cache = True
    cond_free = True
    no_cond_free = False
    whisp_model = "base"
    produce_debug_state = False

    diff_checkpoint = None if diff_checkpoint[-4:] != ".pth" else diff_checkpoint
    tts = load_model(model_dir, high_vram, kv_cache, ar_checkpoint, diff_checkpoint)
    start_time = None
    
    def start_process():

        def show_generation(fp, filename: str):
            """
            audio_buffer = BytesIO()
            save_gen_with_voicefix(g, audio_buffer, squeeze=False)
            torchaudio.save(audio_buffer, g, 24000, format='wav')
            """
            
            end_time = time.time()
            elapsed = end_time - start_time
            elapsed = format_time(elapsed)

            st.write(f"Elapsed: {elapsed} seconds")
            
            # To hold all audio segments and paths of created mp3 files
            all_audio = []
            mp3_files = []

            selected_voices = voice.split(",")
            for k, selected_voice in enumerate(selected_voices):
                if "&" in selected_voice:
                    voice_sel = selected_voice.split("&")
                else:
                    voice_sel = [selected_voice]
                voice_samples, conditioning_latents = load_voice_conditionings(
                    voice_sel, extra_voices_ls
                )

                dir_path_1 = Path(os.path.join(output_path, selected_voice))

            # Iterate over the directories
            i = 0
            while True:
                dir_path = f'{dir_path_1}/{i}/'
                            
                wav_file_path = os.path.join(dir_path, '0.wav')

                # The mp3 files will be named after their parent folder and stored in the script's directory
                mp3_file_path = f'{dir_path}/{i}.mp3'

                if os.path.isfile(wav_file_path):  # Only attempt conversion if the wav file exists
                    convert_wav_to_mp3(wav_file_path, mp3_file_path)
                    all_audio.append(AudioSegment.from_mp3(mp3_file_path))
                    mp3_files.append(mp3_file_path)
                else:
                    break
                i = i + 1
            

            # Combine all audio files
            combined_audio = sum(all_audio)
            current_time = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
            normalized_audio = normalize_volume(combined_audio)
            # Export as mp3
            normalized_audio.export(f"{dir_path_1}/combined_{current_time}.mp3", format="mp3")
            st.audio(f"{dir_path_1}/combined_{current_time}.mp3", format="audio/mp3")
            remove_except_combined_mp3(dir_path_1)
    
        def emptydir(dir_path):
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    print(f'Cleared all error log files.')
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        
        def clear_unfinished_generation(target_dir):
            if not os.path.exists(target_dir):
                print(f"'{target_dir}' does not exist!")
                return
            
            # List all the items in the given directory
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)

                # If it's a directory, remove it
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)

                # If it's a file and doesn't match the required pattern, remove it
                elif not item.startswith("combined") or not item.endswith(".mp3"):
                    os.remove(item_path)          

        # delete all files in temp dir
        emptydir('temp')
        
        with st.spinner(
            f"Generating with voice {voice}. You can see progress in the terminal"
        ):
            os.makedirs(output_path, exist_ok=True)

            selected_voices = voice.split(",")
            for k, selected_voice in enumerate(selected_voices):
                if "&" in selected_voice:
                    voice_sel = selected_voice.split("&")
                else:
                    voice_sel = [selected_voice]
                voice_samples, conditioning_latents = load_voice_conditionings(
                    voice_sel, extra_voices_ls
                )

                voice_path = Path(os.path.join(output_path, selected_voice))
                clear_unfinished_generation(voice_path)

                with timeit(
                    f"Generating {candidates} candidates for voice {selected_voice} (seed={seed})"
                ):
                    nullable_kwargs = {
                        k: v
                        for k, v in zip(
                            ["sampler", "diffusion_iterations", "cond_free"],
                            [sampler, steps, cond_free],
                        )
                        if v is not None
                    }

                    def call_tts(text: str, newseed: int):
                        return tts.tts_with_preset(
                            text,
                            k=candidates,
                            voice_samples=voice_samples,
                            conditioning_latents=conditioning_latents,
                            preset=preset,
                            length_penalty=length_penalty,
                            repetition_penalty=repetition_penalty,
                            top_p=top_p,
                            max_mel_tokens=max_mel_tokens,
                            cvvp_amount=cvvp_amount,
                            temperature=temperature,
                            diffusion_temperature=diffusion_temperature,
                            use_deterministic_seed=newseed,
                            return_deterministic_state=True,
                            half=half,
                            latent_averaging_mode=LATENT_MODES.index(
                                latent_averaging_mode
                            ),
                            **nullable_kwargs,
                        )

                    
                    texts = split_and_recombine_text(
                        text, split_length
                    )

                    progress_bar_max = len(texts)
                    
                    #print("Total audio chunks created: ")
                    #print(len(texts))

                    def remove_multiple_pause_marks(mylist):
                        mynewlist = []
                        chars = ['~','|']

                        for ind in range(0,len(mylist)):
                            if mylist[ind] in chars:
                                if ind + 1 < len(mylist):
                                    if mylist[ind + 1] in chars:
                                        print("Skip this character")
                                        continue
                                    else:
                                        mynewlist.append(mylist[ind])

                                else:
                                    mynewlist.append(mylist[ind])
                            else:
                                mynewlist.append(mylist[ind])
                        return mynewlist

                    def process_array(arr, mark):
                        #print("\n--- Mark: " + mark)
                        arr2 = []
                        
                        for elem in arr:
                            #print("--- Element: " + elem)
                            if mark in elem:
                                parts = elem.split(mark)
                                
                                for i, val in enumerate(parts):
                                    if(val.strip() != ""):
                                        arr2.append(val.strip())
                                        if i+1<len(parts):
                                            arr2.append(mark)
                                    elif(len(parts)>1):
                                        arr2.append(mark)

                            else:
                                arr2.append(elem)

                        return arr2

                    def process_array2(arr):
                        processed = []
                        skip_next = False  # Flag to skip next iteration if we've combined elements

                        marks = ['|', '~']

                        for i, elem in enumerate(arr):
                            if skip_next:
                                skip_next = False
                                continue

                            # Condition to append to the previous chunk
                            if i > 0 and (elem.startswith(',') or elem.endswith(',')) and len(elem) < 10 and all(mark not in arr[i-1] for mark in marks):
                                processed[-1] += " " + elem

                            # Condition to combine with the next chunk
                            elif (i < len(arr) - 1 and 
                                (elem.startswith(',') or elem.endswith(',')) and 
                                len(elem) < 10 and 
                                all(mark not in arr[i+1] for mark in marks)):
                                processed.append(elem + " " + arr[i+1])
                                skip_next = True

                            else:
                                processed.append(elem)

                        return processed

                    texts2 = process_array(texts, '~')
                    texts3 = process_array(texts2, '|')
                    texts3 = process_array2(texts3)
                    texts4 = [item for item in texts3 if item != ""]
                    texts5 = remove_multiple_pause_marks(texts4)

                    texts5_str = ""
                    for t in range(0,len(texts5)):
                            texts5_str = texts5_str + texts5[t] + '\n'
                    with open('errors/chunks.txt', 'a') as file:
                        file.write(texts5_str)
                    #print("\n---- After processing: (| = middle sized pause, ~ = long pause)")
                    #print(texts5)

                    filepaths = infer_on_texts(
                        call_tts,
                        texts5,
                        voice_path,
                        short_break_val,
                        long_break_val,
                        acceptable_diff,
                        acceptable_char_diff,
                        whisp_model,
                        return_deterministic_state=True,
                        return_filepaths=True,
                        lines_to_regen=set(range(len(texts5))),
                        voicefixer=voice_fixer,
                        max_self_correcting_rounds=max_self_correcting_rounds,
                    )
                    for i, fp in enumerate(filepaths):
                        show_generation(fp, f"{selected_voice}-text-{i}.wav")
        if produce_debug_state:
            """Debug states can be found in the output directory"""


    if st.button("Start"):
        assert latent_averaging_mode
        assert preset
        assert voice
        
        sentences = sent_tokenize(text)
        words = word_tokenize(text)

        sentence_count = len(sentences)
        word_count = len(words)
        
        
        
        print(f"Sentence count: {sentence_count}")
        print(f"Word count: {word_count}")

        now = datetime.now()
        time_string = now.strftime("%I:%M %p")
        st.write(f"""
        Sentence count: {sentence_count}  
        Word count: {word_count}  
        Start time: {time_string}  
        """)
        start_time = time.time()

        def normalize_volume(audio_segment, target_dBFS=-20.0):
            difference = target_dBFS - audio_segment.dBFS
            return audio_segment.apply_gain(difference)

        def remove_except_combined_mp3(directory):
            for root_dir, dirs, files in os.walk(directory, topdown=False):  # Start from innermost directories
                # Remove files which are not mp3 or don't start with "combined"
                for name in files:
                    if not (name.endswith('.mp3') and name.startswith('combined')):
                        os.remove(os.path.join(root_dir, name))
                        
                # Remove empty directories
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root_dir, name))  # This will only remove empty directories
                    except OSError as e:
                        # Directory not empty, continue
                        pass

        def convert_wav_to_mp3(wav_file, mp3_file):
            audio = AudioSegment.from_wav(wav_file)
            audio.export(mp3_file, format="mp3", bitrate="192k")     

        def format_time(seconds):
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds %= 60

            if hours:
                return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            elif minutes:
                return f"{int(minutes)}m {int(seconds)}s"
            else:
                return f"{seconds:.2f}s"               

        start_process()
        
        

if __name__ == "__main__":
    main()
