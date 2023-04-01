import sys
import random
import numpy as np
import imageio
from PIL import Image, ImageChops

# Parameters
initial_pause_duration = 2  # In seconds
min_rectangles = 10
max_rectangles = 100
maxRecurse = 5
num_frames = 2000

def offset_color_channels(img, num_rectangles, recurseDepth):
    img_width, img_height = img.size

    for _ in range(num_rectangles):
        # Generate random rectangular area
        x = random.randint(0, img_width - 1)
        y = random.randint(0, img_height - 1)
        w = random.randint(1, img_width - x)
        h = random.randint(1, img_height - y)

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
    
    if recurseDepth == 0:
        return img
    else:
        return offset_color_channels(img, num_rectangles, recurseDepth - 1)

def generate_video(input_image, output_video, num_frames):
    img = Image.open(input_image)

    # Convert the image to RGB mode if it's not already in that mode
    if img.mode != "RGB":
        img = img.convert("RGB")

    img_width, img_height = img.size
    video_writer = imageio.get_writer(output_video, fps=30, quality=9)


    # Show the original frame for the specified duration
    for _ in range(int(30 * initial_pause_duration)):
        video_writer.append_data(np.array(img))

    for frame_num in range(num_frames):
        # Linearly interpolate the number of rectangles based on the frame number
        recurseDepth = int(0 + (frame_num / (num_frames - 1)) * (maxRecurse - 0))
        num_rectangles = int(min_rectangles + (frame_num / (num_frames - 1)) * (max_rectangles - min_rectangles))
        scrambled_img = offset_color_channels(img.copy(), num_rectangles, recurseDepth)
        video_writer.append_data(np.array(scrambled_img))
    video_writer.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python color_channel_offset.py <input_image> <output_video>")
        sys.exit(1)

    input_image = sys.argv[1]
    output_video = sys.argv[2]

    generate_video(input_image, output_video, num_frames)
    print(f"Video with increasing number of color channel offsets within random rectangles saved to {output_video}")
