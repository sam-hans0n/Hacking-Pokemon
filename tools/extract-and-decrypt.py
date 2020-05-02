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


party_data_raw = "C670482E5401384BCDCBCFC3CCCEC6BFFF730202BBBBBBBBBBBBBB00636A0000927170659271706592717065B371576592717065B16F7065957170651571706592377065922975471003937D927170650000000005FF130013000A000C00090009000D000000000000000000000000000000000000000000000000000000000000000000"




def LittleToBigEndian(byte_str):
    bytes_arr = []
    for i in range(0, len(byte_str), 2):
        bytes_arr.append(byte_str[i:i+2])
    bytes_arr = list(reversed(bytes_arr))
    bytes_little_endian = ''.join(bytes_arr) # essentially, the .implode() function from PHP
    return bytes_little_endian

# Always reverse at the LOWEST LEVEL!
# Meaning, reverse once we are done dividing the byte str into objs
def ExtractBytesFromIndexAndReverse(byte_str, start, end):
    return LittleToBigEndian(byte_str[start*2:end*2]) # 2 because there are 2 chars ber byte

# No reverse, for when we have to keep diving bytes into substructures
def ExtractBytesFromIndex(byte_str, start, end):
    return byte_str[start*2:end*2] # 2 because there are 2 chars ber byte


class PokemonParty:
    def __init__(self, party_data_raw):
        self.party_data_raw = party_data_raw
        self.personality_value = ExtractBytesFromIndexAndReverse(self.party_data_raw, 0, 4) # offset 0
        self.OT_ID = ExtractBytesFromIndexAndReverse(self.party_data_raw, 4, 8) # offset 4
        self.nickname = ExtractBytesFromIndexAndReverse(self.party_data_raw, 8, 18) # offset 8
        self.language = ExtractBytesFromIndexAndReverse(self.party_data_raw, 18, 20) # offset 18
        self.OT_name = ExtractBytesFromIndexAndReverse(self.party_data_raw, 20, 27) # offset 20
        self.markings = ExtractBytesFromIndexAndReverse(self.party_data_raw, 27, 28) # offset 27
        self.checksum = ExtractBytesFromIndexAndReverse(self.party_data_raw, 28, 30) # offset 28
        self.unknown = ExtractBytesFromIndexAndReverse(self.party_data_raw, 30, 32) # offset 30
        self.data = PokemonData(ExtractBytesFromIndex(self.party_data_raw, 32, 80), self.personality_value, self.OT_ID) # offset 32
        self.status = ExtractBytesFromIndexAndReverse(self.party_data_raw, 80, 84) # offset 80 -- can't reverse yet
        self.level = ExtractBytesFromIndexAndReverse(self.party_data_raw, 84, 85) # offset 84
        self.pokerus = ExtractBytesFromIndexAndReverse(self.party_data_raw, 85, 86) # offset 85
        self.curr_hp = ExtractBytesFromIndexAndReverse(self.party_data_raw, 86, 88) # offset 86
        self.tot_hp = ExtractBytesFromIndexAndReverse(self.party_data_raw, 88, 90) # offset 88
        self.attack = ExtractBytesFromIndexAndReverse(self.party_data_raw, 90, 92) # offset 90
        self.defense = ExtractBytesFromIndexAndReverse(self.party_data_raw, 92, 94) # offset 92
        self.speed = ExtractBytesFromIndexAndReverse(self.party_data_raw, 94, 96) # offset 94
        self.sp_attack = ExtractBytesFromIndexAndReverse(self.party_data_raw, 96, 98) # offset 96
        self.sp_defense = ExtractBytesFromIndexAndReverse(self.party_data_raw, 98, 100) # offset 98



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
            self.growth = Growth(ExtractBytesFromIndex(self.data, 36, 48))
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
        self.key = int(self.personality_value, 16) ^ int(self.OT_ID, 16)
        self.growth.pokemon_no = int(self.growth.species, 16) ^ self.key


class Growth:
    def __init__(self, data):
        self.data = data
        self.pokemon_no = "" # true pokemon number (in hex)
        self.species = ExtractBytesFromIndexAndReverse(data, 0, 2) # offset 0
        self.item_held = ExtractBytesFromIndexAndReverse(data, 2, 4) # offset 2
        self.experience = ExtractBytesFromIndexAndReverse(data, 4, 8) # offset 4
        self.pp_bonuses = ExtractBytesFromIndexAndReverse(data, 8, 9) # offset 8
        self.friendship = ExtractBytesFromIndexAndReverse(data, 9, 10) # offset 9
        self.unknown = None # offset 10

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

class Miscellaneous:
    def __init__(self, data):
        self.data = data
        self.pokerus_status = ExtractBytesFromIndexAndReverse(data, 0, 1) # offset 0
        self.met_location = ExtractBytesFromIndexAndReverse(data, 1, 2) # offset 1
        self.origin_info = ExtractBytesFromIndexAndReverse(data, 2, 4) # offset 2
        self.IV_Egg_Ability = ExtractBytesFromIndexAndReverse(data, 4, 8) # offset 4
        self.Ribbons_Obediance = ExtractBytesFromIndexAndReverse(data, 8, 12) # offset 8



# personality_value = DD07E0C1 = 3708281025
# order_num = personality_value % 24 = 9
# order = AEMG
# OT_ID = 058DE154 = 93184340
# growth.species = D88A0191
# key = OT_ID XOR personality_value = 058DE154 XOR DD07E0C1 = d88a0195
# pokemon species = d88a0195 XOR D88A0191 = 4

party = PokemonParty(party_data_raw)
pokemon = party.data

print("\n---------------- Pokemon Info ---------------")
print("** The following are in Big Endian format\n")
print("personality_value: " + pokemon.personality_value)
print("OT_ID: " + pokemon.OT_ID)
print("KEY FOUND: " + hex(pokemon.key))

print("\nEncrypted Species (in hex): " + pokemon.growth.species)
print("Pokemon No (in hex): " + hex(pokemon.growth.pokemon_no))

print("\nPokemon order: " + pokemon.order)





# --
