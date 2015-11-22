import sys
import os
import argparse
import cPickle as pickle

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

if __name__ == '__main__' and __package__ is None:
	# allow explicit relative imports in executable script
	# source: http://stackoverflow.com/a/6655098
	parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
	parent_dir = os.path.dirname(parent_dir)
	print parent_dir; sys.stdout.flush()
	sys.path.insert(1, parent_dir)
	import gopca
	__package__ = 'gopca'

import gopca
from gopca import common
from genometools import misc

def read_args_from_cmdline():

	parser = argparse.ArgumentParser(description='')

	parser.add_argument('-g','--gopca-file',required=True)
	parser.add_argument('-o','--output-file',required=True)

	parser.add_argument('-d','--figure-dimensions',type=float,help='in inches',nargs=2,default=[15,15])
	parser.add_argument('-r','--figure-resolution',type=int,help='in dpi',default=150)
	parser.add_argument('-f','--figure-font-size',type=int,help='in pt',default=24)
	parser.add_argument('-m','--figure-font-family',default='serif')
	parser.add_argument('-c','--figure-colormap',default='RdBu_r')
	parser.add_argument('-vn','--figure-vmin',type=float,default=-3.0)
	parser.add_argument('-vx','--figure-vmax',type=float,default=3.0)

	parser.add_argument('-l','--sig-max-name-len',type=int,default=50)
	parser.add_argument('-co','--figure-colorbar-orientation',default='horizontal')
	parser.add_argument('-ca','--figure-colorbar-anchor',type=float,nargs=2,default=(0.95,1.0))
	parser.add_argument('-cs','--figure-colorbar-shrink',type=float,default=0.3)
	parser.add_argument('-cp','--figure-colorbar-pad',type=float,default=0.03)

	parser.add_argument('--plot-in-notebook',action='store_true') # if run using %run

	parser.add_argument('--use-tex',action='store_true')
	parser.add_argument('--matplotlib-backend',default=None)
	parser.add_argument('--disable-sample-clustering',action='store_true')

	return parser.parse_args()

def main(args=None):

	if args is None:
		args = read_args_from_cmdline()

	result_file = args.gopca_file
	output_file = args.output_file
	#go_pickle_file = args.go_pickle_file

	# figure size
	fig_dim = args.figure_dimensions
	fig_res = args.figure_resolution

	# figure text
	use_tex = args.use_tex
	fig_font_size = args.figure_font_size
	fig_font_family = args.figure_font_family

	# figure heatmap
	fig_vmin = args.figure_vmin
	fig_vmax = args.figure_vmax
	fig_cmap = args.figure_colormap

	# figure colorbar
	fig_cbar_orient = args.figure_colorbar_orientation
	fig_cbar_anchor = args.figure_colorbar_anchor
	fig_cbar_shrink = args.figure_colorbar_shrink
	fig_cbar_pad = args.figure_colorbar_pad

	mpl_backend = args.matplotlib_backend
	plot_in_notebook = args.plot_in_notebook

	sig_max_name_len = args.sig_max_name_len

	# read GO-PCA result
	result = None
	with open(result_file,'rb') as fh:
		result = pickle.load(fh)

	signatures = result.signatures
	# generate labels
	labels = [sig.get_pretty_format(omit_acc=True,max_name_length=sig_max_name_len) for sig in signatures]
	samples = result.samples
	S = result.S

	# clustering of rows (signatures)
	print 'Clustering of signatures...', ; sys.stdout.flush()
	distxy = squareform(pdist(S, metric='correlation'))
	R = dendrogram(linkage(distxy, method='average'),no_plot=True)
	order_rows = np.int64([int(l) for l in R['ivl']])
	S = S[order_rows,:]
	labels = [labels[idx] for idx in order_rows]
	print 'done!'; sys.stdout.flush()

	if not args.disable_sample_clustering:
		# clustering of columns (samples)
		print 'Clustering of samples...', ; sys.stdout.flush()
		distxy = squareform(pdist(S.T, metric='euclidean'))
		R = dendrogram(linkage(distxy, method='average'),no_plot=True)
		order_cols = np.int64([int(l) for l in R['ivl']])
		S = S[:,order_cols]
		samples = [samples[j] for j in order_cols]
		print 'done!'; sys.stdout.flush()

	# plotting
	print 'Plotting...', ; sys.stdout.flush()

	import matplotlib as mpl
	if mpl_backend is not None:
		mpl.use(mpl_backend)
	import matplotlib.pyplot as plt
	from matplotlib import rc

	if plot_in_notebook:
		from IPython import get_ipython
		ipython = get_ipython()
		ipython.magic('matplotlib inline')

	if use_tex: rc('text',usetex=True)
	rc('font',family=fig_font_family,size=fig_font_size)
	rc('figure',figsize=(fig_dim[0],fig_dim[1]))
	rc('savefig',dpi=fig_res)

	# plotting
	plt.imshow(S,interpolation='none',aspect='auto',vmin=fig_vmin,vmax=fig_vmax,cmap=fig_cmap)

	minint = int(fig_vmin)
	maxint = int(fig_vmax)
	cbticks = np.arange(minint,maxint+0.01,1.0)
	cb = plt.colorbar(orientation=fig_cbar_orient,shrink=fig_cbar_shrink,pad=fig_cbar_pad,ticks=cbticks,use_gridspec=False,anchor=fig_cbar_anchor)
	cb.ax.tick_params(labelsize='small')
	cb.set_label('Standardized Expression',size='small')

	q,n = S.shape
	plt.yticks(np.arange(q),labels,size='x-small')
	plt.xlabel('Samples (n=%d)' %(n))
	plt.ylabel('Signatures')
	print 'done!'; sys.stdout.flush()

	print 'Saving to file...', ; sys.stdout.flush()
	plt.savefig(output_file,bbox_inches='tight')
	print 'done!'; sys.stdout.flush()

	return 0

if __name__ == '__main__':
	return_code = main()
	sys.exit(return_code)
