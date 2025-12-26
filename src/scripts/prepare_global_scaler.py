import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Wczytaj główny zbiór danych (wszystkie artykuły)
df = pd.read_csv('data/interim/articles_with_score_df.csv')

# Logarytmowanie cytowań przed skalowaniem
# aby rozkład potęgowy nie "zbił" wszystkich wyników do zera.
df['n_citation_log'] = np.log1p(df['n_citation'])

scaler = MinMaxScaler()
scaler.fit(df[['year', 'n_citation_log', 'gov_score']])

# Zapis scaler'a
joblib.dump(scaler, 'models/global_scaler.pkl')
print("Global Scaler saved successfully.")