# California Community College Shopper

Data on community colleges.

## Project Plan

1. Gather all relevant metadata on California Community Colleges using `colleges` endpoint of the [the CCC API](https://api.cccco.edu/).
2. Determine the top $n$ most popular programs of study using [the CCC DataMart](https://datamart.cccco.edu/).
3. Gather all colleges in the CCC system that offer a degree or certificate in those programs using `programs` endpoint [the CCC API](https://api.cccco.edu/).
4. Merge the `colleges` endpoint data with the `programs` endpoint data (one row per college per program).
5. Merge the college data with the DataMart program data (one row per college per program).
6. Merge the data with external sources:
   - labor market projection data on:
      - `college_data["County"]` fuzzy join on `labor_market_data["Metropolitan Statistical Areas"]` 
      - `college_data["TopCode"]` match on `labor_market_data["SOC Code"]` at `labor_market_data["SOC Level"] == 4` (this will be a one-to-many join)
    - College Scorecard data (e.g., enrollment count, student and faculty demographics, retention rate, etc.) on:
      - `college_data["CollegeName"]` join on `college_scorecard["CollegeName"]`
    - Rate My Professors NLP data (sentiment analysis) on:
      - `college_data["CollegeName"]` join on `rate_my_professor["CollegeName"]`
      - `college_data["ProgramTitle"]` fuzzy join on `rate_my_professor["Department"]` (if possible)

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