import os
import json
import shutil
import subprocess


def get_dims(file_path):
    with open(file_path, 'rb') as f:
        # Read the first two bytes
        f.read(2)
        # Read the next byte to find the start of the image
        byte = f.read(1)
        while byte != b'\xff':
            byte = f.read(1)
        # Read the next byte to find the marker
        byte = f.read(1)
        while byte != b'\xc0' and byte != b'\xc2':
            # Skip the segment length
            f.read(1)
            byte = f.read(1)
        # Read the next two bytes for height and width
        f.read(1)  # Skip the precision byte
        height = int.from_bytes(f.read(2), 'big')
        width = int.from_bytes(f.read(2), 'big')
        return float(width), float(height)

with open(f"annotation.json", 'r') as f:
    books = json.load(f)


file_path = os.getcwd()
training_path = f"{file_path}/train"
validation_path = f"{file_path}/val"

page_count = 0
for book in books:
    for page in book["pages"]:
        page_count += 1
        
val_thresh = int(page_count * 0.8)


image_id = 1
for book in books:
    for page in book["pages"]:        
        image_name = ""
        file_name = ""

        copy_image_path = ""
        copy_file_path = ""
        if image_id < val_thresh:
            image_name = f"images{image_id}.jpg"
            file_name = f"images{image_id}.txt"

            copy_image_path = f"{training_path}/images/{image_name}"
            copy_file_path = f"{training_path}/labels/{file_name}"
        elif image_id >= val_thresh:
            image_name = f"images_val{image_id}.jpg"
            file_name = f"images_val{image_id}.txt"

            copy_image_path = f"{validation_path}/images/{image_name}"
            copy_file_path = f"{validation_path}/labels/{file_name}"
            
            
        shutil.copyfile(page["image_paths"]["ja"], copy_image_path)
        
        width, height = get_dims(copy_image_path)
        # class id with 0 is for a frame, and class id for 1 is a bounding box
        with open(copy_file_path, 'w') as file:
            class_id = 0
            for frame in page["frame"]:                
                file.write(f"{class_id} {frame['x']/width:.3f} {frame['y']/height:.3f} {frame['w']/width:.3f} {frame['h']/height:.3f}\n")
                class_id = 1
            
            for text in page["text"]:
                file.write(f"{class_id} {text['x']/width:.3f} {text['y']/height:.3f} {text['w']/width:.3f} {text['h']/height:.3f}\n")

        image_id += 1
