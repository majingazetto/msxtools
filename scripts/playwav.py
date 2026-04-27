#!/usr/bin/env python3
import subprocess
import sys
import os
import wave
import time
import struct
import argparse
import tempfile
import json

def get_real_wave_anim(data, current_sample, sample_width, window_size=240, anim_len=20):
    if not data: return " " * anim_len
    start_byte = current_sample * sample_width
    end_byte = start_byte + (window_size * sample_width)
    chunk = data[start_byte:end_byte]
    if not chunk: return " " * anim_len
    chars = " ▂▃▄▅▆▇█"
    out = ""
    samples_per_char = max(1, len(chunk) // (anim_len * sample_width))
    for i in range(anim_len):
        b_start = i * samples_per_char * sample_width
        try:
            if sample_width == 1:
                val = chunk[b_start]
                idx = min(7, int(val / 32))
            else:
                s_val = struct.unpack("<h", chunk[b_start:b_start+2])[0]
                idx = min(7, int((s_val + 32768) / 8192))
        except: idx = 0
        out += chars[idx]
    return out

def print_progress(current, total, wave_gfx, length=40):
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    curr_t = f"{int(current // 60):02d}:{int(current % 60):02d}"
    total_t = f"{int(total // 60):02d}:{int(total % 60):02d}"
    sys.stdout.write(f'\r {wave_gfx} |{bar}| {percent}% [{curr_t}/{total_t}]')
    sys.stdout.flush()

def play_wav(file_path, invert=False):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found."); return

    # Try to detect file type from metadata
    detected_type = "UNKNOWN"
    meta_path = file_path + ".json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as jf:
                detected_type = json.load(jf).get("type", "UNKNOWN")
        except: pass

    # Instruction mapping
    instructions = {
        "BINARY": 'BLOAD"CAS:",R',
        "BASIC": 'RUN"CAS:"',
        "ASCII": 'LOAD"CAS:",R',
        "UNKNOWN": 'RUN"CAS:" or BLOAD"CAS:",R'
    }
    cmd_text = instructions.get(detected_type, instructions["UNKNOWN"])

    try:
        with wave.open(file_path, 'rb') as wf:
            params = wf.getparams()
            frames_count = wf.getnframes()
            rate = wf.getframerate()
            width = wf.getsampwidth()
            duration = frames_count / float(rate)
            raw_audio_data = wf.readframes(frames_count)
    except Exception as e:
        print(f"Error reading WAV: {e}"); return

    play_path = file_path
    temp_wav = None
    if invert:
        if width == 1:
            inverted_data = bytearray([256 - b if b != 0 else 0 for b in raw_audio_data])
        else:
            count = len(raw_audio_data) // 2
            shorts = list(struct.unpack(f"<{count}h", raw_audio_data))
            inverted_data = struct.pack(f"<{count}h", *[-x for x in shorts])
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        with wave.open(temp_wav.name, 'wb') as twf:
            twf.setparams(params)
            twf.writeframes(inverted_data)
        play_path = temp_wav.name

    print("\n" + "="*70)
    print(f" MSX TAPE PLAYER (Real-time Signal)")
    print("="*70)
    print(f" FILE: {os.path.basename(file_path)}")
    print(f" TYPE: {detected_type}")
    print(f" INFO: {rate} Hz | {'8-bit' if width==1 else '16-bit'} | {'INVERTED' if invert else 'NORMAL'}")
    print("-" * 70)
    print(f" On MSX, type: {cmd_text}")
    print("-" * 70)

    try:
        process = subprocess.Popen(["aplay", "-q", "-c", "2", play_path], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        start_time = time.time()
        while process.poll() is None:
            elapsed = time.time() - start_time
            if elapsed > duration: elapsed = duration
            current_sample = int(elapsed * rate)
            wave_gfx = get_real_wave_anim(raw_audio_data, current_sample, width)
            print_progress(elapsed, duration, wave_gfx)
            time.sleep(0.05)
        print_progress(duration, duration, " " * 20)
        print("\n\n [√] Playback finished.\n")
    except KeyboardInterrupt:
        process.terminate()
        print("\n\n [!] Stopped.\n")
    finally:
        if temp_wav:
            try: os.unlink(temp_wav.name)
            except: pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--invert", action="store_true")
    args = parser.parse_args()
    play_wav(args.input, invert=args.invert)
