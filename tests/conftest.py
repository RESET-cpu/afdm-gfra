import pytest
from threadpoolctl import threadpool_limits

@pytest.fixture(autouse=True)
def single_thread():
    import torch
    torch.set_num_threads(1)
    with threadpool_limits(limits=1):yield
