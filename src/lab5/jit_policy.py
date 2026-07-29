"""TorchScript-compatible PointNav policy — pure PyTorch, no external deps."""
import torch
import torch.nn as nn


class _ResBlock(nn.Module):
    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.relu = nn.ReLU(inplace=False)

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        return self.relu(out + identity)


def _make_layer(inplanes, planes, blocks, stride):
    ds = nn.Sequential(
        nn.Conv2d(inplanes, planes, 1, stride=stride, bias=False),
        nn.BatchNorm2d(planes))
    return nn.Sequential(
        *([_ResBlock(inplanes, planes, stride, downsample=ds)] +
          [_ResBlock(planes, planes) for _ in range(1, blocks)]))


class JITPolicy(nn.Module):
    def __init__(self, in_channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, 32, 7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(32)
        self.relu = nn.ReLU(inplace=False)
        self.maxpool = nn.MaxPool2d(3, stride=2, padding=1)
        self.layer1 = _make_layer(32, 32, 2, stride=1)
        self.layer2 = _make_layer(32, 64, 2, stride=2)
        self.layer3 = _make_layer(64, 128, 2, stride=2)
        self.layer4 = _make_layer(128, 256, 2, stride=2)
        self.cmp = nn.Sequential(
            nn.Conv2d(256, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=False))
        self.avg = nn.AdaptiveAvgPool2d((4, 4))
        self.visual_fc = nn.Sequential(
            nn.Linear(2048, 512),
            nn.ReLU(inplace=False))
        self.tgt_emb = nn.Linear(3, 32)
        self.prev_emb = nn.Embedding(5, 32)
        self.gru = nn.GRU(576, 512, 3)
        self.action_head = nn.Linear(512, 4)

    def forward(self, x, goal, hx):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        if x.shape[-1] > 4:
            x = self.cmp(x)
        x = self.avg(x)
        x = self.visual_fc(x.flatten(1))
        g = self.relu(self.tgt_emb(goal))
        a = self.prev_emb(torch.zeros(1, dtype=torch.long, device=x.device))
        _, h_new = self.gru(torch.cat([x, g, a], dim=-1).unsqueeze(0), hx)
        return self.action_head(h_new[-1]), h_new
