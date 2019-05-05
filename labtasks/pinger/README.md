# Pinger: ein eigenes `ping`

Um zu prüfen, ob ein Host auf der Internet-Schicht erreichbar ist, wird das Programm `ping` benutzt. In der Vorlesung wurde die grundlegende Funktionsweise von `ping` besprochen. 

Implementieren Sie eine eigene Variante des `ping`-Kommandos, das die Erreichbarkeit eines Hosts auf der Internet-Schicht (Vermittlungsschicht) prüft. Zur Bearbeitung empfiehlt sich beispielsweise ein Linux-Betriebssystem (z.B. [Ubuntu](https://www.ubuntu.com/download/desktop)) in einer virtuellen Maschine (z.B. mit [VirtualBox](https://www.virtualbox.org/)).


## Lernziele
* ICMP und IPv4 kennenlernen
* Ermitteln, wie der zu einem ICMP Echo Response zugehoerige Request ermittelt wird
* Annahmen über die Protokollfunktion mit Hilfe von eigenen Beobachtungen plausibilisieren


## Beobachtungen

Vergewissen Sie sich bevor Sie mit der Implementierung beginnen, dass Sie das Paketformat fuer ICMP Echo Anfragen und Antworten verstanden haben.
Das Paketformat (Echo or Echo Reply Message) wird in [RFC 792](https://tools.ietf.org/html/rfc792) ab Seite 13 beschrieben und hier wiedergegeben:
```
Echo or Echo Reply Message

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1   Bit
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Identifier          |        Sequence Number        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Data ...
   +-+-+-+-+-

 IP Fields:

   Addresses

      The address of the source in an echo message will be the
      destination of the echo reply message.  To form an echo reply
      message, the source and destination addresses are simply reversed,
      the type code changed to 0, and the checksum recomputed.

 ICMP Fields:

   Type

      8 for echo message;               // hieraus wird deutlich, dass Type = 8 sein muss fuer Echo-Anfragen

      0 for echo reply message.         // und Type = 0 fuer Echo-Antworten.

   Code

      0                                 // Code muss den Wert 0 haben

   Checksum

      The checksum is the 16-bit ones's complement of the one's
      complement sum of the ICMP message starting with the ICMP Type.
      For computing the checksum , the checksum field should be zero.
      If the total length is odd, the received data is padded with one
      octet of zeros for computing the checksum.  This checksum may be
      replaced in the future.

   Identifier

      If code = 0, an identifier to aid in matching echos and replies,
      may be zero.

   Sequence Number

      If code = 0, a sequence number to aid in matching echos and
      replies, may be zero.

   Description

      The data received in the echo message must be returned in the echo
      reply message.

      The identifier and sequence number may be used by the echo sender
      to aid in matching the replies with the echo requests.  For
      example, the identifier might be used like a port in TCP or UDP to
      identify a session, and the sequence number might be incremented
      on each echo request sent.  The echoer returns these same values
      in the echo reply.

      Code 0 may be received from a gateway or a host.

```

Sie sollen nun einige Beobachtungen machen, indem Sie ICMP-Verkehr mitschneiden und versuchen, Ihr Verständnis von ICMP zu plausibilisieren.
* Schneiden Sie dazu mit Wireshark einen Ping auf die IP-Adresse `8.8.8.8` mit dem existierenden `ping`-Kommando mit. 
```bash
atlas:~ chris$ ping  -c 10  8.8.8.8
PING 8.8.8.8 (8.8.8.8): 56 data bytes
64 bytes from 8.8.8.8: icmp_seq=0 ttl=123 time=10.952 ms
64 bytes from 8.8.8.8: icmp_seq=1 ttl=123 time=10.579 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=123 time=10.427 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=123 time=10.302 ms
64 bytes from 8.8.8.8: icmp_seq=4 ttl=123 time=10.286 ms
64 bytes from 8.8.8.8: icmp_seq=5 ttl=123 time=10.322 ms
64 bytes from 8.8.8.8: icmp_seq=6 ttl=123 time=10.251 ms
64 bytes from 8.8.8.8: icmp_seq=7 ttl=123 time=10.261 ms
64 bytes from 8.8.8.8: icmp_seq=8 ttl=123 time=10.143 ms
64 bytes from 8.8.8.8: icmp_seq=9 ttl=123 time=10.330 ms

--- 8.8.8.8 ping statistics ---
10 packets transmitted, 10 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 10.143/10.385/10.952/0.218 ms
atlas:~ chris$
```
* Speichern Sie das PCAP unter dem Namen `ping-success.pcap`. Oeffnen Sie das PCAP und inspizieren Sie die ICMP-Protokollfelder. Haben Sie verstanden, welche Funktion die Felder `Type`, `Code`, `Checksum`, `Identifier` und `Sequence number` haben?
* Schneiden Sie erneut ein PCAP (`ping-no-response.pcap`) eines `ping`-Aufrufs mit, diesmal allerdings auf eine IP-Adresse, die nicht erreichbar ist, z.B. `8.8.9.9`. Brechen Sie nach einiger Zeit ab. Oeffnen Sie das PCAP und erklaeren Sie sich die Beobachtungen. Was aendert sich hier von Paket zu Paket? Warum?
* Erklaeren Sie insbesondere die Funktion der Felder `Identifier` und `Sequence number`.

Nun sollten Sie die Kernbestandteile eines ICMP Echo-Pakets und seiner Antwort verstanden haben und beginnen mit Ihrer Implementierung.


## Implementierung mit scapy

[Scapy](https://scapy.readthedocs.io/en/latest/introduction.html) ist eine Bibliothek fuer Python, mit der man Netzwerkpakete vergleichsweise einfach erstellen, senden und empfangen kann. Im ersten Schritt bietet es sich an, dass Sie unter Verwendung von scapy eine Implementierung vornehmen.

Lesen und vervollstaendigen Sie die Code-Vorlage in der [Datei pinger_scapy_template.py](pinger_scapy_template.py).

Zur Kontrolle können Sie wiederum den Verkehr, den Ihre Implementierung erzeugt mitschneiden und per Wireshark analysieren. Prüfen Sie anhand des Mitschnitts, ob Ihre Implementierung ICMP-Pakete so versendet wie Sie es erwarten.


## Implementierung ohne scapy

Sie können auch ohne die scapy-Bibliothek implementieren. Allerdings sind dafür vermutlich Inhalte des kommenden Vorlesungskapitels zur Socketprogrammierung hilfreich.
