# ------------------------------------------------------------------------------
# Sam Hanson, 2020
#
# Created for CSCI5981: Binary Analysis and Reverse Engineering
# This script parses hexadecimal memory values (starting at the first party
# byte, location 0x02024284 in RAM) and decrypts pokemon data.
#
# How to Use:
#  1) Have Python3 installed
#  2) Change party_data_raw to be hexadecimal str of your party's memory
#     (just copy/paste > 100 bytes and script will work)
# ------------------------------------------------------------------------------


# Pokemon data is in Little Endian format. It's much easier to have this data
# be in big endian format, however we will need to switch it back to little
# endian format when done modifying data.
def SwitchEndianFormats(byte_str):
    bytes_arr = []
    for i in range(0, len(byte_str), 2):
        bytes_arr.append(byte_str[i:i+2])
    bytes_arr = list(reversed(bytes_arr))
    bytes_little_endian = ''.join(bytes_arr) # essentially, the .implode() function from PHP
    return bytes_little_endian


# Always reverse at the LOWEST LEVEL -- meaning the raw bytes cannot be divided
# into sub-structures!
def ExtractBytesFromIndexAndReverse(byte_str, start, end):
    return SwitchEndianFormats(byte_str[start*2:end*2]) # 2 because there are 2 chars ber byte


# No reverse, for when we have to keep diving bytes into substructures
def ExtractBytesFromIndex(byte_str, start, end):
    return byte_str[start*2:end*2] # 2 because there are 2 chars ber byte


# The class organization choice is to exactly reproduce how it's stored in
# memory.
class Pokemon:
    def __init__(self, party_data_raw):
        self.party_data_raw = party_data_raw
        self.personality_value = ExtractBytesFromIndexAndReverse(self.party_data_raw, 0, 4) # offset 0
        self.OT_ID = ExtractBytesFromIndexAndReverse(self.party_data_raw, 4, 8) # offset 4
        self.nickname = ExtractBytesFromIndex(self.party_data_raw, 8, 18) # offset 8
        self.language = ExtractBytesFromIndexAndReverse(self.party_data_raw, 18, 20) # offset 18
        self.OT_name = ExtractBytesFromIndexAndReverse(self.party_data_raw, 20, 27) # offset 20
        self.markings = ExtractBytesFromIndexAndReverse(self.party_data_raw, 27, 28) # offset 27
        self.checksum = ExtractBytesFromIndexAndReverse(self.party_data_raw, 28, 30) # offset 28
        self.unknown = ExtractBytesFromIndexAndReverse(self.party_data_raw, 30, 32) # offset 30

        self.data = PokemonData( ExtractBytesFromIndex(self.party_data_raw, 32, 80), self.personality_value, self.OT_ID ) # offset 32

        self.status = ExtractBytesFromIndexAndReverse(self.party_data_raw, 80, 84) # offset 80 -- can't reverse yet (sub-data would be reversed incorrectly)
        self.level = ExtractBytesFromIndexAndReverse(self.party_data_raw, 84, 85) # offset 84
        self.pokerus = ExtractBytesFromIndexAndReverse(self.party_data_raw, 85, 86) # offset 85
        self.curr_hp = ExtractBytesFromIndexAndReverse(self.party_data_raw, 86, 88) # offset 86
        self.tot_hp = ExtractBytesFromIndexAndReverse(self.party_data_raw, 88, 90) # offset 88
        self.attack = ExtractBytesFromIndexAndReverse(self.party_data_raw, 90, 92) # offset 90
        self.defense = ExtractBytesFromIndexAndReverse(self.party_data_raw, 92, 94) # offset 92
        self.speed = ExtractBytesFromIndexAndReverse(self.party_data_raw, 94, 96) # offset 94
        self.sp_attack = ExtractBytesFromIndexAndReverse(self.party_data_raw, 96, 98) # offset 96
        self.sp_defense = ExtractBytesFromIndexAndReverse(self.party_data_raw, 98, 100) # offset 98


    def GetRawBytes(self):
        raw_bytes = ""
        raw_bytes += SwitchEndianFormats(self.personality_value)# + " "
        raw_bytes += SwitchEndianFormats(self.OT_ID)# + " "
        raw_bytes += self.nickname# + " "
        raw_bytes += SwitchEndianFormats(self.language)# + " "
        raw_bytes += SwitchEndianFormats(self.OT_name)# + " "
        raw_bytes += SwitchEndianFormats(self.markings)# + " "
        raw_bytes += SwitchEndianFormats(self.checksum)# + " "
        raw_bytes += SwitchEndianFormats(self.unknown)# + " "
        raw_bytes += self.data.GetRawBytes()# + " "
        print(raw_bytes)




