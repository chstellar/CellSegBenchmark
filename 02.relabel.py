import cv2
import os
import numpy as np
import tifffile as tiff

input_path = "/home/jyubq/proj_benchmarking/dast_ss2022test/masks_stitched"
input_file = "stitched_cellpose.tif"
output_path = "/home/jyubq/proj_benchmarking/dast_ss2022test/masks_stitched"
output_file = "relabelled_cellpose.tif"

mask = tiff.imread(os.path.join(input_path, input_file)).astype(np.uint8)
totalcount, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=4) # This works only for uint8 images

# # For visualisation
# for i in [223 - 15, 223 + 15, 447 - 15, 447 + 15, 671 - 15, 671 + 15]:
#     labels[:,i] = 255
#     labels[i,:] = 255
# tiff.imwrite(os.path.join(output_path, f"labelled.tif"), labels.astype(np.uint8))

relabelled = np.zeros(mask.shape, dtype=np.uint32)
count = 0
label_dict = {}

print("For loop started")

for i in range(0, totalcount):
    if i != 0:
        precmp = list(np.argwhere(labels[stats[i][1]:stats[i][1]+stats[i][3], stats[i][0]:stats[i][0]+stats[i][2]] == i))
        # print("precmp coordinates:")
        # print(list(precmp))
        
        # # Extract the coordinates of the pixels that belong to the connected component
        # cc_coords = np.where(labels[stats[i][1]:stats[i][1]+stats[i][3], stats[i][0]:stats[i][0]+stats[i][2]] == i)
        
        # # Create a new list of coordinates that only includes pixels that are part of the connected component
        # precmp = [(cc_coords[0][j], cc_coords[1][j]) for j in range(len(cc_coords[0]))]
        
        value = set(mask[stats[i][1] + coord[0]][stats[i][0] + coord[1]] for coord in precmp)
        # print("Numerics within one connectedComponent")
        # print(list(value))
        if len(value) > 1:
            for j in value:
                count = (count + 1) 
                print(f"Processing cell #{count}")
                # cmp = list(np.intersect(precmp, list(np.argwhere(mask[stats[i][1]:stats[i][1]+stats[i][3], stats[i][0]:stats[i][0]+stats[i][2]] == j))))
                # cmp = [arr for arr in list(np.argwhere(mask[stats[i][1]:stats[i][1]+stats[i][3], stats[i][0]:stats[i][0]+stats[i][2]] == j)) if (arr in arrr for arrr in precmp)]
                cmp = [coord for coord in precmp if mask[stats[i][1] + coord[0], stats[i][0] + coord[1]] == j]
                # cmp = list(np.argwhere(mask[stats[i][1]:stats[i][1]+stats[i][3], stats[i][0]:stats[i][0]+stats[i][2]] == j))
                # print(f"cmp coordinates for value {j}:")
                # print(list(cmp))
                if len(cmp) > 10:
                    for k in range(len(cmp)):
                        # print(stats[i][1], '+', cmp[k][0], '=', stats[i][1] + cmp[k][0], stats[i][0], '+', cmp[k][1], '=', stats[i][0] + cmp[k][1], j)
                        if relabelled[stats[i][1] + cmp[k][0]][stats[i][0] + cmp[k][1]] == 0:
                            relabelled[stats[i][1] + cmp[k][0]][stats[i][0] + cmp[k][1]] = count 
                        # if (stats[i][1] + cmp[k][0], stats[i][0] + cmp[k][1]) not in label_dict:
                        #     label_dict[(stats[i][1] + cmp[k][0], stats[i][0] + cmp[k][1])] = count
                        # relabelled[stats[i][1] + cmp[k][0]][stats[i][0] + cmp[k][1]] = label_dict[(stats[i][1] + cmp[k][0], stats[i][0] + cmp[k][1])]
        else:
            count = (count + 1) 
            print(f"Processing cell #{count}")
            cmp = [coord for coord in precmp if mask[stats[i][1] + coord[0], stats[i][0] + coord[1]] == list(value)[0]]
            # cmp = [arr for arr in list(np.argwhere(mask[stats[i][1]:stats[i][1]+stats[i][3], stats[i][0]:stats[i][0]+stats[i][2]] == list(value)[0])) if (arr in arrr for arrr in precmp)]
            # cmp = list(np.argwhere(mask[stats[i][1]:stats[i][1]+stats[i][3], stats[i][0]:stats[i][0]+stats[i][2]] == list(value)[0]))
            # print(f"cmp coordinates for value {list(value)[0]}:")
            # print(list(cmp))
            if len(cmp) > 10:
                for k in range(len(cmp)):
                    # print(stats[i][1], '+', cmp[k][0], '=', stats[i][1] + cmp[k][0], stats[i][0], '+', cmp[k][1], '=', stats[i][0] + cmp[k][1], j)
                    if relabelled[stats[i][1] + cmp[k][0]][stats[i][0] + cmp[k][1]] == 0:
                        relabelled[stats[i][1] + cmp[k][0]][stats[i][0] + cmp[k][1]] = count 
                    # if (stats[i][1] + cmp[k][0], stats[i][0] + cmp[k][1]) not in label_dict:
                    #     label_dict[(stats[i][1] + cmp[k][0], stats[i][0] + cmp[k][1])] = count
                    # relabelled[stats[i][1] + cmp[k][0]][stats[i][0] + cmp[k][1]] = label_dict[(stats[i][1] + cmp[k][0], stats[i][0] + cmp[k][1])]

# # For visualisation
# for i in [223 - 15, 223 + 15, 447 - 15, 447 + 15, 671 - 15, 671 + 15]:
#     relabelled[:,i] = 255
#     relabelled[i,:] = 255

tiff.imwrite(os.path.join(output_path, output_file), relabelled)