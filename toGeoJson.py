import json
import socket
import time

from geojson import Point, Feature
import pyAISm

json_dict = {}
ships_dict = {}

class Ship:
    mmsi = 0
    cog = -1
    sog = -1
    name = "Unknown"
    heading = -1
    coord = (-1000, -1000)
    shiptype = "Not available"
    aid_type = "Unknown"


def to_point_entity(ais_data):
    ship = Ship()
    if 'mmsi' in ais_data:
        ship.mmsi = ais_data['mmsi']
    if 'course' in ais_data:
        ship.cog = ais_data['course']
    if 'speed' in ais_data:
        ship.sog = round(ais_data['speed']/10, 2)
    if 'heading' in ais_data:
        ship.heading = ais_data['heading']
    if ship.heading == 511:
        ship.heading = 0
    if 'lon' in ais_data:
        ship.coord = (ais_data['lon'], ais_data['lat'])
    ship.name = "Unknown"
    if 'shipname' in ais_data:
        ship.name = ais_data['shipname']
    if 'shiptype' in ais_data:
        ship.shiptype = pyAISm.format_ais(ais_data)['shiptype']
    if 'aid_type' in ais_data:
        ship.aid_type = pyAISm.format_ais(ais_data)['aid_type']
    if ship.mmsi in ships_dict:
        if ship.name == "Unknown" and ships_dict[ship.mmsi].name!="Unknown":
            ship.name = ships_dict[ship.mmsi].name
        if ship.shiptype == "Not available" and ships_dict[ship.mmsi].shiptype != "Not available":
            ship.shiptype = ships_dict[ship.mmsi].shiptype
        if ship.aid_type == "Unknown" and ships_dict[ship.mmsi].aid_type!="Unknown":
            ship.aid_type = ships_dict[ship.mmsi].aid_type
    ships_dict[ship.mmsi] = ship
    point = Point(ship.coord)
    feature = Feature(geometry=point, properties={"id": ship.mmsi, "cog": ship.cog, "sog":ship.sog, "heading": ship.heading, "name": ship.name, "shiptype": ship.shiptype, "aid_type" : ship.aid_type})
    return feature


def update_json_dict(mmsi, point):
    json_dict[mmsi] = point


def to_json_file(json_dict):
    return json.dumps(list(json_dict.values()), ensure_ascii=False)


def decode_stream_example():
    """
    Example for decoding an online data stream
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("ais.exploratorium.edu", 80))
    s.sendall("GET / HTTP/1.1\r\nHost: www.yahoo.com\r\n\r\n".encode())
    while (True):
        msg = (s.recv(4096).decode('utf-8')).splitlines()
        for m in msg:
            try:
                msg = m.rstrip("\n")
                ais_data = pyAISm.decod_ais(msg)  # Return a dictionnary
                if ais_data is not None and 'mmsi' in ais_data:
                    entity_json = to_point_entity(ais_data)
                    update_json_dict(ais_data['mmsi'], entity_json)
                else:
                    continue
                with open('/home/aayaffe/programing/Kamashomat/data.json', 'w', encoding='utf-8') as f:
                    f.write(to_json_file(json_dict))
                # if ais_data['type'] == 5 or ais_data['type'] == 19 or ais_data['type'] == 24 or ais_data['type'] == 21:
                #     print("Message type: ", ais_data['type'])
                print(entity_json)  # Accessing the value of the key
            except pyAISm.UnrecognizedNMEAMessageError as e:
                pass
                print(e)
            except pyAISm.BadChecksumError as e:
                print(e)
            # except Exception as e:
            #     pass
                # print(e)

def decode_file_example():
    """
    Example for decoding an online data stream
    :return:
    """
    with open("ais.exploratorium.edu", "r") as file:
        for aline in file:
            time.sleep(0.3)
            try:
                msg = aline.rstrip("\n")
                ais_data = pyAISm.decod_ais(msg)  # Return a dictionnary
                if ais_data is not None and 'mmsi' in ais_data:
                    entity_json = to_point_entity(ais_data)
                    update_json_dict(ais_data['mmsi'], entity_json)
                else:
                    continue
                with open('C:\programing\Kamashomat\data.json', 'w', encoding='utf-8') as f:
                    f.write(to_json_file(json_dict))
                if ais_data['type'] == 5 or ais_data['type'] == 19 or ais_data['type'] == 24:
                    print("Message type: %d", ais_data['type'])
                print(entity_json)  # Accessing the value of the key
            except pyAISm.UnrecognizedNMEAMessageError as e:
                pass
                print(e)
            except pyAISm.BadChecksumError as e:
                print(e)
            # except Exception as e:
            #     pass
            # print(e)



decode_stream_example()
