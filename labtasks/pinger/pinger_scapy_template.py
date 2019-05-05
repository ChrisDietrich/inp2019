#!/usr/bin/env python3

"""
Sendet eine Reihe an ICMP Echo-Anfragen an eine Ziel-IP-Adresse, wartet auf und verarbeitet die Antworten.

Es wird unter Linux beispielsweise wie folgt aufgerufen:

$ ./pinger_scapy.py 8.8.8.8
"""

import sys
import time
from scapy.all import *

MAX_NUM_PROBES=4

def pinger(dst):
    """
    Sendet ICMP Echo Anfragen und wartet auf Antworten. Gibt eine Zusammenfassung aller gesendeter Pakete aus.
    """
    icmpId = 0x4711
    for i in range(MAX_NUM_PROBES):
        # Erzeuge das ICMP Echo Anfrage-Paket (type=8).
        # Der Parameter seq ist ein Zaehler fuer die Anfrage-Pakete.
        icmpPkt = ICMP() # Hier muss ergaenzt werden!
        """
        scapy liefert die Klasse ICMP mit der ein ICMP-Paket erzeugt werden kann.
        Es hat die folgenden Felder:
        >>> i = ICMP()
        >>> i.default_fields
        {'addr_mask': '0.0.0.0',
         'chksum': None,
         'code': 0,			# 
         'gw': '0.0.0.0',
         'id': 0,
         'length': 0,
         'nexthopmtu': 0,
         'ptr': 0,
         'reserved': 0,
         'seq': 0,
         'ts_ori': 70195301,
         'ts_rx': 70195301,
         'ts_tx': 70195301,
         'type': 8,                     # echo request
         'unused': 0}

        Ueberlegen Sie, welche Felder Sie beim Erzeugen der ICMP-Instanz mit welchen
        Werten versehen muessen. Die Parameteruebergabe funktioniert mit
        Parametername=Parameterwert, also z.B.:
        ICMP(type=5, code=3, ...)
        """

        # Nun wird das Anfragepaket erzeugt. Die unterste Schicht, die wir hier angeben muessen 
        # ist IP (die Vermittlungsschicht). Um alle Schichten darunter kuemmert sich scapy bzw.
        # das Betriebssystem. 
        # Dem IP-Paket geben wir als Ziel-IP-Adresse den Wert der Variable dst an. Scapy kuemmert
        # sich automatisch darum, eine passende Quell-IP-Adresse zu verwenden.
        # Die Schichtung von Paketen erfolgt mit Hilfe des Schraegstrich-Operators '/'.
        ipPkt = IP(dst=dst)
        req = ipPkt/icmpPkt

        # Gib eine Zusammenfassung des fertigen Pakets aus
        req.show2()

        # Die einfachste Art der Implementierung nutzt die Funktion sr() von scapy.
        # Der Name sr() steht dabei fuer `send` und `receive`, also `sende` und `empfange`.
        # Informationen zu sr() finden Sie hier: 
        # https://scapy.readthedocs.io/en/latest/usage.html#send-and-receive-packets-sr
        # Warte maximal 5 Sekunden auf eine Antwort (timeout=5).
        ans, unans = sr(req, timeout=5, verbose=0)
        # Gib eine einzeilige Zusammenfassung von Anfrage und Antwort aus
        ans.summary()
        # Warte 0.9 Sekunden bis zur naechsten Iteration
        time.sleep(0.9)

# Ruft die Funktion pinger auf und reicht das erste Kommandozeilenargument (eine IP-Adresse) als Argument weiter
pinger(sys.argv[1])
