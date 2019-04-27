# Python ipaddress Modul Minitutorial

Die Klassenbibliothek von Python 3 hat das Modul `ipaddress`, siehe auch https://docs.python.org/3/howto/ipaddress.html.
Ein IP-Adressobjekt kann wie folgt aus einem String erzeugt werden:

```python
chris@host:~$ ipython3
Python 3.7.2 (default, Feb 12 2019, 08:15:36)
IPython 7.1.1 -- An enhanced Interactive Python. Type '?' for help.

In [01]: import ipaddress

In [02]: ipaddress.ip_address('192.0.2.1')
Out[02]: IPv4Address('192.0.2.1')
```

Eine IPv4-Adresse kann auch aus einem Integer (Ganzzahl) erzeugt werden, der sich im Bereich [0, 2<sup>32</sup> -1] befinden muss:
```python
In [08]: ipaddress.IPv4Address(0)
Out[08]: IPv4Address('0.0.0.0')

In [09]: ipaddress.IPv4Address(2**32 - 1)
Out[09]: IPv4Address('255.255.255.255')

In [10]: ipaddress.IPv4Address(726314239)
Out[10]: IPv4Address('43.74.172.255')
```

Was passiert bei ```ipaddress.IPv4Address(2**32)```?
```
AddressValueError: 4294967296 (>= 2**32) is not permitted as an IPv4 address
```


## Netzbereich-Objekte erzeugen


IP-Adressobjekte können auch für Netzbereiche angelegt werden. Dabei muss jedoch der Host-Anteil 0 sein, d.h. er darf nicht gesetzt sein:
```python
In [12]: ipaddress.ip_network('192.0.2.0/24')
Out[12]: IPv4Network('192.0.2.0/24')

In [13]: ipaddress.ip_network('192.0.2.1/24')
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
ValueError: 192.0.2.1/24 has host bits set
```

## Ein IP-Adressobjekt für eine Netzwerk-Schnittstelle erzeugen

Wenn ein IPv4-Adressobjekt für eine Netzwerk-Schnittstelle erzeugt werden soll, dann darf der Host-Anteil gesetzt sein. Die Notation 192.0.2.1/24 wird dabei von Netzwerk-Administratoren in der Regel so verstanden, dass damit der Host die IP-Adresse 192.0.2.1 erhält, die im Netzbereich 192.0.2.0/24 liegt. Alternativ kann die Netzmaske auch in dotted decimal notation angegeben werden.
```python
In [14]: ipaddress.ip_interface('192.0.2.1/24')
Out[14]: IPv4Interface('192.0.2.1/24')

In [15]: ipaddress.ip_interface('192.0.2.1/255.255.255.0')
Out[15]: IPv4Interface('192.0.2.1/24')
```


## Mit ipaddress-Objekten arbeiten

Eine häufige Frage lautet: Sei eine Schnittstellen-Notation gegeben (z.B. 192.0.2.1/24), wie lautet dann der Netzwerkbereich in Adressform?
```python
In [16]: host4 = ipaddress.ip_interface('192.0.2.1/24')

In [17]: host4
Out[17]: IPv4Interface('192.0.2.1/24')

In [18]: host4.network
Out[18]: IPv4Network('192.0.2.0/24')
```

Der Bereich ist also 192.0.2.0/24.

Eine andere Frage könnte darin bestehen, wie viele IP-Adressen von einem Netzbereich abgedeckt werden.
```python
In [19]: net4 = ipaddress.ip_network('192.0.2.0/24')
In [20]: net4.num_addresses
Out[20]: 256


In [21]: net4 = ipaddress.ip_network('62.0.0.0/19')
In [22]: net4.num_addresses
Out[22]: 8192
```

Die Netzwerk-Adresse (alle Bits des Hostanteils sind auf 0 gesetzt) und die Broadcast-Adresse (alle Bits des Hostanteils sind auf 1 gesetzt) sind spezielle Adressen. Diese kann man wie folgt ermitteln lassen:
```python
In [27]: net4 = ipaddress.ip_network('62.0.0.0/19')

In [28]: net4.network_address
Out[28]: IPv4Address('62.0.0.0')

In [29]: net4.broadcast_address
Out[29]: IPv4Address('62.0.31.255')
```

Die Netzmaske wird häufig in Anzahl gesetzter Bits angegeben, z.B. /19. Wenn dies umgerechnet werden soll in die dotted decimal notation, geht das z.B. wie folgt:
```python
In [30]: net4 = ipaddress.ip_network('62.0.0.0/19')
In [31]: net4.netmask
Out[31]: IPv4Address('255.255.224.0')
```

Manchmal muss man die tatsächlich benutzbaren IP-Adressen (alle Adressen mit Ausnahme der Netzwerk- sowie der Broadcast-Adresse) iterieren:
```python
In [23]: net4 = ipaddress.ip_network('62.0.0.0/23')
In [24]: for addr in net4.hosts():
    ...:     print(addr)
    ...:
62.0.0.1
62.0.0.2
62.0.0.3
62.0.0.4
...
62.0.1.251
62.0.1.252
62.0.1.253
62.0.1.254
```


