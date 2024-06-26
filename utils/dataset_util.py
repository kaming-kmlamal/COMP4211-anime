import random
import rembg
from PIL import Image
import os
from os import listdir
import shutil
import cv2
import numpy as np

def remove_background(images_dir, output_dir):
    # images_dir: directory of images with background

    images_names = listdir(images_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for image_name in images_names:
        img_path = os.path.join(images_dir, image_name)
        output_path = os.path.join(output_dir, image_name)
        
        if os.path.exists(output_path):
            continue
        
        input = Image.open(img_path)
        input_without_bg = rembg.remove(input)

        white_mask = Image.new("RGBA", input.size, "WHITE")
        white_mask.paste(input_without_bg, mask=input_without_bg)
        
        output = white_mask
        output = output.convert('RGB')

        output.save(output_path)

def combine_edges(images_dir, combined_dir, img_channel=3, img_size=256):
    

    def merge(edges, original_img):
        blank_space = 12
        combined_img = np.zeros((edges.shape[0], edges.shape[1]*2 + blank_space, img_channel))
        combined_img[:, edges.shape[1]:edges.shape[1]+blank_space, :] = 255

        combined_img[:, 0:edges.shape[1], :] = edges
        combined_img[:, edges.shape[1]+blank_space : (edges.shape[1]*2)+blank_space, :] = original_img

        return combined_img

    if not os.path.exists(combined_dir):
        os.makedirs(combined_dir)

    folders = listdir(images_dir)

    cnt =0
    for folder in folders:
        folder_path = os.path.join(images_dir, folder)
        for i, img_name in enumerate(listdir(folder_path)):
            if i == 30:
                break
            img_path = os.path.join(folder_path, img_name)
            output_path2 = os.path.join(combined_dir, str(cnt) + "_combined.jpg")

            input = Image.open(img_path)
        
            new_image =input.resize((img_size,img_size))
            img = np.array(new_image)
            img_diff = np.ones(img.shape) * 255 - img
            img_diff = np.uint8(img_diff)

            new_im = img_diff.copy()
            
            edges = cv2.Canny(image=new_im, threshold1=90, threshold2=230)  # Canny Edge Detection
            edges = np.ones(edges.shape) * 255 - edges
            edges = np.uint8(edges)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            rgb = img[...,::-1].copy()

            if rgb.size != 196608:
                print (img_path,img_name)
                print(edges.size , rgb.size)
                continue
            combined = merge(edges, rgb)
            cv2.imwrite(output_path2, combined)
            cnt = cnt +1


def train_valid_test_split(images_dir,dataset_dir, train=0.8, valid=0.1, test=0.1):
    images_names = os.listdir(images_dir)
    random.shuffle(images_names)
    num_images = len(images_names)

    num_train = num_images*train
    num_valid = num_images*valid
    num_test = num_images-num_train-num_valid

    train_dir = os.path.join(dataset_dir, "train")
    valid_dir = os.path.join(dataset_dir, "valid")
    test_dir = os.path.join(dataset_dir, "test")

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(valid_dir):
        os.makedirs(valid_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    i = 0
    while i < num_train:
        img_name = images_names[i]
        src = os.path.join(images_dir, img_name)
        dst = os.path.join(train_dir, img_name)
        shutil.copy2(src, dst)
        i += 1

    while i < num_train+num_valid:
        img_name = images_names[i]
        src = os.path.join(images_dir, img_name)
        dst = os.path.join(valid_dir, img_name)
        shutil.copy2(src, dst)
        i += 1

    while i < num_train+num_valid+num_test:
        img_name = images_names[i]
        src = os.path.join(images_dir, img_name)
        dst = os.path.join(test_dir, img_name)
        shutil.copy2(src, dst)
        i += 1

def denormalization(image):
    return image/2 + 0.5
