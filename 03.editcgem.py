import os
import pandas as pd
import tifffile as tiff

# input_path = "/home/jyubq/proj_benchmarking/dast_ss2022/masks"
# input_file = "relabelled_stardist_mycode.tif"

# mask = tiff.imread(os.path.join(input_path, input_file))
# # gem = pd.read_csv("/home/jyubq/proj_benchmarking/dast_ss2022/73.trial/03.count/FP200003808_L01_73.raw.gem", sep='\t', header=0, compression='infer', comment='#')
# gem = pd.read_csv("/home/jyubq/proj_benchmarking/dast_ss2022test/Mouse_brain_Adult_GEM_bin1.gem", sep='\t', header=0, compression='infer', comment='#')
# gem['label'] = 0
# gem['label'] = mask[gem['y'], gem['x']]
# gem.to_csv("/home/jyubq/proj_benchmarking/dast_ss2022test/Mouse_brain_Adult_GEM_bin12CellBin.gem", sep = '\t', index=False)
# print(len(gem['label']), gem['label'].value_counts().get(0,0))

# # Match between two gems
# gem1 = pd.read_csv("/home/jyubq/proj_benchmarking/dast_ss2022test/Mouse_brain_Adult_GEM_bin1.gem", sep='\t', header=0, compression='infer', comment='#')
# gem2 = pd.read_csv("/home/jyubq/proj_benchmarking/dast_ss2022test/Mouse_brain_Adult_GEM_CellBin.gem", sep='\t', header=0, compression='infer', comment='#')
# gem1 = gem1.merge(gem2[['x', 'y', 'label']], on=['x', 'y'], how='left')
# gem1['label'] = gem1['label'].fillna(0)
# gem1.to_csv("/home/jyubq/proj_benchmarking/dast_ss2022test/Mouse_brain_Adult_GEM_bin12CellBin.gem", sep='\t', index=False)
# print(len(gem1['label']), gem1['label'].value_counts().get(0,0))

gem0 = pd.read_csv("Mouse_brain_Adult_GEM_bin12CellBin.gem", sep='\t')
gem1 = pd.read_csv("Mouse_brain_Adult_GEM_bin1_stardist_xy.gem", sep='\t')
gem2 = pd.read_csv("Mouse_brain_Adult_GEM_bin1_cellpose_xy.gem", sep='\t')
print(gem0['label'].value_counts().get(0,0)/len(gem0['label']))
print(gem1['label'].value_counts().get(0,0)/len(gem1['label']))
print(gem2['label'].value_counts().get(0,0)/len(gem2['label']))

