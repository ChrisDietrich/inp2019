# Spurleser: Eigene traceroute-Implementierung

Mit Hilfe des Programms `traceroute` wird der Pfad nachvollzogen, den TCP/IP-Pakete im Internet (wahrscheinlich) nehmen. Implementieren Sie Ihr eigenes `traceroute` mit dem Namen `spurleser`.

Implementieren Sie eine eigene Variante des traceroute-Kommandos, das den Pfad zu einem Internet-Host auf der Internet-Schicht (Vermittlungsschicht) ermittelt.

Vergewissen Sie sich bevor Sie mit der Implementierung beginnen, dass Sie die Funktionsweise von `traceroute` verstanden haben.

## Lernziele
* [Wireshark](https://www.wireshark.org)/[tcpdump](https://www.tcpdump.org) verwenden, um sich selbst ein Beispiel-PCAP aufzunehmen wenn das reguläre `traceroute` verwendet wird
* Auswirkungen von IP TTL == 0 verstehen
* Annahmen über die Funktionsweise von `traceroute` treffen und diese gegen die Beobachtungen im PCAP abgleichen/überprüfen
* Eigene Implementierung eines `traceroute`-ähnlichen Programms entwerfen und durchführen
* Raw-Sockets kennenlernen und Programmierung mit Raw-Sockets
* Zuordnung von eingehenden ICMP-Paketen zu vorher gesendeten Paketen herstellen


## Beobachtungen

Beginnen Sie, indem Sie die zur Verfügung gestellte [PCAP-Datei traceroute_8.8.8.8_macos.pcap](traceroute_8.8.8.8_macos.pcap) mit Wireshark öffnen und die Beobachtungen nachvollziehen und erklären.

Das Beispiel-PCAP `traceroute_8.8.8.8_macos.pcap` wurde auf macOS aufgenommen, indem folgender Befehl abgesetzt wurde:
```bash
$ traceroute -n 8.8.8.8
traceroute to 8.8.8.8 (8.8.8.8), 64 hops max, 52 byte packets
 1  192.168.27.1     3.039 ms  1.799 ms  1.824 ms
 2  84.59.211.1      6.066 ms  5.830 ms  6.136 ms
 3  88.79.20.14      6.029 ms  6.337 ms
    88.79.20.10      5.776 ms
 4  188.111.173.152  6.532 ms
    88.79.20.28      6.127 ms  5.434 ms
 5  188.111.129.20   6.441 ms
    188.111.129.26   6.341 ms
    188.111.129.20   6.537 ms
 6  145.254.2.189   10.342 ms
    145.254.2.205   12.582 ms  12.892 ms
 7  72.14.222.128   11.699 ms  12.666 ms  14.444 ms
 8  108.170.241.129 14.258 ms
    108.170.241.161 10.205 ms
    108.170.241.129 11.857 ms
 9  209.85.244.55   12.313 ms
    216.239.51.171  15.563 ms
    216.239.51.3    10.400 ms
10  * 8.8.8.8       15.749 ms  12.104 ms
```

In dem PCAP ist zu erkennen, dass der UDP-Zielport inkrementiert wird, sodass jede Probe einen eindeutigen Zielport hat (beginnend ab 33435). Erklären Sie, warum jede Probe einen eindeutigen Zielport verwendet.

Außerdem fällt auf, dass pro TTL-Wert jeweils 3 Proben verschickt werden. Können Sie hierfür eine Erklärung geben? Warum reicht es evtl. nicht nur eine Probe pro TTL-Wert zu nutzen?

Darüber hinaus gibt es den Fall, dass `TTL exceeded` Nachrichten von **verschiedenen** IP-Adressen zurückgeschickt werden, z.B. bei TTL=3 sind es 88.79.20.14 und 88.79.20.10. Was könnte der Grund dafür sein? Würde man nicht erwarten, dass die TTL immer beim gleichen Router auf dem Weg ausläuft? 

Tipp: Hier haben die Proben vermutlich unterschiedliche Pfade/Routen im Internet genommen, sodass die TTL bei **unterschiedlichen** Routern ausgelaufen ist (TTL exceeded).

Kam es bei der Messung zu Paketverlust? Ja, denn das Paket mit der Nr. 55 (192.168.27.50:53469 -> 8.8.8.8:33462) erhält nie eine Antwort. Es könnte also sein, dass dieses Paket auf dem Weg verloren ging.


## Implementierung

Fuer die Implementierung stehen mehrere Varianten mit unterschiedlichen Schwierigkeitsgraden zur Verfuegung.
1. Implementierung mit scapy
2. Implementierung in Python mit Raw Sockets
3. Implementierung in Python mit Raw Sockets und eigener Zuordnung von Antwort zu Anfrage


### Variante 1: Implementierung mit scapy

Das Skript `spurleser_scapy.py` enthält eine minimale Implementierung mit scapy. Allerdings wird hier auch das Zuordnen abgenommen (über die Funktion `sr1()`), sodass dies auch nicht die beste Variante aus didaktischer Sicht ist. Trotzdem eignet sie sich zum Warmwerden.

```bash
$ sudo ./spurleser_scapy.py
    1 192.168.27.1
    2 84.59.211.1
    3 88.79.20.10
    4 188.111.173.152
    5 188.111.129.24
    6 145.254.2.205
    7 72.14.222.128
    8 108.170.241.140
    9 216.239.42.213
   10 209.85.244.159
   11 108.170.236.248
   12 108.170.252.1
   13 72.14.232.35
Done! 172.217.22.78
```


### Variante 2: Implementierung in Python mit Raw Sockets

Diese Loesung ist vermutlich erst nach Behandlung des Kapitels Netzwerk-Programmierung verständlich.

Das Skript `spurleser_rawsocket_easy.py` ist eine minimale Implementierung, allerdings aus didaktischer Sicht nicht die Beste, da hier das Problem umgangen wird, dass eine eingehende ICMP-Antwort einem vorher gesendeten UDP-Request zugeordnet werden muss. Dies wird vom Kernel erledigt, indem der ICMP Raw Socket auf einen Port gebunden wird. Obwohl Raw Sockets konzeptionell eigentlich keine Ports kennen (da Ports ein Konstrukt der Transportschicht sind), wird das Binden auf einen Port als Mechanismus genommen, damit der Kernel die Zuordnungsarbeit abnimmt.

Das PCAP `spurleser_rawsocket_easy.pcap` enthält einen Paketmitschnitt, als das Skript `./spurleser_rawsocket_easy.py` wie folgt aufgerufen wurde:
```bash
$ sudo ./spurleser_rawsocket_easy.py
    1 fritz.box (192.168.27.1)
    2 dslb-084-059-211-001.084.059.pools.vodafone-ip.de (84.59.211.1)
    3 88.79.20.14 (88.79.20.14)
    4 188.111.173.152 (188.111.173.152)
    5 188.111.129.20 (188.111.129.20)
    6 145.254.2.205 (145.254.2.205)
    7 72.14.222.128 (72.14.222.128)
    8 108.170.241.237 (108.170.241.237)
    9 216.239.40.231 (216.239.40.231)
   10 108.170.236.121 (108.170.236.121)
   11 108.170.236.248 (108.170.236.248)
   12 108.170.252.1 (108.170.252.1)
   13 66.249.95.29 (66.249.95.29)
   14 fra15s16-in-f46.1e100.net (172.217.22.46)
Reached the destination host 172.217.22.46
```


### Variante 3: Implementierung in Python mit Raw Sockets und eigener Zuordnung von Antwort zu Anfrage

Das Skript `spurleser_rawsocket_hard.py` ist eine weitere Implementierung, bei der eine eingehende ICMP-Antwort einem vorher gesendeten UDP-Request zugeordnet wird (mittels des ursprünglichen Quellports). Bei dieser Variante ist der Lerneffekt vermutlich am höchsten.

```bash
$ sudo ./spurleser_rawsocket_hard.py 8.8.8.8
DEBUG:__main__:Sent from port=63076 ttl=1 to 8.8.8.8:33435
DEBUG:__main__:Received 64 bytes from 192.168.27.1
 1    192.168.27.1
DEBUG:__main__:Sent from port=63076 ttl=2 to 8.8.8.8:33436
DEBUG:__main__:Received 64 bytes from 84.59.211.1
 2    84.59.211.1
DEBUG:__main__:Sent from port=63076 ttl=3 to 8.8.8.8:33437
DEBUG:__main__:Received 64 bytes from 88.79.20.10
 3    88.79.20.10
DEBUG:__main__:Sent from port=63076 ttl=4 to 8.8.8.8:33438
DEBUG:__main__:Received 64 bytes from 188.111.173.152
 4    188.111.173.152
DEBUG:__main__:Sent from port=63076 ttl=5 to 8.8.8.8:33439
DEBUG:__main__:Received 96 bytes from 188.111.129.22
 5    188.111.129.22
DEBUG:__main__:Sent from port=63076 ttl=6 to 8.8.8.8:33440
DEBUG:__main__:Received 96 bytes from 145.254.2.189
 6    145.254.2.189
DEBUG:__main__:Sent from port=63076 ttl=7 to 8.8.8.8:33441
DEBUG:__main__:Received 56 bytes from 72.14.222.128
 7    72.14.222.128
DEBUG:__main__:Sent from port=63076 ttl=8 to 8.8.8.8:33442
DEBUG:__main__:Received 96 bytes from 108.170.241.161
 8    108.170.241.161
DEBUG:__main__:Sent from port=63076 ttl=9 to 8.8.8.8:33443
DEBUG:__main__:Received 64 bytes from 108.170.236.219
 9    108.170.236.219
DEBUG:__main__:Sent from port=63076 ttl=10 to 8.8.8.8:33444
DEBUG:__main__:Received 64 bytes from 8.8.8.8
Reached destination 8.8.8.8 at ttl=10
```

