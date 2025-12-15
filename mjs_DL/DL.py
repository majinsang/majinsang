import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np

class MinecraftBrain(nn.Module):
    def __init__(self):
        super(MinecraftBrain, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(5, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 5) 
        )

    def forward(self, x):
        return self.network(x)

def train():
    print("1. 데이터 로딩 및 분할 중...")
    try:
        df = pd.read_csv('dataset.csv')
    except FileNotFoundError:
        print("dataset.csv가 없습니다. make_data.py를 먼저 실행하세요.")
        return

    df = df.sample(frac=1).reset_index(drop=True)

    X = df[['log', 'planks', 'stick', 'has_pickaxe', 'near_tree']].values
    y = df['action_label'].values

    train_size = int(len(df) * 0.8)
    
    X_train = torch.FloatTensor(X[:train_size])
    y_train = torch.LongTensor(y[:train_size])
    
    X_val = torch.FloatTensor(X[train_size:])
    y_val = torch.LongTensor(y[train_size:])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"사용 디바이스: {device}")
    
    X_train = X_train.to(device)
    y_train = y_train.to(device)
    X_val = X_val.to(device)
    y_val = y_val.to(device)

    model = MinecraftBrain().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print(f"2. 학습 시작 (데이터: {len(df)}개, Epochs: 100)")
    
    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        output = model(X_train)
        loss = criterion(output, y_train)
        loss.backward()
        optimizer.step()
        
        model.eval()
        with torch.no_grad():
            val_output = model(X_val)
            val_loss = criterion(val_output, y_val)
            
            preds = torch.argmax(val_output, dim=1)
            correct = (preds == y_val).sum().item()
            accuracy = correct / len(y_val) * 100

        if (epoch+1) % 10 == 0:
            print(f"Epoch {epoch+1:3d}/100 | Train Loss: {loss.item():.4f} | Val Loss: {val_loss.item():.4f} | 검증 정확도: {accuracy:.2f}%")

    torch.save(model.state_dict(), "minecraft_brain.pth")
    print("3. 모델 저장 완료 (minecraft_brain.pth)")

if __name__ == "__main__":
    train()