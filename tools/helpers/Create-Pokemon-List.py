from bs4 import BeautifulSoup

# This was the simplest way I could map the Pokemon name
# to the pokemon id. No way was I gonna do all that by
# hand lol.
with open("Pokemon-Index.html") as f:
    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find("table")

    notDone = True
    unownCount = 0
    row = table.findNext("tr").findNext("tr").findNext("tr")
    while notDone:
        pokemon_tr = row.findNext("tr").text

        str = pokemon_tr.split("\n\n")
        # Clean up strings
        id = str[0].replace(" ", "").replace("\n", "")
        name = str[3].replace(" ", "")
        n = hex(int(id, 16))

        # do something with name and id
        print(id + "|" + name)

        # this is how we know when to stop. There are 28
        # Unown pokemon, and they are the last ids ub
        # memory.
        if name == "Unown":
            unownCount += 1
            if unownCount == 28:
                break
        row = row.findNext("tr")

    f.close()
