# RPi
Contient le code utilisé sur le RPi.
## get_lora.py
Application python servant de relai entre LoRa et MQTT.
Les données de température et d'humidité sont reçues du Heltec en LoRa, et sont renvoyées en MQTT QoS 2 vers le broker MQTT.
## main_interface.py
Application python gérant l'affichage sécurisé des données.
Lorsque une carte est scannée, vérifie si la carte est autorisée via un call API au serveur applicatif.
Une led rouge clignote en keepalive.
Un buzzer agit comme confirmation sonore que la carte est scannée.
## greenhouse-interface.service
Service systemctl s'occupant de lancer main_interface.py au démarrage.
## lora-relay.service
Service systemctl s'occupant de lancer get_lora.py au démarrage.