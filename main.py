import re
import uuid
import json
import dataclasses
from datetime import date

import requests
import pandas as pd
from bs4 import BeautifulSoup

from utils import Logger

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Dnt": "1",
    "Pragma": "no-cache",
    "Referer": "https://educationdestinationasia.com/schools",
    "Sec-Fetch-Site": "same-site",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

URL = "https://educationdestinationasia.com/schools"

PARAMS = {
    "level": "",
    "curriculum": "",
    "country": "",
    "page": 1
}

LEVEL_MAPPINGS = {
    "k": "preschool-kindergarten", 
    "p": "primary", 
    "s": "secondary", 
    "pu": "pre-university",
    "lc": "learning-centre",
    "se": "special-education-needs"
}

COUNTRY_MAPPINGS = { 
    "c": "china", 
    "i": "indonesia", 
    "m": "malaysia", 
    "s": "singapore", 
    "uk": "united-kingdom", 
    "b": "brunei", 
    "sk": "south-korea", 
    "my": "myanmar", 
    "j": "japan", 
    "t": "thailand", 
    "v": "vietnam", 
    "q": "qatar",
    "uae": "united-arab-emirates-uae"
}

CSV_HEADERS = ["ID", "URL", "NAME", "ADDRESS", "CITY", "SCHOOL TYPE", "LEVEL CODE"]

requests.urllib3.disable_warnings()

@dataclasses.dataclass
class School:
    """Store information about a school"""
    ID: str
    URL: str
    NAME: str
    ADDRESS: str
    CITY: str
    SCHOOL_TYPE: str
    LEVEL_CODE: str

class EDAScraper:
    """Scrapes schools from https://educationdestinationasia.com/"""
    def __init__(self) -> None:
        self.logger = Logger(__class__.__name__)
        self.logger.info("*****EDAScraper started*****")

        self.schools = []

        self.__date = date.today()

        self.settings = self.__get_json_settings()

    def __get_json_settings(self) -> dict[str, list[str]]:
        """Reads json settings to determine the levels, curriculums and countries
           to be scraped
        """
        self.logger.info("Fetching settings...")
        
        try:
            with open("./settings/settings.json", "r") as file:
                settings = json.load(file)

                return {
                    "filter by": settings["filter by"],
                    "levels": [LEVEL_MAPPINGS[key] for key in settings["levels"]],
                    "curriculum": settings["curriculum"],
                    "countries": [COUNTRY_MAPPINGS[key] for key in settings["countries"]]
                }
        except:
            self.logger.error("Fatal error occured while getting settings!")

    def __fetch_page(self, params: dict[str, str]) -> BeautifulSoup:
        """Fetches the webpage with the given url"""
        while True:
            try:
                response = requests.get(
                    URL, params=params, headers=HEADERS, timeout=10, verify=False)
                
                if response.ok:
                    return BeautifulSoup(response.text, "html.parser")
                
            except:
                self.logger.warn(
                    f"Error fetching info from page {params['page']}. Retrying...")

    def __extract_schools(self, response: BeautifulSoup, page: int) -> None:
        """Extracts schools from the html response"""
        school_num = len(self.schools)

        for school in response.select("div.box"):
            link_tag = school.select_one('a[target="_blank"]')
            address = school.select_one("h6").get_text(strip=True)

            url = link_tag["href"]
            name = link_tag.get_text(strip=True)
            city = address.split(",")[0]
            
            levels, levelcodes = self.__extract_levels(school)

            school_type = ", ".join(levels)
            level_code = ", ".join(levelcodes)
            
            self.schools.append(School(ID=str(uuid.uuid4()), 
                                       URL=url, 
                                       NAME=name, 
                                       ADDRESS=address, 
                                       CITY=city, 
                                       SCHOOL_TYPE=school_type, 
                                       LEVEL_CODE=level_code))
        
        page_results = len(self.schools) - school_num

        self.logger.info(f"Page: {page} || Schools Found: {page_results}"
                         f" || Total schools: {len(self.schools)}")
    
    @staticmethod
    def __extract_levels(school: BeautifulSoup) -> tuple[list]:
        """Extracts levels for a given school"""
        levels = []
        levelcodes = []

        for level in school.select("span.is-info"):
            levels.append(level.get_text(strip=True))

            if re.search(r"primary", levels[-1], re.I):
                levelcodes.append("p")
            elif re.search(r"kinder", levels[-1], re.I):
                levelcodes.append("k")
            elif re.search(r"pre-univ", levels[-1], re.I):
                levelcodes.append("pu")
            elif re.search(r"university", levels[-1], re.I):
                levelcodes.append("u")
            elif re.search(r"secondary", levels[-1], re.I):
                levelcodes.append("s")

        return levels, levelcodes
    
    def __scrape_schools_from_country(self, country: str) -> None:
        """Scrapes schools from a given country"""
        last_page, page = None, 1

        if country.strip():
            self.logger.info("Scraping schools from {}".format(country.capitalize()))

            PARAMS["country"] = country

        else:
            self.logger.info("Scraping schools...")

        while True:
            PARAMS["page"] = page

            soup = self.__fetch_page({**PARAMS})

            self.__extract_schools(soup, page)

            if last_page is None:
                page_tags = soup.select("ul.pagination-list > li > a")

                last_page = 1

                if len(page_tags):
                    last_page = int(page_tags[-1].get_text(strip=True))

            if page % 10 == 0:
                self.__save_to_csv(self.schools)

            if page >= last_page: break

            page += 1
        
        self.__save_to_csv(self.schools)

    def __save_to_csv(self, schools: list[School]) -> None:
        """Saves the results to csv"""
        self.logger.info("Saving records to csv...")

        results = []

        [results.append(dict(zip(CSV_HEADERS, list(dataclasses.asdict(school).values())))) 
         for school in schools]
        
        df = pd.DataFrame(schools)

        df.to_csv(f"./output/eda_data_{self.__date}.csv", index=False)

        self.logger.info(f"{len(df)} records saved.")

    def scrape(self) -> None:
        """Entry point to the scraper"""
        filters = self.settings["filter by"]

        if "curriculum" in filters:
            PARAMS["curriculum"] = ",".join(self.settings["curriculum"])
        
        countries = [""]

        if "countries" in filters:
            countries = self.settings["countries"]

        if "levels" in filters:
            PARAMS["level"] = ",".join(self.settings["levels"])

        [self.__scrape_schools_from_country(country) for country in  countries]


if __name__ == "__main__":
    app = EDAScraper()
    app.scrape()