
import Pokemon

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

party_data_raw = "C670482E5401384BCDCBCFC3CCCEC6BFFF730202BBBBBBBBBBBBBB00636A0000927170659271706592717065B371576592717065B16F7065957170651571706592377065922975471003937D927170650000000005FF130013000A000C00090009000D0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

# Check whether user provided name is a valid Pokemon name against our "database"
def isValidPokemonName(name):
    with open("Pokemon-List.txt", "r") as f:
        data = f.read()
        pokemon_data = data.split("\n")
        for poke in pokemon_data:
            if name == poke[poke.find("|")+1:]: # extract only the name
                return True
    return False

# Check whether user provided level is a valid Pokemon level
def isValidPokemonLevel(level):
    if (int(level) >= 1 and int(level) <= 100):
        return True
    else:
        return False

# Get the Pokemon ID number from out "database" via corresponding Pokemon name
def GetPokemonID(name):
    with open("Pokemon-List.txt", "r") as f:
        data = f.read()
        pokemon_data = data.split("\n")
        for poke in pokemon_data:
            if name == poke[poke.find("|")+1:]:
                return poke[:3]

    return None


# Pokemon games use a proprietary character encoding...
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

if len(party_data_raw) == 0:
    print("You must add the byte data of your first Pokemon to party_data_raw!")
pokemon = Pokemon.Pokemon(party_data_raw)
pokemon_data = pokemon.data

name = input("Enter name of Pokemon (a-z): ")
while not isValidPokemonName(name):
    print("\n\n That Pokemon does not exist.")
    name = input("Enter name of Pokemon (capitalize first letter): ")

# Set new pokemon info:
pokemon.nickname = EncodeName(name)
id = int(GetPokemonID(name), 16)
diff = id - 7
pokemon.checksum = hex(int(pokemon.checksum, 16) + diff)[-4:]
pokemon.data.growth.species = hex(id ^ pokemon_data.key)[-4:] # extract last 4 chars

print("\nCopy this into the memory map starting at 0x02024284:")
pokemon.GetRawBytes()

# FUTURE VERSIONS:
# new_level = input("Enter new pokemon level (1-100): ")
# while not isValidPokemonLevel(new_level):
#     print("\n\n That level is invalid. Must be 1-100")
#     new_level = input("Enter new pokemon level (1-100): ")
