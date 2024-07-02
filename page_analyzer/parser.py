import requests
from bs4 import BeautifulSoup


# function for getting data from site for urls_checks db table
def get_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return False

    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.find('h1')
    title = soup.find('title')
    description = soup.find('meta', attrs={'name': 'description'})

    site_content = {
        'response_code': response.status_code,
        'h1': h1.get_text() if h1 else '',
        'title': title.get_text() if title else '',
        'description': description['content'] if description else ''
    }
    return site_content
