
# Sam Hanson

import pprint


trainer_data_raw = "95273B7E54E18D05BDC2BBCCC7BBC8BEBFCC0202BBBBBBBBBBBBBB00E5F90000C1C6B67BC1C6B67BC1C6B67BC5C6B67B46C6B67BC180B67BC19EB359AB36275BC1C6B67BCBC69B7BC1C6B67BE2EEB67B0000000005FF130013000A000A000B0009000B0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FF0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"


class Trainer:
    def __init__(self, trainer_data_raw):
        self.trainer_data_raw = trainer_data_raw
        self.personality_value = self.ExtractBytesFromIndex(0, 4) # offset 0
        self.OT_ID = self.ExtractBytesFromIndex(4, 8) # offset 4
        self.nickname = self.ExtractBytesFromIndex(8, 18) # offset 8
        self.language = self.ExtractBytesFromIndex(18, 20) # offset 18
        self.OT_name = self.ExtractBytesFromIndex(20, 27) # offset 20
        self.markings = self.ExtractBytesFromIndex(27, 28) # offset 27
        self.checksum = self.ExtractBytesFromIndex(28, 30) # offset 28
        self.unknown = self.ExtractBytesFromIndex(30, 32) # offset 30
        self.data = PokemonData(self.ExtractBytesFromIndex(32, 80)) # offset 32
        self.status = self.ExtractBytesFromIndex(80, 84) # offset 80
        self.level = self.ExtractBytesFromIndex(84, 85) # offset 84
        self.pokerus = self.ExtractBytesFromIndex(85, 86) # offset 85
        self.curr_hp = self.ExtractBytesFromIndex(86, 88) # offset 86
        self.tot_hp = self.ExtractBytesFromIndex(88, 90) # offset 88
        self.attack = self.ExtractBytesFromIndex(90, 92) # offset 90
        self.defense = self.ExtractBytesFromIndex(92, 94) # offset 92
        self.speed = self.ExtractBytesFromIndex(94, 96) # offset 94
        self.sp_attack = self.ExtractBytesFromIndex(96, 98) # offset 96
        self.sp_defense = self.ExtractBytesFromIndex(98, 100) # offset 98

    def ExtractBytesFromIndex(self, start, end):
        return self.trainer_data_raw[start*2:end*2]





class PokemonData:
    def __init__(self, data):
        self.key = None
        self.data = data



class GrowthSection:
    def __init__(self, species, item_held, experience, pp_bonuses, friendship, unknown):
        self.species = species
        self.item_helf = item_held
        self.experience = experience
        self.pp_bonuses = pp_bonuses
        self.friendship = friendship
        self.unknown = unknown

class AttacksSection:
    def __init__(self, move1, move2, move3, move4, pp1, pp2, pp3, pp4):
        self.move1 = move1
        self.move2 = move2
        self.move3 = move3
        self.move




print(Trainer(trainer_data_raw).trainer_data_raw + "\n")

print(Trainer(trainer_data_raw).personality_value)
print(Trainer(trainer_data_raw).OT_ID)
print(Trainer(trainer_data_raw).nickname)
print(Trainer(trainer_data_raw).language)
print(Trainer(trainer_data_raw).OT_name)
print(Trainer(trainer_data_raw).markings)
print(Trainer(trainer_data_raw).checksum)
print(Trainer(trainer_data_raw).unknown)
print(Trainer(trainer_data_raw).data)
print(Trainer(trainer_data_raw).status)
print(Trainer(trainer_data_raw).level)
print(Trainer(trainer_data_raw).pokerus)
print(Trainer(trainer_data_raw).curr_hp)
print(Trainer(trainer_data_raw).tot_hp)
print(Trainer(trainer_data_raw).attack)
print(Trainer(trainer_data_raw).defense)
print(Trainer(trainer_data_raw).speed)
print(Trainer(trainer_data_raw).sp_attack)
print(Trainer(trainer_data_raw).sp_defense)
