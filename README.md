# Monitor Helmet Usage and Passenger Compliance for Motorbike Riders using Computer Vision

This is project is extracting motorcycle license plates if the rider or passenger is not wearing a helmet.

This project is using YOLOV5 algorithm to detect the rider, licence plate and riders head. And classify wheather the rider is wearing a helmet or not. If not wearing a helmet then, it will save the licence plate number in a seperate folder, and also will capture rider image in a separate folder. After every 5min via a scheduler number plate images will convert to text and store violation data in a database table. Image will then renamed to to number plate text and moved to a different folder. From storing to renaming and moving to deleting will be captured on a log file.

<img
src="./output.gif"
/>


M.M.M Mubarak
BSc in Data Science | Batch 3