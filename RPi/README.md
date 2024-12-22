# RPi
Contient le code utilisé sur le RPi.
## Flask
Deprecated flask app for sys info. May be removed soon.
## LoRa - get_lora.py
Application python servant de relai entre LoRa et MQTT.
Les données de température et d'humidité sont reçues du Heltec en LoRa, et sont renvoyées en MQTT QoS 2 vers le broker MQTT.
## RFID - authentication.py
Application python gérant l'affichage sécurisé des données.
Lorsque une carte est scannée, vérifie si la carte est autorisée via un call API au serveur applicatif.
Une led rouge clignote en keepalive, et bascule vers la led verte de manière continue durant une session autorisée déclenchée par le scan d'une bonne carte RFID.
Un buzzer agit comme confirmation sonore que la carte est scannée.
