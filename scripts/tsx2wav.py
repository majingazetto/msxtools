#!/usr/bin/env python3
import sys
import wave
import struct
import argparse
import os
import json

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

class TSX2WAV:
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
        self.write_pulses(3223, 2168)
        self.write_pulse(667)
        self.write_pulse(735)
        for byte in data:
            for i in range(8):
                if byte & (128 >> i): self.write_pulses(2, 1710)
                else: self.write_pulses(2, 855)
        if pause_ms > 0: self.write_pulse(2000)
        self.write_silence(100 if self.fast else (pause_ms + self.extra_pause))

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
        t_pilot = 238 if self.fast else struct.unpack("<H", data[2:4])[0]
        n_pilot = 5000 if self.fast else struct.unpack("<H", data[4:6])[0]
        t_zero = (238*2) if self.fast else struct.unpack("<H", data[6:8])[0]
        t_one = 238 if self.fast else struct.unpack("<H", data[8:10])[0]
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

    def convert(self, tsx_path, wav_path, lead_in=0):
        file_size = os.path.getsize(tsx_path)
        if lead_in > 0: self.write_silence(lead_in)
        with open(tsx_path, "rb") as f:
            sig = f.read(10)
            if sig[0:8] != b"ZXTape!\x1a":
                print(f"Error: Invalid signature {sig[0:8]}"); return
            while True:
                pos = f.tell()
                print_progress(pos, file_size, prefix='Converting:', suffix=f'Pos {pos}')
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
                elif bid in (0x5A, 0x21, 0x30, 0x22): # Skip varying length blocks
                    if bid == 0x5A: f.read(9)
                    elif bid == 0x21: f.read(f.read(1)[0])
                    elif bid == 0x30: f.read(f.read(1)[0])
                    else: pass
                else: 
                    # Try a small step if unknown to avoid infinite loop
                    pass
            print_progress(file_size, file_size, prefix='Converting:', suffix='Complete')
        
        print(f"Detected MSX File Type: {self.detected_type}")
        print(f"Writing {len(self.samples)} samples to {wav_path}...")
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(1); wf.setframerate(self.sample_rate)
            wf.writeframes(self.samples)
            
        # Optional: Save a small metadata file alongside the WAV
        meta_path = wav_path + ".json"
        with open(meta_path, "w") as jf:
            json.dump({"type": self.detected_type}, jf)
        print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input"); parser.add_argument("output")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--extra-pause", type=int, default=0)
    parser.add_argument("--rate", type=int, default=96000)
    args = parser.parse_args()
    TSX2WAV(sample_rate=args.rate, fast=args.fast, invert=args.invert, extra_pause=args.extra_pause).convert(args.input, args.output)
