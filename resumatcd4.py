import logging
import serial
from crccheck.crc import Crc16Buypass
import struct


# Adresse Anzahl MenueEntry MenueName_de
# 0x0000 0x0002 00.00 Versions-Nummer
# 0x0002 0x0003 00.01 Versions-Datum
# 0x0005 0x0003 00.02 Betriebs-Mode
# 0x0008 0x0004 01.00 Temp-Aussen
# 0x000C 0x0004 01.01 Temp-Aussen-24h
# 0x0010 0x0004 01.02 Temp-Aussen-1h
# 0x0014 0x0004 01.03 Temp-Ruecklauf Soll
# 0x0018 0x0004 01.04 Temp-Ruecklauf
# 0x001C 0x0004 01.05 Temp-Vorlauf
# 0x0020 0x0004 01.06 Temp-WW Soll
# 0x0024 0x0004 01.07 Temp-WW Ist
# 0x0028 0x0004 01.08 Temp-Raum
# 0x002C 0x0004 01.09 Temp-Raum-1h
# 0x0030 0x0004 01.10 Temp-WQuelle-Ein
# 0x0034 0x0004 01.11 Temp-WQuelle-Aus
# 0x0038 0x0004 01.12 Temp-Verdampfer
# 0x003C 0x0004 01.13 Temp-Kondensator
# 0x0040 0x0004 01.14 Temp-Saugleitung
# 0x0044 0x0004 01.15 Temp-frei
# 0x0048 0x0004 01.16 Druck-Verdampfer
# 0x004C 0x0004 01.17 Druck-Kondensator
# 0x00F3 0x0001 02.00 Handabschaltung
# 0x00F4 0x0004 02.01 Hzg Einsatzzeitpunkt Sollwert
# 0x00F8 0x0004 02.02 Hzg Ruecklauf Sollwert am Einsatzp.
# 0x00FC 0x0004 02.03 Kennline Steigung Soll
# 0x0100 0x0004 02.04 Kennline Obere Begrenzung
# 0x0050 0x0004 02.05 Hzg: Temp Ruecklauf Soll
# 0x0054 0x0004 02.06 Hzg: Temp Ruecklauf Ist
# 0x0104 0x0001 02.07 Sollwertanhebung 4k fuer 24 Stunden
# 0x0105 0x0004 02.08 Pilotraum Sollwert
# 0x0109 0x0001 02.09 Pilotraum Faktor
# 0x010A 0x0004 02.10 Externe Anhebung
# 0x010E 0x0003 02.11 Freigabe Heizung
# 0x0111 0x0003 02.12 Sperren Heizung
# 0x0114 0x0003 02.13 Sollwertaenderung Ein
# 0x0117 0x0003 02.14 Sollwertaenderung Aus
# 0x011A 0x0004 02.15 St. 2 Kl. Obere Begrenzung
# 0x011E 0x0004 02.16 Kennlinie Hysterese
# 0x0122 0x0001 02.17 Pumpen Nachlaufzeit
# 0x0123 0x0001 03.00 Abschaltung
# 0x0124 0x0004 03.01 Klg Einsatzzeitpunkt
# 0x0128 0x0004 03.02 Ruecklauftemp. Sollwert am Einsatzzeitp.
# 0x012C 0x0004 03.03 Klg Kennlinie Steigung Soll
# 0x0130 0x0004 03.04 Kennlinie untere Begrenzung
# 0x0058 0x0004 03.05 Klg: Temp Ruecklauf Soll
# 0x005C 0x0004 03.06 Klg: Temp Ruecklauf Ist
# 0x0134 0x0001 04.00 Abschaltung
# 0x0135 0x0003 04.01 Zeit ein
# 0x0138 0x0003 04.02 Zeit aus
# 0x0060 0x0004 04.03 WW: Temp Ist
# 0x013b 0x0004 04.04 Warmwasser Soll
# 0x013F 0x0004 04.05 Beckenwasser Temperatur Soll
# 0x0143 0x0004 04.06 Warmwasser Hysterese
# 0x0147 0x0004 04.07 Beckenwasser Hysterese
# 0x0064 0x0003 05.00 Uhrzeit
# 0x0067 0x0003 05.01 Datum
# 0x006A 0x0004 05.02 Betriebsstunden Kompressor
# 0x006E 0x0004 05.03 Betriebsstunden Heizbetrieb
# 0x0072 0x0004 05.04 Betriebsstunden Warmwasserbetrieb
# 0x0076 0x0004 05.05 Betriebsstunden Stufe 2
# 0x007A 0x0003 05.06 Messbeginn Zeit Kompressor
# 0x007D 0x0003 05.07 Messbeginn Datum Kompressor
# 0x0080 0x0003 05.08 Messbeginn Zeit Pumpen
# 0x0083 0x0003 05.09 Messbeginn Datum Pumpen
# 0x0086 0x0001 05.10 Betriebsstunden Reset Kompressor
# 0x0087 0x0001 05.11 Betriebsstunden Reset Pumpen
# 0x0088 0x0001 06.00 Kennwort
# 0x0089 0x0001 06.01 Werkseinstellung
# 0x014B 0x0001 06.02 Modem Klingelzeichen
# 0x014C 0x0001 06.03 Fremdzugriff
# 0x014D 0x0001 06.04 Schluesselnummer
# 0x014E 0x0003 06.05 SetBetriebsMode
# 0x008A 0x0001 06.06 Reset Waermepumpe
# 0x0151 0x0001 06.07 Hzg: Externe Freigabe
# 0x0152 0x0004 06.08 Hzg: Externe Ruecklaufsteuerung
# 0x0156 0x0004 06.09 St2: TempQAus < Min
# 0x015A 0x0004 06.10 St2: TempVerd < Min
# 0x015E 0x0001 06.11 Estrich Aufheizen
# 0x015F 0x0001 06.12 Hzg: Externe Steuerung
# 0x0160 0x0001 06.13 St2 bei EVU Absch.
# 0x0161 0x0001 06.14 Frg. Beckenwasser
# 0x0162 0x0004 06.15 Scale Faktor
# 0x0166 0x0004 06.16 Offset Niederdr.
# 0x016A 0x0004 06.17 Offset Hochdr.
# 0x016E 0x0001 06.18 DO-Handkanal
# 0x016F 0x0001 06.19 DO-Handkanal Ein
# 0x008B 0x0002 06.20 CRC-Summe
# 0x0174 0x0001 06.21 Neu-Start
# 0x0175 0x0001 06.22 Run-Flag
# 0x008E 0x0002 06.23 Display Zeile 1
# 0x0090 0x0001 06.24 Display Zeile 2
# 0x0091 0x0003 07.00 Ausfall Zeit
# 0x0094 0x0003 07.01 Ausfall Datum
# 0x0097 0x0001 07.02 Ausfall Betriebszustaende
# 0x0098 0x0001 07.03 Ausfall DO Buffer
# 0x0099 0x0001 07.04 Ausfall DI Buffer
# 0x009A 0x0001 07.05 Ausfall AI Error
# 0x009B 0x0001 07.06 Ausfall AI DI
# 0x009C 0x0004 07.07 Ausfall AI Temp Aussen
# 0x00A0 0x0004 07.08 Ausfall AI Temp WQ Ein
# 0x00A4 0x0004 07.09 Ausfall AI Temp WQ Aus
# 0x00A8 0x0004 07.10 Ausfall AI Temp Verdampfer
# 0x00AC 0x0004 07.11 Ausfall AI Temp Heizung Ein
# 0x00B0 0x0004 07.12 Ausfall AI Temp Heizung Aus
# 0x00B4 0x0004 07.13 Ausfall AI Temp Kondensation
# 0x00B8 0x0004 07.14 Ausfall AI Temp Warmwasser
# 0x00BC 0x0001 07.15 Ausfall Term AI Error
# 0x00BD 0x0001 07.16 Ausfall Term AI Di
# 0x00BE 0x0004 07.17 Ausfall AI Temp Raum
# 0x00C2 0x0001 07.18 Clear Ausfälle
# 0x00C3 0x0001 08.00 Unterbrechungen
# 0x00C4 0x0001 08.01 Warnung Eingangsseite
# 0x00C5 0x0001 08.02 Warnung Ausgangsseite
# 0x00C6 0x0001 08.03 Warnung Sonstige
# 0x00C7 0x0001 08.04 Ausfall
# 0x00C8 0x0001 08.05 AI Error Fuehler Ausfall
# 0x00C9 0x0001 08.06 AI Di Fuehler defekt
# 0x00C9 0x0003 08.07 Kontrollwert fuer Fuehlerkalibrierung
# 0x00CC 0x0001 08.08 Unterbrechung Raumfuehler
# 0x00CD 0x0001 08.09 Kurzschluss Raumfuehler
# 0x0171 0x0001 08.10 Unterbrechung Warung Eingangsseite
# 0x0172 0x0001 08.11 Unterbrechung Warung Ausgangsseite
# 0x0173 0x0001 08.12 Unterbrechung Warung Ausgangsseite
# 0x00CE 0x0001 09.00 Betriebszustaende
# 0x00CF 0x0001 09.01 DO-Buffer
# 0x00D0 0x0001 09.02 DI-Buffer
# 0x00D1 0x0002 09.03 Gesamtstatus
# 0x00D3 0x0002 09.04 Status Verriegelung
# 0x00D5 0x0002 09.05 Status Heizung
# 0x00D7 0x0002 09.06 Status Kühlung
# 0x00D9 0x0002 09.07 Status Stufe2
# 0x00DB 0x0002 09.08 Status Wasser
# 0x00DC 0x0002 09.09 Status WPumpe
# 0x00DF 0x0001 09.10 Mode Heizung
# 0x00E0 0x0001 09.11 Mode Kuehlung
# 0x00E1 0x0001 09.12 Mode Warmwasser
# 0x0000 0x0001 10.00 Logger Zyklus
# 0x0000 0x0001 10.01 Initialisierung des Loggers
# 0x0000 0x0004 10.02 Speicherfehler des Loggers
# 0x00E3 0x0003 10.03 Uhrzeit der Initialisierung
# 0x00E6 0x0003 10.04 Datum der Initialisierung
# 0x00E9 0x0002 10.05 Maximale Anzahl der Datensaetze
# 0x00EB 0x0003 10.06 Laufende Nr. aktueller Datensatz
# 0x00ED 0x0002 10.07 Anzahl gespeicherter Datensaetze
# 0x00EF 0x0002 10.08 Groesse eines Datensatzes
# 0x00F1 0x0002 10.09 Max Groesse das Datenspeicher



