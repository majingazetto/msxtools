#!/usr/bin/env python3
import wave
import sys
import os

def invert_wav(input_path, output_path):
    print(f"Inverting {input_path} -> {output_path}")
    with wave.open(input_path, 'rb') as wi:
        params = wi.getparams()
        width = wi.getsampwidth()
        frames = wi.readframes(wi.getnframes())
        
        if width == 1:
            # 8-bit unsigned: invert around 128
            inverted = bytearray()
            for b in frames:
                inverted.append(256 - b if b != 0 else 0)
        else:
            # 16-bit signed: simple negation
            import struct
            count = len(frames) // 2
            data = struct.unpack(f"<{count}h", frames)
            inverted = struct.pack(f"<{count}h", *[-x for x in data])
            
    with wave.open(output_path, 'wb') as wo:
        wo.setparams(params)
        wo.writeframes(inverted)
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: invertwav.py <in.wav> <out.wav>")
    else:
        invert_wav(sys.argv[1], sys.argv[2])
