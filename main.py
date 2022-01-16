import sys, urllib.request, os
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup as bso

COOKIE = "ansi_sciagnij=vgj84dvni6ojeo3sjb05m56rd2"
SEARCH_URL = "http://animesub.info/szukaj.php"
DOWNLOAD_URL = "http://animesub.info/sciagnij.php"
CODE_STANDARD = "ISO-8859-2"

def get_html_soup_object(url, headers = ""):
    try:
        headers_args = urllib.parse.urlencode(headers)
        if headers_args != "":
            url += "?" + headers_args
            
        request = urllib.request.Request(url)
        request.add_header("Cookie", COOKIE)
        
        fp = urllib.request.urlopen(request)
        bytes = fp.read()
        fp.close()
        
    except HTTPError as e:
        bytes = e.read()
    except URLError:
        print("Błąd sieci! Upewnij się czy działa połączenie z internetem.")
        sys.exit(2)
        
    html = bytes.decode(CODE_STANDARD)
        
    return bso(html, "html.parser")

def download_subtitles(url, data, search_text):
    try:
        for title, post_data in data:
            request = urllib.request.Request(url, data=post_data.encode('utf-8'))
            request.add_header("Cookie", COOKIE)
            request.add_header("Content-Type", "application/x-www-form-urlencoded")
            
            fp = urllib.request.urlopen(request)
            bytes = fp.read()
            fp.close()
            
            html = bytes.decode(CODE_STANDARD)
            bso_data = bso(html, "html.parser")
            if len(bso_data.find_all("center")) != 0:
                print(bso_data.find("center").get_text())
            else:
                folder_path = os.path.join("Downloaded", search_text)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                file_name = os.path.join(folder_path, title + '.zip')
                if not os.path.exists(file_name):
                    ass = open(file_name, 'wb')
                    ass.write(bytes)
                    ass.close()
                    print("Pomyślnie zapisano plik '" + title + "'!")
                else:
                    print("Plik '" + title + "' już istnieje, więc został pominięty.")
        
    except HTTPError as e:
        bytes = e.read()
    except URLError:
        print("Błąd sieci! Upewnij się czy działa połączenie z internetem.")
        sys.exit(2)
    
def parse_file_name(name):
    banned_chars = ['\\', '/', ':', '?', '"', '<', '>', '|']
    for char in banned_chars:
        name = name.replace(char, "_")
        
    return name
    
def search_subtitles(search_text):
    page = 0
    is_found = False
    while True:
        titles = []
        post_data = []
        headers = {
            "szukane" : search_text,
            "pTitle" : "org",
            "pSortuj": "t_jap",
            "od": page
        }
        
        all_data = get_html_soup_object(SEARCH_URL, headers).find_all(class_="Napisy")
        all_data = all_data[1:]
        for table in all_data:
            data = table.findAll(class_="KNap")
            title = data[0].findAll("td")[0].get_text()
            name = data[1].findAll("td")[1].get_text() 
            titles.append(parse_file_name(title + " " + name))
            
            inputs = table.find(class_="KKom").find_all("input")
            id = inputs[0]['value']
            sh = inputs[1]['value']
            
            post_text = "id=" + id + "&sh=" + sh + "&single_file=Pobierz+napisy"
            post_data.append(post_text)

        if len(all_data) == 0:
            break
        else:
            is_found = True
        
        zipped_data = zip(titles, post_data)
        download_subtitles(DOWNLOAD_URL, zipped_data, search_text)
        page += 1
    
    return is_found

def main(argv):
    is_found = search_subtitles(argv[0])
    if not is_found:
        print("Nie znaleziono!")
    
if __name__ == "__main__":
    main(sys.argv[1:])
    