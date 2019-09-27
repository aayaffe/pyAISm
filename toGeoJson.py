import json
import socket
from geojson import Point, Feature
import pyAISm

json_dict = {}


def to_point_entity(ais_data):
    mmsi = ais_data['mmsi']
    coord = (ais_data['lon'], ais_data['lat'])
    point = Point(coord)
    feature = Feature(geometry=point, properties={"id": mmsi})
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
    s.sendall("GET / HTTP/1.1\r\nHost: www.cnn.com\r\n\r\n".encode())
    while (True):
        msg = (s.recv(4096).decode('utf-8')).splitlines()


        for m in msg:
            try:
                msg = m.rstrip("\n")
                ais_data = pyAISm.decod_ais(msg)  # Return a dictionnary
                entity_json = to_point_entity(ais_data)
                update_json_dict(ais_data['mmsi'], entity_json)
                with open('data.json', 'w', encoding='utf-8') as f:
                    f.write(to_json_file(json_dict))
                print(to_json_file(json_dict))  # Accessing the value of the key
            # except pyAISm.UnrecognizedNMEAMessageError as e:
            #     pass
            #     # print(e)
            # except pyAISm.BadChecksumError as e:
            #     print(e)
            except Exception as e:
                pass
                # print(e)


decode_stream_example()
