from bs4 import BeautifulSoup


with open("Pokemon-Index.html") as f:
    html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find("table")

    notDone = True
    row = table.findNext("tr").findNext("tr").findNext("tr").findNext("tr")
    while notDone:
        pokemon = row.findNext("tr").text


        print(pokemon.replace("\n", "*")) # .replace("\n", " | ")
        row = row.findNext("tr")
        exit()

    f.close()
