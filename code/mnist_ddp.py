import os
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim
from torch.nn.parallel import DistributedDataParallel as DDP
from torchvision import datasets, transforms


def run():
    # 1. 初始化环境变量
    dist.init_process_group(backend="gloo")
    local_rank = int(os.environ["LOCAL_RANK"])
    torch.cuda.set_device(local_rank)

    # 2. 准备数据
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    # 使用 DistributedSampler 自动分配数据
    sampler = torch.utils.data.distributed.DistributedSampler(dataset)
    loader = torch.utils.data.DataLoader(dataset, batch_size=64, sampler=sampler)

    # 3. 定义模型并包装 DDP
    model = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10)).to(local_rank)
    ddp_model = DDP(model, device_ids=[local_rank])
    optimizer = optim.SGD(ddp_model.parameters(), lr=0.01)

    # 4. 训练循环
    for epoch in range(2):
        sampler.set_epoch(epoch)
        for data, target in loader:
            optimizer.zero_grad()
            output = ddp_model(data.to(local_rank))
            loss = nn.functional.cross_entropy(output, target.to(local_rank))
            loss.backward()
            optimizer.step()

    print("Training finished!")
    dist.destroy_process_group()


if __name__ == "__main__":
    run()
