
# Realtime-DWLS
Detection - Warning - Logging - Scraping

An application utilizing PyTorch with YOLOv5 and cv2 to process video input in real time  
and perform detections in realtime.

This project was developed as a result of my bachelor thesis where the goal was to  
develop a  program to detect and warn against game in vicinity of public roads.

The application uses a PyTorch and a custom trained YOLOv5s model to accuratly detect  
game based on video input. Video data for GUI is processed with cv2.

A simple MQTT messaging client is used to send information about warnings to remote  
units, which makes the application able to run in two configurations where you can  
process the input locally or remotly.




## Authors

- [@jwlei](https://github.com/jwlei)

## Badges

[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)


## Demo

![Demo](https://github.com/jwlei/real-time-object-detection-YOLOv5-cv2/blob/master/Realtime-dwls/resources/media/demo.gif)
## Installation

Clone the project

```bash
git clone https://github.com/jwlei/real-time-object-detection-YOLOv5-cv2
```

Go to the project directory

```bash
cd my-project/Realtime-DWLS
```

Optional: Create and activate a virtual environment
```bash
python -m venv name_environment
```
```bash
name_environment\Scripts\activate.bat
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install PyTorch for your version, supplied is for Python 3.10:

* CUDA
```bash
pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu113
```

* Non-CUDA
```bash
pip install torch torchvision
```

## Run Locally

Run the main application

```bash
python main.py
```

External MQTT Subscriber with a simple warning GUI
```bash
python external_mqtt/ext_mqtt_subscriber.py
```

External MQTT Publisher which can supply an URL for a model for the main application to download
```
python external_mqtt/ext_mqtt_publisher.py http://url.to/yourmodel.pt
```
## Features

- Video input from remote URL, Local camera or local media file
- Local or remote processing and warning independetly
- Can push new YOLOv5 model from remote by supplying an URL in a message
- Can run headlessly
- Can scrape images of detections at user defined interval
- Downloads remote model on first startup
- Customizable configuration
    - Resize video output
    - Run with setup or straight from configuration
    - Set default video/model and remote model source
    - Save images on detection, with user defined interval
    - User defined confidence threshold at which detections are made
    - Run headlessly or with GUI


## License

[MIT](https://choosealicense.com/licenses/mit/)

