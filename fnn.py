import torch
from torch import nn
from sys import argv
from helpers.myDataset import *
from helpers.myfunc import *
from torch.utils.data import DataLoader

#test device status
device_status=torch.cuda.is_available()
if device_status:
	try:
		device_id=free_device_id(argv[1])
	except:
		device_id=0

#initialize model
net=nn.Sequential(
	nn.Linear(35,32),
	nn.ELU(),
	nn.Linear(32,32),
	nn.ELU(),
	nn.Linear(32,32),
	nn.ELU(),
	nn.Linear(32,19)
)
if device_status:
	net=net.to(device_id)

#set hyperparameters
loss_func=nn.CrossEntropyLoss()
opt=torch.optim.Adam(net.parameters(),lr=0.001)
mini_batch=4

#load dataset
trainData=TrainData('soybean','./datasets/soybean_multi/soybean-large.data')
testData=TestData('soybean','./datasets/soybean_multi/soybean-large.data')

trainLoader=DataLoader(
	dataset=trainData,
	batch_size=mini_batch,
	shuffle=True,
	num_workers=0
)
testLoader=DataLoader(
	dataset=testData,
	batch_size=testData.__len__(),
	shuffle=False,
	num_workers=0
)

if __name__=='__main__':

	#train & test
	for epoch in range(101):
		net=net.train()
		for _,(x,y) in enumerate(trainLoader):
			if device_status:
				x,y=x.to(device_id),y.to(device_id)

			#calcualte estimated results
			opt.zero_grad()
			y_hat=net(x)

			#calculate loss and propagate back
			loss=loss_func(y_hat,y)
			loss.backward()
			opt.step()

		# if epoch%10!=0:
		# 	continue

		net=net.eval()
		positive_n=0
		for _,(x,y) in enumerate(testLoader):
			if device_status:
				x=x.to(device_id)

			#predict
			with torch.no_grad():
				y_hat=net(x)	

			#compare and count
			for i in range(len(y)):
				if torch.argmax(y_hat[i]).item()==y[i].item():
					positive_n+=1

		print('epoch = %d	accuracy = %f' %(epoch,positive_n/testData.__len__()))

	#save parameters
	torch.save(net.state_dict(),'./results/fnn.pkl')