logger = logging.getLogger()


class BaseRCD4():
    unit = ""
    default_poll_intervall = 60
    device_class = ""
    def toJson(self):
        return self

class GenericInteger(int, BaseRCD4):
    pass

class GenericFloat(float, BaseRCD4):
    pass

class Temperature(GenericFloat):
    unit = "°C"
    default_poll_intervall = 120
    device_class = "temperature"

    def toJson(self):
        return str(self)

    def __str__(self) -> str:
        return str(round(self, 2))

class BitField(BaseRCD4):
    bit_names = ["0", "1", "2", "3", "4", "5", "6", "7"]

    def __init__(self, byte: int) -> None:
        self.data = byte
    
    def get_bit(self, name: str):
        try:
            idx = self.bit_names.index(name)
            return (self.data >> idx) & 1
        except ValueError:
            raise AttributeError
    def toJson(self):
        res = ""
        for bit_name in self.bit_names:
            if bit_name:
                v = self.get_bit(bit_name)
                if v:
                    res = res + bit_name + ", "
        return res
    
    def __str__(self) -> str:
        res = "|"
        for bit_name in self.bit_names:
            v = self.get_bit(bit_name)
            res = res + bit_name + ": "+ str(v)+", "
        return res+"|"

    @classmethod
    def __class_getitem__(cls, bit_names):
        bit_names = [bit_name for bit_name in bit_names if type(bit_name) == str and len(bit_name) > 0]
        return type("_".join(bit_names), (BitField, ), {
            "bit_names": bit_names,
        })


