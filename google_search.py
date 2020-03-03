from googlesearch import search
import io
import pdfplumber
from recon.core.module import BaseModule
import re


class Module(BaseModule):
    meta = {
        'name': 'Google Search Contact Harvester',
        'author': 'schwankner',
        'version': '1.0',
        'description': 'Harvests e-mails via Google by searching with Google Search and opening and parsing the results. Can parse html as well as pdfs and add e-mails to the \'contacts\' table.',
        'dependencies': ['googlesearch', 'pdfplumber'],
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
                r = self.request('GET', url, stream=True, timeout=self.options['timeout'], verify=False)
                if 200 == r.status_code and 'application/pdf' == r.headers['Content-Type']:
                    with io.BytesIO() as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                        pdf = pdfplumber.load(f)
                        text = ''
                        for i in range(0, len(pdf.pages)):
                            page = pdf.pages[i]

                            page_text = page.extract_text()
                            if isinstance(page_text, str):
                                text = text + page_text
                        pdf.close()
                        return text
            except Exception as e:
                self.alert(url + ' ' + str(e))
        else:
            try:
                r = self.request('GET', url, stream=True, timeout=self.options['timeout'], verify=False)
                if 200 == r.status_code:
                    return r.text
            except Exception as e:
                self.alert(url + ' ' + str(e))

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

