from googlesearch import search
import requests
import io
import pdfplumber
from recon.core.module import BaseModule
from recon.mixins.search import BingAPIMixin
import re


class Module(BaseModule, BingAPIMixin):
    meta = {
        'name': 'Google Search Contact Harvester',
        'author': 'schwankner',
        'version': '1.0',
        'description': 'Harvests e-mails via Google by searching with Google Search and opening and parsing the results. Can parse html as well as pdfs and add e-mails to the \'contacts\' table.',
        'comments': (
            'Be sure to set the \'locale\' option to the region your target is located in.',
            'You will get better results if you use the Google Search page from your targets country',
        ),
        'query': 'SELECT DISTINCT domain FROM domains WHERE domain IS NOT NULL',
        'options': (
            ('locale', 'de', True, 'use the Google Search page from this tld'),
            ('limit', 100, True, 'limit total number of results you parse from Google'),
            ('timeout', 10, False, 'timeout for page requests'),
        ),
    }

    def get_text(self, url):
        if url[-4:] == '.pdf':
            try:
                with requests.get(url, stream=True, timeout=self.options['timeout'], verify=False) as r:
                    if 200 == r.status_code and 'application/pdf' == r.headers['Content-Type']:
                        with io.BytesIO() as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                            pdf = pdfplumber.load(f)
                            page = pdf.pages[0]
                            text = page.extract_text()
                            pdf.close()
                            return text
            except requests.exceptions.RequestException as e:
                self.alert(url, e)
        else:
            try:
                with requests.get(url, stream=True, timeout=self.options['timeout'], verify=False) as r:
                    if 200 == r.status_code:
                        return r.text
            except requests.exceptions.RequestException as e:
                self.alert(url, e)

    def module_run(self, domains):
        for domain in domains:
            found = {}
            query = "\"@" + domain + "\""
            for url in search(query,  # The query you want to run
                              tld=self.options['locale'],  # The top level domain
                              lang=self.options['locale'],  # The language
                              num=10,  # Number of results per page
                              start=0,  # First result to retrieve
                              stop=self.options['limit'],  # Last result to retrieve
                              pause=2.0,  # Lapse between HTTP requests
                              ):

                text = self.get_text(url)
                if isinstance(text, str):
                    findings = re.findall(
                        r"(?:[A-Za-z0-9!#$%&'*+=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@" + domain,
                        text)
                    for finding in findings:
                        if finding not in found:
                            self.insert_contacts(email=finding, notes='Source: ' + url)
                            found[finding] = [finding]

