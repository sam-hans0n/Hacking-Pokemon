
import Pokemon

party_data_raw = "C670482E5401384BCDCBCFC3CCCEC6BFFF730202BBBBBBBBBBBBBB00636A0000927170659271706592717065B371576592717065B16F7065957170651571706592377065922975471003937D927170650000000005FF130013000A000C00090009000D0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"



# personality_value = DD07E0C1 = 3708281025
# order_num = personality_value % 24 = 9
# order = AEMG
# OT_ID = 058DE154 = 93184340
# growth.species = D88A0191
# key = OT_ID XOR personality_value = 058DE154 XOR DD07E0C1 = d88a0195
# pokemon species = d88a0195 XOR D88A0191 = 4

pokemon = Pokemon.Pokemon(party_data_raw)
pokemon_data = pokemon.data

# print("\n---------------- Pokemon Info ---------------")
# print("** The following are in Big Endian format:\n")
# print("personality_value: " + pokemon_data.personality_value)
# print("OT_ID: " + pokemon_data.OT_ID)
# print("KEY FOUND: " + hex(pokemon_data.key))
#
# print("\nEncrypted Species (in hex): " + pokemon_data.growth.species)
# print("Pokemon No (in hex): " + hex(pokemon_data.growth.pokemon_no))
#
# print("\nPokemon order: " + pokemon_data.order)


# Checksum information:
print("\n\nChecksum: " + pokemon.checksum)

new_pokemon = input("Enter name of Pokemon: ")
new_id = input("Enter ID of Pokemon: ")
