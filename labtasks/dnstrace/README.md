# DnsTrace: Eigene Implementierung eines iterativen DNS-Resolvers

Implementieren Sie einen iterativen DNS-Resolver. Der Resolver soll die bei der DNS-Auflösung durchgeführten Schritte (insbesondere die sog. Referrals) protokollieren.

Vergewissen Sie sich bevor Sie mit der Implementierung beginnen, dass Sie die Funktionsweise von DNS und insbesondere den Unterschied zwischen der rekursiven und der iterativen DNS-Auflösung verstanden haben. Eine Erläuterung des Unterschieds wird in der Vorlesung geliefert und ist auch auf [dieser Wikipedia-Seite](https://de.wikipedia.org/wiki/Rekursive_und_iterative_Namensaufl%C3%B6sung) dokumentiert.

## Lernziele
* Wireshark/tcpdump verwenden, um anhand eines Beispiel-PCAP die iterative DNS-Auflösung zu verstehen
* Annahmen über die Funktionsweise von DNS treffen und diese gegen die Beobachtungen im PCAP abgleichen/überprüfen
* Eigene Implementierung eines DNS-Resolvers unter Zuhilfenahme einer DNS-Paketbibliothek entwerfen und durchführen


## Beobachtungen

Beginnen Sie, indem Sie die zur Verfügung gestellte [PCAP-Datei dns.pcap](dns.pcap) mit Wireshark öffnen und die Beobachtungen nachvollziehen und erklären. Das PCAP wurde mitgeschnitten, als die Domain `chrisdietri.ch` iterativ aufgelöst wurde. Dabei sind folgende 4 Referrals (Verweise) aufgetreten:

```
chrisdietri.ch:                     F.ROOT-SERVERS.NET.         ->      a.nic.ch.
chrisdietri.ch:                     a.nic.ch.                   ->      dns2.registrar-servers.com.
    dns2.registrar-servers.com.:    C.ROOT-SERVERS.NET.         ->      c.gtld-servers.net.
    dns2.registrar-servers.com.:    c.gtld-servers.net.         ->      a1.verisigndns.com.
```

1. Woher stammt die IP-Adresse des Nameservers 192.5.5.241, an den im ersten Paket des PCAPs die DNS-Anfrage geschickt wird?
Tipp: Führen Sie eine Rückwärtsauflösung der IP-Adresse 192.5.5.241 mit folgendem Befehl durch:
```
dig +short -x 192.5.5.241
```
Gibt Ihnen die Domain einen Hinweis?

2. Untersuchen Sie das Paket Nr. 2, insbesondere die DNS-Informationen. Warum ist die `Answer`-Sektion leer? Wozu dienen die Einträge der `Authority`-Sektion? Tipp: Wie funktioniert ein Referral (ein Verweis)?

3. In Paket 2, welche Informationen sind in der `Additional`-Sektion enthalten? Tipp: Sagt Ihnen der Begriff `Glue Records` etwas?

4. Versuchen Sie alle 4 Referrals (Verweise), die oben genannt sind, im PCAP nachzuvollziehen. Geben Sie dabei pro Referral (Verweis) an, welches Paket den jeweiligen Referral bedingt. 

Beispiel: 
> Das erste Referral erfolgt durch Paket Nr. 2, da hier die `Answer`-Sektion leer ist und in der `Authority`-Sektion Nameserver-Records (Typ `NS`) zu finden sind. Die `Authority`-Sektion enthält insgesamt 8 NS-Records (`a.nic.ch` bis `h.nic.ch`), von denen der Anfrager sich einen aussuchen kann. Um zu einem NS-Record (z.B. `a.nic.ch`) die dazugehörige IP-Adresse zu erhalten, sind in der `Additional`-Sektion Informationen gegeben, die einem Nameserver eine (oder mehrere) IP-Adressen zuweisen, z.B. `a.nic.ch` zu 130.59.31.41.

5. Gehen Sie analog für alle Referrals vor. Was ist das Besondere an dem Referral `a.nic.ch.  ->  dns2.registrar-servers.com.`? Schauen Sie sich in dem dazugehörigen DNS-Paket insbesondere die `Additional`-Sektion an.



## Implementierung

Die Implementierung soll in Python 3 erfolgen und die [dnspython-Bibliothek](http://www.dnspython.org/) verwenden. 



## Testfälle

Testen Sie Ihre Implementierung, indem Sie die folgenden Domains auflösen und dabei die bereitgestellten Ausgaben ableichen:

* chrisdietri.ch
* www.internet-sicherheit.de

Die Ausgabe Ihres Tools könnte dabei ähnlich zur folgenden sein:
```
$ ./dnstrace.py chrisdietri.ch
chrisdietri.ch                  : K.ROOT-SERVERS.NET.              (193.0.14.129   )   ->   a.nic.ch.                        (130.59.31.41)
chrisdietri.ch                  : a.nic.ch.                        (130.59.31.41   )   ->   dns2.registrar-servers.com.      (no glue record for dns2.registrar-servers.com.)
  dns2.registrar-servers.com.   : M.ROOT-SERVERS.NET.              (202.12.27.33   )   ->   a.gtld-servers.net.              (192.5.6.30)
  dns2.registrar-servers.com.   : a.gtld-servers.net.              (192.5.6.30     )   ->   a1.verisigndns.com.              (209.112.113.33)
  dns2.registrar-servers.com.   : answer ip=216.87.152.33      dns2.registrar-servers.com. -> 216.87.152.33
chrisdietri.ch                  : answer ip=81.169.252.150     chrisdietri.ch. -> 81.169.252.150
```

In der ersten Zeile ist das Referral vom Root-Nameserver `K.ROOT-SERVERS.NET.` mit der IP-Adresse 193.0.14.129 auf den Nameserver `a.nic.ch` zu sehen. Komfortablerweise wird hier ein Glue Record mitgeliefert, d.h. die Domain `a.nic.ch` zeigt auf die IP-Adresse 130.59.31.41.

Die zweite Zeile zeigt ein Referral von `a.nic.ch.` (IP-Adresse 130.59.31.41) auf `dns2.registrar-servers.com.`. Hier ist allerdings kein Glue Record vorhanden. Daher muss das Tool nun zunächst `dns2.registrar-servers.com.` auflösen. Dies geschieht in den 3 folgenden, eingerückten Zeilen.

Anschließend wird wieder die Auflösung von `chrisdietri.ch` fortgeführt.
