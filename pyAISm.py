# coding: latin-1
# A bunch of naive pythons functions to decode somes ais_data/AIVDM messages:
# try with !AIVDO,1,1,,,B00000000868rA6<H7KNswPUoP06,0*6A
# doc : http://catb.org/gpsd/AIVDM.html
#################################################################################
# HOW TO USE IT :
# msg = '!AIVDO,1,1,,,B00000000868rA6<H7KNswPUoP06,0*6A' 
# ais_data = decod_ais(msg)
# ais_format = format_ais(ais_data)
# print ais_data, ais_data['lon'], ais_format['lon']
#################################################################################

def b2si(bytes):
    # converts signed pack of bytes (as a string) to signed int
    # bytes = '1001001010010010...' up to 6*82 bits
    temp = bytes
    if bytes[0]=='1':
        l = len(temp)-1
        while temp[l]=='0':
            l -= 1
        temp2=temp[:l].replace('1', '2')
        temp3=temp2.replace('0', '1')
        temp4=temp3.replace('2', '0')
        temp=temp4+temp[l:]
        return -int(temp,2)
    else:
        return int(temp,2)

def get_payload(msg):
    msg = msg.split(',')
    return msg[5]

##############################################################################

def decod_payload(payload):
    # convert the payload from ASCII char to a data pack of bytes to be decoded
    # payload = '177KQJ5000G?tO`K>RA1wUbN0TKH' up to 82 chars
    data = ''
    for i in range(len(payload)):
        char = ord(payload[i])-48
        if char>40:
            char = char -8
        bit = '{0:b}'.format(char)
        base = '000000'
        bit = base[0:6-len(bit)]+bit
        data = data + bit
    return data

def decod_6bits_ascii(bits):
    # decode 6bits into an ascii char, with respect to the 6bits ascii table
    ascii = int(bits,2)
    if ascii < 32:
        ascii+=64
    return chr(ascii)

def decod_name(data):
    # decode 6bits strings
    name = ''
    for k in range(len(data)/6):
        letter = decod_6bits_ascii(data[6*k:6*(k+1)])
        if letter != '@':
            name += letter
    return name

def decod_data(data):
    # decode AIS payload and return a dictionnary with key:value
    # input : '11110011000101....' by pack of 6 bits
    # returns {'type':18, etc...}
    # if needed, see http://catb.org/gpsd/AIVDM.html
    type_nb = int(data[0:6],2)

    def decod_5(data):
        ais_data                 = {'type':int(data[0:6],2)}
        ais_data['repeat']       = int(data[6:8],2)
        ais_data['mmsi']         = int(data[8:38],2)
        ais_data['ais_version']  = int(data[38:40],2)
        ais_data['imo']          = int(data[40:70],2)
        ais_data['callsign']     = decod_name(data[70:112])
        ais_data['shipname']     = decod_name(data[112:232])
        ais_data['shiptype']     = int(data[232:240],2)
        ais_data['to_bow']       = int(data[240:249],2)
        ais_data['to_stern']     = int(data[249:258],2)
        ais_data['to_port']      = int(data[258:264],2)
        ais_data['to_starboard'] = int(data[264:270],2)
        ais_data['epfd']         = int(data[270:274],2)
        ais_data['month']        = int(data[274:278],2)
        ais_data['day']          = int(data[278:283],2)
        ais_data['hour']         = int(data[283:288],2)
        ais_data['minute']       = int(data[288:294],2)
        ais_data['draught']      = int(data[294:302],2)
        ais_data['dte']          = data[302]
        return ais_data

    def decod_18(data):
        ais_data             = {'type':int(data[0:6],2)}
        ais_data['repeat']   = int(data[6:8],2)
        ais_data['mmsi']     = int(data[8:38],2)
        ais_data['speed']    = int(data[46:56],2)
        ais_data['accuracy'] = data[56]
        ais_data['lon']      = b2si(data[57:85])/600000.0
        ais_data['lat']      = b2si(data[85:112])/600000.0
        ais_data['course']   = int(data[112:124],2)
        ais_data['heading']  = int(data[124:133],2)
        ais_data['second']   = int(data[133:139],2)
        ais_data['regional'] = int(data[139:141],2)
        ais_data['cs']       = data[141]
        ais_data['display']  = data[142]
        ais_data['dsc']      = data[143]
        ais_data['band']     = data[144]
        ais_data['msg22']    = data[145]
        ais_data['assigned'] = data[146]
        ais_data['raim']     = data[147]
        ais_data['radio']    = int(data[148:168],2)
        return ais_data
    
    def decod_19(data):
        ais_data                 = {'type':int(data[0:6],2)}
        ais_data['speed']        = int(data[46:56],2)
        ais_data['accuracy']     = data[56]
        ais_data['lon']          = b2si(data[57:85])/600000.0
        ais_data['lat']          = b2si(data[85:112])/600000.0
        ais_data['course']       = int(data[112:124],2)
        ais_data['heading']      = int(data[124:133],2)
        ais_data['second']       = int(data[133:139],2)
        ais_data['regional']     = int(data[139:143],2)
        ais_data['shipname']     = decod_name(data[143:263])
        ais_data['to_bow']       = int(data[271:280],2)
        ais_data['to_stern']     = int(data[280:288],2)
        ais_data['to_port']      = int(data[289:295],2)
        ais_data['to_starboard'] = int(data[295:301],2)
        ais_data['epfd']         = int(data[301:305],2)
        ais_data['raim']         = data[305]
        ais_data['dte']          = data[306]
        ais_data['assigned']     = data[307]
        return ais_data

    decod_type = {
                    5  : decod_5,
                    18 : decod_18,
                    19 : decod_19,
                 }
    try:
        ais_data = decod_type[type_nb](data)
    except:
        print "ERROR : Cannot decode message type "+str(type_nb)
        ais_data = {'type':type_nb}
        raise
    return ais_data

