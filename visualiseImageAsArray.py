import os
import numpy as np
import tifffile as tiff


# Load the single-channel image and convert the image to a NumPy array
# array = np.array(tiff.imread("/home/jyubq/proj_benchmarking/dast_ss2022/73.trial/04.register/DAPI_SS200000135TL_D1_mask.tif")[15000:15000+5*448,15000:15000+5*448])
path = "/home/jyubq/proj_benchmarking/dast_ss2022/masks_test"
array = np.array(tiff.imread(os.path.join(path, "cropped_mask_DAPI_SS200000135TL_D1_regist_extended_001_000.tif")))

# Open the output file in write mode
with open(os.path.join(path, "001_000.txt"), "w") as f:
    # Iterate over the rows in the image array
    for row in array:
        # Convert each element in the row to a string and join them with tabs
        row_values = "\t".join(str(element) for element in row)
        # Write the row values to the file
        f.write(row_values + "\n")