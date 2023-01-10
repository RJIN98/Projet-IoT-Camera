# MiniProjet_IoT ESP avec camera

Le projet est sert à Comptage de personnes, avec un ESP32 Vroom sur platine TinyGS 2G4 (Mikrobus, I2C, SPI) + cam OV7670.

![TinyGS 2G4](Camera Module OV7670 - Twins Chip 1-1000x1000.jpg)

## Objectifs


* Utilisation un module de caméra bon marché.
* Possibilité de se connecter au WiFi.
* Possibilité de visualiser le flux vidéo à partir d'un PC et d'un smartphone également.
* Le logiciel d'affichage doit être indépendant de la plate-forme
* Faible consommation d'énergie. Fonctionne sur batterie.



## Microcontroller
### ESP32


Le processeur est suffisamment rapide pour fournir l'horloge de la caméra (XCLK) - signal d'horloge supérieur à 10 MHZ. Il dispose de suffisamment de RAM pour capturer une image complète de 160x120x2 (QQVGA). Et il est équipé de capacités Wifi.



## Algorithme de streaming vidéo utilisant WebSocket

* Établissez une connexion Websocket entre le client du navigateur et ESP32.

* Le navigateur envoie un message "démarrer" à ESP32. Le message de démarrage contient le type de résolution d'image. 80x60, 160x120 ou 320x240.

* ESP32 commence à capturer des images et les envoie au navigateur à l'aide de webSocket.sendBIN. Le format d'image est RVB565. Par conséquent, la taille de trame totale est de (taille de trame en pixels) X 2 octets. Dans cette solution, la mémoire est suffisamment allouée pour tenir dans une trame de taille 160x120x2 octets (QQVGA).

* En cas de résolution 320x240, l'image est capturée 2 fois. Dans la première capture, la première moitié de la trame est envoyée et dans la seconde capture, la moitié restante est envoyée via le websocket. Un drapeau de début et un drapeau de fin sont utilisés pour informer le navigateur de l'ordre des trames partielles.

* Après avoir reçu le drapeau de fin, le navigateur demande ESP32 pour la trame suivante. ESP32 continue comme à l'étape 3.

##  Détails d'implémentation

1. Nous avons connecté le ESP32 à l'alimentation 5V. ESP32 démarre et se configure lui-même en tant que point d'accès et poste de travail. Il se connecte au meilleur réseau Wifi disponible parmi les options proposées.

```
void initWifiMulti()
{
    wifiMulti.addAP(ssid_AP_1, pwd_AP_1);
    wifiMulti.addAP(ssid_AP_2, pwd_AP_2);
    wifiMulti.addAP(ssid_AP_3, pwd_AP_3);

    Serial.println("Connecting Wifi...");

    while(wifiMulti.run() != WL_CONNECTED) {
       delay(5000);        
       Serial.print(".");
    }
    
    Serial.print("\n");
    Serial.print("WiFi connected : ");
    Serial.print("IP address : ");
    Serial.println(WiFi.localIP());
}
```
2. Connexion le PC/téléphone intelligent au point d'accès Esp32AP


3. Ouvert le navigateur Google Chrome avec adresse 192.168.4.1. 

      QQ-VGA (120x160) est le canevas d'affichage par défaut.


4. L'ESP32 agit comme un serveur Web qui sert une page Web contenant un programme javascript pour se connecter à ESP32 via Websocket et capturer des données d'image binaires pour les afficher sur HTML5 Canvas.

```
void serve() {
  WiFiClient client = server.available();
  if (client) 
  {
    //Serial.println("New Client.");
    String currentLine = "";
    while (client.connected()) 
    {
      if (client.available()) 
      {
        char c = client.read();
        //Serial.write(c);
        if (c == '\n') 
        {
          if (currentLine.length() == 0) 
          {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();
            client.print(canvas_htm);
            client.println();
            break;
          } 
          else 
          {
            currentLine = "";
          }
        } 
        else if (c != '\r') 
        {
          currentLine += c;
        }
        
      }
    }
    client.stop();

  }  
}
```

