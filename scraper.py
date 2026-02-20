import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/"
response = requests.get(url)

# Force proper UTF-8 decoding
response.encoding = response.apparent_encoding  

soup = BeautifulSoup(response.text, "html.parser")
books = soup.select(".product_pod")

for book in books:
    title = book.h3.a["title"]
    price = book.select_one(".price_color").text.replace("Â", "")  # remove weird char
    print(title, "-", price)



