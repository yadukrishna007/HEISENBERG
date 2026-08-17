import torch

print("PyTorch Version:", torch.__version__)
print("CUDA Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device Name:", torch.cuda.get_device_name(0))
    print("Device Count:", torch.cuda.device_count())
    print("VRAM Allocated (MB):", torch.cuda.memory_allocated() / (1024 * 1024))
    print("VRAM Reserved (MB):", torch.cuda.memory_reserved() / (1024 * 1024))
