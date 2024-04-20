import requests
from bs4 import BeautifulSoup

language = "en"

url = f'https://astana.citypass.kz/{language}/category/muzei-i-galerei/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
links = soup.select('a.sights__item--btn, a.sights__item--btn-linck')
plain_links = [link['href'] for link in links if 'href' in link.attrs]

new_plain_links = []
for i in range(len(plain_links)):
    if not plain_links[i] in new_plain_links:
        new_plain_links.append(plain_links[i])
print(plain_links)
print(new_plain_links)
print(len(new_plain_links))
input()
plain_links = new_plain_links
def clean_data(text):
    replacements = {
        '&shy;': '',  # Remove soft hyphens
        '&nbsp;': ' ',  # Replace non-breaking spaces with regular spaces
        'NBSP': ' ',  # Assuming 'NPSB' should be removed; adjust if it's a typo
        'SHY': ' ',  # Remove if it appears as plain text
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

base_url = f'https://astana.citypass.kz/{language}/'
normalized_links = []
for link in plain_links:
    if base_url in link:
        normalized_links.append(link)

parsed_data = []

for link in normalized_links:
    print(link)
    response = requests.get(link)
    if response.status_code != 200:
        print("Error code: ", response.status_code)
        raise Exception(link)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        page_soup = BeautifulSoup(response.text, 'html.parser')

        title = page_soup.find('div', class_='object_content--title')
        description = page_soup.find('div', class_='object_content--desc')
        title_text = title.get_text(strip=True) if title else 'No Title Found'

        # description_parts = []
        # description_ps = page_soup.select('div.object_content--desc p')
        # for p in description_ps:
        #     print(p)
        #     if not p.find('strong'):
        #         # Only add text from <p> tags without any <br> tags
        #         description_parts.append(p.get_text(strip=True))
        # description_text = ' '.join(description_parts)
        description_text = description.get_text(strip=True) if description else 'No Description Found'

        address_div = page_soup.find('div', class_='object__info--adres')
        if address_div:
            # Extract text, then clean it to remove unnecessary characters
            address = address_div.get_text(separator=" ", strip=True)
        else:
            address = 'No address specified'
        transport_numbers = []
        transport_spans = page_soup.select('div.object_content-too span')
        for span in transport_spans:
            number = span.get_text(strip=True).replace('№', '').replace(',', '').strip()
            if number.isdigit():
                transport_numbers.append(number)

        timetable = []
        timetable_entries = page_soup.select('div.object_content--timetable ul li')
        for entry in timetable_entries:
            period = entry.find('div', class_='object_content-one').get_text(strip=True)
            hours = entry.find('div', class_='object_content-too').get_text(strip=True)
            timetable.append(f"{period}: {hours}")

        if not transport_numbers:
            timetable = "No bus numbers specified"

        if not timetable:
            timetable = "No schedule specified"

        print(type(title), type(description_text), type(address), type(transport_numbers), type(timetable))

        page_info = {
            'url': link,
            'title': title_text,
            'description': description_text,
            'address': address,
            'transport_numbers': transport_numbers,
            'timetable': timetable
        }

        parsed_data.append(page_info)

        with open(f'info_{language}.txt', 'a') as f:
            for key, value in page_info.items():
                if key == 'description':
                    new_value = clean_data(value)
                else:
                    new_value = value
                f.writelines(f"{key}==={new_value}\n")
            f.writelines("\n\n\n\n\n")
