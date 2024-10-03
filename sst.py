import os
import logging
import argparse
import time  # For introducing a delay between requests
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return api_key

def read_file(file_path):
    """Helper function to read content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        logging.error(f"Error reading {file_path}: {str(e)}")
        return None

def transcribe_audio(file_path, client, council_text, agenda_text):
    logging.info(f"Transcribing: {file_path}")
    
    # Create the transcription prompt with council members and agenda
    prompt = f"""
Trascrivi il contenuto dell'audio della seduta del Consiglio Comunale di San Cesario, composto da:
{council_text}

Ordine del giorno:
{agenda_text}
"""

    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="it",
                prompt=prompt
            )
        return transcription.text
    except Exception as e:
        logging.error(f"Error transcribing {file_path}: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Transcribe MP3 files to text using OpenAI API.")
    parser.add_argument("-i", "--input_dir", default="./mp3_parts", help="Directory containing MP3 files to transcribe (default: ./mp3_parts)")
    parser.add_argument("-o", "--output_dir", default="./transcriptions", help="Directory to store transcriptions (default: ./transcriptions)")
    parser.add_argument("-c", "--council_file", default="./assets/council.txt", help="File containing council members list (default: ./assets/council.txt)")
    parser.add_argument("-a", "--agenda_file", default="./assets/agenda.txt", help="File containing agenda (default: ./assets/agenda.txt)")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    client = OpenAI(api_key=get_api_key())

    # Read the council members list and agenda from files
    council_text = read_file(args.council_file)
    agenda_text = read_file(args.agenda_file)

    if not council_text or not agenda_text:
        logging.error("Council members or agenda file could not be read. Exiting.")
        return

    for filename in os.listdir(args.input_dir):
        if filename.endswith(".mp3"):
            input_path = os.path.join(args.input_dir, filename)
            output_path = os.path.join(args.output_dir, f"{os.path.splitext(filename)[0]}.txt")
            
            transcription = transcribe_audio(input_path, client, council_text, agenda_text)
            if transcription:
                with open(output_path, 'w') as f:
                    f.write(transcription)
                logging.info(f"Transcription saved to: {output_path}")
            else:
                logging.warning(f"Failed to transcribe {filename}")

            # Wait for 5 seconds before processing the next file
            time.sleep(5)

if __name__ == "__main__":
    main()
