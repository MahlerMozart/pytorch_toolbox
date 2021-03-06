####################################################
##### This is focal loss class for multi class #####
##### University of Tokyo Doi Kento            #####
####################################################

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
# I refered https://github.com/clcarwin/focal_loss_pytorch/blob/master/focalloss.py

class MultiClassFocalLoss(nn.Module):

    def __init__(self, gamma=0, weight=None, size_average=True):
        super(MultiClassFocalLoss, self).__init__()

        self.gamma = gamma
        self.weight = weight
        self.size_average = size_average

    def forward(self, input, target):
        if input.dim()>2:
            input = input.view(input.size(0), input.size(1), -1)
            input = input.transpose(1,2)
            input = input.contiguous().view(-1, input.size(2)).squeeze()
        if target.dim()>2:
            target = target.view(target.size(0), target.size(1), -1)
            target = target.transpose(1,2)
            target = target.contiguous().view(-1, target.size(2))
        else:
            target = target.view(-1, 1)

        # compute the negative likelyhood
        logpt = F.log_softmax(input)
        logpt = logpt.gather(1,target.long())
        logpt = logpt.view(-1).squeeze()
        pt = nn.Softmax()(input)
        pt = pt.gather(1, target).view(-1)

        # implement the class balancing (Coming soon...)
        if self.weight is not None:
            if self.weight.type() != input.data.type():
                self.weight = self.weight.type_as(input.data)
            b_h_w, c = input.size()
            weight_tensor = Variable(self.weight[target.data.long().squeeze()])

        # compute the loss
        if self.weight is not None:
            loss = -1 * weight_tensor * (1-pt)**self.gamma * logpt
        else:
            loss = -1 * (1-pt)**self.gamma * logpt

        # averaging (or not) loss
        if self.size_average:
            return loss.mean()
        else:
            return loss.sum()
