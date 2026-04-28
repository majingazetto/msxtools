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

# --- CONSTANTS (Following openMSX TsxImage.cc and MaxDuino) ---
TZX_Z80_FREQ = 3500000  # 3.5MHz
DEFAULT_OUTPUT_FREQ = 96000 
AMPLITUDE = 126 

CAS_MAGIC = b"\x1f\xa6\xde\xba\xcc\x13\x7d\x74"

# ANSI Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_CYAN = "\033[36m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_RED = "\033[31m"
C_BLUE = "\033[34m"
C_MAGENTA = "\033[35m"

def print_progress(current, total, prefix='', suffix='', length=50, fill='█'):
    if total <= 0: return
    current = max(0, min(current, total))
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{C_GREEN}{bar}{C_RESET}| {percent}% {suffix}', end='\r', flush=True)
    if current >= total: print()

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

def print_play_progress(current, total, wave_gfx, block_info, wave_color, length=40):
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    curr_t = f"{int(current // 60):02d}:{int(current % 60):02d}"
    total_t = f"{int(total // 60):02d}:{int(total % 60):02d}"
    sys.stdout.write('\r\033[K') 
    sys.stdout.write(f' {C_BOLD}BLOCK:{C_RESET} {C_CYAN}{block_info:<40}{C_RESET}\n')
    sys.stdout.write('\033[K') 
    sys.stdout.write(f' {wave_color}{wave_gfx}{C_RESET} |{C_GREEN}{bar}{C_RESET}| {C_BOLD}{percent:>5}%{C_RESET} [{curr_t}/{total_t}]')
    sys.stdout.write('\033[F') 
    sys.stdout.flush()

