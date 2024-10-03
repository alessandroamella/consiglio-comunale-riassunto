import os
import argparse
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return api_key

def read_file(file_path):
    """Helper function to read the content of a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        logging.error(f"Error reading {file_path}: {str(e)}")
        raise

def read_transcriptions(directory):
    """Read all transcription files in the given directory and concatenate them."""
    transcriptions = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as f:
                transcriptions.append(f.read())
    return " ".join(transcriptions)

def generate_report(date, mandate, council, agenda, transcription):
    """Generate a report based on the transcription using Google Gemini API."""
    prompt = f"""
Di seguito vi è una trascrizione di ciò che è stato detto al Consiglio Comunale di San Cesario sul Panaro, datato {date}.
Consiglio per il mandato {mandate} (qua sono tutti i NOMI dei membri del Consiglio):
{council}
L'ordine del giorno è stato il seguente:
{agenda}

Riassumi ogni punto dell'ordine del giorno in 2-4 paragrafi, sintetizzando le discussioni emerse durante la seduta.
Il testo deve seguire un filo logico che colleghi gli argomenti trattati, eventuali emendamenti proposti e altre osservazioni, in modo che il lettore possa seguire facilmente lo svolgimento delle discussioni.
Se sono stati proposti emendamenti, descrivi il loro contenuto, il motivo e il contesto in cui sono stati proposti, insieme al loro esito.
Se sono state sollevate obiezioni o discussioni, riporta brevemente i punti principali sollevati da ciascuna parte coinvolta.
Includi solo le informazioni essenziali e rilevanti per ciascun punto, evitando dettagli superflui o ripetitivi.
Riguardante la votazione di ogni mozione, indica semplicemente se è stata approvata o respinta, senza entrare nei dettagli sui voti, sulle modalità di voto, né su chi ha votato e come.
Se possibile, includi alla fine del riassunto di ciascun punto se la proposta è stata approvata o respinta.
Stile e formato:

Il report deve essere redatto in modo da risultare chiaro e scorrevole per i cittadini, evitando termini troppo tecnici o complicati.
Assicurati che il testo sia piacevole da leggere, ma mantieni un tono professionale e accurato nei contenuti.
Il documento finale deve essere lungo tra le 3 e le 5 pagine.
Scrivi la risposta in formato Markdown, limitandoti ai riassunti dei punti all'ordine del giorno, senza aggiungere introduzioni o conclusioni.

Considerazioni sulle fonti:

Poiché la trascrizione è stata effettuata automaticamente, potrebbero esserci errori nei nomi o nei dati. NON INSERIRE NOMI O INFORMAZIONI CHE NON SIANO PRESENTI NELL'ELENCO UFFICIALE DEI MEMBRI DEL CONSIGLIO. Se un nome non è incluso nel Consiglio sopra elencato, OMETTILO dal report poiché è frutto di un errore di trascrizione.
Se alcune informazioni non sono chiare o complete, ometti i dettagli specifici e mantieni il riassunto più generico e comprensibile.


Di seguito la trascrizione:
{transcription}
"""
    
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text

def main():
    parser = argparse.ArgumentParser(description="Generate a council meeting report using Google Gemini API.")
    parser.add_argument("--transcription_dir", required=True, help="Directory containing transcription files")
    parser.add_argument("--output", default="council_report.md", help="Output file for the generated report (default: council_report.md)")
    
    # Load files from assets directory
    assets_dir = "./assets"
    date_file = os.path.join(assets_dir, "date.txt")
    mandate_file = os.path.join(assets_dir, "mandate.txt")
    council_file = os.path.join(assets_dir, "council.txt")
    agenda_file = os.path.join(assets_dir, "agenda.txt")

    args = parser.parse_args()

    try:
        genai.configure(api_key=get_api_key())

        # Read date, mandate, council, and agenda from respective files in the assets directory
        date = read_file(date_file)
        mandate = read_file(mandate_file)
        council = read_file(council_file)
        agenda = read_file(agenda_file)
        
        # Print the read data
        logging.info(f"Date: {date}")
        logging.info(f"Mandate: {mandate}")
        logging.info(f"Council: {council}")
        logging.info(f"Agenda: {agenda}")

        # Read the transcriptions from the transcription directory
        transcription = read_transcriptions(args.transcription_dir)
        logging.info("Transcriptions read successfully")

        # Generate the report
        report = generate_report(date, mandate, council, agenda, transcription)
        logging.info("Report generated successfully")

        # Write the generated report to the output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logging.info(f"Report saved to {args.output}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
