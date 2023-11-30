import os
import sys
import tifffile as tiff
import numpy as np
import re

# Path to masks
path = "/home/jyubq/proj_benchmarking/dast_ss2022test/masks_stitched"

# Initialize variables
patch_size = None
stride_horizontal = None
stride_vertical = None
stitched_height = None
stitched_width = None

if os.path.exists(os.path.join(path, "parameters.txt")):
    print("Reading parameters from metadata...")
    # Read parameters from the text file
    with open(os.path.join(path, "parameters.txt"), "r") as file:
        lines = file.readlines()

    # Extract parameter values from the text file
    for line in lines:
        if line.startswith("Patch Size:"):
            patch_size = tuple(map(int, line.split(":")[1].strip().replace("(", "").replace(")", "").split(",")))
        elif line.startswith("Horizontal Stride:"):
            stride_horizontal = int(line.split(":")[1].strip())
        elif line.startswith("Vertical Stride:"):
            stride_vertical = int(line.split(":")[1].strip())
        elif line.startswith("Image Size:"):
            stitched_height, stitched_width = map(int, line.split(":")[1].strip().replace("(", "").replace(")", "").split(","))
        elif line.startswith("Number of Rows:"):
            num_rows = int(line.split(":")[1].strip())
        elif line.startswith("Number of Columns:"):
            num_cols = int(line.split(":")[1].strip())

    # Check if any parameter is missing
    if (
        patch_size is None
        or stride_horizontal is None
        or stride_vertical is None
        or stitched_height is None
        or stitched_width is None
        or num_rows is None
        or num_cols is None
    ):
        print("Error: Missing parameter in the text file.")
        sys.exit(1)

    # Print the extracted parameters
    print("Patch Size:", patch_size)
    print("Stitched Image Size:", (stitched_height, stitched_width))
    print("Stride Size:", (stride_vertical, stride_horizontal))

    # Convert parameters to integers if needed
    patch_size = tuple(int(val) for val in patch_size)
    stride_horizontal = int(stride_horizontal)
    stride_vertical = int(stride_vertical)
    stitched_height = int(stitched_height)
    stitched_width = int(stitched_width)
    num_rows = int(num_rows)
    num_cols = int(num_cols)
else:
    print("Manually setting parameters...")
    # Initialize variables
    patch_size = (448, 448)
    stride_horizontal = 224
    stride_vertical = 224
    stitched_height = 26880
    stitched_width = 26880
    num_rows = 118
    num_cols = 118

    # Print the extracted parameters
    print("Patch Size:", patch_size)
    print("Stitched Image Size:", (stitched_height, stitched_width))
    print("Stride Size:", (stride_vertical, stride_horizontal))

def get_row_col(filename):
    match = re.search(r'(\d+)_(\d+)\.tif$', filename)
    if match:
        row, col = map(int, match.groups())
        return row, col
    else:
        raise ValueError(f"Invalid filename format: {filename}")

# Create an empty array to store the stitched image.
stitched = np.zeros((stitched_height, stitched_width), dtype=np.uint16)

os.chdir(path)

