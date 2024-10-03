import os
import math
import logging
import argparse
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def split_mp3(input_file, output_dir, max_size_mb=25):
    if not os.path.exists(input_file):
        logging.error(f"Error: File '{input_file}' not found.")
        return []

    logging.info(f"Loading audio file: {input_file}")
    audio = AudioSegment.from_mp3(input_file)

    max_size_bytes = max_size_mb * 1024 * 1024
    logging.info(f"Target size per part: {max_size_mb} MB ({max_size_bytes} bytes)")

    base_name = os.path.splitext(os.path.basename(input_file))[0]

    bytes_per_ms = (audio.frame_rate * audio.sample_width * audio.channels) / 8000
    ms_per_chunk = math.floor(max_size_bytes / bytes_per_ms)

    logging.info(f"Audio duration: {len(audio)} ms")
    logging.info(f"Calculated chunk duration: {ms_per_chunk} ms")

    output_files = []
    start = 0
    part = 1

    while start < len(audio):
        end = min(start + ms_per_chunk, len(audio))
        
        chunk = audio[start:end]
        
        output_filename = os.path.join(output_dir, f"{base_name}_part{part:03d}.mp3")
        
        logging.info(f"Exporting chunk {part}: {start} ms to {end} ms")
        chunk.export(output_filename, format="mp3")
        
        chunk_size = os.path.getsize(output_filename)
        logging.info(f"Created: {output_filename} (Size: {chunk_size/1024/1024:.2f} MB)")

        output_files.append(output_filename)
        start = end
        part += 1

    logging.info("Splitting complete. Check the output files.")
    return output_files

def main():
    parser = argparse.ArgumentParser(description="Split large MP3 file into smaller parts.")
    parser.add_argument("input_file", help="Path to the input MP3 file")
    parser.add_argument("-o", "--output_dir", default="./mp3_parts", help="Directory to store the MP3 parts (default: ./mp3_parts)")
    parser.add_argument("-s", "--max_size", type=int, default=25, help="Maximum size of each part in MB (default: 25)")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    split_mp3(args.input_file, args.output_dir, args.max_size)

if __name__ == "__main__":
    main()