class TSXPlay:
    BLOCK_NAMES = {
        0x10: "Standard Speed Data", 0x11: "Turbo Speed Data", 0x12: "Pure Tone",
        0x13: "Pulse Sequence", 0x14: "Pure Data", 0x15: "Direct Recording",
        0x20: "Silence / Pause", 0x21: "Group Start", 0x22: "Group End",
        0x23: "Jump to Block", 0x24: "Loop Start", 0x25: "Loop End",
        0x2B: "Signal Level", 0x30: "Text Description", 0x32: "Archive Info",
        0x35: "Custom Info Block", 0x4B: "Kansas City Standard (MSX)", 0x5A: "Glue Block",
        0xFE: "MSX CAS Data Block"
    }

    ARCHIVE_FIELDS = {
        0x00: "Title", 0x01: "Publisher", 0x02: "Author", 0x03: "Release Date",
        0x04: "Language", 0x05: "Game Type", 0x06: "Price", 0x07: "Protection",
        0x08: "Origin", 0xFF: "Comment"
    }

    def __init__(self, sample_rate=DEFAULT_OUTPUT_FREQ, fast=False, invert=False, extra_pause=0):
        self.sample_rate, self.fast, self.invert, self.extra_pause = sample_rate, fast, invert, extra_pause
        self.current_value, self.phase_changed, self.samples, self.accum_samples = 127, False, bytearray(), 0.0
        self.detected_type, self.block_map = "UNKNOWN", []
        self.metadata = {} # Metadata found in the TSX
        self.file_path = None
        self.raw_blocks = [] # For CAS to TSX conversion

    def get_msx_info(self, data):
        if not data or len(data) < 16: return None
        h_bin, h_bas, h_asc = b"\xd0"*10, b"\xd3"*10, b"\xea"*10
        m_type = ""
        if data[0:10] == h_bin: m_type = "BINARY"
        elif data[0:10] == h_bas: m_type = "BASIC"
        elif data[0:10] == h_asc: m_type = "ASCII"
        if m_type:
            if self.detected_type == "UNKNOWN" or m_type == "BASIC": self.detected_type = m_type
            name = data[10:16].decode('ascii', 'ignore').strip()
            return f"{m_type} (\"{name}\")"
        return None

    def write_sample(self, t_states, value):
        num_samples_float = (t_states * self.sample_rate) / TZX_Z80_FREQ
        self.accum_samples += num_samples_float
        count = int(self.accum_samples)
        self.accum_samples -= count
        unsigned_val = ((-value if self.invert else value) + 128) & 0xFF
        if count > 0: self.samples.extend(bytes([unsigned_val] * count))

    def write_pulse(self, t_states):
        self.write_sample(t_states, self.current_value)
        self.current_value = -self.current_value

    def write_pulses(self, count, t_states):
        for _ in range(count): self.write_pulse(t_states)

    def write_silence(self, ms):
        if ms <= 0: return
        num_samples = int((ms / 1000.0) * self.sample_rate)
        self.samples.extend(b'\x80' * num_samples)
        self.current_value = 127

    def process_block_10(self, pause_ms, data):
        if not self.phase_changed: self.current_value = -127
        self.phase_changed = False
        is_data = (data[0] == 0xFF) if data else True
        n_pilot_std = 3223 if is_data else 8063
        t_p, t_1, t_0, n_p, s1, s2 = 2168, 1710, 855, n_pilot_std, 667, 735
        self.write_pulses(n_p, t_p); self.write_pulse(s1); self.write_pulse(s2)
        for byte in data:
            for i in range(8):
                if byte & (128 >> i): self.write_pulses(2, t_1)
                else: self.write_pulses(2, t_0)
        if pause_ms > 0: self.write_pulse(2000)
        self.write_silence(pause_ms + self.extra_pause)

    def process_block_11(self, data):
        pilot_t, sync1_t, sync2_t, zero_t, one_t, pilot_n = struct.unpack("<HHHHHH", data[0:12])
        last_bits, pause_ms = data[12], struct.unpack("<H", data[13:15])[0]
        actual_data = data[18:]
        if not self.phase_changed: self.current_value = -127
        self.phase_changed = False
        self.write_pulses(pilot_n, pilot_t); self.write_pulse(sync1_t); self.write_pulse(sync2_t)
        for i, byte in enumerate(actual_data):
            bits = 8 if i < len(actual_data)-1 else (last_bits if last_bits else 8)
            for b in range(bits):
                if byte & (128 >> b): self.write_pulses(2, one_t)
                else: self.write_pulses(2, zero_t)
        if pause_ms > 0: self.write_pulse(2000)
        self.write_silence(pause_ms + self.extra_pause)

    def process_block_4b(self, data):
        pause_ms = struct.unpack("<H", data[0:2])[0]
        if self.fast:
            t_p, n_p, t_0, t_1 = 364, 15000, 729, 364
        else:
            t_p, n_p, t_0, t_1 = struct.unpack("<HHHH", data[2:10])
        bit_cfg, byte_cfg, actual_data = data[10], data[11], data[12:]
        if not self.phase_changed: self.current_value = 127
        self.phase_changed = False
        n_0, n_1 = (bit_cfg >> 4) or 16, (bit_cfg & 0x0F) or 16
        n_start, v_start = (byte_cfg >> 6) & 3, (byte_cfg >> 5) & 1
        n_stop, v_stop = (byte_cfg >> 3) & 3, (byte_cfg >> 2) & 1
        msb = byte_cfg & 1
        self.write_pulses(n_p, t_p)
        if self.fast: self.write_pulse(333); self.write_pulse(367)
        for byte in actual_data:
            for _ in range(n_start):
                for _ in range(n_1 if v_start else n_0): self.write_pulse(t_1 if v_start else t_0)
            for i in range(8):
                bit = (byte >> (7-i if msb else i)) & 1
                for _ in range(n_1 if bit else n_0): self.write_pulse(t_1 if bit else t_0)
            for _ in range(n_stop):
                for _ in range(n_1 if v_stop else n_0): self.write_pulse(t_1 if v_stop else t_0)
        self.write_silence(pause_ms + self.extra_pause)

    def process_msx_bytes(self, data):
        # MSX Standard: 1 start bit (0), 8 data bits (LSB first), 2 stop bits (1)
        # 1200 baud: '1' is 2400Hz (half-cycle 729), '0' is 1200Hz (half-cycle 1458)
        t_1, t_0 = 729, 1458
        if self.fast:
            t_1, t_0 = 364, 729 # 2400 baud
            
        for byte in data:
            # Start bit (0): 2 pulses of t_0
            for _ in range(2): self.write_pulse(t_0)
            # 8 Data bits (LSB first)
            for i in range(8):
                bit = (byte >> i) & 1
                if bit:
                    for _ in range(4): self.write_pulse(t_1)
                else:
                    for _ in range(2): self.write_pulse(t_0)
            # 2 Stop bits (1): 2 * 4 pulses = 8 pulses of t_1
            for _ in range(8): self.write_pulse(t_1)

    def process_cas_block(self, data):
        # Long: 8063 pulses, Short: 3223 pulses
        is_header = False
        if len(data) >= 10:
            if data[0:10] in (b"\xd0"*10, b"\xd3"*10, b"\xea"*10): is_header = True
            
        n_p = 8063 if is_header else 3223
        t_p = 729 if not self.fast else 364
        s1, s2 = 333, 367 # Sync pulses
        if self.fast: s1 //= 2; s2 //= 2
        
        if not self.phase_changed: self.current_value = 127
        self.phase_changed = False
        
        self.write_pulses(n_p, t_p)
        self.write_pulse(s1); self.write_pulse(s2)
        self.process_msx_bytes(data)
        self.write_silence(1000)

    def save_tsx(self, tsx_path, metadata=None):
        with open(tsx_path, "wb") as f:
            f.write(b"ZXTape!\x1a\x01\x15") # Header TZX 1.21
            
            # --- METADATA BLOCKS ---
            if metadata:
                # 1. Text Description (0x30)
                if metadata.get("Description"):
                    desc = metadata["Description"].encode('ascii', 'ignore')[:255]
                    f.write(b"\x30")
                    f.write(bytes([len(desc)]))
                    f.write(desc)
                
                # 2. Archive Info (0x32)
                archive_data = bytearray()
                fields = { 0x00: "Title", 0x01: "Publisher", 0x02: "Author", 0x03: "Release Date", 0xFF: "Comment" }
                field_count = 0
                for tid, key in fields.items():
                    val = metadata.get(key)
                    if val:
                        txt = val.encode('ascii', 'ignore')[:255]
                        archive_data.extend(bytes([tid, len(txt)]))
                        archive_data.extend(txt)
                        field_count += 1
                
                if field_count > 0:
                    f.write(b"\x32")
                    f.write(struct.pack("<H", len(archive_data) + 1))
                    f.write(bytes([field_count]))
                    f.write(archive_data)

            # --- DATA BLOCKS ---
            for block_data in self.raw_blocks:
                is_header = False
                if len(block_data) >= 10 and block_data[0:10] in (b"\xd0"*10, b"\xd3"*10, b"\xea"*10):
                    is_header = True
                
                n_p = 8063 if is_header else 3223
                t_p, t_0, t_1 = (364, 729, 364) if self.fast else (729, 1458, 729)
                s1, s2 = (166, 183) if self.fast else (333, 367)
                
                dlen = len(block_data)
                blen = 21 + dlen
                f.write(b"\x4B")
                f.write(struct.pack("<I", blen))
                f.write(struct.pack("<H", 1000)) # Pause 1s
                f.write(struct.pack("<H", t_p))
                f.write(struct.pack("<H", n_p))
                f.write(struct.pack("<H", s1))
                f.write(struct.pack("<H", s2))
                f.write(struct.pack("<H", t_0))
                f.write(struct.pack("<H", t_1))
                # MSX Specific: BitCfg=0x24 (2/4 pulses), ByteCfg=0x54 (1 start, 2 stop, LSB)
                f.write(b"\x24\x54\x08") # Offset 14, 15, 16
                f.write(struct.pack("<I", dlen))
                f.write(block_data)
        print(f"\n {C_GREEN}[√] TSX file saved to:{C_RESET} {C_YELLOW}{tsx_path}{C_RESET}")

    def list_blocks(self, file_path):
        is_cas = file_path.lower().endswith(".cas")
        print(f"\n{C_BOLD}{'CAS' if is_cas else 'TSX/TZX'} Block List for:{C_RESET} {C_YELLOW}{os.path.basename(file_path)}{C_RESET}")
        print("-" * 60)
        with open(file_path, "rb") as f:
            if is_cas:
                data = f.read()
                ptr = 0
                while True:
                    idx = data.find(CAS_MAGIC, ptr)
                    if idx == -1: break
                    pos = idx
                    print(f"[{C_GREEN}{hex(pos)}{C_RESET}] ID {C_YELLOW}0xFE{C_RESET}: {C_CYAN}MSX CAS Data Block{C_RESET}")
                    ptr = idx + 8
            else:
                sig = f.read(10)
                if sig[0:8] != b"ZXTape!\x1a" and sig[0:8] != b"TSX Tape": return
                while True:
                    pos = f.tell()
                    bid_raw = f.read(1)
                    if not bid_raw: break
                    bid = bid_raw[0]
                    name = self.BLOCK_NAMES.get(bid, f"Unknown Block ({hex(bid)})")
                    print(f"[{C_GREEN}{hex(pos)}{C_RESET}] ID {C_YELLOW}{hex(bid)}{C_RESET}: {C_CYAN}{name}{C_RESET}")
                    if bid == 0x10: f.read(struct.unpack("<HH", f.read(4))[1])
                    elif bid == 0x11: f.read(struct.unpack("<I", f.read(0x12)[0x0F:0x12] + b"\x00")[0])
                    elif bid == 0x12: f.read(4)
                    elif bid == 0x13: f.read(1 + f.read(1)[0] * 2)
                    elif bid == 0x14: f.read(7 + struct.unpack("<I", f.read(3) + b"\x00")[0])
                    elif bid in (0x20, 0x23, 0x24): f.read(2)
                    elif bid in (0x21, 0x30): f.read(f.read(1)[0])
                    elif bid == 0x2B: f.read(5)
                    elif bid == 0x32: f.read(struct.unpack("<H", f.read(2))[0])
                    elif bid == 0x35: f.read(16); f.read(struct.unpack("<I", f.read(4))[0])
                    elif bid == 0x4B: f.read(struct.unpack("<I", f.read(4))[0])
                    elif bid == 0x5A: f.read(9)
                    else: break
        print("-" * 60 + "\n")

    def convert(self, file_path, wav_path=None, tsx_path=None, lead_in=0, silent=False, metadata=None):
        self.file_path = file_path
        file_size = os.path.getsize(file_path)
        effective_lead_in = lead_in if lead_in > 0 else (1000 if self.fast else 500)
        if wav_path or not tsx_path: # Lead-in for audio
            if effective_lead_in > 0: self.block_map.append((0, "Silence (Lead-in)")); self.write_silence(effective_lead_in)
        
        if file_path.lower().endswith(".cas"):
            with open(file_path, "rb") as f:
                content = f.read()
                blocks = content.split(CAS_MAGIC)
                for i, block in enumerate(blocks):
                    if not block: continue
                    if not silent: print_progress(i, len(blocks), prefix='Processing CAS:', suffix=f'Block {i}')
                    msx = self.get_msx_info(block)
                    current_info = f"MSX {msx}" if msx else "CAS Data Block"
                    self.block_map.append((len(self.samples), current_info))
                    self.raw_blocks.append(block)
                    if not tsx_path or wav_path: self.process_cas_block(block)
                if not silent: print_progress(len(blocks), len(blocks), prefix='Processing CAS:', suffix='Complete')
        else:
            with open(file_path, "rb") as f:
                sig = f.read(10)
                if sig[0:8] != b"ZXTape!\x1a" and sig[0:8] != b"TSX Tape": return
                while True:
                    pos = f.tell()
                    if not silent: print_progress(pos, file_size, prefix='Converting TSX:', suffix=f'Pos {hex(pos)}')
                    bid_raw = f.read(1)
                    if not bid_raw: break
                    bid = bid_raw[0]
                    b_name = self.BLOCK_NAMES.get(bid, f"Block {hex(bid)}")
                    current_info = b_name
                    if bid == 0x10:
                        pause, length = struct.unpack("<HH", f.read(4)); data = f.read(length); msx = self.get_msx_info(data)
                        if msx: current_info = f"MSX {msx}"
                        self.block_map.append((len(self.samples), current_info)); self.process_block_10(pause, data)
                    elif bid == 0x4B:
                        blen = struct.unpack("<I", f.read(4))[0]; data = f.read(blen); msx = self.get_msx_info(data[12:])
                        if msx: current_info = f"MSX {msx}"
                        self.block_map.append((len(self.samples), current_info)); self.process_block_4b(data)
                    elif bid == 0x30:
                        l = f.read(1)[0]; txt = f.read(l).decode('ascii', 'ignore').strip()
                        if txt: self.metadata["Description"] = txt
                    elif bid == 0x32:
                        blen = struct.unpack("<H", f.read(2))[0]; bdata = f.read(blen)
                        num_strings = bdata[0]; ptr = 1
                        for _ in range(num_strings):
                            if ptr >= blen: break
                            tid = bdata[ptr]; slen = bdata[ptr+1]; ptr += 2
                            stxt = bdata[ptr:ptr+slen].decode('ascii', 'ignore').strip()
                            ptr += slen
                            fname = self.ARCHIVE_FIELDS.get(tid, f"Field {hex(tid)}")
                            if stxt: self.metadata[fname] = stxt
                    else:
                        self.block_map.append((len(self.samples), current_info))
                        if bid == 0x11: hdr = f.read(0x12); dlen = struct.unpack("<I", hdr[0x0F:0x12] + b"\x00")[0]; self.process_block_11(hdr + f.read(dlen))
                        elif bid == 0x12: t, n = struct.unpack("<HH", f.read(4)); self.write_pulses(n, t)
                        elif bid == 0x13: n = f.read(1)[0]; [self.write_pulse(struct.unpack("<H", f.read(2))[0]) for _ in range(n)]
                        elif bid == 0x20: self.write_silence(struct.unpack("<H", f.read(2))[0])
                        elif bid == 0x2B: self.phase_changed = True; self.current_value = -127 if struct.unpack("<I", f.read(4))[0] == 0 else 127; f.read(1)
                        elif bid == 0x35: f.read(16); f.read(struct.unpack("<I", f.read(4))[0])
                        elif bid in (0x5A, 0x21, 0x30, 0x22): [f.read(9) if bid==0x5A else f.read(f.read(1)[0]) if bid in (0x21, 0x30) else None]
                        else: break
                if not silent: print_progress(file_size, file_size, prefix='Converting TSX:', suffix='Complete')
        
        if tsx_path and self.raw_blocks: self.save_tsx(tsx_path, metadata)
        if wav_path:
            with wave.open(wav_path, "wb") as wf: wf.setnchannels(1); wf.setsampwidth(1); wf.setframerate(self.sample_rate); wf.writeframes(self.samples)

    def play(self):
        if not self.samples: return
        instructions = { "BINARY": 'BLOAD"CAS:",R', "BASIC": 'RUN"CAS:"', "ASCII": 'LOAD"CAS:",R', "UNKNOWN": 'RUN"CAS:" or BLOAD"CAS:",R' }
        cmd_text = instructions.get(self.detected_type, instructions["UNKNOWN"])
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as twf:
            temp_name = twf.name
            with wave.open(twf, 'wb') as wf: wf.setnchannels(1); wf.setsampwidth(1); wf.setframerate(self.sample_rate); wf.writeframes(self.samples)
        
        print("\n" + f"{C_YELLOW}═{C_RESET}"*70 + f"\n {C_BOLD}{C_CYAN}MSX TAPE PLAYER{C_RESET}\n" + f"{C_YELLOW}═{C_RESET}"*70)
        
        # Display Filename
        print(f" {C_BOLD}FILE        :{C_RESET} {C_MAGENTA}{os.path.basename(self.file_path)}{C_RESET}")

        # Display Metadata if available
        if self.metadata:
            for k, v in self.metadata.items():
                print(f" {C_BOLD}{k:<12}:{C_RESET} {C_YELLOW}{v}{C_RESET}")
        
        print(f"{C_YELLOW}─{C_RESET}"*70)
            
        print(f" {C_BOLD}ENTRY TYPE  :{C_RESET} {C_GREEN}{self.detected_type}{C_RESET}\n {C_BOLD}MSX COMMAND :{C_RESET} {C_CYAN}{cmd_text}{C_RESET}\n" + f"{C_YELLOW}═{C_RESET}"*70 + "\n\n")
        
        duration = len(self.samples) / float(self.sample_rate)
        try:
            process = subprocess.Popen(["aplay", "-q", "-c", "1", temp_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            start_time = time.time()
            while process.poll() is None:
                elapsed = time.time() - start_time
                if elapsed > duration: elapsed = duration
                current_sample = int(elapsed * self.sample_rate)
                current_info = "Silence"; wave_color = C_RED
                for start, info in self.block_map:
                    if current_sample >= start:
                        current_info = info
                        if "BASIC" in info: wave_color = C_GREEN
                        elif "BINARY" in info: wave_color = C_CYAN
                        elif "ASCII" in info: wave_color = C_YELLOW
                        elif "Silence" in info: wave_color = C_RED
                        else: wave_color = C_BLUE
                    else: break
                print_play_progress(elapsed, duration, get_real_wave_anim(self.samples, current_sample, 1), current_info, wave_color)
                time.sleep(0.05)
            print_play_progress(duration, duration, " " * 20, "Playback Finished", C_RESET)
            print(f"\n\n {C_GREEN}[√] Done.{C_RESET}\n")
        except KeyboardInterrupt:
            process.terminate(); print(f"\n\n {C_RED}[!] Interrupted.{C_RESET}\n")
        finally:
            try: os.unlink(temp_name)
            except: pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TSX/TZX/CAS Player and Converter")
    parser.add_argument("input", help="Input TSX/TZX/CAS file")
    parser.add_argument("-w", "--wav", dest="output", help="Output WAV file")
    parser.add_argument("-t", "--tsx", dest="tsx_output", help="Output TSX file")
    parser.add_argument("--ls", action="store_true", help="List blocks and info")
    parser.add_argument("--play", action="store_true", help="Play audio (default)")
    parser.add_argument("--fast", action="store_true", help="Use 2400 baud fast mode")
    parser.add_argument("--invert", action="store_true", help="Invert phase")
    parser.add_argument("--rate", type=int, default=96000, help="Sample rate")
    
    # Metadata arguments
    meta_group = parser.add_argument_group("Metadata (for TSX output)")
    meta_group.add_argument("--title", help="Game title")
    meta_group.add_argument("--author", help="Author name")
    meta_group.add_argument("--publisher", help="Publisher name")
    meta_group.add_argument("--year", help="Release year")
    meta_group.add_argument("--desc", help="Text description")
    
    args = parser.parse_args()
    
    player = TSXPlay(sample_rate=args.rate, fast=args.fast, invert=args.invert)
    
    if args.ls:
        player.list_blocks(args.input)
    
    # Metadata dictionary for save_tsx
    metadata = {
        "Title": args.title,
        "Author": args.author,
        "Publisher": args.publisher,
        "Release Date": args.year,
        "Description": args.desc
    }
    
    if args.tsx_output:
        player.convert(args.input, tsx_path=args.tsx_output, metadata=metadata)
    elif args.output:
        player.convert(args.input, wav_path=args.output)
    elif not args.ls:
        player.convert(args.input, None, silent=True)
        player.play()
