# Ubuntu
Contient le code utilisé sur les VMs Ubuntu.
## SRV_APP
Le serveur applicatif de Horticonnect. Suivant une architecture microservices, ses différentes composantes sont orchestrées via docker-compose.
Fait également tourner un Flask app qui permet l'auth des cartes RFID.
## SRV_MAINT
La machine permettant d'accéder en VNC au RPi. Elle joue donc le rôle de machine de maintenance.
