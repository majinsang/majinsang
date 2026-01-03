import pandas as pd
df = pd.read_csv("minecraft_mlp_data_final.csv")
print(df['action_label'].value_counts())