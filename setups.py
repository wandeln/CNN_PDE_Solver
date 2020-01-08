import torch
import numpy as np

"""
ask-tell interface:
ask(): ask for batch of v_cond(t),cond_mask(t),flow_mask(t),v(t),p(t)
tell(v,p): tell results for v(t+1),p(t+1) of batch
"""

class Dataset:
	def __init__(self,w,h,batch_size=100,dataset_size=1000):
		self.h,self.w = h,w
		self.batch_size = batch_size
		self.dataset_size = dataset_size
		self.v = torch.zeros(dataset_size,2,h,w)
		self.p = torch.zeros(dataset_size,1,h,w)
		self.v_cond = torch.zeros(dataset_size,2,h,w)# one could also think about p_cond...
		self.cond_mask = torch.zeros(dataset_size,1,h,w)
		self.flow_mask = torch.zeros(dataset_size,1,h,w)
		
		for i in range(dataset_size):
			self.reset_env(i)
		
		self.t = 0
	
	def reset_env(self,index):
		#CODO: add more different environemts
		self.v[index,:,:,:] = 0
		self.p[index,:,:,:] = 0
		
		self.cond_mask[index,:,:,:]=0
		self.cond_mask[index,:,0:3,:]=1
		self.cond_mask[index,:,(self.h-3):self.h,:]=1
		self.cond_mask[index,:,:,0:5]=1
		self.cond_mask[index,:,:,(self.w-5):self.w]=1
		
		if np.random.rand()<0.5:
			object_h = np.random.randint(5,20) # object height / 2
			object_w = np.random.randint(5,20) # object width / 2
			flow_v = 3*(np.random.rand()-0.5)*2
			object_y = np.random.randint(self.h//2-10,self.h//2+10)
			if flow_v>0:
				object_x = np.random.randint(self.w//4-10,self.w//4+10)
			else:
				object_x = np.random.randint(3*self.w//4-10,3*self.w//4+10)
			
			self.cond_mask[index,:,(object_y-object_h):(object_y+object_h),(object_x-object_w):(object_x+object_w)] = 1
			self.v_cond[index,1,10:(self.h-10),0:5]=flow_v
			self.v_cond[index,1,10:(self.h-10),(self.w-5):self.w]=flow_v
			
		else:
			flow_v = 3*(np.random.rand()-0.5)*2
			self.v_cond[index,1,10:(self.h//4),0:5]=flow_v
			self.v_cond[index,1,(3*self.h//4):(self.h-10),(self.w-5):self.w]=flow_v
			self.cond_mask[index,:,(self.h//3-2):(self.h//3+2),0:(3*self.w//4)] = 1
			self.cond_mask[index,:,(2*self.h//3-2):(2*self.h//3+2),(self.w//4):self.w] = 1
		
		self.flow_mask[index,:,:,:] = 1-self.cond_mask[index,:,:,:]
	
	def ask(self):
		self.indices = np.random.choice(self.dataset_size,self.batch_size)
		return self.v_cond[self.indices],self.cond_mask[self.indices],self.flow_mask[self.indices],self.v[self.indices],self.p[self.indices]
	
	def tell(self,v,p):
		self.v[self.indices,:,:,:] = v.detach()
		self.p[self.indices,:,:,:] = p.detach()
		
		self.t += 1
		if self.t % 20000/self.batch_size == 0:#ca x*batch_size steps until env gets reset
			i = (self.t/2)%self.dataset_size
			self.reset_env(int(i))



