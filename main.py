from crewai import Crew
from textwrap import dedent
from agents import CustomAgents
from tasks import CustomTasks
from fpdf import FPDF
import os
from dotenv import load_dotenv
import requests
from serpapi import GoogleSearch
import re
from colorama import Fore, Style
import subprocess
from PIL import Image
load_dotenv()
 
def search_unsplash(query):
    """Searches Unsplash for images related to the given query."""
    params = {
        "engine": "google_images",
        "q": query,
        "api_key": os.environ["SERPAPI_API_KEY"]
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "images_results" in results:
        image_url = results["images_results"][0]["original"]
    else:
        print("No images found for the given query.")
        return ""

    # Get the file extension from the URL, default to .jpg if none found
    file_extension = os.path.splitext(image_url)[1]
    if not file_extension:
        file_extension = '.jpg'  # Default extension
    
    # Ensure the extension is one of the supported types
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if file_extension.lower() not in supported_extensions:
        file_extension = '.jpg'  # Default to jpg if unsupported extension

    words = query.split()[:5]
    safe_words = [re.sub(r'[^a-zA-Z0-9_]', '', word) for word in words]
    filename = "_".join(safe_words).lower() + file_extension
    filepath = os.path.join(os.getcwd(), "images", filename)

    # Create the 'images' directory if it doesn't exist
    images_dir = os.path.join(os.getcwd(), "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        # Add permission check
        os.chmod(images_dir, 0o777)  # Give full permissions to the directory

    # Download the image
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        os.chmod(filepath, 0o666)  # Give read/write permissions to the file
        print(f"Image downloaded successfully: {filepath}")
    else:
        print("Failed to download the image.")
        return ""

    return filepath
 
# Add image validation and conversion function
def ensure_valid_jpeg(image_path):
    try:
        # Try to open the image with PIL
        img = Image.open(image_path)
        
        # If image is not JPEG, convert it
        if img.format != 'JPEG':
            jpeg_path = os.path.splitext(image_path)[0] + '_converted.jpg'
            # Convert to RGB mode if necessary (in case of PNG with transparency)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            img = img.convert('RGB')
            img.save(jpeg_path, 'JPEG', quality=95)
            return jpeg_path
        return image_path
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return None

class CustomCrew:
    def __init__(self, topic, preference):
        self.topic = topic
        self.preference = preference
 
    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = CustomAgents()
        tasks = CustomTasks()
 
        # Define your custom agents
        note_generation_agent = agents.note_generation_agent()
        data_agent = agents.data_agent()
        image_agent = agents.image_agent()
        structure_agent = agents.Structure_agent()
        pdf_agent = agents.pdf_agent()
 
        # Define your custom tasks
        data_task = tasks.generate_notes_task(data_agent, self.topic, self.preference)
        image_task = tasks.search_images_task(image_agent, self.topic, data_task)
        structuring_task = tasks.structure_content_task(structure_agent, data_task)
        pdf_task = tasks.generate_pdf_task(pdf_agent, structuring_task)
 
        # Define your custom crew
        crew = Crew(
            agents=[note_generation_agent, data_agent, structure_agent, pdf_agent],
            tasks=[data_task,structuring_task, pdf_task],
            verbose=True,
        )
        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print(Fore.CYAN + r"""
________                    _______            __               _____   .___ 
\_____  \    ____    ____   \      \    ____ _/  |_   ____     /  _  \  |   |
 /   |   \  /    \ _/ __ \  /   |   \  /  _ \\   __\_/ __ \   /  /_\  \ |   |
/    |    \|   |  \\  ___/ /    |    \(  <_> )|  |  \  ___/  /    |    \|   |
\_______  /|___|  / \___  >\____|__  / \____/ |__|   \___  > \____|__  /|___|
        \/      \/      \/         \/                    \/          \/      
 
 
""" + Style.RESET_ALL)
 
 
 
    print(Fore.CYAN + "\n-------------------------------")
    import sys

    if len(sys.argv) > 1:
        topic = "docker"
    else:
        topic = input(Fore.YELLOW + dedent("""Enter the topic for which you want to generate notes: """) + Style.RESET_ALL)
    preference = input(Fore.YELLOW + dedent("""Enter the preferred length of notes (short or long): """) + Style.RESET_ALL)
    custom_crew = CustomCrew(topic, preference)
    result = custom_crew.run()
 
    print(Fore.GREEN + "\n\n########################")
    print(Fore.GREEN + "## Here is your custom crew run result:")
    print(Fore.GREEN + "########################\n")
    print(Fore.CYAN + result + Style.RESET_ALL)
    print("########################\n")
    print(result)
    # Create the PDF file
# Create the PDF file
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
 
# Add the result to the PDF
result_lines = result.split("\n\n")
image_path = search_unsplash(topic)
last_line = 0
 
for i, line in enumerate(result_lines):
    pdf.multi_cell(0, 10, txt=line)
    if i == len(result_lines) - 1:  # If this is the last paragraph
        last_line = pdf.get_y()  # Get the y-coordinate of the last line
 
    pdf.cell(0, 10, txt="", ln=1)  # Add some vertical spacing between paragraphs
 
try:
    # Convert/validate image before adding to PDF
    valid_image_path = ensure_valid_jpeg(image_path)
    if valid_image_path:
        pdf.image(valid_image_path, x=10, y=last_line + pdf.font_size * 1.2, w=130)
    else:
        print(f"Skipping invalid image: {image_path}")
except Exception as e:
    print(f"Error adding image to PDF: {str(e)}")
    # Continue with the rest of the PDF generation

# Create the 'pdf' directory if it doesn't exist
pdf_dir = "pdf"
if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)
 
# Save the PDF file
pdf_file_path = os.path.join(pdf_dir, f"notes_{topic.replace(' ', '_')}.pdf")
pdf.output(pdf_file_path, 'F')
print(f"\n\033[1;34mPDF file created: {pdf_file_path}\033[0m")
 
#Open the PDF file
if os.name == 'nt':  # Windows
    os.startfile(pdf_file_path)
else:  # Unix-based systems (macOS, Linux)
  subprocess.call(['xdg-open', pdf_file_path])