for index, filename in enumerate(sorted(os.listdir(path))):
    if filename.endswith(".tif") and not filename.startswith("stitch") and not filename.startswith("relabel"):
        i, j = get_row_col(filename)
        x = j * stride_horizontal
        y = i * stride_vertical
        mask1 = tiff.imread(os.path.join(path, filename))
        print(f"Processing patch {i}, {j}:")
        if i == 0:
            if j == 0:
                print("Case 1")
                
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound1 = {i: coords for i, coords in cells1.items() if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432}
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208 and not any(447.0 == coord[0] for coord in np.argwhere(mask2 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask2 == i))}
                bound2 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208 and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 223}

                for index1, coords1 in bound1.items():
                    for index2, coords2 in bound2.items():
                        if 100 * len(set((coord1[0], coord1[1]) for coord1 in coords1).intersection(set((coord2[0], coord2[1] + 224) for coord2 in coords2))) // len(set((coord1[0], coord1[1]) for coord1 in coords1)) >= 50:
                            del cells1[index1]

                for index1, coords1 in cells1.items():
                    for i in range(len(coords1)):
                        stitched[y + coords1[i][0]][x + coords1[i][1]] = index1

                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells1 = {}
                bound1 = {}
                cells2 = {}
                bound2 = {}

            elif j != 0 and j != num_cols - 2 and j != num_cols - 1:
                print("Case 2")
                
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432 and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound1 = cells1
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208 and not any(447.0 == coord[0] for coord in np.argwhere(mask2 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask2 == i))}
                bound2 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208 and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 223}

                for index1, coords1 in bound1.items():
                    for index2, coords2 in bound2.items():
                        if 100 * len(set((coord1[0], coord1[1]) for coord1 in coords1).intersection(set((coord2[0], coord2[1] + 224) for coord2 in coords2))) // len(set((coord1[0], coord1[1]) for coord1 in coords1)) >= 50:
                            for i in range(len(coords1)):
                                stitched[y + coords1[i][0]][x + coords1[i][1]] = 0
                                
                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells1 = {}
                bound1 = {}
                cells2 = {}
                bound2 = {}
                
            elif j == num_cols - 2:
                print("Case 3")
                
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432 and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound1 = cells1
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208 and not any(447.0 == coord[0] for coord in np.argwhere(mask2 == i))}
                bound2 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208 and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 223}

                for index1, coords1 in bound1.items():
                    for index2, coords2 in bound2.items():
                        if 100 * len(set((coord1[0], coord1[1]) for coord1 in coords1).intersection(set((coord2[0], coord2[1] + 224) for coord2 in coords2))) // len(set((coord1[0], coord1[1]) for coord1 in coords1)) >= 50:
                            for i in range(len(coords1)):
                                stitched[y + coords1[i][0]][x + coords1[i][1]] = 0
                                
                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells1 = {}
                bound1 = {}
                cells2 = {}
                bound2 = {}

        elif i != 0 and i != num_rows - 1:
            if j == 0:
                print("Case 4")
                
                mask0 = tiff.imread(sorted(os.listdir(path))[index - num_cols])
                print(f"mask0 is read as {sorted(os.listdir(path))[index - num_cols]}.")
                mask00 = tiff.imread(sorted(os.listdir(path))[index - num_cols + 1])
                print(f"mask00 is read as {sorted(os.listdir(path))[index - num_cols + 1]}.")
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells0 = {i: np.argwhere(mask0 == i) for i in range(1, np.max(mask0) + 1) if max(coord[0] for coord in np.argwhere(mask0 == i)) >= 432}
                bound0 = cells0
                cells00 = {
                    i: np.argwhere(mask00 == i)
                    for i in range(1, np.max(mask00) + 1)
                    if np.argwhere(mask00 == i).size > 0 and
                    max(coord[0] for coord in np.argwhere(mask00 == i)) >= 432 and
                    min(coord[1] for coord in np.argwhere(mask00 == i)) >= 208
                }
                bound00 = cells00
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[0] for coord in np.argwhere(mask1 == i) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound10 = {i: coords for i, coords in cells1.items() if max(coord[0] for coord in np.argwhere(mask1 == i)) >= 208 and min(coord[0] for coord in np.argwhere(mask1 == i)) <= 223}
                bound12 = {i: coords for i, coords in cells1.items() if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432}
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if (max(coord[0] for coord in np.argwhere(mask2 == i)) >= 208 and max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask2 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask2 == i))}
                bound20 = {i: coords for i, coords in cells2.items() if max(coord[0] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[0] for coord in np.argwhere(mask2 == i)) <= 238}
                bound21 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 238}

                for index0, coords0 in bound0.items():
                    for index10, coords10 in bound10.items():
                        if 100 * len(set((coord0[0], coord0[1]) for coord0 in coords0).intersection(set((coord10[0] + 224, coord10[1]) for coord10 in coords10))) // len(set((coord0[0], coord0[1]) for coord0 in coords0)) >= 50:
                            for i in range(len(coords0)):
                                stitched[y + coords0[i][0] - 224][x + coords0[i][1]] = 0
                
                for index00, coords00 in bound00.items():
                    for index20, coords20 in bound20.items():
                        if 100 * len(set((coord00[0], coord00[1]) for coord00 in coords00).intersection(set((coord20[0] + 224, coord20[1]) for coord20 in coords20))) // len(set((coord00[0], coord00[1]) for coord00 in coords00)) >= 50:
                            for i in range(len(coords00)):
                                stitched[y + coords00[i][0] - 224][x + coords00[i][1] + 224] = 0

                for index12, coords12 in bound12.items():
                    for index21, coords21 in bound21.items():
                        if 100 * len(set((coord12[0], coord12[1]) for coord12 in coords12).intersection(set((coord21[0], coord21[1] + 224) for coord21 in coords21))) // len(set((coord12[0], coord12[1]) for coord12 in coords12)) >= 50:
                            del cells1[index12]

                for index1, coords1 in cells1.items():
                    for i in range(len(coords1)):
                        stitched[y + coords1[i][0]][x + coords1[i][1]] = index1

                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells0 = {}
                bound0 = {}
                cells00 = {}
                bound00 = {}
                cells1 = {}
                bound10 = {}
                bound12 = {}
                cells2 = {}
                bound20 = {}
                bound21 = {}

            elif j != 0 and j != num_cols - 2 and j != num_cols - 1:
                print("Case 5")
                mask00 = tiff.imread(sorted(os.listdir(path))[index - num_cols + 1])
                print(f"mask00 is read as {sorted(os.listdir(path))[index - num_cols + 1]}.")
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                bound0 = cells0
                cells00 = {
                    i: np.argwhere(mask00 == i)
                    for i in range(1, np.max(mask00) + 1)
                    if np.argwhere(mask00 == i).size > 0 and
                    max(coord[0] for coord in np.argwhere(mask00 == i)) >= 432 and
                    min(coord[1] for coord in np.argwhere(mask00 == i)) >= 208
                }
                bound00 = cells00
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[0] for coord in np.argwhere(mask1 == i) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound12 = {i: coords for i, coords in cells1.items() if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432}
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if (max(coord[0] for coord in np.argwhere(mask2 == i)) >= 208 and max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask2 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask2 == i))}
                bound20 = {i: coords for i, coords in cells2.items() if max(coord[0] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[0] for coord in np.argwhere(mask2 == i)) <= 238}
                bound21 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 238}
                
                for index00, coords00 in bound00.items():
                    for index20, coords20 in bound20.items():
                        if 100 * len(set((coord00[0], coord00[1]) for coord00 in coords00).intersection(set((coord20[0] + 224, coord20[1]) for coord20 in coords20))) // len(set((coord00[0], coord00[1]) for coord00 in coords00)) >= 50:
                            for i in range(len(coords00)):
                                stitched[y + coords00[i][0] - 224][x + coords00[i][1] + 224] = 0

                for index12, coords12 in bound12.items():
                    for index21, coords21 in bound21.items():
                        if 100 * len(set((coord12[0], coord12[1]) for coord12 in coords12).intersection(set((coord21[0], coord21[1] + 224) for coord21 in coords21))) // len(set((coord12[0], coord12[1]) for coord12 in coords12)) >= 50:
                            for i in range(len(coords12)):
                                stitched[y + coords12[i][0]][x + coords12[i][1]] = 0

                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells0 = {}
                bound0 = {}
                cells00 = {}
                bound00 = {}
                cells1 = {}
                bound10 = {}
                bound12 = {}
                cells2 = {}
                bound20 = {}
                bound21 = {}

            elif j == num_cols - 2:
                print("Case 6")
                mask00 = tiff.imread(sorted(os.listdir(path))[index - num_cols + 1])
                print(f"mask00 is read as {sorted(os.listdir(path))[index - num_cols + 1]}.")
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells00 = {
                    i: np.argwhere(mask00 == i)
                    for i in range(1, np.max(mask00) + 1)
                    if np.argwhere(mask00 == i).size > 0 and
                    max(coord[0] for coord in np.argwhere(mask00 == i)) >= 432 and
                    max(coord[1] for coord in np.argwhere(mask00 == i)) >= 208
                }
                bound00 = cells00
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[0] for coord in np.argwhere(mask1 == i) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound12 = {i: coords for i, coords in cells1.items() if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432}
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if (max(coord[0] for coord in np.argwhere(mask2 == i)) >= 208 and max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask2 == i))}
                bound20 = {i: coords for i, coords in cells2.items() if max(coord[0] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[0] for coord in np.argwhere(mask2 == i)) <= 238}
                bound21 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 238}

                for index00, coords00 in bound00.items():
                    for index20, coords20 in bound20.items():
                        if 100 * len(set((coord00[0], coord00[1]) for coord00 in coords00).intersection(set((coord20[0] + 224, coord20[1]) for coord20 in coords20))) // len(set((coord00[0], coord00[1]) for coord00 in coords00)) >= 50:
                            for i in range(len(coords00)):
                                stitched[y + coords00[i][0] - 224][x + coords00[i][1] + 224] = 0

                for index12, coords12 in bound12.items():
                    for index21, coords21 in bound21.items():
                        if 100 * len(set((coord12[0], coord12[1]) for coord12 in coords12).intersection(set((coord21[0], coord21[1] + 224) for coord21 in coords21))) // len(set((coord12[0], coord12[1]) for coord12 in coords12)) >= 50:
                            for i in range(len(coords12)):
                                stitched[y + coords12[i][0]][x + coords12[i][1]] = 0

                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells0 = {}
                bound0 = {}
                cells00 = {}
                bound00 = {}
                cells1 = {}
                bound10 = {}
                bound12 = {}
                cells2 = {}
                bound20 = {}
                bound21 = {}

        elif i == num_rows - 1:
            if j == 0:
                print("Case 7")
                mask0 = tiff.imread(sorted(os.listdir(path))[index - num_cols])
                print(f"mask0 is read as {sorted(os.listdir(path))[index - num_cols]}.")
                mask00 = tiff.imread(sorted(os.listdir(path))[index - num_cols + 1])
                print(f"mask00 is read as {sorted(os.listdir(path))[index - num_cols + 1]}.")
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells0 = {i: np.argwhere(mask0 == i) for i in range(1, np.max(mask0) + 1) if max(coord[0] for coord in np.argwhere(mask0 == i)) >= 432}
                bound0 = cells0
                cells00 = {
                    i: np.argwhere(mask00 == i)
                    for i in range(1, np.max(mask00) + 1)
                    if np.argwhere(mask00 == i).size > 0 and
                    max(coord[0] for coord in np.argwhere(mask00 == i)) >= 432 and
                    min(coord[1] for coord in np.argwhere(mask00 == i)) >= 208
                }
                bound00 = cells00
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[0] for coord in np.argwhere(mask1 == i) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound10 = {i: coords for i, coords in cells1.items() if max(coord[0] for coord in np.argwhere(mask1 == i)) >= 208 and min(coord[0] for coord in np.argwhere(mask1 == i)) <= 223}
                bound12 = {i: coords for i, coords in cells1.items() if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432}
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if (max(coord[0] for coord in np.argwhere(mask2 == i)) >= 208 and max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208) and not any(447.0 == coord[1] for coord in np.argwhere(mask2 == i))}
                bound20 = {i: coords for i, coords in cells2.items() if max(coord[0] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[0] for coord in np.argwhere(mask2 == i)) <= 238}
                bound21 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 238}

                for index0, coords0 in bound0.items():
                    for index10, coords10 in bound10.items():
                        if 100 * len(set((coord0[0], coord0[1]) for coord0 in coords0).intersection(set((coord10[0] + 224, coord10[1]) for coord10 in coords10))) // len(set((coord0[0], coord0[1]) for coord0 in coords0)) >= 50:
                            for i in range(len(coords0)):
                                stitched[y + coords0[i][0] - 224][x + coords0[i][1]] = 0
                
                for index00, coords00 in bound00.items():
                    for index20, coords20 in bound20.items():
                        if 100 * len(set((coord00[0], coord00[1]) for coord00 in coords00).intersection(set((coord20[0] + 224, coord20[1]) for coord20 in coords20))) // len(set((coord00[0], coord00[1]) for coord00 in coords00)) >= 50:
                            for i in range(len(coords00)):
                                stitched[y + coords00[i][0] - 224][x + coords00[i][1] + 224] = 0

                for index12, coords12 in bound12.items():
                    for index21, coords21 in bound21.items():
                        if 100 * len(set((coord12[0], coord12[1]) for coord12 in coords12).intersection(set((coord21[0], coord21[1] + 224) for coord21 in coords21))) // len(set((coord12[0], coord12[1]) for coord12 in coords12)) >= 50:
                            del cells1[index12]

                for index1, coords1 in cells1.items():
                    for i in range(len(coords1)):
                        stitched[y + coords1[i][0]][x + coords1[i][1]] = index1

                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells0 = {}
                bound0 = {}
                cells00 = {}
                bound00 = {}
                cells1 = {}
                bound10 = {}
                bound12 = {}
                cells2 = {}
                bound20 = {}
                bound21 = {}

            elif j != 0 and j != num_cols - 2 and j != num_cols - 1:
                print("Case 8")
                mask00 = tiff.imread(sorted(os.listdir(path))[index - num_cols + 1])
                print(f"mask00 is read as {sorted(os.listdir(path))[index - num_cols + 1]}.")
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells00 = {
                    i: np.argwhere(mask00 == i)
                    for i in range(1, np.max(mask00) + 1)
                    if np.argwhere(mask00 == i).size > 0 and
                    max(coord[0] for coord in np.argwhere(mask00 == i)) >= 432 and
                    min(coord[1] for coord in np.argwhere(mask00 == i)) >= 208
                }
                bound00 = cells00
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[0] for coord in np.argwhere(mask1 == i) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound12 = {i: coords for i, coords in cells1.items() if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432}
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if (max(coord[0] for coord in np.argwhere(mask2 == i)) >= 208 and max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208) and not any(447.0 == coord[1] for coord in np.argwhere(mask2 == i))}
                bound20 = {i: coords for i, coords in cells2.items() if max(coord[0] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[0] for coord in np.argwhere(mask2 == i)) <= 238}
                bound21 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 238}
                
                for index00, coords00 in bound00.items():
                    for index20, coords20 in bound20.items():
                        if 100 * len(set((coord00[0], coord00[1]) for coord00 in coords00).intersection(set((coord20[0] + 224, coord20[1]) for coord20 in coords20))) // len(set((coord00[0], coord00[1]) for coord00 in coords00)) >= 50:
                            for i in range(len(coords00)):
                                stitched[y + coords00[i][0] - 224][x + coords00[i][1] + 224] = 0

                for index12, coords12 in bound12.items():
                    for index21, coords21 in bound21.items():
                        if 100 * len(set((coord12[0], coord12[1]) for coord12 in coords12).intersection(set((coord21[0], coord21[1] + 224) for coord21 in coords21))) // len(set((coord12[0], coord12[1]) for coord12 in coords12)) >= 50:
                            for i in range(len(coords12)):
                                stitched[y + coords12[i][0]][x + coords12[i][1]] = 0

                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells0 = {}
                bound0 = {}
                cells00 = {}
                bound00 = {}
                cells1 = {}
                bound10 = {}
                bound12 = {}
                cells2 = {}
                bound20 = {}
                bound21 = {}

            elif j == num_cols - 2:
                print("Case 9")
                mask00 = tiff.imread(sorted(os.listdir(path))[index - num_cols + 1])
                print(f"mask00 is read as {sorted(os.listdir(path))[index - num_cols + 1]}.")
                mask2 = tiff.imread(sorted(os.listdir(path))[index + 1])
                print(f"mask1 is read as {filename}.")
                print(f"mask2 is read as {sorted(os.listdir(path))[index + 1]}.")
                cells00 = {
                    i: np.argwhere(mask00 == i)
                    for i in range(1, np.max(mask00) + 1)
                    if np.argwhere(mask00 == i).size > 0 and
                    max(coord[0] for coord in np.argwhere(mask00 == i)) >= 432 and
                    max(coord[1] for coord in np.argwhere(mask00 == i)) >= 208
                }
                bound00 = cells00
                cells1 = {i: np.argwhere(mask1 == i) for i in range(1, np.max(mask1) + 1) if max(coord[0] for coord in np.argwhere(mask1 == i) >= 208) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[0] for coord in np.argwhere(mask1 == i)) and not any(447.0 == coord[1] for coord in np.argwhere(mask1 == i))}
                bound12 = {i: coords for i, coords in cells1.items() if max(coord[1] for coord in np.argwhere(mask1 == i)) >= 432}
                cells2 = {i: np.argwhere(mask2 == i) for i in range(1, np.max(mask2) + 1) if (max(coord[0] for coord in np.argwhere(mask2 == i)) >= 208 and max(coord[1] for coord in np.argwhere(mask2 == i)) >= 208)}
                bound20 = {i: coords for i, coords in cells2.items() if max(coord[0] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[0] for coord in np.argwhere(mask2 == i)) <= 238}
                bound21 = {i: coords for i, coords in cells2.items() if max(coord[1] for coord in np.argwhere(mask2 == i) >= 208) and min(coord[1] for coord in np.argwhere(mask2 == i)) <= 238}

                for index00, coords00 in bound00.items():
                    for index20, coords20 in bound20.items():
                        if 100 * len(set((coord00[0], coord00[1]) for coord00 in coords00).intersection(set((coord20[0] + 224, coord20[1]) for coord20 in coords20))) // len(set((coord00[0], coord00[1]) for coord00 in coords00)) >= 50:
                            for i in range(len(coords00)):
                                stitched[y + coords00[i][0] - 224][x + coords00[i][1] + 224] = 0

                for index12, coords12 in bound12.items():
                    for index21, coords21 in bound21.items():
                        if 100 * len(set((coord12[0], coord12[1]) for coord12 in coords12).intersection(set((coord21[0], coord21[1] + 224) for coord21 in coords21))) // len(set((coord12[0], coord12[1]) for coord12 in coords12)) >= 50:
                            for i in range(len(coords12)):
                                stitched[y + coords12[i][0]][x + coords12[i][1]] = 0

                for index2, coords2 in cells2.items():
                    for i in range(len(coords2)):
                        stitched[y + coords2[i][0]][x + coords2[i][1] + 224] = index2

                cells0 = {}
                bound0 = {}
                cells00 = {}
                bound00 = {}
                cells1 = {}
                bound10 = {}
                bound12 = {}
                cells2 = {}
                bound20 = {}
                bound21 = {}

# For visualisation
# for i in [223 - 15, 223 + 15, 447 - 15, 447 + 15, 671 - 15, 671 + 15]:
#     stitched[:,i] = 255
#     stitched[i,:] = 255
  
tiff.imwrite(os.path.join(path, "stitched_cellpose.tif"), stitched[:26465,:26459])