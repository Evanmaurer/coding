import torch
import torch.nn as nn

class SystemPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1, dropout=0.0):
        super(SystemPredictor, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

def load_trained(model_path, meta, device='cpu'):
    model = SystemPredictor(meta["input_size"], meta["hidden_size"],
                            meta["output_size"], meta.get("num_layers", 1))
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state)
    model.to(device).eval()
    return model