def decod_ais(msg):
    # main function to decode somes ais_data/AIVDM messages:
    # try with '!ais_data,1,1,,,B00000000868rA6<H7KNswPUoP06,0*6A'
    # doc : http://catb.org/gpsd/AIVDM.html
    payload = get_payload(msg)
    nmsg = msg.split(',')
    if nmsg[1]!= 1:
        if nmsg[2]!=nmsg[1]:
            with open('.tmp.txt','a') as tmp_payload:
                tmp_payload.write(payload+'\n')
            return {'none':'Multi sentences AIS '}
        else:
            with open('.tmp.txt','r') as tmp_payload:
                payload = ''
                for line in tmp_payload:
                    payload += line.strip('\n')
            payload += get_payload(msg)
            with open('.tmp.txt','w') as tmp_payload:
                tmp_payload.write('')
    data = decod_payload(payload)
    ais_data = decod_data(data)
    return ais_data

##############################################################################

def format_coord(coord_dec,Dir=''):
    # get position in decimal base and return a string with position in arc-base
    # takes 43.29492333333334
    # returns 43°17'41.7"N
    tmp = str(coord_dec).split('.')
    deg = float(tmp[0])
    mnt = float('0.'+tmp[1])*60
    tmp = str(mnt).split('.')
    sec = float('0.'+tmp[1])*60
    return str(int(deg))+'°'+str(int(mnt))+"'"+str(sec)[:6]+'"'+Dir

def format_ais(ais_base):
    # format the ais_data database to user-friendly display
    ais_format = ais_base.copy()

    def format_lat(lat):
        return (format_coord(lat,'N') if lat > 0 else format_coord(lat,'S'))

    def format_lon(lon):          
        return (format_coord(lon,'E') if lon > 0 else format_coord(lon,'W'))

    def format_course(course):
        return 'N/A' if course == 3600 else str(course*0.1)+'° relative to North'

    def format_heading(heading):
        return 'N/A' if heading == 511 else str(heading)+'°'

    def format_second(second):
        if second == 60:
            return 'N/A'
        elif second == 61:
            return 'manual mode'
        elif second == 62:
            return 'EPFS in estimated mode'
        elif second == 63:
            return 'PS inoperative'
        else:
            return second

    def format_cs(cs):
        return 'Class B SOTDMA' if cs == '0' else 'Class B CS'

    def format_display(display):
        return 'N/A' if display == '0' else 'Display available'

    def format_dsc(dsc):
        if dsc == '1':
          return 'VHF voice radio with DSC capability'
  
    def format_band(band):
        if band == '1':
            return 'Can use any frequency of the marine channel'

    def format_msg22(msg22):
        if msg22 == '1':
            return 'Accepts channel assignment via Type 22 Message'

    def format_assigned(assigned):
        if assigned == '0':
            return 'Autonomous mode'

    def format_dte(dte):
        return 'Data terminal ready' if dte == '0' else 'Data terminal N/A'

    def format_epfd(epfd):
        epfd_types = {  0 : 'Undefined',
                        1 : 'GPS',
                        2 : 'GLONASS',
                        3 : 'GPS/GLONASS',
                        4 : 'Loran-C',
                        5 : 'Cayka',
                        6 : 'Integrated',
                        7 : 'Surveyed',
                        8 : 'Galileo'}
        return epfd_types[epfd]
    

    format_list = {
                  'lat':format_lat,
                  'lon':format_lon,
                  'course':format_course,
                  'heading':format_heading,
                  'second':format_second,
                  'cs':format_cs,
                  'display':format_display,
                  'dsc':format_dsc,
                  'band':format_band,
                  'msg22':format_msg22,
                  'assigned':format_assigned,
                  'dte':format_dte,
                  'epfd':format_epfd
                  }

    for key in ais_format.keys():
        if format_list.has_key(key):
            ais_format[key] = format_list[key](ais_format[key])

    return ais_format

msg = []
msg.append('!AIVDM,2,1,3,B,55P5TL01VIaAL@7WKO@mBplU@<PDhh000000001S;AJ::4A80?4i@E53,0*3E')
msg.append('!AIVDM,2,2,3,B,1@0000000000000,2*55')

for msgs in msg:
    ais = decod_ais(msgs)
    print ais
    ais2 = format_ais(ais)
    print ais2