L'adresse IP de la Station Wifi est fournie par l'ESP32 lors de l'ouverture de la prise Web. ESP32 envoie l'adresse IP de la station au client Web.

Ainsi, la caméra peut avoir deux IP. Correction de 192.168.4.1 lorsqu'il crée un point d'accès et une adresse IP de station attribués par le routeur lorsque ESP32 se connecte à un autre réseau WiFi.
```
IPAddress localip;
  
  switch (type) {
    case WStype_DISCONNECTED:             // if the websocket is disconnected
      Serial.printf("[%u] Disconnected!\n", num);
      break;
    case WStype_CONNECTED: {              // if a new websocket connection is established
        IPAddress ip = webSocket.remoteIP(num);
        Serial.printf("[%u] Connected from %d.%d.%d.%d url: %s\n", num, ip[0], ip[1], ip[2], ip[3], payload);
//        rainbow = false;                  // Turn rainbow off when a new connection is established
           gWebSocketConnected = true;
           webSocket.sendBIN(0, &ip_flag, 1);
           localip = WiFi.localIP();
           sprintf(ipaddr, "%d.%d.%d.%d", localip[0], localip[1], localip[2], localip[3]);
           webSocket.sendTXT(0, (const char *)ipaddr);
           
      }
      break;
```
Le client Web Socket est un navigateur Web. Par conséquent, notre dispositif d'affichage est multiplateforme. Il peut être visualisé sur un PC et un smartphone prenant en charge le canevas HTML5. Le code suivant montre comment le client Web gère le socket Web.
```
    function initWebSocket() {
    
        if ("WebSocket" in window) {
            if (ws != null) {
                ws.close();
            } 
         	
            ws = new WebSocket('ws://' +  camera_ip + ':81/', ['arduino']);
	    if (ws == null) {
                document.getElementById("connecting").innerText = "Failed to connect to camera [ " + camera_ip + " ]";
                return;		
	    }
            ws.binaryType = 'arraybuffer';


            // open websocket 
            ws.onopen = function() {
                document.getElementById("canvas7670").style.visibility = "visible";
                document.getElementById("connecting").style.visibility = "hidden";
		document.getElementById("constatus").innerText = "Connected to " + ws.url;
		if (gcanvasid != null && gcanvasid != "") {
		    capture(gcanvasid);
		}
            };//ws.onopen
           
            // receive message 
            ws.onmessage = function (evt) { 
                var arraybuffer = evt.data;
                if (arraybuffer.byteLength == 1) {
                    flag  = new Uint8Array(evt.data); // Start Flag
                    if (flag == 0xAA) {
                       ln = 0;                   
                    }
                    if (flag == 0xFF) {
                       //alert("Last Block");
                    }

		    if (flag == 0x11) {
                       //alert("Camera IP");
                    }

		} else {

                    if (flag == 0x11) {
                       //alert("Camera IP " + evt.data);
		       camera_ip = evt.data;
		       document.getElementById("wifi-ip").innerText = camera_ip;
                       flag = 0;			    
		    } else {
                       var bytearray = new Uint8Array(evt.data);
                       display(bytearray, arraybuffer.byteLength, flag);
		    }
                }

            }; //ws.onmessage
            
            // close websocket
            ws.onclose = function() { 
                document.getElementById("canvas7670").style.visibility = "hidden";
                document.getElementById("connecting").style.visibility = "visible";
            }; //ws.onclose

            // websocket error handling
            ws.onerror = function(evt) {
                document.getElementById("canvas7670").style.visibility = "hidden";
                document.getElementById("connecting").style.visibility = "visible";
                document.getElementById("connecting").innerText = "Error " + evt.data;
		document.getElementById("constatus").innerText = "";
	    };
	    
        } else {
           // The browser doesn't support WebSocket
           alert("WebSocket NOT supported by your Browser!");
        }
    } 


```





