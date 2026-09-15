# divide_data.py
import torch
from torch.utils.data import random_split
import torchvision
import torchvision.transforms as transforms
import os
import argparse

def partition_dataset(num_clients: int, output_dir="./benchmark/dataset/partitions", data_dir="./benchmark/dataset/data"):
    os.makedirs(output_dir, exist_ok=True)
    abs_output_dir = os.path.abspath(output_dir)
    print(f"[INFO] Saving client partitions in directory: {abs_output_dir}")

    transform = transforms.Compose([transforms.ToTensor()])
    dataset = torchvision.datasets.CIFAR10(root=data_dir, train=True, download=False, transform=transform)
    total_size = len(dataset)
    part_size = total_size // num_clients

    lengths = [part_size] * num_clients
    remainder = total_size % num_clients
    for i in range(remainder):
        lengths[i] += 1

    partitions = random_split(dataset, lengths, generator=torch.Generator().manual_seed(42))
    for i, part in enumerate(partitions):
        partition_file = os.path.join(abs_output_dir, f"client_{i}.pt")
        torch.save(part, partition_file)
        print(f"[INFO] Saved partition {i} with {len(part)} samples at {partition_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_clients", type=int, default=3, help="Number of clients")
    parser.add_argument("--output_dir", type=str, default="./benchmark/dataset/partitions")
    args = parser.parse_args()
    partition_dataset(num_clients=args.num_clients, output_dir=args.output_dir)
