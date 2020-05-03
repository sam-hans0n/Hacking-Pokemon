
import Pokemon


party_data_raw = "C670482E5401384BCDCBCFC3CCCEC6BFFF730202BBBBBBBBBBBBBB00636A0000927170659271706592717065B371576592717065B16F7065957170651571706592377065922975471003937D927170650000000005FF130013000A000C00090009000D0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

def isValidPokemonName(name):
    with open("Pokemon-List.txt", "r") as f:
        data = f.read()
        pokemon_data = data.split("\n")
        for poke in pokemon_data:
            if name == poke[poke.find("|")+1:]: # extract only the name
                return True
    return False


def isValidPokemonLevel(level):
    if (int(level) >= 1 and int(level) <= 100):
        return True
    else:
        return False


def GetPokemonID(name):
    with open("Pokemon-List.txt", "r") as f:
        data = f.read()
        pokemon_data = data.split("\n")
        for poke in pokemon_data:
            if name == poke[poke.find("|")+1:]:
                return poke[:3]

    return None


# Pokemon games use a proprietary character encoding... This is an unfortunate
# hurdle but one that must be overcame.
# I like to think of this as the 'fast way' to convert to pokemon character
# standards.
def EncodeName(str):
    columns = "0123456789ABCDEF"
    table = []
    table.append(["B", "***********ABCDE"])
    table.append(["C", "FGHIJKLMNOPQRSTU"])
    table.append(["D", "VWXYZabcdefghijk"])
    table.append(["E", "lmnopqrstuvwxyz"])

    encoded_str = ""
    char_count = 0
    for char in str:
        for row in table:
            if char in row[1]:
                encoded_str += row[0]
                encoded_str += columns[row[1].find(char)]
                char_count += 1
    return encoded_str + (10-char_count)*"00" # nickname is always 10 bytes




# ---- Main ----

pokemon = Pokemon.Pokemon(party_data_raw)
pokemon_data = pokemon.data

print("key: " + hex(pokemon.data.key))
print("order: " + pokemon.data.order + "\n")

name = input("Enter name of Pokemon (a-z): ")
while not isValidPokemonName(name):
    print("\n\n That Pokemon does not exist.")
    name = input("Enter name of Pokemon (capitalize first letter): ")

# Set new pokemon info:
pokemon.nickname = EncodeName(name)
id = int(GetPokemonID(name), 16)
diff = id - 7
pokemon.checksum = hex(int(pokemon.checksum, 16) + diff)[-4:]
print(str(diff))
pokemon.data.growth.species = hex(id ^ pokemon_data.key)[-4:] # extract last 4 chars

print("\nold str:")
print("C670482E 5401384B CDCBCFC3CCCEC6BFFF73 0202 BBBBBBBBBBBBBB 00 636A 0000 92 71 70 65 92 71 70 65 92 71 70 65 B371 5765 9271 7065 B1 6F 70 65 9571 7065 15717065 92 37 70 65 92 29 7547 1003937D 92717065 0000000005FF130013000A000C00090009000D0000")

print("\nspecies = " + pokemon.data.growth.species)
print("\nnew str:")
pokemon.GetRawBytes()
exit()

new_level = input("Enter new pokemon level (1-100): ")
while not isValidPokemonLevel(new_level):
    print("\n\n That level is invalid. Must be 1-100")
    new_level = input("Enter new pokemon level (1-100): ")























#