PCB are made to integrate up to 2 Mikrobus modules including SX1280 technology. Mikrobus board is an add-on board socket standard made by [mikroe](https://www.mikroe.com/mikrobus). This makes the ground station adjustable and modular.
![MiKroBus module](https://github.com/thingsat/tinygs_2g4station/blob/main/MiKroBus_module%20-%20Pinout_specification.PNG) 

There are 2 different PCB version:
* Board_Tinysgs_2.4GHz_V1, which contains: ESP32 Wroom 32 + 2 Mikrobus modules + Grove connectors (RXTX,I2C,ANA)
* Board_Tinysgs_2.4GHz_V2, which contains: ESP32 Wroom 32 + 2 Mikrobus modules + Grove connectors (RXTX,I2C,ANA) + H-Bridges for driving stepper + Power supply

We made the board as modular as possible. It is possible to implement all modules as desired, as long as it respects the Mikrobus pin specification. Mikrobus module are connected by SPI, I2C, UART and more GPIO. They are both supplied by 3V and Mikrobus_1 is also supplied by 5V if desired. 2 SMA connector mount edge are available on board. Theyre a connected to a SMA male connector, which allows to plug any signal that we want through a SMA female connector.

Both Mikrobus boards are connected to the ESP 32 by SPI. They are using the same SPI bus (SPI_0).

PCB are made on [KiCad](https://www.kicad.org/), which is a free software for electronics circuit board design. PCBs has been manufactered by [JLCPCB](https://jlcpcb.com/).

##  Power

A [Power Bank NCR18650B Battery shield](https://www.amazon.com/Diymore-Lithium-Battery-Charging-Arduino/dp/B07SZKNST4) made for Arduino and ESP32 can be plugged under the board using the 4 screw holes.

##  Mikrobus adapters for SX1280 modules

The design of two Mikrobus adapters for SX1280 modules are currently provided by the project.

The pinouts of [Lambda80 SX1280 module adapter](./Mikrobus_Board_Lambda80C/) and the [EByte E28 SX1280 module adapter](./Mikrobus_Board_EbyteE28/) have some differences.

> Two versions of the E28 module exists: 12S & 20S

```
E28 module
AN  <-> Busy
INT <-> DIO1
PWM <-> DIO2

Lambda80C module
AN  <-> DIO1
INT <-> Busy
PWM <-> DIO2
```


##  Other Mikrobus adapters for SX1280 modules

* [ ] [Geditech](https://www.geditech.fr/)'s LoRa SX1280 adapter
* [ ] [Stuart Robinson's (GW7HPW) Breadboard Friendly Board for NiceRF SX1280 Module](https://www.tindie.com/products/stuartsprojects/breadboard-friendly-board-for-nicrf-sx1280-module/)
* [ ] [Stuart Robinson's (GW7HPW) Breadboard Friendly Board for Ebyte E28 Module](https://www.tindie.com/products/stuartsprojects/breadboard-friendly-board-for-ebyte-e28-module/)

## Other Mikrobus modules (for the second Mikrobus slot)

Have a look into the [shop](https://www.mikroe.com/shop)

* [ ] [Geditech](https://www.geditech.fr/)'s LoRa Microchip RN2483 (for 433 MHz and 868 MHz ISM bands)

## Firmware

Firmware are into [./Firmware](./Firmware).

## Off-the-shelves gateways for LoRa 2.4 GHz

Those gateways had 3 LoRa® 2.4GHz channels for Rx and 1 LoRa® 2.4GHz channels for Tx.

* [Multitech MTCDT + MCard MTAC-LORA-2G4-3](https://www.multitech.net/developer/software/lora/mtac-lora-2g4-3/)
* [SX1280Z3DSFGW1 LoRa® 2.4GHz 3 Channels Single SF Reference Design](https://fr.semtech.com/products/wireless-rf/lora-24ghz/sx1280zxxxxgw1) (included a removable mPCIe card).
* [Embit EMB-FEM2GW-O-2G4](http://www.embit.eu/products/gateways-2/emb-fem2gw-o-2g4/) (included a removable mPCIe card EMB-LR1280-mPCIe-4x).


## References

* [ESP32-DevKitC V4 Getting Started Guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/hw-reference/esp32/get-started-devkitc.html)
* [ESP32 Wroom 32 D/U Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf)

## Buy

### ESP32 Wroon 32U

* [ESP32-DevKitC-32U @ Aliexpress](https://fr.aliexpress.com/wholesale?SearchText=ESP32+Wroom+32U)
* [ESP32-DevKitC-32U @ Mouser](https://www.mouser.fr/ProductDetail/Espressif-Systems/ESP32-DevKitC-32U?qs=%252BEew9%252B0nqrCEVvpkdH%2FG5Q==)
* [ESP32-DevKit-LiPo @ Olimex](https://www.olimex.com/Products/IoT/ESP32/ESP32-DevKit-LiPo/open-source-hardware)

> **Important: ESP32 Wroon 32U had 38 pins and an UFL connector for an external (high gain and directive) antenna. ESP32 Wroon 32D had 38 pins and a PCB antenna. Choose ESP32 Wroon 32U for a better link margin.**

### SX1280 modules

* [LAMBDA80C-24D @ Farnell](https://fr.farnell.com/rf-solutions/lambda80c-24d/transceiver-2mbps-2-5ghz/dp/2988574?st=lambda80) (UFL connector + EM shield)
* [LAMBDA80C-24S @ Mouser](https://www.mouser.fr/ProductDetail/RF-Solutions/LAMBDA80C-24S?qs=17u8i%2FzlE89dhjIrlJ9FHg%3D%3D) (UFL connector + EM shield)
* [EByte E28-2G4M20S @ Aliexpress](https://fr.aliexpress.com/item/1005001812057589.html) (UFL connector + EM shield)

### PCB

* [Wuerth Elektronik](https://www.we-online.com/web/fr/wuerth_elektronik/start.php) 
* [JLCPCB](https://jlcpcb.com/)

### Headers and connectors
* [20-pin stackable headers (x2)](https://www.mouser.fr/ProductDetail/SparkFun/PRT-14311?qs=sGAEpiMZZMv0NwlthflBiwoz7B0w9MUDoIB50flBSMs%3D) for ESP32 : should be resized to 19 pins.
* [8-pin stackable headers (x2)](https://www.mouser.fr/ProductDetail/SparkFun/PRT-10007?qs=sGAEpiMZZMvShe%252BZiYheitG2EllKzxS98FBwaVjriqQ%3D) for Mikrobus modules.
* [Grove connectors (x3 but optional)](https://www.mouser.fr/ProductDetail/Seeed-Studio/110990030?qs=1%252B9yuXKSi8Dw9fpnq%252BdNzQ%3D%3D).

### Power (Optional)
* [Diymore 2x18650 Battery Pack @ Aliexpress](https://fr.aliexpress.com/item/33016661427.html)
* [DFRobot Solar Power Manager 5V](https://www.dfrobot.com/product-1712.html)
* [DFRobot Solar Power Manager Micro](https://www.dfrobot.com/product-1781.html)
* [Adafruit Universal USB / DC / Solar Lithium Ion/Polymer charger - bq24074](https://learn.adafruit.com/adafruit-bq24074-universal-usb-dc-solar-charger-breakout/design-notes)

### Misc
* [SuperAntennaz](https://wiki.satnogs.org/SuperAntennaz)

## Licenses

For PCB designs, the license is [Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

For Software, check the license into each directory.

## Todolist

* [x] PCB for ESP32 Wroom 32 (38 pins) + 2 Mikrobus modules + 3 groves connectors (RXTX,I2C,ANA)
* [ ] PCB for ESP32 Wroom 32 (38 pins) + 2 Mikrobus modules + 3 groves connectors (RXTX,I2C,ANA) + H-Bridges for driving stepper + Power supply
* [x] Mikrobus adapter for Lambda80 SX1280 module
* [x] Mikrobus adapter for EByte E28 SX1280 module
* [ ] Mikrobus adapter for [SX1280PATR24 module](https://fr.aliexpress.com/item/1005001598235704.html) 
* [ ] Mikrobus adapter for [Miromico FMLR STM SX1280 module](https://miromico.ch/portfolio/fmlr-8x-x-stlx/?lang=en)
* [ ] Mikrobus adapter for [NiceRF SX1280 module](https://stuartsprojects.github.io/2019/10/07/2-4ghz-nicerf-sx1280-lora-balloon-tracker-85km-achieved.html)
* [ ] Mikrobus adapter for [Microchip RN2483 module](https://www.microchip.com/en-us/product/RN2483)
* [ ] Mikrobus protoshield
* [x] [Arduino sketches](./Firmware/Arduino/SX1280) for ESP32 Wroom 32 + E28 Mikrobus module
* [x] [Arduino sketches](./Firmware/Arduino/SX1280) for ESP32 Wroom 32 + Lambda80 Mikrobus module
* [ ] [Arduino sketches](./Firmware/Arduino/SX1280) for Wio Terminal + Lambda80 Mikrobus module
* [ ] Move UART Grove connector for using Grove cable with ESP32-WROOM-32D (PCB antenna)
* [ ] TinyGS firmware for ESP32 Wroom 32 + E28 Mikrobus module
* [ ] TinyGS firmware for ESP32 Wroom 32 + Lambda80 Mikrobus module
* [ ] TinyGS firmware for ESP32 Wroom 32 + [Miromico FMLR STM SX1280 module](https://miromico.ch/portfolio/fmlr-8x-x-stlx/?lang=en)
* [ ] TinyGS firmware for ESP32 Wroom 32 + [LR1120 Dev Kit module](https://fr.semtech.com/products/wireless-rf/lora-edge/lr1120dvk1tbks) for such modulations and bands : LoRa SubGHz, LoRa 2.4GHz, LR-FHSS, S-Band (1.9-2.1GHz)
* [ ] TinyGS firmware for [Wio Terminal](https://wiki.seeedstudio.com/Wio-Terminal-Getting-Started/) + Lambda80 Mikrobus module
* [ ] Power consumption study with [X-NUCLEO-LPM01A](https://www.st.com/en/evaluation-tools/x-nucleo-lpm01a.html)
* [ ] RIOTOS firmware for ESP32 Wroom 32 + Lambda80 module (cubesat emulator)
* [ ] Test the [Geditech](https://www.geditech.fr/)'s LoRa Microchip RN2483 (for 433 MHz and 868 MHz ISM bands) on second slot.
* [ ] Add slots for I2C and UART grove connectors into the two Mikrobus slots (can be used when the Mikrobus slot is not used)
* [ ] Add slot for female header in order to plug a low-cost SDCard SPI breakout (useful for data logging)
* [ ] Add slot for female/male header in order to plug a low-cost DS1307/DS3231 breakout (useful for timestamping data log entries)
* [ ] Add extra slot for power sources (3V3, VCC)
* [ ] Add white label for DevEUI and serial number on silkscreen layer
* [ ] Add pin for IRQ on [GNSS PPS](https://en.wikipedia.org/wiki/Pulse-per-second_signal)
* [ ] Design Fritzing part for the station
* [x] add licenses

## Media

Here the picture of the board_V1, with or without modules. On last picture, a GPS, a magnetometer and a joystick are connected by grove connection.

![TinyGS 2G4](./images/gateway_tinygs_2g4-d-all_components.jpg)
Mounted PCB with Grove boards ([Grove Thumb Joystick](https://wiki.seeedstudio.com/Grove-Thumb_Joystick/), [Grove  LSM6DS3 Accelerometer Gyroscope](https://wiki.seeedstudio.com/Grove-6-Axis_AccelerometerAndGyroscope/), [Grove GPS](https://wiki.seeedstudio.com/Grove-GPS/)) and Lamdba80 and E28 module.
![TinyGS 2G4](./images/gateway_tinygs_2g4-a.jpg)
![TinyGS 2G4](./images/gateway_tinygs_2g4-c.jpg)
![250 PCB for TinyGS 2G4](./images/250_2g4_ground_stations.jpg)
![TinyGS 2G4 Mount Party @ IUT1 Grenoble Dept GEII](./images/tinygs2G4_mount_party.jpg)
