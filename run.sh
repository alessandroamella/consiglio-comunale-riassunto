#!/bin/bash

# Check if input files are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <input_audio.mp3> <input_pdf.pdf>"
    exit 1
fi

input_audio="$1"
input_pdf="$2"
mp3_parts_dir="./mp3_parts"
transcriptions_dir="./transcriptions"
ocr_output="ocr_output.txt"
final_report="council_report.md"

# Run PDF OCR
echo "Performing OCR on PDF..."
python pdf_ocr.py "$input_pdf" -o "$ocr_output"

# Check if OCR was successful
if [ $? -ne 0 ]; then
    echo "Error: PDF OCR failed"
    exit 1
fi

# Extract information from OCR output
date=$(grep -oP 'Data: \K.*' "$ocr_output")
mandate=$(grep -oP 'Mandato: \K.*' "$ocr_output")
council=$(sed -n '/Composizione del Consiglio:/,/Ordine del giorno:/p' "$ocr_output" | sed '1d;$d')
agenda=$(sed -n '/Ordine del giorno:/,/$/p' "$ocr_output" | sed '1d')

# Run MP3 splitter
echo "Splitting MP3 file..."
python mp3_splitter.py "$input_audio" -o "$mp3_parts_dir"

# Check if MP3 splitter was successful
if [ $? -ne 0 ]; then
    echo "Error: MP3 splitting failed"
    exit 1
fi

# Run speech-to-text
echo "Transcribing audio files..."
python speech_to_text.py -i "$mp3_parts_dir" -o "$transcriptions_dir"

# Check if speech-to-text was successful
if [ $? -ne 0 ]; then
    echo "Error: Transcription failed"
    exit 1
fi

# Generate report using Gemini
echo "Generating report..."
python generate_council_report.py --date "$date" --mandate "$mandate" --council "$council" --agenda "$agenda" --transcription_dir "$transcriptions_dir" --output "$final_report"

# Check if report generation was successful
if [ $? -ne 0 ]; then
    echo "Error: Report generation failed"
    exit 1
fi

echo "Process completed successfully. Final report saved as $final_report"