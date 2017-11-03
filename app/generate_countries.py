import bs4

class GenerateCountries:
    @staticmethod
    def get_countries():

        try:
            html = open('countries.html', 'r')
        except FileNotFoundError:
            html = open('app/countries.html', 'r')

        soup = bs4.BeautifulSoup(html, "lxml")
        c = list()

        for option in soup.find_all('option'):
            #print(option['value'] + ", " + option.text)
            c.append((option['value'], option.text))

        html.close()
        return c
