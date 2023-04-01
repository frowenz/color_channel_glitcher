import sys
import random
import numpy as np
import imageio
from PIL import Image, ImageChops, ImageOps
import math

# Parameters
original = None # global variable to store the original image
initial_pause_duration = 0.1  # In seconds
min_rectangles = 1
max_rectangles = 50
maxRecurse = 3
num_frames = 1800

# Divide this number be 10 to get the actual probability percentage
permanent_glitch_probability = 1  

def offset_color_channels(img, num_rectangles, recurseDepth, completion):
    img_width, img_height = img.size
    global original

    if completion == 0:
        return img

    x_max = math.ceil(completion * (img_width - 1))
    y_max = math.ceil(completion * (img_height - 1))

    for _ in range(num_rectangles):
        # Generate random rectangular area›
        x = random.randint(0, img_width - 1)
        y = random.randint(0, img_height - 1)

        w = random.randint(1, x_max)
        h = random.randint(1, y_max)

        # Crop the rectangular area from the image
        img_crop = img.crop((x, y, x + w, y + h))

        # Split the cropped image into color channels
        r, g, b = img_crop.split()

        # Apply random offsets to a randomly chosen color channel within the cropped area
        chosen_channel = random.choice(['r', 'g', 'b'])
        if chosen_channel == 'r':
            r_offset = random.randint(-w, w)
            r = ImageChops.offset(r, r_offset, 0)
        elif chosen_channel == 'g':
            g_offset = random.randint(-w, w)
            g = ImageChops.offset(g, g_offset, 0)
        else:
            b_offset = random.randint(-w, w)
            b = ImageChops.offset(b, b_offset, 0)

        # Merge the color channels back into a single image
        img_offset = Image.merge("RGB", (r, g, b))

        # Paste the offset image back onto the original image
        img.paste(img_offset, (x, y))

        # Make glitch permanent based on the probability
        if random.randint(1, 1000) <= permanent_glitch_probability:
            original.paste(img_offset, (x, y))

        img.paste(img_offset, (x, y))

        # Ensure x and y are within the image bounds
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))

    if recurseDepth == 0:
        if (int(completion * num_frames)) % 100 == 0: 
            print("\rCompletion: {:.2f}%".format(completion * 100), end='', flush=True)
        else:
            print("here")
        return img
    else:
        return offset_color_channels(img, num_rectangles, recurseDepth - 1, completion)

def generate_video(input_image, num_frames):
    global original
    original = Image.open(input_image)

    output_video = input_image.replace('.png', '.mp4')

    # Convert the image to RGB
    original = original.convert("RGB")

    # Pad the image so that its dimensions are divisible by 2
    img_width, img_height = original.size
    pad_width = img_width + (2 - img_width % 2) % 2
    pad_height = img_height + (2 - img_height % 2) % 2
    original = ImageOps.expand(original, (0, 0, pad_width - img_width, pad_height - img_height), fill=0)

    # Generates a corner variable of the form [0,0] or [1,1] or [0,1] or [1,0]
    corner = [random.randint(0,1), random.randint(0,1)]
    
    # video_writer = imageio.get_writer(output_video, fps=30, quality=9)
    video_writer = imageio.get_writer(output_video, fps=30, quality=9, macro_block_size=1)

    # Show the original frame for the specified duration
    for _ in range(int(30 * initial_pause_duration)):
        video_writer.append_data(np.array(original))

    for frame_num in range(num_frames):
        # Linearly interpolate the number of rectangles based on the frame number
        completion = frame_num / (num_frames - 1)
        recurseDepth = int((0 + completion) * (maxRecurse - 0))
        num_rectangles = int((min_rectangles + completion) * (max_rectangles - min_rectangles))
        scrambled_img = offset_color_channels(original.copy(), num_rectangles, recurseDepth, completion)
        video_writer.append_data(np.array(scrambled_img))
    video_writer.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python color_channel_offset.py <input_image>")
        sys.exit(1)

    input_image = sys.argv[1]
    generate_video(input_image, num_frames)

