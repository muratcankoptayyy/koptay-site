import requests

# 🔑 Tokeni BURAYA yapıştır (tırnak içinde!)
ACCESS_TOKEN = "EAAUtDMHauXgBPvQuK10Rn25FBlI0wc8ZCazGC8HSUHOnQIeJZCmkqOZBqO6kBIcczet2VAED0IsFjjhu8CCBJtczhi8Fswd5cxPM6Mkf3tvkPqQr7KblV8ydzxwMZA9P3jXwWDzVA5g4ZAt6dvdEselaYzlLFZBQ6PQejuo4sk9PSnGPZCXRTZC1QVm7ASUDieZBUVuDbSrj7rUXIywqo32cZCjbBRyOnuvfjqYWlbHQjX0Wb4O5MZD"

# 📱 WhatsApp Business test numaranın ID'si (Meta Developers panelinden kopyalayacaksın)
PHONE_NUMBER_ID = "855387697648523"  

# 🎯 Hedef telefon numarası (senin numaran)
TO_NUMBER = "905307111864"

url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
data = {
    "messaging_product": "whatsapp",
    "to": TO_NUMBER,
    "type": "text",
    "text": {"body": "Merhaba! WhatsApp API üzerinden gelen ilk mesaj 🎉"}
}

response = requests.post(url, headers=headers, json=data)

print("Durum Kodu:", response.status_code)
print("Cevap:", response.json())
