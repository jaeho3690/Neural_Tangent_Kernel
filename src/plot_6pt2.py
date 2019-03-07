# -*- coding: utf-8 -*-
"""Copy of Neural_tangent_kernel.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tWrLqrNB1WJ2a3PT9flEYYi5vNRqeUMt
"""

import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import seaborn as sns
sns.set()

from collections import OrderedDict

import sys
sys.path.append("../")
from Neural_Tangent_Kernel.src.NTK_net import LinearNeuralTangentKernel, FourLayersNet, train_net, circle_transform, variance_est, cpu_tuple, kernel_mats

use_cuda = True if torch.cuda.is_available() else False

"""# Reproducing the experiments in the neural tangent kernel paper.



## 6.2
# gamma_data = np.array([-2.2, -1, 1, 2.2])
# target_data = np.array([-0.4, -0.2, 0.3, 0.3])
### Define the input and target data
"""
def plot_6pt2(gamma_data, target_data):
	
	gamma_data = torch.tensor(gamma_data)
	target_data = torch.tensor(target_data).float()
	input_data = circle_transform(gamma_data)
	if use_cuda:
		input_data = input_data.cuda()
		target_data = target_data.cuda()

	"""### Create Plot"""

	gamma_vec = torch.tensor(np.linspace(-np.pi, np.pi, 100))
	circle_points = circle_transform(gamma_vec)
	if use_cuda:
		circle_points = circle_points.cuda()

	for i in range(10):
	# 1000 width first
		net = FourLayersNet(1000)
		if use_cuda:
			net = net.cuda()
		train_net(net, 1000, input_data, target_data)
		output_vec = net(circle_points).cpu()
		plt.plot(gamma_vec.numpy(), output_vec.detach().numpy(), color='red',
			linestyle='--', alpha = 0.3)
		# 50 width
		net = FourLayersNet(50)
		if use_cuda:
			net = net.cuda()
		train_net(net, 1000, input_data, target_data)
		output_vec = net(circle_points).cpu()
		plt.plot(gamma_vec.numpy(), output_vec.detach().numpy(), color='green',
		linestyle='--', alpha = 0.3)

	#print('Completed initialisation {}'.format(i))

	plt.xlabel('$\gamma$')
	plt.ylabel('$f_{ \\theta}(sin(\gamma),cos(\gamma))$')
	net = FourLayersNet(1000)
	K_testvtrain, K_trainvtrain = kernel_mats(net, gamma_data, gamma_vec, kernels = 'both')
	K_trainvtrain_inv = torch.inverse(K_trainvtrain)
	"""### Getting the GP process plot is harder (I think) because of a lack of a standard kernel, here is an attempt but it is probably horrifically inefficient"""

	n_pts=100

	temp_mat = torch.mm(K_testvtrain, K_trainvtrain_inv)	

	# number of points in plot

	target_data = target_data.cpu()

	mean_vec = torch.mm(temp_mat, target_data.unsqueeze(1))
	"""%%time
	# grad_mat is kappa on p7 of NTK paper
	for i, gamma in enumerate(gamma_test):
	if i%10 == 0:
	print('point {}'.format(i))
	circle_pt = circle_transform(gamma)
	if use_cuda and torch.cuda.is_available():
	circle_pt = circle_pt.cuda()
	loss = net(circle_pt)
	grads = cpu_tuple(torch.autograd.grad(loss,net.parameters(), retain_graph = True)) # extract NN gradients 
	for j in range(len(grad_list)):
	pt_grad = grad_list[j] # the gradients at the jth (out of 4) data point
	grad_mat[i, j] = sum([torch.sum(torch.mul(grads[u], pt_grad[u])) for u in range(len(grads))])
	"""

	"""### It remains to estimate sigma matrix"""

	variance_vec = variance_est(10000, 100, temp_mat, 10000)

	plt.plot(gamma_vec.numpy(), mean_vec.view(-1).detach().numpy()+1.28*np.sqrt(variance_vec.detach().numpy()),
	 color='darkblue', linestyle = '--')
	plt.plot(gamma_vec.numpy(), mean_vec.view(-1).detach().numpy()-1.28*np.sqrt(variance_vec.detach().numpy()), 
	 color='darkblue', linestyle = '--', label = '$n=\infty, \{P_{10}, P_{90}\}$')
	plt.plot(gamma_vec.numpy(), mean_vec.view(-1).detach().numpy()+0*np.sqrt(variance_vec.detach().numpy()), 
	 color='darkblue', label = '$n=\infty, P_{50}$')


	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = OrderedDict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys(), loc = 'upper left')


	plt.show()
