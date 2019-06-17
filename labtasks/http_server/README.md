# HttpServer: Eigene Implementierung eines HTTP-Servers

Implementieren Sie einen minimalen HTTP/1.1-Server (bzw. eine Teilmenge von HTTP/1.1). Der Server soll auf TCP-Port 80 lauschen, HTTP-Requests (z.B. eines Browsers) entgegen nehmen und angeforderte Dateien aus einem angegebenen Wurzelverzeichnis (sog. Document Root) servieren.
Als Beispiel können Sie das Unterverzeichnis `documentRoot` benutzen.

Vergewissen Sie sich bevor Sie mit der Implementierung beginnen, dass Sie die Funktionsweise von HTTP verstanden haben.

## Lernziele
* Wireshark/tcpdump verwenden, um anhand eines Beispiel-PCAP reguläres HTTP in Version 1.1 zu verstehen
* Annahmen über die Funktionsweise von HTTP treffen und diese gegen die Beobachtungen im PCAP abgleichen/überprüfen
* Eigene Implementierung eines HTTP-Servers entwerfen und durchführen
* Erfahrungen im Umgang mit nicht vertrauenswürdigen Eingaben vom Netzwerk sammeln


## Beobachtungen

Beginnen Sie, indem Sie die zur Verfügung gestellte [PCAP-Datei http.pcap](http.pcap) mit Wireshark öffnen und die Beobachtungen nachvollziehen und erklären.

* Werden persistente Verbindungen genutzt?
 * Wenn ja, woran erkennen Sie das? Welche Header sind dafür ausschlaggebend?
* Wie wird der Header `Content-Length` benutzt?


## Implementierung

Die Implementierung soll in Python 3 erfolgen und die [Socket-Bibliothek](https://docs.python.org/3/library/socket.html) verwenden. 

Den Detailgrad an Implementierung von HTTP/1.1 bestimmen Sie selbst. Mindestens die `GET`-Methode muss implementiert werden. Bei nicht vorhandenen URIs soll ein 404-Fehler zurueckgegeben werden, der als HTML mitteilt, dass die angeforderte Seite nicht gefunden wurde.
* Setzen Sie mindestens die folgenden Header
 * `Content-Length`
 * `Last-Modified`
 * `Date`
 * `Expires`
 * `Connection`
 * `Server`
 * `Cache-Control`
 * `ETag`


