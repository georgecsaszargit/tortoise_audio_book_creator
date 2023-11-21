import os
import sys
import shutil
from random import randint
from typing import List, Optional, Set, Union
from pathlib import Path
from typing import Any, Callable
import librosa
import sounddevice as sd
import nltk
from nltk.tokenize import word_tokenize
import torch
import torchaudio
import whisper
from fuzzywuzzy import fuzz
import re
from tortoise.utils.audio import get_voices, load_audio, load_voices
from tortoise.utils.text import split_and_recombine_text
from drawille import Canvas
from PIL import Image, ImageDraw, ImageFont


# Ensure you've downloaded the necessary NLTK data
nltk.download('punkt')

round_before_self_correcting = True
rounds = 0
last_difference_in_words = 0
current_chunk = None
error_score1 = 0 #Total number of self correcting rounds
error_score2 = 0 #Sum word diff value for all self correcting rounds
error_score3 = 0 #Total number of failed self correcting rounds

def draw_text_to_canvas(text, font_spacing):
    # Create a PIL image to draw the text with ample space, assuming maximum width for now.
    image = Image.new('L', (len(text) * font_spacing * 2, font_spacing * 5), 255)  # Adjust the canvas size based on font size
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Calculate starting position for the first character
    x_pos = font_spacing  # Starting a bit into the canvas based on font size
    for char in text:
        # Draw the character
        draw.text((x_pos, font_spacing / 2), char, font=font, fill=0)
        # Using getbbox to get the width of the character
        char_width = font.getbbox(char)[2] - font.getbbox(char)[0]
        # Move the x_pos by the width of the character and add a space based on font size
        x_pos += char_width + (font_spacing // 10)

    # Convert the PIL image to a drawille canvas
    canvas = Canvas()
    for x in range(image.width):
        for y in range(image.height):
            if image.getpixel((x, y)) < 128:  # if pixel is "dark"
                canvas.set(x, y)
    
    return canvas

def printx(text, font_spacing=15):
    canvas = draw_text_to_canvas(text, font_spacing)
    print(canvas.frame())


def get_all_voices(extra_voice_dirs_str: str = ""):
    extra_voice_dirs = extra_voice_dirs_str.split(",") if extra_voice_dirs_str else []
    return sorted(get_voices(extra_voice_dirs)), extra_voice_dirs


def parse_voice_str(voice_str: str, all_voices: List[str]):
    selected_voices = all_voices if voice_str == "all" else voice_str.split(",")
    selected_voices = [v.split("&") if "&" in v else [v] for v in selected_voices]
    for voices in selected_voices:
        for v in voices:
            if v != "random" and v not in all_voices:
                raise ValueError(
                    f"voice {v} not available, use --list-voices to see available voices."
                )

    return selected_voices


def voice_loader(selected_voices: list, extra_voice_dirs: List[str]):
    for voices in selected_voices:
        yield voices, *load_voices(voices, extra_voice_dirs)


def parse_multiarg_text(text: List[str]):
    return (" ".join(text) if text else "".join(line for line in sys.stdin)).strip()


def split_text(text: str, text_split: str):
    if text_split:
        desired_length, max_length = map(int, text_split.split(","))
        if desired_length > max_length:
            raise ValueError(
                f"--text-split: desired_length ({desired_length}) must be <= max_length ({max_length})"
            )
        texts = split_and_recombine_text(text, desired_length, max_length)
    else:
        texts = split_and_recombine_text(text)
    #
    if not texts:
        raise ValueError("no text provided")
    return texts


def validate_output_dir(output_dir: str, selected_voices: list, candidates: int):
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        if len(selected_voices) > 1:
            raise ValueError('cannot have multiple voices without --output-dir"')
        if candidates > 1:
            raise ValueError('cannot have multiple candidates without --output-dir"')
    return output_dir


def check_pydub(play: bool):
    if play:
        try:
            import pydub
            import pydub.playback

            return pydub
        except ImportError:
            raise RuntimeError(
                '--play requires pydub to be installed, which can be done with "pip install pydub"'
            )


def get_seed(seed: Optional[int]):
    return randint(0, 2**32 - 1) if seed is None else seed

def get_seed_cust():
    return randint(0, 2**32 - 1)

def run_and_save_tts(
    call_tts,
    text,
    newseed: int,
    output_dir: Path,
    return_deterministic_state,
    voicefixer=bool,
    return_filepaths=False,
):
    output_dir.mkdir(exist_ok=True)
    if return_deterministic_state:
        gen, dbg = call_tts(text,newseed)
        torch.save(dbg, output_dir / "dbg.pt")
    else:
        gen = call_tts(text,newseed)
    #
    if not isinstance(gen, list):
        gen = [gen]
    gen = [g.squeeze(0).cpu() for g in gen]
    fps = []
    for i, g in enumerate(gen):
        fps.append(output_dir / f"{i}.wav")
        save_gen_with_voicefix(g, fps[-1], squeeze=False, voicefixer=voicefixer)
        # torchaudio.save(output_dir/f'{i}.wav', g, 24000)
    #return fps if return_filepaths else gen
    return fps,gen

def create_empty_wav(file_path: str, duration_ms: int, sample_rate=24000):
    """
    Create an empty WAV file. The duration is given in milliseconds.
    """
    # Convert duration from milliseconds to seconds
    duration_s = duration_ms / 1000.0
    
    # Calculate the total number of samples for the given duration
    num_samples = int(sample_rate * duration_s)
    
    # Create an empty tensor filled with zeros
    empty_tensor = torch.zeros(1, num_samples)
    
    # Save the tensor as a WAV file
    torchaudio.save(file_path, empty_tensor, sample_rate)

def count_words(text):
    # Remove all special characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Combine multiple spaces into just one space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # Count the words
    return len(cleaned_text.split())

def count_chars(text):
    # Remove all special characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Combine multiple spaces into just one space
    cleaned_text = re.sub(r'\s+', '', cleaned_text).strip()
    
    # Count the words
    return len(cleaned_text)

def compare_before_after_generation(before, after, acceptable_diff, acceptable_char_diff):
    compare_pass = True
    
    # Check how similar the sentences are
    # Word count comparison
    #print("Word length for original text: " + str(count_words(before)))
    #print("Word length for generated text: " + str(count_words(after)))
    difference_in_words = abs(count_words(after) - count_words(before))
    if difference_in_words > acceptable_diff:
        # Now do char number diff
        difference_in_chars = abs(count_chars(after) - count_chars(before))
        print("Char difference: " + str(difference_in_chars))
        if difference_in_chars > acceptable_char_diff:
            compare_pass = False
            print("Verification failed. Word difference: " + str(difference_in_words) + " Char difference: " + str(difference_in_chars))

    return {"compare_pass": compare_pass, "difference_in_words": difference_in_words}

def infer_on_texts(
    call_tts: Callable[[str], Any],
    texts: List[str],
    output_dir: Union[str, Path],
    short_break_val: int,
    long_break_val: int,
    acceptable_diff: 0,
    acceptable_char_diff: 0,
    whisp_model: str,
    return_deterministic_state: bool,
    lines_to_regen: Set[int],
    logger=print,
    return_filepaths=False,
    voicefixer=bool,
    max_self_correcting_rounds=3,
):
    # Global declaration
    global round_before_self_correcting
    global rounds
    global last_difference_in_words
    global current_chunk
    global error_score1
    global error_score2
    global error_score3
    # Reset vars   
    round_before_self_correcting = True 
    rounds = 0
    last_difference_in_words = 0
    current_chunk = None
    error_score1 = 0
    error_score2 = 0
    error_score3 = 0
    #---------
    
    audio_chunks = []
    base_p = Path(output_dir)
    base_p.mkdir(exist_ok=True)
    
    for text_idx, text in enumerate(texts):

        line_p = base_p / f"{text_idx}"
        line_p.mkdir(exist_ok=True)

        #
        if text_idx not in lines_to_regen:
            files = list(line_p.glob("*.wav"))
            if files:
                logger(f"loading existing audio fragments for [{text_idx}]")
                
                print("\n")
                printx(str(text_idx+1) + " of " + str(len(texts)) + "----------", 20)
                print("\n")
                
                audio_chunks.append([load_audio(str(f), 24000) for f in files])
                continue
            else:
                logger(f"no existing audio fragment for [{text_idx}]")
                
                print("\n")
                printx(str(text_idx+1) + " of " + str(len(texts)) + "----------", 20)
                print("\n")
                
        else:
            
            #whisper_model = "large-v2"
            whisper_model = whisp_model
            model = whisper.load_model(whisper_model,'cuda')
            #print("Breaks")
            #print(short_break_val)
            #print(long_break_val)
            if '~' in text:
                #logger(f"skipping TTS for text with ~ character {text_idx}: {text}")
                empty_file_path = line_p / f"0.wav"
                create_empty_wav(empty_file_path, long_break_val)
                # Here you might want to append something to audio_chunks for the empty audio
                audio_chunks.append([torch.empty(1, 0)])  # Add an empty tensor for this text
                print("\n")
                printx("CHUNK " + str(text_idx+1) + "/" + str(len(texts)), 10)
                printx("ADDED LONG PAUSE", 10)
                print("\n")
            elif '|' in text:
                #logger(f"skipping TTS for text with | character {text_idx}: {text}")
                empty_file_path = line_p / f"0.wav"
                create_empty_wav(empty_file_path, short_break_val)
                # Here you might want to append something to audio_chunks for the empty audio
                audio_chunks.append([torch.empty(1, 0)])  # Add an empty tensor for this text
                print("\n")
                printx("CHUNK " + str(text_idx+1) + "/" + str(len(texts)),10)
                printx("ADDED SHORT PAUSE", 10)
                print("\n")
            else:

                def custom_generate(
                    call_tts: Callable[[str], Any],
                    text: str,
                    newseed: int,
                    line_p,
                    return_deterministic_state: bool,
                    voicefixer: bool,
                ):
                    current_chunk = run_and_save_tts(
                        call_tts,
                        text,
                        newseed,
                        line_p,
                        return_deterministic_state,
                        voicefixer,
                        return_filepaths=True
                    )

                    return current_chunk

                print("\n")
                printx("CHUNK " + str(text_idx+1) + "/" + str(len(texts)), 10)
                print("\n")
                
                #logger(f"generating audio for text {text_idx}: {text}")
                
                def cust_generate2(text, max_self_correcting_rounds):
                    global rounds
                    global last_difference_in_words
                    global current_chunk
                    global round_before_self_correcting
                    global error_score1
                    global error_score2
                    global error_score3
                                        
                    if round_before_self_correcting != True:
                        rounds += 1
                    round_before_self_correcting = False
                    
                    if rounds <= max_self_correcting_rounds:
                        # Use the current time as the seed for random number generation
                        my_seed = get_seed_cust()
                        
                        # Generate
                        current_chunk = custom_generate(call_tts,text,my_seed,line_p,return_deterministic_state,voicefixer)
                        
                        # Verifying
                        print("\norig - " + text)
                        result = model.transcribe(str(current_chunk[0][0]))
                        print('new  - ' + result['text'].lstrip())
                        
                        # Compare
                        compare_passed = compare_before_after_generation(text.lower(), result['text'].lower(), acceptable_diff, acceptable_char_diff)
                        
                        # If generation failed
                        if not compare_passed['compare_pass']:
                            error_score1 += 1
                            error_score2 += compare_passed['difference_in_words']

                            if rounds == 0:
                                # First generation
                                # Save last generated file in temp
                                last_difference_in_words = compare_passed['difference_in_words']
                                source_file_path = str(current_chunk[0][0])
                                destination_file_path = "temp/last_generated.wav"
                                shutil.copyfile(source_file_path, destination_file_path)
                                #printx("Backed up wav to temp",10)

                            elif compare_passed['difference_in_words']>last_difference_in_words:
                                # if previous round was better than the currently generated, then restore
                                source_file_path = "temp/last_generated.wav"
                                destination_file_path = str(current_chunk[0][0])
                                shutil.copyfile(source_file_path, destination_file_path)
                                #printx("Restored wav from temp",10)

                            else:
                                # if previous round was worse or the same than the currently generated
                                last_difference_in_words = compare_passed['difference_in_words']
                                source_file_path = str(current_chunk[0][0])
                                destination_file_path = "temp/last_generated.wav"
                                shutil.copyfile(source_file_path, destination_file_path)
                                #printx("Backed up wav to temp",10)
                            
                            if rounds != max_self_correcting_rounds:
                                print("\n")                                                              
                                printx("DIFF:" + str(compare_passed['difference_in_words']), 10)
                                printx("SELF CORRECT " + str(rounds + 1) + "/" + str(max_self_correcting_rounds), 10)
                                print("\n")
                                
                                cust_generate2(text, max_self_correcting_rounds)
                            else:
                                print("\n")                                                              
                                printx("DIFF:" + str(compare_passed['difference_in_words']), 10)
                                print("\n")
                                printx("STOP", 10)
                                print("\n")

                                rounds = 0
                                round_before_self_correcting = True
                                error_score3 += 1

                        else:
                            print("\n")
                            printx("VERIFY PASS",20)
                            print("\n")
                            rounds = 0
                            round_before_self_correcting = True

                    else:
                        
                        print("\n")
                        printx("ERROR", 20)
                        print("Generated audio never passed verification.")
                        print("\n")
                        
                        rounds = 0
                        round_before_self_correcting = True
                        error_score3 += 1
                
                cust_generate2(text, max_self_correcting_rounds)
                audio_chunks.append(current_chunk[1])

    print("\n")
    printx("FINISHED",20)
    print("\n")
    printx("ERROR REPORT")
    print("\n")
    print("Failed self correcting rounds: " + str(error_score3))
    print("Total self correcting rounds: " + str(error_score1))
    print("Sum word diff for all self correcting rounds: " + str(error_score2))
    print("\n")

    fnames = []
    results = []
    
    # Select out the best candidate
    # george
    
    
    for i in range(len(audio_chunks[0])):
        resultant = torch.cat([c[i] for c in audio_chunks], dim=-1)
        fnames.append(base_p / f"combined-{i}.wav")
        
        save_gen_with_voicefix(
            resultant, fnames[-1], squeeze=False, voicefixer=voicefixer
        )  # do not run fix on combined!!
        results.append(resultant)
        # torchaudio.save(base_p/'combined.wav', resultant, 24000)
    
    return fnames if return_filepaths else results


from voicefixer import VoiceFixer

vfixer = VoiceFixer()


def save_gen_with_voicefix(g, fpath, squeeze=True, voicefixer=False):
    torchaudio.save(fpath, g.squeeze(0).cpu() if squeeze else g, 24000, format="wav")
    if voicefixer:
        vfixer.restore(
            input=fpath,
            output=fpath,
            cuda=True,
            mode=0,
            # your_vocoder_func = convert_mel_to_wav # TODO test if integration with unvinet improves things
        )
