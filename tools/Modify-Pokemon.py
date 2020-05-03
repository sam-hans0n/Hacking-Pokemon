
import Pokemon

party_data_raw = "C670482E5401384BCDCBCFC3CCCEC6BFFF730202BBBBBBBBBBBBBB00636A0000927170659271706592717065B371576592717065B16F7065957170651571706592377065922975471003937D927170650000000005FF130013000A000C00090009000D0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"


def isValidPokemonName(name):
    with open("Pokemon-List.txt", "r") as f:
        data = f.read()

        pokemon_data = data.split("\n")
        for pokemon in pokemon_data:
            if name in pokemon:
                return False
            else:
                return True


# Pokemon games use a proprietary character encoding... This is an unfortunate
# hurdle but one that must be overcame.
# I like to think of this as the 'fast way' to convert to pokemon character
# standards.
def EncodeStr(str):

    columns = "0123456789ABCDEF"
    table = []
    table.append(["B", "***********ABCDE"])
    table.append(["C", "FGHIJKLMNOPQRSTU"])
    table.append(["D", "VWXYZabcdefghijk"])
    table.append(["E", "lmnopqrstuvwxyz"])

    encoded_str = ""
    for char in str:
        for row in table:
            if char in row[1]:
                encoded_str += row[0]
                encoded_str += columns[row[1].find(char)]

    return encoded_str


    #for c in row


# personality_value = DD07E0C1 = 3708281025
# order_num = personality_value % 24 = 9
# order = AEMG
# OT_ID = 058DE154 = 93184340
# growth.species = D88A0191
# key = OT_ID XOR personality_value = 058DE154 XOR DD07E0C1 = d88a0195
# pokemon species = d88a0195 XOR D88A0191 = 4

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

# ---- Main ----

pokemon = Pokemon.Pokemon(party_data_raw)
pokemon_data = pokemon.data


name = input("Enter name of Pokemon (a-z): ")
#if isValidPokemonName(name):
    #print("\n\n That Pokemon does not exist.")
    #name = input("Enter name of Pokemon (a-z): ")

print(EncodeStr(name))

new_id = input("Enter ID of Pokemon (hex from 1-1B7): ")
new_level = input("Enter new pokemon level (1-100): ")























#
