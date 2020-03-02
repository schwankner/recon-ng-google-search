#Google Search email/contact harverster for recon-ng


## What does it do?
This is a <a href="https://bitbucket.org/LaNMaSteR53/recon-ng">recon-ng</a> module that allows to import contacts from pages found via Google Search. It parses the found pages and takes all contacts found for a domain and stores them into the contacts tables.

## Installation
Just put it in the `modules/recon/domain-contacts` directory (or any modules subdirectory) of the recon-ng framwork. This is

     ~/.recon-ng/modules/recon/domain-contacts
     
on Kali.

Do 

    modules reload
    
and you should be ready to go.

## Example

```
[recon-ng][default] > workspaces create Telekom
[recon-ng][telekom] > db insert domains
domain (TEXT): telekom.de
notes (TEXT): 
[*] 1 rows affected.
[recon-ng][telekom] > modules load recon/domains-contacts/google_search
[recon-ng][telekom][google_search] > run
...

```
## Help

```

      Name: Google Search Contact Harvester
    Author: schwankner
   Version: 1.0

Description:
  Harvests e-mails via Google by searching with Google Search and opening and parsing the results. Can
  parse html as well as pdfs and add e-mails to the 'contacts' table.

Options:
  Name     Current Value  Required  Description
  -------  -------------  --------  -----------
  LIMIT    100            yes       limit total number of results you parse from Google
  LOCALE   de             yes       use the Google Search page from this tld
  SOURCE   default        yes       source of input (see 'info' for details)
  TIMEOUT  10             no        timeout for page requests

Source Options:
  default        SELECT DISTINCT domain FROM domains WHERE domain IS NOT NULL
  <string>       string representing a single input
  <path>         path to a file containing a list of inputs
  query <sql>    database query returning one column of inputs

Comments:
  * Be sure to set the 'locale' option to the region your target is located in.
  * You will get better results if you use the Google Search page from your targets country


```


