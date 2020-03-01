import os

import torch.optim
from torch import nn
from torch.utils.data import DataLoader
from torchvision.transforms import Compose

from models.CNNmodel import CNN2d
from training_loop import Trainer, VAETrainer
from utils import Initial_dataset_loader, get_fourier_coeff, PlotToImage, ShortenOrElongateTransform
import pandas as pd
import numpy as np


class Manager:
    def __init__(self, experiment_name, model, dataset, criterion, optimizer, scheduler=None, VAE=False, full=False, ortho=None, transforms=None):
        self.experiment_name = self._get_full_name(experiment_name)
        self.model = model
        self.datasets = os.path.join(os.getcwd(), "datasets", dataset)
        self.train_dataset_path = os.path.join(self.datasets, "train")
        self.train_dataset = Initial_dataset_loader(self.train_dataset_path, full=full, ortho=ortho, transforms=transforms)
        self.train_dataloader = DataLoader(self.train_dataset, 64, shuffle=True, num_workers=0)
        self.test_dataset_path = os.path.join(self.datasets, "test")
        self.test_dataset = Initial_dataset_loader(self.test_dataset_path, full=full, ortho=ortho)
        self.test_dataloader = DataLoader(self.test_dataset, 64, shuffle=True, num_workers=0)
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        if not VAE:
            self.trainer = Trainer(self.experiment_name, self.model, self.train_dataloader, self.test_dataloader, criterion,
                                   optimizer, scheduler)
        else:
            self.trainer = VAETrainer(self.experiment_name, self.model, self.train_dataloader, self.test_dataloader,
                                      optimizer, criterion, scheduler)

    def run(self, number_of_epochs):
        print("Starting experiment - " + self.experiment_name)
        self.max_f1, self.max_acc = self.trainer.train(number_of_epochs)

    def get_results(self):
        return [[self.experiment_name, "model in tensorboard", self.max_acc, self.max_f1]]

    def _get_full_name(self, name):
        max = 0
        for subdir in os.listdir(os.path.join(os.getcwd(), "experiments")):
            if name in subdir:
                var = int(subdir.split('_')[-1])
                if var > max:
                    max = var
        return name + "_" + str(max+1)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # group = parser.add_mutually_exclusive_group()
    # parser.add_argument("name", type=str, help="name of the experiment")
    # parser.add_argument("-m", "--model", type=str, help="Model to train ('FC', 'LSTM', 'VAE'")
    # parser.add_argument("-d", "--dataset", action=str, help="subfolder of the datasets folder")
    # args = parser.parse_args()
    name = "CNN2d"
    model = CNN2d((180, 180))
    dataset = "full_corrected_dataset"
    criterion = nn.CrossEntropyLoss()
    # optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9, nesterov=True, weight_decay=0.0001)
    # optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    # manager = Manager(name, model, dataset, criterion, optimizer, VAE=False, ortho=lambda x,y :np.polynomial.chebyshev.chebfit(x,y,7))
    transforms = Compose([
        PlotToImage((180,180), "cubic")
    ])
    manager = Manager(name, model, dataset, criterion, optimizer, transforms=transforms)
    manager.run(500)
    # cols = ["Nazwa", "Parametry", "Accuracy [%]", "F1 Score"]
    # result_dataframe = pd.DataFrame(columns=cols)
    # length = 500
    # rootdir = os.path.join(os.getcwd(), 'experiments')
    # dataset = "full_splitted_dataset"
    # datasets = os.path.join(os.getcwd(), "datasets", dataset)
    # train_dataset_path = os.path.join(datasets, "train")
    # train_dataset = Initial_dataset_loader(train_dataset_path)
    # weights = train_dataset.get_class_weights()
    # train_dataset = Initial_dataset_loader(train_dataset_path, full=True)
    # weights_5cls = train_dataset.get_class_weights()
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # weights_5cls = weights_5cls.to(device)
    # weights = weights.to(device)
    # model = FCmodel(178, 4, 32, 16)
    # name_full = "try"
    # criterion = nn.CrossEntropyLoss(weights)
    # optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    # manager = Manager(name_full, model, dataset, criterion, optimizer, VAE=False, ortho=get_fourier_coeff)
    # manager.run(10)
    # result_dataframe = result_dataframe.append(pd.DataFrame(manager.get_results(), columns=cols), ignore_index=True)
    # print(result_dataframe)