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
#
# Future To-Do's:
#   * User enters pokemon name, bytes automagically propagate into party struct
# ------------------------------------------------------------------------------





party_data_raw = "C1E007DD54E18D05BDC2BBCCC7BBC8BEBFCC0202BBBBBBBBBBBBBB00DA1200009F01A7D895018AD8B6298AD895018AD895018AD895018AD895598FFA75FF9AF395018AD891018AD812018AD895478AD80000000005FF120012000B000A000B000B000B0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FF000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FF0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

def ToBigEndian(byte_str):
    bytes_arr = []
    for i in range(0, len(byte_str), 2):
        bytes_arr.append(byte_str[i:i+2])
    bytes_arr = list(reversed(bytes_arr))

    bytes_little_endian = ''.join(bytes_arr) # essentially, the .implode() function from PHP
    return bytes_little_endian

def ExtractBytesFromIndex(byte_str, start, end):
    return byte_str[start*2:end*2] # 2 because there are 2 chars ber byte


class PokemonParty:
    def __init__(self, party_data_raw):
        self.party_data_raw = party_data_raw
        self.personality_value = ExtractBytesFromIndex(self.party_data_raw, 0, 4) # offset 0
        self.OT_ID = ExtractBytesFromIndex(self.party_data_raw, 4, 8) # offset 4
        self.nickname = ExtractBytesFromIndex(self.party_data_raw, 8, 18) # offset 8
        self.language = ExtractBytesFromIndex(self.party_data_raw, 18, 20) # offset 18
        self.OT_name = ExtractBytesFromIndex(self.party_data_raw, 20, 27) # offset 20
        self.markings = ExtractBytesFromIndex(self.party_data_raw, 27, 28) # offset 27
        self.checksum = ExtractBytesFromIndex(self.party_data_raw, 28, 30) # offset 28
        self.unknown = ExtractBytesFromIndex(self.party_data_raw, 30, 32) # offset 30
        self.data = PokemonData(ExtractBytesFromIndex(self.party_data_raw, 32, 80), self.personality_value, self.OT_ID) # offset 32
        self.status = ExtractBytesFromIndex(self.party_data_raw, 80, 84) # offset 80
        self.level = ExtractBytesFromIndex(self.party_data_raw, 84, 85) # offset 84
        self.pokerus = ExtractBytesFromIndex(self.party_data_raw, 85, 86) # offset 85
        self.curr_hp = ExtractBytesFromIndex(self.party_data_raw, 86, 88) # offset 86
        self.tot_hp = ExtractBytesFromIndex(self.party_data_raw, 88, 90) # offset 88
        self.attack = ExtractBytesFromIndex(self.party_data_raw, 90, 92) # offset 90
        self.defense = ExtractBytesFromIndex(self.party_data_raw, 92, 94) # offset 92
        self.speed = ExtractBytesFromIndex(self.party_data_raw, 94, 96) # offset 94
        self.sp_attack = ExtractBytesFromIndex(self.party_data_raw, 96, 98) # offset 96
        self.sp_defense = ExtractBytesFromIndex(self.party_data_raw, 98, 100) # offset 98



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
        self.PopulateSubstructureData()

        self.key = ""
        self.Decrypt_PokemonData() # decrypt substructure data



    def PopulateSubstructureData(self):
        ## This functions exists for a couple reasons:
        #    a) Find the substructure order, since the game "randomly" generates
        #       it.
        #    b) Correctly populate substructure with extracted bytes from
        #       PokemonData struct. Specifically: order, growth, attack, ev,
        #       and misc properties.

        order_num = int(self.personality_value, 16) % 24 # formula for finding struct order
        if order_num == 0:
            self.order = "GAEM"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 1:
            self.order = "GAME"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 2:
            self.order = "GEAM"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 3:
            self.order = "GEMA"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 4:
            self.order = "GMAE"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 5:
            self.order = "GMEA"
            self.growth = Growth(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 6:
            self.order = "AGEM"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 7:
            self.order = "AGME"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 8:
            self.order = "AEGM"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 9:
            self.order = "AEMG"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ToBigEndian(ExtractBytesFromIndex(self.data, 36, 48)))
        elif order_num == 10:
            self.order = "AMGE"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 11:
            self.order = "AMEG"
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 0, 12))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 12:
            self.order = "EGAM"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 13:
            self.order = "EGMA"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 14:
            self.order = "EAGM"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.misc = Miscellaneous(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 15:
            self.order = "EAMG"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 24, 36))
            self.Growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 16:
            self.order = "EMGA"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 17:
            self.order = "EMAG"
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 0, 12))
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 18:
            self.order = "MGAE"
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 19:
            self.order = "MGEA"
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 20:
            self.order = "MAGE"
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 21:
            self.order = "MAEG"
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 12, 24))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 22:
            self.order = "MEGA"
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 24, 36))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 36, 48))
        elif order_num == 23:
            self.order = "MEAG"
            self.miscellaneous = Miscellaneous(ExtractBytesFromIndex(self.data, 0, 12))
            self.ev = EV_Condition(ExtractBytesFromIndex(self.data, 12, 24))
            self.attack = Attacks(ExtractBytesFromIndex(self.data, 24, 36))
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))



    def Decrypt_PokemonData(self):

        # Need 32-bit (4 byte) decryption key
        print(self.personality_value)
        print(self.OT_ID)
        print("personality - dec: " + str(int(self.personality_value, 16)))
        print("ot_id - dec: " + str(int(self.OT_ID, 16)))
        print("ANS: " + str(int(self.OT_ID, 16) ^ int(self.personality_value, 16)))
        self.key = int(self.personality_value, 16) ^ int(self.OT_ID, 16)
        print("KEY = " + str(self.key))
        print("self.growth.species: " + self.growth.species)
        species = int(self.growth.species, 16) ^ self.key


