Repository contenant le projet Kayak. 
Le projet est entièrement réalisé dans le notebook: Projet_Kayak.ipynb.
Le scrapping est réalisé par le fichier Booking_scrapping.py
Le fichier City_dest_ID.csv est nécessaire pour venir scrapper les données de chaque ville sur Booking.com

Les fichiers Df_current, df_previsions et score_city, sont issus de la partie "météorologique". Ils contiennent respectivement
les prévisions météo actuelles et futures, et le score de chaque ville qui permet de définir la ville privilégiée.

Le fichier Booking_results.csv contient les informations des hotels scrappés sur Booking.com

Les fichiers Booking_results.csv et Df_previsions.csv sont envoyés sur un bucket S3.

Enfin dans une dernière partie, les deux fichiers précédents sont téléchargés sur S3, pour être transférés vers une database.
La database est ensuite intérrogé via SQL Alchemy, et des commandes SQL sont aussi envoyées directement dans PGAdmin.
Des screens des requêtes se situent dans le dossier "screen/"
