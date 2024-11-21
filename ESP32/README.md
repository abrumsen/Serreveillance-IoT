# ESP32
Contient le code utilisé sur l'ESP32.
## Déployer le firmware de l'ESP32
```bash
# Nécessite esptool.py:
pip install esptool
# Éffacer la flash:
esptool.py --port /dev/ttyUSB0 erase_flash
# Déployer le firmware:
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ESP32_GENERIC-20231005-v1.21.0.bin
```
## Les fichiers main.py et boot.py
Ces fichiers sont automatiquement exécutés au démarrage de l'ESP32. Ce pseudocode reprend leur schéma d'exécution:
```
do
    boot.py
while True:
    main.py
```