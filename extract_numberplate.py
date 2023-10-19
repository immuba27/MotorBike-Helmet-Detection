import schedule
import time
import os
import requests
import mysql.connector
import datetime
import shutil  # Added for file moving

import logging

# Configuring logging
logging.basicConfig(filename='extract_numberplate.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def my_job():
    print("Job is running...")  # Replace this with the code you want to execute
    # Set your PlateRecognizer API token here
    api_token = 'eea3f25dd03596bb429aab3de722fa70f83b0ef7'

    # Define the folder containing the images
    image_folder = 'number_plates/'

    # Define the regions (change to your country)
    regions = ['gb', 'it']

    # Define the folder for updated images
    updated_image_folder = 'number_plates_updated/'

    # MySQL database configuration
    db_config = {
        'user': 'mubarak',
        'password': '1234',
        'host': 'localhost',
        'database': 'motorbike'
    }

    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Iterate over the files in the folder
    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(image_folder, filename)

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

                # Get the current datetime as a string
                current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Check if the license plate number already exists in the database
                check_query = "SELECT * FROM numberplatedetection WHERE number_plate = %s"
                check_data = (plate_text,)
                cursor.execute(check_query, check_data)
                existing_record = cursor.fetchone()

                if not existing_record:
                    # Insert the extracted text into the MySQL database table
                    insert_query = "INSERT INTO numberplatedetection (datetime, violation_type, number_plate) VALUES (%s, %s, %s)"
                    insert_data = (current_datetime, 'Helmet-less', plate_text)
                    cursor.execute(insert_query, insert_data)
                    connection.commit()

                    print(f'Image: {filename}, Plate Text: {plate_text} (Inserted into MySQL)')
                    logging.info(f'Image: {filename}, Plate Text: {plate_text} (Inserted into MySQL)')

                    current_date = datetime.datetime.now().strftime('%Y-%m-%d')

                    # Rename the image file with extracted text and move it to the updated folder
                    new_filename = f'{plate_text}_{current_date}.jpg'
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

# Schedule the job to run every 5 minutes
# schedule.every(1).minutes.do(my_job)

# Run the scheduler
# while True:
#     schedule.run_pending()
#     time.sleep(1)  # Sleep for 1 second to avoid high CPU usage