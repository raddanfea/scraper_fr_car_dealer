

# Scraper

A simple selenium scraper that scrapes all cars and all configurations from https://store.opel.fr and puts the results into a sql db.

# Webpage

A simple flask webpage that can display the scraped results.  
Can filter based on scraping date and configuration details.


# Crontab

```
2 * * * /path/to/python /path/to/script.py
```

- Runs this script every day at 2 AM.