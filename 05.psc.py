import stereo as st
import os
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
data_path = "/home/jyubq/proj_benchmarking/dast_ss2022test/Mouse_brain_Adult_GEM_bin12CellBin.gef"
data_out = '/import/home/jyubq/proj_benchmarking/dast_ss2022test/06.sccell'
os.makedirs(data_out, exist_ok=True)
data = st.io.read_gef(file_path=data_path, bin_type='cell_bins')
datatype = "default_mycode"

# QC
data.tl.cal_qc()
data.plt.violin()
plt.savefig(f"{data_out}/{datatype}_qc")

data.plt.spatial_scatter()
plt.savefig(f"{data_out}/{datatype}_spatial_qc")

# Filtering
data.plt.genes_count()
plt.savefig(f"{data_out}/{datatype}_count")

data.tl.filter_cells(
        min_gene=200,
        min_n_genes_by_counts=3,
        max_n_genes_by_counts=2500,
        pct_counts_mt=5,
        inplace=True
        )

data.tl.raw_checkpoint()

# Normalisation

data.tl.normalize_total()
data.tl.log1p()

data.tl.highly_variable_genes(
            min_mean=0.0125,
            max_mean=3,
            min_disp=0.5,
            n_top_genes=2000,
            res_key='highly_variable_genes'
            )

data.plt.highly_variable_genes(res_key='highly_variable_genes')
plt.savefig(f"{data_out}/{datatype}_deg")

data.tl.scale()

# Dimension reduction
data.tl.pca(
        use_highly_genes=True,
        n_pcs=30,
        res_key='pca'
        )
data.tl.neighbors(pca_res_key='pca', res_key='neighbors')

data.tl.umap(
        pca_res_key='pca',
        neighbors_res_key='neighbors',
        res_key='umap'
        )

data.plt.umap(gene_names=['Lsamp'], res_key='umap')
plt.savefig(f"{data_out}/{datatype}_umap")

# Clustering
data.tl.phenograph(phenograph_k=30, pca_res_key='pca', res_key='phenograph')

data.plt.cluster_scatter(res_key='phenograph')
plt.savefig(f"{data_out}/{datatype}_cluster")

# Marker gene
data.tl.find_marker_genes(
        cluster_res_key='phenograph',
        method='t_test',
        use_highly_genes=False,
        use_raw=True
        )

data.plt.marker_genes_text(
        res_key='marker_genes',
        markers_num=10,
        sort_key='scores'
        )
plt.savefig(f"{data_out}/{datatype}_markers_name")

data.plt.marker_genes_scatter(res_key='marker_genes', markers_num=5)
plt.savefig(f"{data_out}/{datatype}_markers")

grp = "1"
data.plt.marker_gene_volcano(group_name=f'{grp}.vs.rest', vlines=False) # change group_name if necessary
plt.savefig(f"{data_out}/{datatype}_volcano")

data.tl.filter_marker_genes(
    marker_genes_res_key='marker_genes',
    min_fold_change=1,
    min_in_group_fraction=0.25,
    max_out_group_fraction=0.5,
    res_key='marker_genes_filtered'
)

# # Cluster annotation
# data.plt.interact_annotation_cluster(
#             res_cluster_key='phenograph',
#             res_marker_gene_key='marker_genes',
#             res_key='phenograph_annotation'
#             )
# plt.savefig(f"{data_out}/{datatype}_no_annotation")

# annotation_dict = {}
# for i in range(1, 141):
#     key = i
#     value = "test" + str(i)
#     annotation_dict[key] = value

# data.tl.annotation(
#         annotation_information=annotation_dict,
#         cluster_res_key='phenograph',
#         res_key='phenograph_annotation'
#         )

# data.plt.cluster_scatter(res_key='phenograph_annotation')
# plt.savefig(f"{data_out}/{datatype}_annotation")

# st.io.write_h5ad(
#         data,
#         use_raw=True,
#         use_result=True,
#         key_record={'cluster':['phenograph'],},
#         output=f"{data_out}/{datatype}.h5ad",
#         )

# st.io.write_h5ad(
#         data,
#         use_raw=True,
#         use_result=False,
#         key_record=None,
#         )

st.io.stereo_to_anndata(data,
                        flavor='scanpy',
                        output=f"{data_out}/{datatype}_scanpy.h5ad")

st.io.stereo_to_anndata(data,
                        flavor='seurat',
                        output=f"{data_out}/{datatype}_seurat.h5ad")