class PokemonData:
    def __init__(self, data, personality_value, OT_ID):
        self.data = data
        self.personality_value = personality_value
        self.OT_ID = OT_ID

        self.order = "" # substructures are randomly ordered
        self.growth = None
        self.attack = None
        self.ev = None
        self.misc = None
        self.PopulateSubstructureData() # initialize growth order, growth, attack, ev, misc

        self.key = ""
        self.Decrypt_PokemonData() # decrypt substructure data


    ## This functions exists for a couple reasons:
    #    a) Find the substructure order, since the game "randomly" generates
    #       it.
    #    b) Correctly populate substructure with extracted bytes from
    #       PokemonData struct. Specifically: order, growth, attack, ev,
    #       and misc properties.
    def PopulateSubstructureData(self):
        order_num = int(self.personality_value, 16) % 24 # formula for finding struct order

        if order_num == 0:
            self.order = "GAEM"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.growth, self.attack, self.ev, self.misc]
        elif order_num == 1:
            self.order = "GAME"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.growth, self.attack, self.misc, self.ev]
        elif order_num == 2:
            self.order = "GEAM"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.growth, self.ev, self.attack, self.misc]
        elif order_num == 3:
            self.order = "GEMA"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.growth, self.ev, self.misc, self.attack]
        elif order_num == 4:
            self.order = "GMAE"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.growth, self.misc, self.attack, self.ev]
        elif order_num == 5:
            self.order = "GMEA"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.growth, self.misc, self.ev, self.attack]
        elif order_num == 6:
            self.order = "AGEM"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.attack, self.growth, self.ev, self.misc]
        elif order_num == 7:
            self.order = "AGME"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.attack, self.growth, self.misc, self.ev]
        elif order_num == 8:
            self.order = "AEGM"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.attack, self.ev, self.growth, self.misc]
        elif order_num == 9:
            self.order = "AEMG"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.attack, self.ev, self.misc, self.growth]
        elif order_num == 10:
            self.order = "AMGE"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.attack, self.misc, self.growth, self.ev]
        elif order_num == 11:
            self.order = "AMEG"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.attack, self.misc, self.growth, self.ev]
        elif order_num == 12:
            self.order = "EGAM"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.ev, self.growth, self.attack, self.misc]
        elif order_num == 13:
            self.order = "EGMA"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.ev, self.growth, self.misc, self.attack]
        elif order_num == 14:
            self.order = "EAGM"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.ev, self.attack, self.growth, self.misc]
        elif order_num == 15:
            self.order = "EAMG"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.ev, self.attack, self.misc, self.growth]
        elif order_num == 16:
            self.order = "EMGA"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.ev, self.attack, self.misc, self.growth]
        elif order_num == 17:
            self.order = "EMAG"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.ev, self.misc, self.attack, self.growth]
        elif order_num == 18:
            self.order = "MGAE"
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.misc, self.growth, self.attack, self.ev]
        elif order_num == 19:
            self.order = "MGEA"
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.misc, self.growth, self.ev, self.attack]
        elif order_num == 20:
            self.order = "MAGE"
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.misc, self.attack, self.growth, self.ev]
        elif order_num == 21:
            self.order = "MAEG"
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.misc, self.attack, self.ev, self.growth]
        elif order_num == 22:
            self.order = "MEGA"
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.misc, self.ev, self.growth, self.attack]
        elif order_num == 23:
            self.order = "MEAG"
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
            self.subs = [self.misc, self.ev, self.attack, self.growth]


    def Decrypt_PokemonData(self):
        self.key = int(self.personality_value, 16) ^ int(self.OT_ID, 16) # Need 32-bit (4 byte) decryption key
        self.growth.pokemon_no = int(self.growth.species, 16) ^ self.key

    def GetRawBytes(self):
        raw_bytes = ""

        for sub in self.subs:
            raw_bytes += sub.GetRawBytes()
        return raw_bytes



class Growth:
    def __init__(self, data):
        self.data = data
        self.pokemon_no = "" # true pokemon number (in hex)
        self.species = ExtractBytesFromIndexAndReverse(data, 0, 2) # offset 0
        self.item_held = ExtractBytesFromIndexAndReverse(data, 2, 4) # offset 2
        self.experience = ExtractBytesFromIndexAndReverse(data, 4, 8) # offset 4
        self.pp_bonuses = ExtractBytesFromIndexAndReverse(data, 8, 9) # offset 8
        self.friendship = ExtractBytesFromIndexAndReverse(data, 9, 10) # offset 9
        self.unknown = ExtractBytesFromIndexAndReverse(data, 10, 12) # offset 10

    def GetRawBytes(self):
        raw_bytes = ""
        raw_bytes += SwitchEndianFormats(self.species)# + " "
        raw_bytes += SwitchEndianFormats(self.item_held)# + " "
        raw_bytes += SwitchEndianFormats(self.experience)# + " "
        raw_bytes += SwitchEndianFormats(self.pp_bonuses)# + " "
        raw_bytes += SwitchEndianFormats(self.friendship)# + " "
        raw_bytes += SwitchEndianFormats(self.unknown)# + " "
        #print("growth: " + raw_bytes)
        return raw_bytes

