# download_data.py
import torchvision
import torchvision.transforms as transforms
import os

def download_cifar10(data_dir="./benchmark/dataset/data/cifar"):
    os.makedirs(data_dir, exist_ok=True)
    transform = transforms.Compose([transforms.ToTensor()])
    torchvision.datasets.CIFAR10(root=data_dir, train=True, download=True, transform=transform)
    torchvision.datasets.CIFAR10(root=data_dir, train=False, download=True, transform=transform)
    print(f"CIFAR10 downloaded successfully in '{data_dir}'")

if __name__ == "__main__":
    download_cifar10()
