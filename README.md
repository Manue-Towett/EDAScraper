# EDAScraper
Scrapes schools from https://educationdestinationasia.com/schools

#### Configuration
The following are the configurations that you can do with the settings.json file:
- filter by:
    - use this setting to specify which filters should be applied.

    - values are any of:
            ["levels", "countries", "curriculum"]

    - NB: if you do not specify a filter, for example "level", then the "level" setting will be ignored and will not be used.

- "levels": 
    - use this setting to specify the levels filters to be applied.

    - values are:
            ["k", "p", "s", "pu", "lc", "se"]

    - These level codes are mapped to:
        ```
            "k" = preschool-kindergarten
            "p" = primary
            "s" = secondary
            "pu" = pre-university
            "lc" = learning-centre
            "se" = special-education-needs
        ```
- "countries": 
    - use this setting to specify the country/countries to be scraped.

    - values are:
            ["uae", "c", "i", "m", "s", "uk", "b", "sk", "my", "j", "t", "v", "q"]

    - These country codes are mapped to:
        ```
            "c" =china
            "i" = indonesia
            "m" = malaysia
            "s" = singapore
            "uk" = united-kingdom
            "b" = brunei
            "sk" = south-korea 
            "my" = myanmar
            "j" = japan
            "t" = thailand
            "v" = vietnam
            "q" = qatar
            "uae" = united-arab-emirates-uae
        ```
    
"curriculum": 
    - use this to set the curriculums to be scraped

    - values are:
            ["australian", 
            "cambridge", 
            "american", 
            "canadian", 
            "igcse", 
            "indian", 
            "international-baccalaureate",
            "islamic",
            "malaysian",
            "singaporean",
            "british",
            "international-primary",
            "a-levels",
            "german",
            "french",
            "international-middle-years-curriculum",
            "japanese-1",
            "international-preschool-curriculum",
            "chinese"]
    

#### Usage
- Requires python 3.10+
- Open the terminal
- change terminal's directory into the project directory
- If running for the first time, install dependencies using the command:
    
    ```pip install -r requirements.txt```

- Run the script using the command:
    - For linux/mac:
        
        ```python3 main.py```

    - For windows:
        
        ```python main.py```