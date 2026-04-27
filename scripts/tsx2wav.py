#!/usr/bin/env python3
import sys
import wave
import struct
import argparse
import os
import json
import time
import subprocess
import tempfile

# --- CONSTANTS (Following openMSX TsxImage.cc) ---
TZX_Z80_FREQ = 3500000  # 3.5MHz
DEFAULT_OUTPUT_FREQ = 96000 
AMPLITUDE = 126 

def print_progress(current, total, prefix='', suffix='', length=50, fill='█'):
    if total <= 0: return
    current = max(0, min(current, total))
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r', flush=True)
    if current >= total:
        print()

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

def print_play_progress(current, total, wave_gfx, length=40):
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    curr_t = f"{int(current // 60):02d}:{int(current % 60):02d}"
    total_t = f"{int(total // 60):02d}:{int(total % 60):02d}"
    sys.stdout.write(f'\r {wave_gfx} |{bar}| {percent}% [{curr_t}/{total_t}]')
    sys.stdout.flush()

class TSX2WAV:
    BLOCK_NAMES = {
        0x10: "Standard Speed Data Block",
        0x11: "Turbo Speed Data Block",
        0x12: "Pure Tone",
        0x13: "Pulse Sequence",
        0x14: "Pure Data Block",
        0x15: "Direct Recording Block",
        0x20: "Silence / Pause Block",
        0x21: "Group Start",
        0x22: "Group End",
        0x23: "Jump to Block",
        0x24: "Loop Start",
        0x25: "Loop End",
        0x26: "Call Sequence",
        0x27: "Return from Sequence",
        0x28: "Select Block",
        0x2A: "Stop the Tape if in 48K Mode",
        0x2B: "Signal Level",
        0x30: "Text Description",
        0x31: "Message Block",
        0x32: "Archive Info",
        0x33: "Hardware Type",
        0x35: "Custom Info Block",
        0x4B: "Kansas City Standard (MSX)",
        0x5A: "Glue Block"
    }

    def __init__(self, sample_rate=DEFAULT_OUTPUT_FREQ, fast=False, invert=False, extra_pause=0):
        self.sample_rate = sample_rate
        self.fast = fast
        self.invert = invert
        self.extra_pause = extra_pause
        self.current_value = 127
        self.phase_changed = False
        self.samples = bytearray()
        self.accum_samples = 0.0
        self.detected_type = "UNKNOWN"

    def write_sample(self, t_states, value):
        num_samples_float = (t_states * self.sample_rate) / TZX_Z80_FREQ
        self.accum_samples += num_samples_float
        count = int(self.accum_samples)
        self.accum_samples -= count
        final_value = -value if self.invert else value
        unsigned_val = (final_value + 128) & 0xFF
        for _ in range(count):
            self.samples.append(unsigned_val)

    def write_pulse(self, t_states):
        self.write_sample(t_states, self.current_value)
        self.current_value = -self.current_value

    def write_pulses(self, count, t_states):
        for _ in range(count):
            self.write_pulse(t_states)

    def write_silence(self, ms):
        if ms <= 0: return
        num_samples = int((ms / 1000.0) * self.sample_rate)
        for _ in range(num_samples):
            self.samples.append(128)
        self.current_value = 127

    def process_block_10(self, pause_ms, data):
        if not self.phase_changed: self.current_value = -127
        self.phase_changed = False
        
        # Standard 1200: 2168 pilot, 1710 one, 855 zero
        # Standard 2400: 1084 pilot, 855 one, 427 zero (half of 1200)
        t_pilot = 1084 if self.fast else 2168
        t_one = 855 if self.fast else 1710
        t_zero = 427 if self.fast else 855
        
        # Pilot: 12000 pulses (~2.5s at 2400baud) if fast, else standard 3223
        self.write_pulses(12000 if self.fast else 3223, t_pilot)
        self.write_pulse(667 if not self.fast else 333) # sync1
        self.write_pulse(735 if not self.fast else 367) # sync2
        for byte in data:
            for i in range(8):
                if byte & (128 >> i): self.write_pulses(2, t_one)
                else: self.write_pulses(2, t_zero)
        if pause_ms > 0: self.write_pulse(2000)
        self.write_silence(1000 if self.fast else (pause_ms + self.extra_pause))

    def process_block_11(self, data):
        if len(data) < 18: return
        pilot_t, sync1_t, sync2_t, zero_t, one_t, pilot_n = struct.unpack("<HHHHHH", data[0:12])
        last_bits = data[12]
        pause_ms = struct.unpack("<H", data[13:15])[0]
        actual_data = data[18:]
        if not self.phase_changed: self.current_value = -127
        self.phase_changed = False
        self.write_pulses(pilot_n, pilot_t)
        self.write_pulse(sync1_t)
        self.write_pulse(sync2_t)
        for i, byte in enumerate(actual_data):
            bits = 8 if i < len(actual_data)-1 else (last_bits if last_bits else 8)
            for b in range(bits):
                if byte & (128 >> b): self.write_pulses(2, one_t)
                else: self.write_pulses(2, zero_t)
        if pause_ms > 0: self.write_pulse(2000)
        self.write_silence(100 if self.fast else (pause_ms + self.extra_pause))

    def process_block_4b(self, data):
        if len(data) < 12: return
        pause_ms = struct.unpack("<H", data[0:2])[0]
        t_pilot_orig = struct.unpack("<H", data[2:4])[0]
        n_pilot_orig = struct.unpack("<H", data[4:6])[0]
        t_zero_orig = struct.unpack("<H", data[6:8])[0]
        t_one_orig = struct.unpack("<H", data[8:10])[0]

        # Default to original values
        t_pilot, n_pilot, t_zero, t_one = t_pilot_orig, n_pilot_orig, t_zero_orig, t_one_orig

        if self.fast:
            # Detect standard 1200 baud: '1' pulse ~729, '0' pulse ~1458
            # We allow some tolerance (729 +/- 100)
            is_1200 = (600 < t_one_orig < 850) and (1300 < t_zero_orig < 1600)
            if is_1200:
                t_pilot = 364
                n_pilot = 5000  # Standard 2400 pilot length
                t_zero = 729
                t_one = 364

        bit_cfg, byte_cfg = data[10:12]
        actual_data = data[12:]

        # MSX Header Detection
        if self.detected_type == "UNKNOWN" and len(actual_data) >= 10:
            if actual_data[0:10] == b"\xd0"*10: self.detected_type = "BINARY"
            elif actual_data[0:10] == b"\xd3"*10: self.detected_type = "BASIC"
            elif actual_data[0:10] == b"\xea"*10: self.detected_type = "ASCII"

        if not self.phase_changed: self.current_value = 127
        self.phase_changed = False
        num_zero_p = (bit_cfg >> 4) if (bit_cfg >> 4) else 16
        num_one_p = (bit_cfg & 0x0F) if (bit_cfg & 0x0F) else 16
        n_start, v_start = (byte_cfg >> 6) & 3, (byte_cfg >> 5) & 1
        n_stop, v_stop = (byte_cfg >> 3) & 3, (byte_cfg >> 2) & 1
        msb = byte_cfg & 1
        self.write_pulses(n_pilot, t_pilot)
        for byte in actual_data:
            for _ in range(n_start):
                for _ in range(num_one_p if v_start else num_zero_p): self.write_pulse(t_one if v_start else t_zero)
            for i in range(8):
                bit = (byte >> (7-i if msb else i)) & 1
                if bit:
                    for _ in range(num_one_p): self.write_pulse(t_one)
                else:
                    for _ in range(num_zero_p): self.write_pulse(t_zero)
            for _ in range(n_stop):
                for _ in range(num_one_p if v_stop else num_zero_p): self.write_pulse(t_one if v_stop else t_zero)
        self.write_silence(100 if self.fast else (pause_ms + self.extra_pause))

    def list_blocks(self, tsx_path):
        print(f"\nTSX/TZX Block List for: {os.path.basename(tsx_path)}")
        print("-" * 60)
        with open(tsx_path, "rb") as f:
            sig = f.read(10)
            if sig[0:8] != b"ZXTape!\x1a":
                print(f"Error: Invalid signature {sig[0:8]}"); return
            print(f"Version: {sig[8]}.{sig[9]}")
            while True:
                pos = f.tell()
                bid_raw = f.read(1)
                if not bid_raw: break
                bid = bid_raw[0]
                name = self.BLOCK_NAMES.get(bid, f"Unknown Block ({hex(bid)})")
                print(f"[{hex(pos)}] ID {hex(bid)}: {name}")
                if bid == 0x10:
                    pause, length = struct.unpack("<HH", f.read(4))
                    print(f"  Length: {length}, Pause: {pause}ms")
                    f.read(length)
                elif bid == 0x11:
                    hdr = f.read(0x12)
                    dlen = struct.unpack("<I", hdr[0x0F:0x12] + b"\x00")[0]
                    print(f"  Data Length: {dlen}")
                    f.read(dlen)
                elif bid == 0x12: f.read(4)
                elif bid == 0x13: f.read(1 + f.read(1)[0] * 2)
                elif bid == 0x14: f.read(7 + struct.unpack("<I", f.read(3) + b"\x00")[0])
                elif bid == 0x20: print(f"  Pause: {struct.unpack('<H', f.read(2))[0]}ms")
                elif bid == 0x21: f.read(f.read(1)[0])
                elif bid == 0x22: pass
                elif bid == 0x23: f.read(2)
                elif bid == 0x24: f.read(2)
                elif bid == 0x25: pass
                elif bid == 0x2B: f.read(5)
                elif bid == 0x30:
                    l = f.read(1)[0]
                    txt = f.read(l).decode('ascii', 'ignore')
                    print(f"  Description: {txt}")
                elif bid == 0x32:
                    l = struct.unpack("<H", f.read(2))[0]
                    f.read(l)
                elif bid == 0x35:
                    f.read(16)
                    l = struct.unpack("<I", f.read(4))[0]
                    f.read(l)
                elif bid == 0x4B:
                    blen = struct.unpack("<I", f.read(4))[0]
                    print(f"  Length: {blen}")
                    f.read(blen)
                elif bid == 0x5A: f.read(9)
                else:
                    print(f"  [!] Cannot parse block {hex(bid)}, stopping.")
                    break
        print("-" * 60 + "\n")

    def convert(self, tsx_path, wav_path=None, lead_in=0, silent=False):
        file_size = os.path.getsize(tsx_path)
        if lead_in > 0: self.write_silence(lead_in)
        with open(tsx_path, "rb") as f:
            sig = f.read(10)
            if sig[0:8] != b"ZXTape!\x1a":
                if not silent: print(f"Error: Invalid signature {sig[0:8]}")
                return
            while True:
                pos = f.tell()
                if not silent: print_progress(pos, file_size, prefix='Converting:', suffix=f'Pos {pos}')
                bid_raw = f.read(1)
                if not bid_raw: break
                bid = bid_raw[0]
                if bid == 0x10:
                    pause, length = struct.unpack("<HH", f.read(4))
                    self.process_block_10(pause, f.read(length))
                elif bid == 0x11:
                    hdr = f.read(0x12)
                    dlen = struct.unpack("<I", hdr[0x0F:0x12] + b"\x00")[0]
                    self.process_block_11(hdr + f.read(dlen))
                elif bid == 0x12:
                    t, n = struct.unpack("<HH", f.read(4))
                    self.write_pulses(n, t)
                elif bid == 0x13:
                    n = f.read(1)[0]
                    for _ in range(n): self.write_pulse(struct.unpack("<H", f.read(2))[0])
                elif bid == 0x20: self.write_silence(struct.unpack("<H", f.read(2))[0])
                elif bid == 0x2B:
                    self.phase_changed = True
                    self.current_value = -127 if struct.unpack("<I", f.read(4))[0] == 0 else 127
                    f.read(1)
                elif bid == 0x4B:
                    blen = struct.unpack("<I", f.read(4))[0]
                    self.process_block_4b(f.read(blen))
                elif bid == 0x32: f.read(struct.unpack("<H", f.read(2))[0])
                elif bid == 0x35: f.read(16); f.read(struct.unpack("<I", f.read(4))[0])
                elif bid in (0x5A, 0x21, 0x30, 0x22):
                    if bid == 0x5A: f.read(9)
                    elif bid == 0x21: f.read(f.read(1)[0])
                    elif bid == 0x30: f.read(f.read(1)[0])
                    else: pass
                else: pass
            if not silent: print_progress(file_size, file_size, prefix='Converting:', suffix='Complete')
        
        if not silent: print(f"Detected MSX File Type: {self.detected_type}")
        
        if wav_path:
            if not silent: print(f"Writing {len(self.samples)} samples to {wav_path}...")
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1); wf.setsampwidth(1); wf.setframerate(self.sample_rate)
                wf.writeframes(self.samples)
            meta_path = wav_path + ".json"
            with open(meta_path, "w") as jf:
                json.dump({"type": self.detected_type}, jf)

    def play(self):
        if not self.samples:
            print("No audio data to play."); return

        instructions = {
            "BINARY": 'BLOAD"CAS:",R',
            "BASIC": 'RUN"CAS:"',
            "ASCII": 'LOAD"CAS:",R',
            "UNKNOWN": 'RUN"CAS:" or BLOAD"CAS:",R'
        }
        cmd_text = instructions.get(self.detected_type, instructions["UNKNOWN"])

        # Write to a temporary file for aplay
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as twf:
            temp_name = twf.name
            with wave.open(twf, 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(1); wf.setframerate(self.sample_rate)
                wf.writeframes(self.samples)

        print("\n" + "="*70)
        print(f" MSX TAPE PLAYER")
        print("="*70)
        print(f" TYPE: {self.detected_type}")
        print("-" * 70)
        print(f" On MSX, type: {cmd_text}")
        print("-" * 70)

        duration = len(self.samples) / float(self.sample_rate)
        try:
            process = subprocess.Popen(["aplay", "-q", "-c", "1", temp_name], 
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            start_time = time.time()
            while process.poll() is None:
                elapsed = time.time() - start_time
                if elapsed > duration: elapsed = duration
                current_sample = int(elapsed * self.sample_rate)
                wave_gfx = get_real_wave_anim(self.samples, current_sample, 1)
                print_play_progress(elapsed, duration, wave_gfx)
                time.sleep(0.05)
            print_play_progress(duration, duration, " " * 20)
            print("\n\n [√] Playback finished.\n")
        except KeyboardInterrupt:
            process.terminate()
            print("\n\n [!] Stopped.\n")
        finally:
            try: os.unlink(temp_name)
            except: pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TSX to WAV converter and player")
    parser.add_argument("input", help="Input TSX/TZX file")
    parser.add_argument("output", nargs="?", help="Output WAV file (optional if using --play)")
    parser.add_argument("--ls", action="store_true", help="List blocks and info")
    parser.add_argument("--play", action="store_true", help="Play the audio directly")
    parser.add_argument("--fast", action="store_true", help="Use 2400 baud fast loading")
    parser.add_argument("--invert", action="store_true", help="Invert audio phase")
    parser.add_argument("--extra-pause", type=int, default=0, help="Extra pause in ms")
    parser.add_argument("--rate", type=int, default=96000, help="Sample rate")
    args = parser.parse_args()

    converter = TSX2WAV(sample_rate=args.rate, fast=args.fast, invert=args.invert, extra_pause=args.extra_pause)
    
    if args.ls:
        converter.list_blocks(args.input)
    
    if args.output or args.play:
        converter.convert(args.input, args.output, silent=(args.play and not args.output))
        if args.play:
            converter.play()
    elif not args.ls:
        parser.print_help()
