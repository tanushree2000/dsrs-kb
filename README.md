# DSRS Knowledge Base Automation

## Overview

I am a student at the University of Illinois working to build a knowledge base for the Data Science Research Service Each week this repository automatically updates four csv files and a sqlite database by scraping the DSRS website This project shows how to gather content organize it into tables and keep it up to date without manual effort

## Contents

This repository contains the following files:

* `refresh_dsrs_kb.py`: Python script that fetches data from the DSRS site rebuilds all csv files and recreates the sqlite database
* `dsrs_sections.csv`: Top level categories such as Research Support Student Internships and Data Science Consulting along with descriptions and links
* `dsrs_internships.csv`: Four internship area entries with detailed descriptions and source url
* `dsrs_services.csv`: Research Support services along with any sub service information
* `dsrs_consulting.csv`: Core Data Science Consulting services with sub service details
* `dsrs_kb.db`: Sqlite database containing two tables Category and Item populated from the csv files
* `.github/workflows/refresh_dsrs_kb.yml`: GitHub Actions workflow that runs every Monday morning Central Time and on demand to refresh the data and push updates back to this repository

## How to Run Locally

1. Install the required Python packages by running:

   ```
   pip install requests beautifulsoup4 pandas
   ```
2. Run the script:

   ```
   python refresh_dsrs_kb.py
   ```

   This command will recreate `dsrs_sections.csv`, `dsrs_internships.csv`, `dsrs_services.csv`, `dsrs_consulting.csv` and `dsrs_kb.db` in your current directory You can open these files or explore `dsrs_kb.db` with any sqlite client

## GitHub Actions

* The workflow is scheduled to run each Monday at 9 AM Central Time using a cron schedule in the yaml file
* You can also trigger the workflow manually by clicking the Run workflow button under the Actions tab for “Weekly DSRS KB Refresh” in this repository
* When the workflow runs it will checkout this repository install dependencies run `refresh_dsrs_kb.py` and then commit any changed csv files or database back to the repo

## Contact

If you have any questions or need more information feel free to open an issue in this repository 