class Attacks:
    def __init__(self, data):
        self.data = data
        self.move1 = ExtractBytesFromIndexAndReverse(data, 0, 2) # offset 0
        self.move2 = ExtractBytesFromIndexAndReverse(data, 2, 4) # offset 2
        self.move3 = ExtractBytesFromIndexAndReverse(data, 4, 6) # offset 4
        self.move4 = ExtractBytesFromIndexAndReverse(data, 6, 8) # offset 6
        self.pp1 = ExtractBytesFromIndexAndReverse(data, 8, 9) # offset 8
        self.pp2 = ExtractBytesFromIndexAndReverse(data, 9, 10) # offset 9
        self.pp3 = ExtractBytesFromIndexAndReverse(data, 10, 11) # offset 10
        self.pp4 = ExtractBytesFromIndexAndReverse(data, 11, 12) # offset 11

    def GetRawBytes(self):
        raw_bytes = ""
        raw_bytes += SwitchEndianFormats(self.move1)# + " "
        raw_bytes += SwitchEndianFormats(self.move2)# + " "
        raw_bytes += SwitchEndianFormats(self.move3)# + " "
        raw_bytes += SwitchEndianFormats(self.move4)# + " "
        raw_bytes += SwitchEndianFormats(self.pp1)# + " "
        raw_bytes += SwitchEndianFormats(self.pp2)# + " "
        raw_bytes += SwitchEndianFormats(self.pp3)# + " "
        raw_bytes += SwitchEndianFormats(self.pp4)# + " "
        #print("attacks: " + raw_bytes)
        return raw_bytes

class EV_Condition:
    def __init__(self, data):
        self.data = data
        self.hp_ev = ExtractBytesFromIndexAndReverse(data, 0, 1) # offset 0
        self.attack_ev = ExtractBytesFromIndexAndReverse(data, 1, 2) # offset 1
        self.defense_ev = ExtractBytesFromIndexAndReverse(data, 2, 3) # offset 2
        self.speed_ev = ExtractBytesFromIndexAndReverse(data, 3, 4) # offset 3
        self.sp_attack_ev = ExtractBytesFromIndexAndReverse(data, 4, 5) # offset 4
        self.sp_defense_ev = ExtractBytesFromIndexAndReverse(data, 5, 6) # offset 5
        self.coolness = ExtractBytesFromIndexAndReverse(data, 6, 7) # offset 6
        self.beauty = ExtractBytesFromIndexAndReverse(data, 7, 8) # offset 7
        self.cuteness = ExtractBytesFromIndexAndReverse(data, 8, 9) # offset 8
        self.smartness = ExtractBytesFromIndexAndReverse(data, 9, 10) # offset 9
        self.toughness = ExtractBytesFromIndexAndReverse(data, 10, 11) # offset 10
        self.feel = ExtractBytesFromIndexAndReverse(data, 11, 12) # offset 11

    def GetRawBytes(self):
        raw_bytes = ""
        raw_bytes += SwitchEndianFormats(self.hp_ev)# + " "
        raw_bytes += SwitchEndianFormats(self.attack_ev)# + " "
        raw_bytes += SwitchEndianFormats(self.defense_ev)# + " "
        raw_bytes += SwitchEndianFormats(self.speed_ev)# + " "
        raw_bytes += SwitchEndianFormats(self.sp_attack_ev)# + " "
        raw_bytes += SwitchEndianFormats(self.sp_defense_ev)# + " "
        raw_bytes += SwitchEndianFormats(self.coolness)# + " "
        raw_bytes += SwitchEndianFormats(self.beauty)# + " "
        raw_bytes += SwitchEndianFormats(self.cuteness)# + " "
        raw_bytes += SwitchEndianFormats(self.smartness)# + " "
        raw_bytes += SwitchEndianFormats(self.toughness)# + " "
        raw_bytes += SwitchEndianFormats(self.feel)# + " "
        #print("ev_cond: " + raw_bytes)
        return raw_bytes

class Miscellaneous:
    def __init__(self, data):
        self.data = data
        self.pokerus_status = ExtractBytesFromIndexAndReverse(data, 0, 1) # offset 0
        self.met_location = ExtractBytesFromIndexAndReverse(data, 1, 2) # offset 1
        self.origin_info = ExtractBytesFromIndexAndReverse(data, 2, 4) # offset 2
        self.IV_Egg_Ability = ExtractBytesFromIndexAndReverse(data, 4, 8) # offset 4
        self.Ribbons_Obediance = ExtractBytesFromIndexAndReverse(data, 8, 12) # offset 8

    def GetRawBytes(self):
        raw_bytes = ""
        raw_bytes += SwitchEndianFormats(self.pokerus_status)# + " "
        raw_bytes += SwitchEndianFormats(self.met_location)# + " "
        raw_bytes += SwitchEndianFormats(self.origin_info)# + " "
        raw_bytes += SwitchEndianFormats(self.IV_Egg_Ability)# + " "
        raw_bytes += SwitchEndianFormats(self.Ribbons_Obediance)# + " "
        #print("Misc: " + raw_bytes)
        return raw_bytes