class Attribute:
    def __init__(self, address: int, length: int, menu_entry: str, id: str, type: BaseRCD4,  pretty_name = None) -> None:
        self.id = id
        self.pretty_name = pretty_name or id
        self.address = address
        self.length = length
        self.type = type
        self.menu_entry = menu_entry

        self.poll_intervall = self.type.default_poll_intervall
        self.unit = self.type.unit
        self.device_class = self.type.device_class


class ResumatCD4:
    class ByteSequence:
        start = bytes.fromhex("1002")
        end = bytes.fromhex("1003")

        read_command = bytes.fromhex("0115")
        read_response = bytes.fromhex("0017")
    
    attributes = {
        "Version":            Attribute(0x0000, 0x0002, "00.00", "Version", GenericInteger,),
        "Temp-Aussen":        Attribute(0x0008, 0x0004, "01.00", "Temp-Aussen", Temperature,),
        "Temp-Ruecklauf-Soll":Attribute(0x0014, 0x0004, "01.03", "Temp-Ruecklauf-Soll", Temperature,),
        "Temp-Ruecklauf":     Attribute(0x0018, 0x0004, "01.04", "Temp-Ruecklauf", Temperature,),
        "Temp-Vorlauf":       Attribute(0x001C, 0x0004, "01.05", "Temp-Vorlauf", Temperature,),
        "Temp-WW-Soll":       Attribute(0x0020, 0x0004, "01.06", "Temp-WW-Soll", Temperature,),
        "Temp-WW-Ist":        Attribute(0x0024, 0x0004, "01.07", "Temp-WW-Ist", Temperature,),
        "Temp-Raum":          Attribute(0x0028, 0x0004, "01.08", "Temp-Raum", Temperature,),
        "Temp-WQuelle-Ein":   Attribute(0x0030, 0x0004, "01.10", "Temp-WQuelle-Ein", Temperature,),
        "Temp-WQuelle-Aus":   Attribute(0x0034, 0x0004, "01.11", "Temp-WQuelle-Aus", Temperature,),
        "Unterbrechungen":    Attribute(0x00C3, 0x0001, "08.00", "Unterbrechungen",   BitField, "Unterbrechungen"),
        "WarnungEingang":     Attribute(0x00C4, 0x0001, "08.01", "WarnungEingang",    BitField["VerdampfungstemperaturZuNiedrig", "TemperaturQuelleAustrittZuNiedrig", "DiffQuelleEinQuelleAusZuHoch", "DiffQuelleAusVerdampfungZuHoch"], "Warnung Eingangsseite"),
        "WarnungAusgang":     Attribute(0x00C5, 0x0001, "08.02", "WarnungAusgang",    BitField["", "KondensationstemperaturZuHoch", "DiffHzgVorlaufRuecklaufZuNiedrig", "DiffHzgVorlaufRuecklaufZuHoch", "DiffKondensationVorlaufZuHoch"], "Warnung Ausgangsseite"),
        "WarnungSonstige":    Attribute(0x00C6, 0x0001, "08.03", "WarnungSonstige",   BitField["RuecklauffuehlerDefekt", "VorlauffuehlerDefekt", "AussenwandfuehlerDefkt", "DoBufferHandstellung", "SolestandMin"], "Warnung Sonstige"),
        "Ausfall":            Attribute(0x00C7, 0x0001, "08.04", "Ausfall",           BitField, "Ausfälle"),
        "Betriebszustaende":  Attribute(0x00CE, 0x0001, "09.00", "Betriebszustaende", BitField),
        "DI-Buffer":          Attribute(0x00D0, 0x0001, "09.02", "DI-Buffer", BitField),
        "Mode-Heizung":       Attribute(0x00DF, 0x0001, "09.10", "Mode-Heizung",      BitField["0-UnterbrFuehlerfehler", "1-KeinBedarf", "2-Unterdrueckt", "3-Zeitprog", "4-Sommer", "5-SchnellAufhz", "6-Aus", "7-Normal"]),
        "Mode-Kuehlung":      Attribute(0x00E0, 0x0001, "09.11", "Mode-Kuehlung",     BitField["0", "1", "2", "3-Aus", "4", "5", "6", "7"],),
        "Mode-Warmwasser":    Attribute(0x00E1, 0x0001, "09.12", "Mode-Warmwasser",   BitField["0", "1", "2", "3-KeinBedarf", "4", "5", "6", "7"],),
    }

    def __init__(self, port = '/dev/heizung', baudrate = 9600) -> None:
        self.serial = serial.Serial(port, baudrate)
        
    def build_read_command(self, address, length):
        if type(address) == int:
            address = address.to_bytes(2, byteorder='big')
        if type(length) == int:
            length = length.to_bytes(2, byteorder='big')
        command = self.ByteSequence.read_command + address + length
        crc = Crc16Buypass.calcbytes(command)
        return self.ByteSequence.start + command + self.ByteSequence.end + crc

    def send(self, bytes_to_send):
        logger.debug("Data sent: %s", bytes.hex(bytes_to_send))
        self.serial.write(bytes_to_send)
        self.serial.flush()
    
    def receive(self):    
        header = self.serial.read_until(bytes.fromhex("FF") + self.ByteSequence.start)
        data = self.serial.read_until(self.ByteSequence.end)
        crc = self.serial.read(2)
        footer = self.serial.read(1)  # expected FF

        return header[1:] + data + crc

    def parse_read_response(self, data):
        resp = data[:-2]
        crc = data[-2:]
        if not resp.startswith(self.ByteSequence.start):
            raise Exception("error start: {} expected {}".format(resp[:2], self.ByteSequence.start))
        if not resp.endswith(self.ByteSequence.end):
            raise Exception("error end: {} expected {}".format(resp[-2:], self.ByteSequence.end))
        read_resp = resp[2:-2]
        exp_crc = Crc16Buypass.calcbytes(read_resp)
        if crc != exp_crc:
            raise Exception("crc not correct: {} expected {}".format(crc, exp_crc))
        if not read_resp.startswith(self.ByteSequence.read_response):
            raise Exception("error read response: {} expected {}".format(read_resp[:2], self.ByteSequence.read_response))
        data = read_resp[2:]

        # The byte 0x10 get escaped with another 0x10. Remove those.
        res = bytearray([data[0]])
        prev_b = res[0]
        for b in data[1:]:
            if prev_b == 0x10 and b == 0x10:
                prev_b = None  # allow multiple escaped 0x10
            else:
                res.append(b)
                prev_b = b
        return bytes(res)


    def get_attr(self, attr_id):
        attr = self.attributes[attr_id]
        data = self.build_read_command(attr.address, attr.length)
        self.send(data)
        resp_bytes = self.receive()
        resp = self.parse_read_response(resp_bytes)
        
        resp_value = self.bytes_to_type(resp, attr.type)

        return resp_value
    
    def get_multiple_attr(self, *attr_ids):
        attrs = filter(lambda attr: attr.id in attr_ids, self.attributes.values())
        attrs = sorted(attrs, key = lambda a: a.address)
        min_address = attrs[0].address
        length = attrs[-1].address - min_address + attrs[-1].length 

        data = self.build_read_command(min_address, length)
        self.send(data)
        resp_bytes = self.receive()
        resp = self.parse_read_response(resp_bytes)
        
        res = {}
        for attr in attrs:
            offset = attr.address-min_address
            value = self.bytes_to_type(resp[offset:offset+attr.length], attr.type)
            res[attr.id] = value

        return res

    def bytes_to_type(self, bytes, val_type):
        if issubclass(val_type, GenericFloat):
            val = struct.unpack('<f', bytes)[0]
            return val_type(val)
        elif issubclass(val_type, GenericInteger):
            val = int.from_bytes(bytes, byteorder='big')
            return val_type(val)
        elif issubclass(val_type, BitField):
            return val_type(bytes[0])
        else:
            return bytes
