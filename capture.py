import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import os
import random

def normalize_url(url):
    return url.rstrip('/')

def should_ignore_url(url):
    return any(ignore_term in url for ignore_term in ['.php', '/wp-json/', '/wp-admin/'])

def crawl_website(domain, sleep_time_range):
    crawled_urls = set()
    to_crawl = [f'https://{normalize_url(domain)}']

    if not os.path.exists('./captures'):
        os.makedirs('./captures')

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    txt_file = f'./captures/{domain}-capture-{timestamp}.txt'
    html_file = f'./captures/{domain}-capture-{timestamp}.html'

    print(f"Generating capture files: {txt_file}, {html_file}")

    with open(txt_file, 'w') as f:
        f.write("Type\tURL\tStatus_Code\tSize\tHeight\n")

    # Setting up HTML with Bootstrap styling
    with open(html_file, 'w') as f:
        f.write("""
        <html>
        <head>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
        <div class="container mt-4">
            <h1>All URLs</h1>
            <table class='table table-bordered table-striped'>
                <tr>
                    <th>Type</th><th>URL</th><th>Status Code</th><th>Size</th><th>Height</th>
                </tr>
        """)

    while to_crawl:
        url = to_crawl.pop(0)
        normalized_url = normalize_url(url)

        if should_ignore_url(normalized_url):
            continue

        if normalized_url not in crawled_urls:
            print(f"Crawling: {normalized_url}")
            try:
                response = requests.get(normalized_url)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                continue

            crawled_urls.add(normalized_url)
            content_type = response.headers.get('Content-Type', '')
            status_code = response.status_code
            page_size = len(response.content)
            page_height = ''

            if 'text/html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_height = len(str(soup.find('body')).split('\n'))

                for tag_name, attr_name in [('a', 'href'), ('script', 'src'), ('link', 'href')]:
                    for tag in soup.find_all(tag_name, **{attr_name: True}):
                        new_url = urljoin(normalized_url, tag[attr_name])
                        new_url = normalize_url(new_url)
                        parsed_url = urlparse(new_url)
                        if parsed_url.netloc == domain and not parsed_url.fragment:
                            if not should_ignore_url(new_url):
                                to_crawl.append(new_url)

                content_type_label = 'HTML'

            elif 'text/css' in content_type or 'application/javascript' in content_type:
                content_type_label = 'Asset'

            elif 'image/' in content_type:
                content_type_label = 'Image'

            else:
                content_type_label = 'Other'

            with open(txt_file, 'a') as f:
                f.write(f"{content_type_label}\t{normalized_url}\t{status_code}\t{page_size}\t{page_height}\n")

            # Using Bootstrap styled table rows
            with open(html_file, 'a') as f:
                f.write(f"<tr><td>{content_type_label}</td><td><a href='{normalized_url}' target='_blank'>{normalized_url}</a></td><td>{status_code}</td><td>{page_size}</td><td>{page_height}</td></tr>")

            sleep_time = random.uniform(*sleep_time_range)
            time.sleep(sleep_time)

    with open(html_file, 'a') as f:
        f.write("</table></div></body></html>\n")

    print("Crawl complete. Capture files generated.")

if __name__ == "__main__":
    domain = input("Enter the domain of the website to crawl (e.g., example.com): ")

    print("Select the type of crawl:")
    print("1. Aggressive (Sleep time between 100ms-500ms)")
    print("2. Careful (Sleep time between 500ms-3000ms)")

    crawl_type_selection = input("Enter the number corresponding to your choice: ").strip()

    sleep_time_range = (0.1, 0.5) if crawl_type_selection == '1' else (0.5, 3)

    crawl_website(domain, sleep_time_range)