class Growth:
    def __init__(self, data):
        self.data = data
        self.species = ToBigEndian(ExtractBytesFromIndex(data, 0, 2)) # offset 0
        self.item_held = ExtractBytesFromIndex(data, 2, 4) # offset 2
        self.experience = ExtractBytesFromIndex(data, 4, 8) # offset 4
        self.pp_bonuses = ExtractBytesFromIndex(data, 8, 9) # offset 8
        self.friendship = ExtractBytesFromIndex(data, 9, 10) # offset 9
        self.unknown = None # offset 10

class Attacks:
    def __init__(self, data):
        self.data = data
        self.move1 = ExtractBytesFromIndex(data, 0, 2) # offset 0
        self.move2 = ExtractBytesFromIndex(data, 2, 4) # offset 2
        self.move3 = ExtractBytesFromIndex(data, 4, 6) # offset 4
        self.move4 = ExtractBytesFromIndex(data, 6, 8) # offset 6
        self.pp1 = ExtractBytesFromIndex(data, 8, 9) # offset 8
        self.pp2 = ExtractBytesFromIndex(data, 9, 10) # offset 9
        self.pp3 = ExtractBytesFromIndex(data, 10, 11) # offset 10
        self.pp4 = ExtractBytesFromIndex(data, 11, 12) # offset 11

class EV_Condition:
    def __init__(self, data):
        self.data = data
        self.hp_ev = ExtractBytesFromIndex(data, 0, 1) # offset 0
        self.attack_ev = ExtractBytesFromIndex(data, 1, 2) # offset 1
        self.defense_ev = ExtractBytesFromIndex(data, 2, 3) # offset 2
        self.speed_ev = ExtractBytesFromIndex(data, 3, 4) # offset 3
        self.sp_attack_ev = ExtractBytesFromIndex(data, 4, 5) # offset 4
        self.sp_defense_ev = ExtractBytesFromIndex(data, 5, 6) # offset 5
        self.coolness = ExtractBytesFromIndex(data, 6, 7) # offset 6
        self.beauty = ExtractBytesFromIndex(data, 7, 8) # offset 7
        self.cuteness = ExtractBytesFromIndex(data, 8, 9) # offset 8
        self.smartness = ExtractBytesFromIndex(data, 9, 10) # offset 9
        self.toughness = ExtractBytesFromIndex(data, 10, 11) # offset 10
        self.feel = ExtractBytesFromIndex(data, 11, 12) # offset 11

class Miscellaneous:
    def __init__(self, data):
        self.data = data
        self.pokerus_status = ExtractBytesFromIndex(data, 0, 1) # offset 0
        self.met_location = ExtractBytesFromIndex(data, 1, 2) # offset 1
        self.origin_info = ExtractBytesFromIndex(data, 2, 4) # offset 2
        self.IV_Egg_Ability = ExtractBytesFromIndex(data, 4, 8) # offset 4
        self.Ribbons_Obediance = ExtractBytesFromIndex(data, 8, 12) # offset 8




party = PokemonParty(party_data_raw)
# print(party.party_data_raw + "\n")
#
# print(party.personality_value)
# print(party.OT_ID)
# print(party.nickname)
# print(party.language)
# print(party.OT_name)
# print(party.markings)
# print(party.checksum)
# print(party.unknown)
# print(party.status)
# print(party.level)
# print(party.pokerus)
# print(party.curr_hp)
# print(party.tot_hp)
# print(party.attack)
# print(party.defense)
# print(party.speed)
# print(party.sp_attack)
# print(party.sp_defense)
# print("\n\n")




# pok_data_order = party.data.order
# print("pok_data_order: " + pok_data_order)
# print("party.data.growth.data: " + party.data.growth.data)
# print("party.data.growth.species: " + party.data.growth.species)
# print("party.data.misc.data: " + party.data.misc.data)
# print("\n")



# personality_value = DD07E0C1 = 3708281025
# order_num = personality_value % 24 = 9
# order = AEMG
# OT_ID = 058DE154 = 93184340
# growth.species = D88A0191
# key = OT_ID XOR personality_value = 058DE154 XOR DD07E0C1 = d88a0195
# pokemon species = d88a0195 XOR D88A0191 = 4


pokemon = party.data

print("personality_value = " + pokemon.personality_value)
print("personality - dec: " + str(int(pokemon.personality_value, 16)))
print("\n")

print("OT_ID = " + pokemon.OT_ID)
print("\n")

print("pokemon.growth.species = " + pokemon.growth.species)
print("DATA: " + pokemon.growth.data)
print("\n")

print("KEY = " + str(pokemon.key))
print("\n")

print("ANS: " + str(int(pokemon.OT_ID, 16) ^ int(pokemon.personality_value, 16)))
print("\n")





# --
