import json
import csv

# JSON dosyasını oku
with open('words.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# CSV dosyasına sadece 'word' alanlarını yaz
with open('fixed_combined_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['words'])  # Başlık satırı

    for entry in data:
        writer.writerow([entry['word']])
