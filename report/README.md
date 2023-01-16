# MiniProjet_IoT ESP avec camera

Le projet est sert à Comptage de personnes, avec un ESP32 Vroom sur platine TinyGS 2G4 (Mikrobus, I2C, SPI) + cam OV7670.

![camera](https://github.com/RJIN98/desktop-tutorial/blob/main/endpoint/pic/camera.jpg) 



## Objectifs


* Utilisation un module de caméra bon marché.
* Possibilité de se connecter au WiFi.
* Possibilité de visualiser le flux vidéo à partir d'un PC et d'un smartphone également.
* Comptage le nombreux de personne sur l'écran.



## Microcontroller ESP32


Le processeur est suffisamment rapide pour fournir l'horloge de la caméra (XCLK) - signal d'horloge supérieur à 10 MHZ. Il dispose de suffisamment de RAM pour capturer une image complète de 160x120x2 (QQVGA). Et il est équipé de capacités Wifi.



## Algorithme de streaming vidéo utilisant WebSocket

* Établissez une connexion Websocket entre le client du navigateur et ESP32.

* Le navigateur envoie un message "démarrer" à ESP32. Le message de démarrage contient le type de résolution d'image. 80x60, 160x120 ou 320x240.

* ESP32 commence à capturer des images et les envoie au navigateur à l'aide de webSocket.sendBIN. Le format d'image est RVB565. Par conséquent, la taille de trame totale est de (taille de trame en pixels) X 2 octets. Dans cette solution, la mémoire est suffisamment allouée pour tenir dans une trame de taille 160x120x2 octets (QQVGA).

* En cas de résolution 320x240, l'image est capturée 2 fois. Dans la première capture, la première moitié de la trame est envoyée et dans la seconde capture, la moitié restante est envoyée via le websocket. Un drapeau de début et un drapeau de fin sont utilisés pour informer le navigateur de l'ordre des trames partielles.

* Après avoir reçu le drapeau de fin, le navigateur demande ESP32 pour la trame suivante. ESP32 continue comme à l'étape 3.

##  Détails d'implémentation

1. Nous avons connecté le ESP32 à l'alimentation 5V. ESP32 démarre et se configure lui-même en tant que point d'accès et poste de travail. Il se connecte au meilleur réseau Wifi disponible parmi les options proposées.


2. Connexion le PC/téléphone intelligent au point d'accès Esp32AP

![172](https://github.com/RJIN98/desktop-tutorial/blob/main/endpoint/pic/connect_wifi.jpeg) 
![camera](https://github.com/RJIN98/desktop-tutorial/blob/main/endpoint/pic/esp32_wifi.jpeg) 


3. Ouvert le navigateur Google Chrome avec adresse 192.168.4.1. 

      QQ-VGA (120x160) est le canevas d'affichage par défaut.
      
      
![camera](https://github.com/RJIN98/desktop-tutorial/blob/main/endpoint/pic/QQ_VGA.jpeg) 

4. L'ESP32 agit comme un serveur Web qui sert une page Web contenant un programme javascript pour se connecter à ESP32 via Websocket et capturer des données d'image binaires pour les afficher sur HTML5 Canvas.


      L'adresse IP de la Station Wifi est fournie par l'ESP32 lors de l'ouverture de la prise Web. ESP32 envoie l'adresse IP de la station au client Web.         Nous pouvons donc aussi connecter avec le WiFi IP 172.20.10.12 par l'appareil partage du connection réseux.
      
      
      ![172_camera](https://github.com/RJIN98/desktop-tutorial/blob/main/endpoint/pic/172_camera.jpeg) 

      Ainsi, la caméra peut avoir deux IP. Correction de 192.168.4.1 lorsqu'il crée un point d'accès et une adresse IP de station attribués par le routeur       lorsque ESP32 se connecte à un autre réseau WiFi.

      

## Schéma électrique

Les connexions des broches des appareils peuvent également être trouvées dans le code et le shéma desous. Nous avons remarqué que les broches 34, 35, 36(VP), 39(VN) sont en lecture seule. Elles ne peuvent pas être utilisées pour I2C, l'horloge (XCLK). Les broches 0, 2 et 5 sont utilisées comme signaux de démarrage. Elles ne doivent pas être utilisées comme entrées pour éviter des problèmes lors de la programmation. La broche 5 est également reliée à la LED sur la carte. Les broches 6 à 11 sont à proscrire car elles sont reliées à la mémoire flash SPI connectée à l'ESP32.

![schema_electrique](https://github.com/RJIN98/desktop-tutorial/blob/main/endpoint/enclosure/electrique.png) 



## Les fonctionnalités prévues
Le projet est sert à Comptage de personnes, avec un ESP32 Vroom sur platine TinyGS 2G4 (Mikrobus, I2C, SPI) + cam OV7670.
### Celles réalisées 
Nous avons réussi d'afficher la video ( envoyé par camera )sur une adresse http ( crée par ESP32 ), et de choisir une taille d'image ( QVGA, QQVGA, QQQVGA). 

### Celles non réalisés
Faire le comptage de personnes dans l'image. 

## Problèmes rencontrés




## Video Demo

![Video](https://github.com/RJIN98/desktop-tutorial/blob/main/endpoint/video/video.mp4) 
