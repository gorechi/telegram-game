import requests

url = "https://lingvotech-ru-lingvo-v1.p.rapidapi.com/api"

querystring = {"sentence":"разбойница","op":"syntax_API"}

headers = {
	"X-RapidAPI-Key": "75ce9dc7f2msh1fce950769923b2p16e39ajsnf59d1d2dfaa9",
	"X-RapidAPI-Host": "lingvotech-ru-lingvo-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())