# companies-house-api

Helps Download documents using companies house api

https://developer.companieshouse.gov.uk/api

## Setup

Sign up and get token for the api. 
Add token to a passwords.py as follows. (Make sure passwords.py is in your .gitignore)

``` AUTH_TOKEN = YOURTOKEN ```


When setting up token you have to specify IP, but the token apears to work with any ip.

## Useage

```

python companies.py -s <search term> -n <number of companies> -d <number of documents per company>

```

e.g.

```

python companies.py -s dog -n 20 -d 5

```

## Bugs

@TODO Fix bug with the nubmer of companies

