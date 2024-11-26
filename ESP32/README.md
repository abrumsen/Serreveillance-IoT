# ESP32
Contient le code utilisé sur l'ESP32. Tout les requirements devraient être repris dans `requirements.txt`
## Déployer le firmware de l'ESP32
```bash
# Nécessite esptool.py:
pip install esptool
# Éffacer la flash:
esptool.py --port /dev/ttyUSB0 erase_flash
# Déployer le firmware:
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ESP32_GENERIC-20231005-v1.21.0.bin
```
## Se connecter en série
```bash
# Nécessite picocom, ainsi que de faire partie du groupe uucmp sur Arch Linux.
picocom --b 115200 /dev/ttyUSB0
```
## Gérer les fichiers de l'ESP32
```bash
# Nécessite ampy:
pip install adafruit-ampy
# Commandes utiles:
ampy -p /dev/ttyUSB0 ls
ampy -p /dev/ttyUSB0 get boot.py
ampy -p /dev/ttyUSB0 put monprogramme.py main.py
# Commandes pour notre setup:
ampy -p /dev/ttyUSB0 put main.py main.py
```
### Les fichiers main.py et boot.py
Ces fichiers sont automatiquement exécutés au démarrage de l'ESP32. Ce pseudocode reprend leur schéma d'exécution:
```
do
    boot.py
while True:
    main.py
```
## Pinout
![Pinout ESP32](ESP32Pinout.png)