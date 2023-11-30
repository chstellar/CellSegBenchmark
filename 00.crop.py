import os
import cv2
from PIL import Image
import tifffile
import numpy as np
Image.MAX_IMAGE_PIXELS = 471585296 

# Set up paths.
input_folder = "/import/home/jyubq/proj_benchmarking/dast_ss2022test/04.register"
output_folder = "/home/jyubq/proj_benchmarking/dast_ss2022test/cropped_stitched"
os.makedirs(output_folder, exist_ok=True)

# Set up patch size and stride.
patch_size = (448, 448) # Expected image size.
stride_horizontal = 224 # Horizontal stride, smaller than patch size.
stride_vertical = 224 # Vertical stride, smaller than patch size.

# Loop over all images in the input folder.
for filename in os.listdir(input_folder):
    if filename.endswith("extended.tif"):
        # Load the image.
        image_path = os.path.join(input_folder, filename)
        # image = cv2.imread(image_path) # cv2 version
        # image = Image.open(image_path) # PIL version
        image = tifffile.imread(image_path) # tifffile version

        # Calculate the number of patches we'll need.
        # height, width, _ = image.shape # cv2 version
        # width, height = image.size # PIL version
        height, width = image.shape # tifffile version
        num_rows = (height - patch_size[0]) // stride_vertical 
        num_cols = (width - patch_size[1]) // stride_horizontal

        # Loop over all patches and save them.
        for i in range(num_rows):
            # if i > 0:
            #     break
            for j in range(num_cols):
                top = i * stride_vertical
                left = j * stride_horizontal
                # Deal with most cases
                if i != num_rows - 1 and j != num_cols - 1:
                    bottom = top + patch_size[0]
                    right = left + patch_size[1]

                    # patch = image[top:bottom, left:right] # cv2 version
                    # patch = image.crop((left, top, right, bottom)) # PIL version
                    patch = image[top:bottom, left:right].astype(np.uint16) # tifffile version
                    patch_filename = f"{filename.split('.tif')[0]}_{str(i).zfill(len(str(num_rows)))}_{str(j).zfill(len(str(num_cols)))}.tif"
                    # cv2.imwrite(os.path.join(output_folder, patch_filename), patch) # cv2 version
                    # patch.save(os.path.join(output_folder, patch_filename)) # PIL version
                    tifffile.imwrite(os.path.join(output_folder, patch_filename), patch) # tifffile version
                    print(f"Successfully save patch {patch_filename}.")
                # Deal with the last column
                elif j == num_cols - 1 and i != num_rows - 1:
                    bottom = top + patch_size[0]
                    right = width

                    # patch = image[top:bottom, left:right] # cv2 version
                    # patch = image.crop((left, top, right, bottom)) # PIL version
                    patch = image[top:bottom, left:right].astype(np.uint16) # tifffile version
                    patch_filename = f"{filename.split('.tif')[0]}_{str(i).zfill(len(str(num_rows)))}_{str(j).zfill(len(str(num_cols)))}.tif"
                    # cv2.imwrite(os.path.join(output_folder, patch_filename), patch) # cv2 version
                    # patch.save(os.path.join(output_folder, patch_filename)) # PIL version
                    tifffile.imwrite(os.path.join(output_folder, patch_filename), patch) # tifffile version
                # Deal with the last row
                elif i == num_rows - 1 and j != num_cols - 1:
                    bottom = height
                    right = left + patch_size[1]

                    # patch = image[top:bottom, left:right] # cv2 version
                    # patch = image.crop((left, top, right, bottom)) # PIL version
                    patch = image[top:bottom, left:right].astype(np.uint16) # tifffile version
                    patch_filename = f"{filename.split('.tif')[0]}_{str(i).zfill(len(str(num_rows)))}_{str(j).zfill(len(str(num_cols)))}.tif"
                    # cv2.imwrite(os.path.join(output_folder, patch_filename), patch) # cv2 version
                    # patch.save(os.path.join(output_folder, patch_filename)) # PIL version
                    tifffile.imwrite(os.path.join(output_folder, patch_filename), patch) # tifffile version
                    print(f"Successfully save patch {patch_filename}.")
                # Deal with the last diagonal
                elif i == num_rows - 1 and j == num_cols - 1:
                    bottom = height
                    right = width

                    # patch = image[top:bottom, left:right] # cv2 version
                    # patch = image.crop((left, top, right, bottom)) # PIL version
                    patch = image[top:bottom, left:right].astype(np.uint16) # tifffile version
                    patch_filename = f"{filename.split('.tif')[0]}_{str(i).zfill(len(str(num_rows)))}_{str(j).zfill(len(str(num_cols)))}.tif"
                    # cv2.imwrite(os.path.join(output_folder, patch_filename), patch) # cv2 version
                    # patch.save(os.path.join(output_folder, patch_filename)) # PIL version
                    tifffile.imwrite(os.path.join(output_folder, patch_filename), patch) # tifffile version
                    print(f"Successfully save patch {patch_filename}.")
        
print("Finished cropping. Cropped images are stored at:", output_folder)

# Open the text file in write mode.
with open(os.path.join(output_folder, "parameters.txt"), 'w') as f:
    # Write the information to the text file.
    f.write(f"Patch Size: {patch_size}\n")
    f.write(f"Horizontal Stride: {stride_horizontal}\n")
    f.write(f"Vertical Stride: {stride_vertical}\n")
    # f.write(f"Image Size: ({image.shape[0]}, {image.shape[1]})\n") # cv2 version
    # f.write(f"Image Size: ({image.size[1]}, {image.size[0]})\n") # PIL version
    f.write(f"Image Size: ({image.shape[0]}, {image.shape[1]})\n") # tifffile version
    f.write(f"Number of Rows: {num_rows}\n")
    f.write(f"Number of Columns: {num_cols}\n")    

print("Metadata is stored at:", output_folder)