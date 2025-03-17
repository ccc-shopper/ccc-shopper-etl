# California Community College Shopper

Data on community colleges.

## Directory

### Major Contributing Files

- `report.pdf` is the final report.
- `college_level_data.ipynb` contains exploratory data analysis using the [the CCCCO API](https://api.cccco.edu/) and the College Scorecard API.
- `cccco_data_mart.ipynb` contains ETL scripts and exploratory data analysis on data from the [the CCC DataMart](https://datamart.cccco.edu/).
- `labor_market.ipynb` contains contains exploratory data analysis on the data from [California Employment Development Department](https://data.ca.gov/).
- `sentiment_analysis.ipynb` contains ETL scripts and a sentiment analysis on the colleges using [ratemyprofessors.com](https://www.ratemyprofessors.com/).

### Secondary Files and Resources

- `scripts/` contains modules that handle the ETL processes from the CCCCO API, the College Scorecard API, and the California Employment Development Department API.
- `data/` contains the CSV output of some of the ETL processes discussed above.
- `docs/` contains the HTML for the interactive plots generated in the code discussed above.
- `figures/` contains the static plots generated in the code discussed above.
- `resources/` contains CSVs downloaded from the web to assist in translating between data sources.
- `jupyter/` contains a set of Jupyter notebooks that were used in the early stages of this project to test the ETL processes. Not relevant to the final project.
- `pdfs/` contains the PDF versions of the four `.ipynb` files used to conduct the analysis. 

## Project Plan

1. Gather all relevant metadata on California Community Colleges using `colleges` endpoint of the [the CCCCO API](https://api.cccco.edu/).
2. Gather all relevant federally collected data (e.g., enrollment count, student and faculty demographics, etc) on California Community Colleges using the [College Scorecard API](https://collegescorecard.ed.gov/data/api-documentation/)
3. Determine popular programs of study and student demographics using [the CCCCO DataMart](https://datamart.cccco.edu/).
6. Cross reference these data with external sources:
   - labor market projection data.
   - Rate My Professors NLP data (sentiment analysis).

## Data Sources

- [api.cccco.edu](https://api.cccco.edu/): basic metadata on community colleges/districts/programs.
- [datamart.cccco.edu](https://datamart.cccco.edu/): aggregates of regulatory reports to the California Community College Chancellor's Office.
- [collegescorecard.ed.gov](https://collegescorecard.ed.gov/): institution-level data and field of study data for all colleges receiving Title IV aid.
- [ratemyprofessors.com](https://www.ratemyprofessors.com/): professor and school ratings (for sentiment analysis).
- [data.ca.gov](https://data.ca.gov/): labor market projections.

## Possible Directions for Future Work

**Add transfer pipeline statistics from the UC system**:

- https://www.universityofcalifornia.edu/about-us/information-center/transfers-major
  - Tableau workbook is hosted [here](https://visualizedata.ucop.edu/t/Public/views/Transfersbymajor/Bycommunitycollege?%3Aembed=y&amp;%3AapiID=embhost0&amp;%3AapiInternalVersion=1.132.0&amp;%3AapiExternalVersion=3.7.0&amp;navType=0&amp;navSrc=Opt&amp;%3AdisableUrlActionsPopups=n&amp;%3Atabs=y&amp;%3Atoolbar=bottom&amp;%3Adevice=default&amp;mobile=n&amp;%3AhideEditButton=n&amp;%3AhideEditInDesktopButton=n&amp;%3AsuppressDefaultEditBehavior=n&amp;%3Ajsdebug=n)
