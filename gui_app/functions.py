import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import pandas as pd
import threading

from classes import PDF

from analyzer import analyze

def create_gui():
    def process_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            # Show loading label and progress bar
            loading_label.config(text="Procesando...", font=("Arial", 14))
            progress_bar.start()

            print("File selected:", file_path)
            
            # Process the file in a separate thread
            thread = threading.Thread(target=get_pdf, args=(file_path,))

            # Start the thread
            thread.start()

            # wait for the thread to finish
            while thread.is_alive():
                root.update()
                continue

            # Complete the processing
            complete_processing()

    def complete_processing():
        # Hide loading label and progress bar
        loading_label.config(text="Listo!", font=("Arial", 14))
        progress_bar.stop()

    root = tk.Tk()
    root.title("Analizador de Whatsapp")

    # Configure the window size and position
    window_width = 400
    window_height = 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Configure the window background color
    root.configure(bg="#128C7E")

    # Create a label for the title
    title_label = tk.Label(root, text="Analizador de Whatsapp", font=("Arial", 16), bg="#128C7E", fg="white")
    title_label.pack(pady=20)

    # Create a button with custom styling
    select_button = tk.Button(root, text="Seleccionar Archivo .txt", font=("Arial", 14), padx=10, pady=5, bg="#075E54", fg="white", command=process_file)
    select_button.pack()

    # Create a label for the loading status
    loading_label = tk.Label(root, text="", font=("Arial", 14), bg="#128C7E", fg="white")
    loading_label.pack(pady=10)

    # Create a progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.pack(pady=10)

    root.mainloop()

def get_pdf(input):

    df = analyze(input)

    # We get the number of messages per user
    number_of_messages = df.groupby('Usuario')['Mensaje'].count()

    # Create a PDF object
    pdf = PDF()

    # Set the title of the document
    pdf.set_title('My Document')

    # Add a new page
    pdf.add_page()

    # Set the font and size for the main content
    pdf.set_font('Arial', '', 12)

    # Write content to the PDF
    pdf.chapter_title('Whastapp Analysis')
    pdf.chapter_body(number_of_messages.to_string())

    # Generate the PDF file
    pdf.output('my_document.pdf', 'F')

    print("PDF generated successfully!")

