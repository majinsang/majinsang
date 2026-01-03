import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

ACTION_MAP = {
    "chop-tree": 0, "craft-planks": 1, "craft-sticks": 2, "craft-pickaxe": 3,
    "find-tree": 4, "craft-crafting-table": 5, "place-crafting-table": 6,
    "move-to-crafting-table": 7, "wait": 8
}

DATA_PATH = "minecraft_mlp_data_final.csv" 
MODEL_SAVE_PATH = "minecraft_agent_model.pth"

if not os.path.exists(DATA_PATH):
    print(f"에러: {DATA_PATH} 파일을 찾을 수 없습니다.")
    exit()

df = pd.read_csv(DATA_PATH)

X = df.drop('action_label', axis=1).values
y = df['action_label'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

class MinecraftDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
    def __len__(self): return len(self.X)
    def __getitem__(self, idx): return self.X[idx], self.y[idx]

train_loader = DataLoader(MinecraftDataset(X_train, y_train), batch_size=64, shuffle=True)
test_loader = DataLoader(MinecraftDataset(X_test, y_test), batch_size=64)

class MinecraftMLP(nn.Module):
    def __init__(self, input_size, num_classes):
        super(MinecraftMLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(128, 64),
            nn.ReLU(),
            

            nn.Linear(64, 32),
            nn.ReLU(),
            

            nn.Linear(32, num_classes)
        )
        
    def forward(self, x):
        return self.network(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MinecraftMLP(input_size=7, num_classes=len(ACTION_MAP)).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 100
print(f"학습을 시작합니다. (장치: {device}, 샘플 수: {len(df)})")

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    if (epoch+1) % 10 == 0:
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss/len(train_loader):.4f}, Accuracy: {accuracy:.2f}%")

torch.save({
    'model_state_dict': model.state_dict(),
    'scaler': scaler,
    'action_map': ACTION_MAP,
    'input_size': 7,
    'num_classes': 9
}, MODEL_SAVE_PATH)

print("-" * 30)
print(f"학습 완료! 모델이 '{MODEL_SAVE_PATH}'에 저장되었습니다.")