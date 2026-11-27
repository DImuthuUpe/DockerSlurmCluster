import os
import socket

import lightning as L
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class Regressor(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(32, 64), nn.ReLU(), nn.Linear(64, 1))

    def on_train_start(self):
        print(f"rank {self.global_rank}/{self.trainer.world_size} "
              f"(local {self.local_rank}) on {socket.gethostname()}", flush=True)

    def training_step(self, batch, _):
        x, y = batch
        loss = nn.functional.mse_loss(self.net(x), y)
        self.log("loss", loss, sync_dist=True, prog_bar=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-2)


def make_data():
    g = torch.Generator().manual_seed(0)  # identical dataset on every rank
    x = torch.randn(8192, 32, generator=g)
    y = x @ torch.randn(32, 1, generator=g) + 0.1 * torch.randn(8192, 1, generator=g)
    return DataLoader(TensorDataset(x, y), batch_size=64)


if __name__ == "__main__":
    torch.set_num_threads(int(os.environ.get("SLURM_CPUS_PER_TASK", 1)))
    trainer = L.Trainer(
        accelerator="cpu",
        strategy="ddp",
        num_nodes=int(os.environ["SLURM_NNODES"]),
        devices=int(os.environ["SLURM_NTASKS_PER_NODE"]),
        max_epochs=5,
        logger=False,
        enable_checkpointing=False,
    )
    trainer.fit(Regressor(), make_data())
    if trainer.is_global_zero:
        print(f"final loss: {trainer.callback_metrics['loss']:.4f}")