import os
import logging
import csv
from datetime import date, timedelta

import scrapy
from scrapy.crawler import CrawlerProcess

class BookingSpider(scrapy.Spider):
    # Name of spider
    name = 'booking_spider'
    start_urls = ['https://www.booking.com/searchresults.fr.html']
    max_pages = 3

    PATH_FILE = os.path.dirname(__file__)
    NAME_FILE = "City_dest_ID.csv"
    # NAME_FILE = "City_dest_ID_test.csv"
    PATHNAME_FILE = PATH_FILE + "\\" + NAME_FILE

    print(PATHNAME_FILE)

    def __init__(self, *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        self.dictionnaire_dest_id = self.lire_csv_vers_dictionnaire(BookingSpider.PATHNAME_FILE, cle_colonne=0, valeur_colonne=1)
        self.city = ''


    def parse(self, response):
        # Le formulaire de recherche est identifié par le xpath suivant
        form_xpath = '//form[@action="https://www.booking.com/searchresults.fr.html"]'
        
        for city,dest_id in self.dictionnaire_dest_id.items():
            form_data = {
                'ss': city,
                'ssne': city,
                'ssne_untouched': city,
                'autocomplete': '1',
                'checkin': str(date.today()),
                'checkout': str(date.today()+ timedelta(days=7)),
                'lang': 'fr',
                'sb': '1',
                'src_elem': 'sb',
                'src': 'searchresults',
                'group_adults': '2',
                'no_rooms': '1',
                'group_children': '0',
                'dest_type': 'city',
                'dest_id': dest_id,
            } 

            print("*****************************************")
            print(f"Préparation de la soumission du formulaire avec: {form_data}")

            yield scrapy.FormRequest.from_response(
            # yield scrapy.FormRequest(
                response,
                formxpath=form_xpath,  # You might need to adjust this form XPath
                formdata=form_data,
                callback=self.parse_results,
                cb_kwargs={'city': city}
            )


    def parse_results(self, response, city):
        # This function will be called after (hopefully) the search results page loads.

        print(f"Successfully navigated to: {response.url}")

        hotel_blocks = response.xpath('//div[@data-testid="property-card"]')

        if not hotel_blocks:
             print(f"Pas d'hotel trouvé sur la page de résultats {response.url}")
        else:
            print(f"Nombre d'hôtels trouvés: {len(hotel_blocks)}")

        # Extract hotel names
        for hotel in hotel_blocks:
            hotel_name = str(hotel.xpath('.//div[@data-testid="title"]/text()').get())
            if hotel_name:
                # Gestion du prix de l'hotel
                hotel_price_unicode = hotel.xpath('.//span[@data-testid="price-and-discounted-price"]/text()').get()
                # hotel_price_parts = hotel_price_unicode.split()
                try:
                    hotel_price = str(hotel_price_unicode)
                    
                except (ValueError, IndexError):
                    hotel_price = 0


                # Gestion du review de l'hotel
                hotel_review = hotel.xpath('.//div[@data-testid="review-score"]/div/div[1]/text()').get()

                # Gestion du rating de l'hotel
                hotel_rating_stars_xpath = hotel.xpath('.//div[@data-testid="rating-stars"]')
                hotel_rating_stars = len(hotel_rating_stars_xpath.xpath('.//span'))

                # Gestion de la position de l'hotel au centre
                hotel_position = hotel.xpath('.//span[@data-testid="distance"]/text()').get()

                # Gestion de la description de l'hotel
                hotel_description_base = hotel.xpath('.//div[@data-testid="property-card-unit-configuration"]')
                hotel_description_list = []
                for description in hotel_description_base:
                    spans = description.xpath('.//span/text()').getall()
                    hotel_description_list.extend(spans)
                # print(hotel_description_list)
                hotel_description = '. '.join(hotel_description_list)

                yield {
                    'city': city,
                    'hotel_name': hotel_name,
                    'hotel_price': hotel_price,
                    'hotel_position': hotel_position,
                    'hotel_review': hotel_review,
                    'hotel_rating_star': hotel_rating_stars,
                    'hotel_description': hotel_description,
                    'hotel_url': hotel.xpath('.//a/@href').get(),
                     }
                
 
    def lire_csv_vers_dictionnaire(self,nom_fichier_csv, cle_colonne=0, valeur_colonne=1):
        """
        Lit un fichier CSV et stocke les données dans un dictionnaire.

        Args:
            nom_fichier_csv: Le nom du fichier CSV à lire (chaîne de caractères).
            cle_colonne: L'index de la colonne à utiliser comme clé du dictionnaire (entier, par défaut 0).
            valeur_colonne: L'index de la colonne à utiliser comme valeur du dictionnaire (entier, par défaut 1).

        Returns:
            Un dictionnaire où les clés proviennent de la colonne spécifiée par cle_colonne
            et les valeurs proviennent de la colonne spécifiée par valeur_colonne.
            Retourne un dictionnaire vide en cas d'erreur ou si le fichier est vide.
        """
        donnees = {}
        try:
            with open(nom_fichier_csv, 'r', newline='') as fichier_csv:
                reader = csv.reader(fichier_csv)
                header = next(reader, None)  # Lire la première ligne (en-tête)

                for row in reader:
                    if row:  # Vérifier si la ligne n'est pas vide
                        try:
                            cle = row[cle_colonne].strip()
                            valeur = row[valeur_colonne].strip()
                            donnees[cle] = valeur
                        except IndexError:
                            print(f"Avertissement: Ligne ignorée dans '{nom_fichier_csv}' car elle ne contient pas assez de colonnes.")
        except FileNotFoundError:
            print(f"Erreur: Le fichier '{nom_fichier_csv}' n'a pas été trouvé.")
        except Exception as e:
            print(f"Une erreur s'est produite lors de la lecture du fichier CSV '{nom_fichier_csv}': {e}")
        return donnees

# Name of the file where the results will be saved
filename = "Booking_results.csv"

# If file already exists, delete it before crawling (because Scrapy will concatenate the last and new results otherwise)
PATH = "C:\\Users\\marce\\OneDrive\\Documents\\Formation_JEDHA\\Fullstack\\09 -- Certification\\Kayak\\"
if filename in os.listdir(PATH):
        os.remove(PATH + filename)

# Declare a new CrawlerProcess with some settings
process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/97.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        PATH + filename: {"format": "csv"},
    }
})

# Start the crawling using the spider you defined above
process.crawl(BookingSpider)
process.start()