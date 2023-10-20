# import schedule
import time
import os
import requests
import mysql.connector
import datetime
import shutil
import logging

# Configuring logging
logging.basicConfig(filename='extract_numberplate.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def my_job():
    print("Job is running...")  # Replace this with the code you want to execute
    # Setting your PlateRecognizer API token here
    api_token = 'eea3f25dd03596bb429aab3de722fa70f83b0ef7'

    # Defining the folder containing the images
    image_folder = 'number_plates/'

    # Defining the regions (change to your country)
    regions = ['gb', 'it']

    # Defining the folder for updated images
    updated_image_folder = 'number_plates_updated/'

    # MySQL database configuration
    db_config = {
        'user': 'mubarak',
        'password': '1234',
        'host': 'localhost',
        'database': 'motorbike'
    }

    # Establishing a connection to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Iterating over the files in the folder
    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(image_folder, filename)

            # Extracting the file prefix
            file_prefix = filename.split('_')[0]

            # Setting default violation type
            violation_type = 'Unknown Violation'

            if file_prefix == 'nohelmet':
                violation_type = 'No-Helmet Detection'
            elif file_prefix == 'triples':
                violation_type = 'Triples Detected'

            with open(image_path, 'rb') as fp:
                response = requests.post(
                    'https://api.platerecognizer.com/v1/plate-reader/',
                    data={'regions': regions},
                    files={'upload': fp},
                    headers={'Authorization': f'Token {api_token}'}
                )

            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                plate_text = data['results'][0]['plate']
                plate_text = str(plate_text).upper()

                # Getting the current datetime as a string
                current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Checking if the license plate number already exists in the database
                check_query = "SELECT * FROM numberplatedetection WHERE number_plate = %s"
                check_data = (plate_text,)
                cursor.execute(check_query, check_data)
                existing_record = cursor.fetchone()

                if not existing_record:
                    # Inserting the extracted text into the MySQL database table
                    insert_query = "INSERT INTO numberplatedetection (datetime, violation_type, number_plate) VALUES (%s, %s, %s)"
                    insert_data = (current_datetime, violation_type, plate_text)
                    cursor.execute(insert_query, insert_data)
                    connection.commit()

                    print(f'Image: {filename}, Plate Text: {plate_text} (Inserted into MySQL)')
                    logging.info(f'Image: {filename}, Plate Text: {plate_text} (Inserted into MySQL)')

                    current_date = datetime.datetime.now().strftime('%Y-%m-%d')

                    # Renaming the image file with extracted text and move it to the updated folder
                    new_filename = f'{file_prefix}_{plate_text}_{current_date}.jpg'
                    new_image_path = os.path.join(updated_image_folder, new_filename)
                    shutil.move(image_path, new_image_path)
                    logging.info(f"File '{filename}' removed successfully.")

                else:
                    print(f'Image: {filename}, Plate Text: {plate_text} already exists in the database')
                    logging.warning(f'Image: {filename}, Plate Text: {plate_text} already exists in the database')

                    file_path = os.path.join(image_folder, filename)
                    try:
                        os.remove(file_path)
                        print(f"File '{filename}' removed successfully.")
                        logging.info(f"File '{filename}' removed successfully.")

                    except OSError as e:
                        print(f"Error: {e} - {file_path}")
                        logging.error(f"Error: {e} - {file_path}")
            else:
                print(f'Image: {filename}, No plate detected')
                logging.info(f"File '{filename}' No plate detected.")


    # Close the database connection
    cursor.close()
    connection.close()
    print("Job is completed...")
