import pandas as pd

# Eski dosyayı doğru encoding ile oku (bozulmaması için Latin-1 veya cp1254 kullanabiliriz)
df = pd.read_csv("fixed_combined_data.csv", encoding="utf-8")

# Tekrar UTF-8 olarak kaydet
df.to_csv("fixed_combined_data.csv", index=False, encoding="utf-8")
