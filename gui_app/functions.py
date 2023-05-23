import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import threading
from classes import PDF
from analyzer import analyze
from matplotlib import pyplot as plt
import os

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


def get_df_from_csv(input):

    # We read the csv file Fecha,Hora,Usuario,Mensaje,polarity,neg,neu,pos
    df = pd.read_csv(input, sep=',', names=['Fecha', 'Hora', 'Usuario', 'Mensaje', 'polarity', 'neg', 'neu', 'pos'], encoding='utf-8', header=None)

    return df

def get_pdf(input):

    # df = get_df_from_csv('../chats/chat_sentiment.csv')
    # df['polarity'] = pd.to_numeric(df['polarity'], errors='coerce')

    df = analyze(input)

    # We get the number of messages per user
    number_of_messages = df.groupby('Usuario')['Mensaje'].count()
    print(number_of_messages)

    # Create a PDF object
    pdf = PDF()

    # Set the title of the document
    pdf.set_title('Whatsapp Analysis')

    # Add a new page
    pdf.add_page()

    # Set the font and size for the main content
    pdf.set_font('Times', '', 11)

    # We get the most positive and negative users
    users_polarity = df.groupby('Usuario')['polarity'].mean()
    most_positive_user = users_polarity.idxmax()
    second_most_positive_user = users_polarity.drop(most_positive_user).idxmax()
    third_most_positive_user = users_polarity.drop([most_positive_user, second_most_positive_user]).idxmax()

    # We draw a rectangle
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(20, 25, 180, 80, 'DF')

    pdf.set_y(25)
    pdf.set_font('Times', '', 16)
    pdf.cell(0, 10, 'Usuarios más positivos', 0, 1, 'C')


    pdf.image('assets/medal_1.png', x=25, y=35, w=50)
    pdf.set_font('Arial', 'B', 24)
    pdf.set_xy(80, 50)
    pdf.cell(0, 10, most_positive_user, 0, 1, 'L')

    pdf.image('assets/medal_2.png', x=130, y=35, w=25)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_xy(155, 45)
    pdf.cell(0, 10, second_most_positive_user, 0, 1, 'L')

    pdf.image('assets/medal_3.png', x=130, y=65, w=25)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_xy(155, 75)
    pdf.cell(0, 10, third_most_positive_user, 0, 1, 'L')


    # We make a bar plot with the number of messages per user
    plt.bar(number_of_messages.index, number_of_messages.values)
    plt.xticks(rotation=45)
    plt.title('Número de mensajes por usuario')
    plt.savefig('number_of_messages.png')
    pdf.image('number_of_messages.png', x=10, y=120, w=100)

    # We make a pie plot with the number of messages per user
    plt.clf()
    plt.pie(number_of_messages.values, labels=number_of_messages.index, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('Porcentaje de mensajes por usuario')
    plt.savefig('number_of_messages_pie.png')
    pdf.image('number_of_messages_pie.png', x=10, y=202, w=100)

    # We make a histogram with the activity per hour in the day, in intervals of 0.1 hours
    df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M', errors='coerce')
    df['Hora'] = df['Hora'].dt.hour + df['Hora'].dt.minute/60

    plt.clf()
    plt.hist(df['Hora'], bins=24*6)
    plt.xlabel('Hora')
    plt.ylabel('Mensajes')
    plt.title('Actividad por hora')
    plt.savefig('activity_per_hour.png')
    pdf.image('activity_per_hour.png', x=110, y=120, w=100)

    # We make a histogram with the activity per day of the week
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%m/%d/%y', errors='coerce')
    df['Dia'] = df['Fecha'].dt.dayofweek

    plt.clf()
    plt.hist(df['Dia'], bins=7)
    plt.xlabel('Día')
    plt.ylabel('Mensajes')
    plt.title('Actividad por día de la semana')
    plt.xticks([0,1,2,3,4,5,6], ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
    plt.savefig('activity_per_day.png')
    pdf.image('activity_per_day.png', x=110, y=202, w=100)

    pdf.set_y(110)
    pdf.set_font('Times', '', 16)
    pdf.cell(0, 10, 'Estadísticas', 0, 1, 'C')

    # Generate the PDF file
    pdf.output('my_document.pdf', 'F')

    # we remove the images
    os.remove('number_of_messages.png')
    os.remove('number_of_messages_pie.png')
    os.remove('activity_per_hour.png')
    os.remove('activity_per_day.png')

    print("PDF generated successfully!")

