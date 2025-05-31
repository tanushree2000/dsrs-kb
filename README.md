# DSRS Knowledge Base Automation

## Overview

I am a student at the University of Illinois and I built this project to create a dynamic, automated knowledge base for Data Science Research Service, DSRS. DSRS drives data centric innovation on campus by providing infrastructure, research support, and student internships. Instead of manually collecting and updating information about DSRS offerings, I automated the process so that every week the repository fetches the latest content, structures it, and makes it available both as CSV files and a SQLite database.

Everything happens in a single Google Colab notebook and a Python script called `refresh_dsrs_kb.py`. The GitHub Actions workflow in this repository runs that script every Monday at nine AM Central Time and commits any changes back to the repository. That way, DSRS services, internships, and consulting information stay current without extra manual effort.

If you want to explore the code interactively, you can view and run it on Colab:
[Open the Colab Notebook](https://colab.research.google.com/drive/1JWt8YECXh8gbY2NJ8abPjqWXuDpMrNXT?usp=sharing)

## Motivation and Content Sourcing

DSRS publishes a lot of valuable information on its website, but it updates frequently. Instead of downloading web pages by hand or copying and pasting descriptions into a document, I wrote a pipeline that does the following:

1. Scrapes top level categories from the DSRS homepage (Research Support, Student Internships, Data Science Consulting).
2. Fetches details for each category, such as the four main internship areas under Students and all the research support services under Research Support.
3. Encodes consulting services in code, because that content is static and easier to define manually rather than scrape.
4. Collects this content into CSV files. Each CSV file represents one area of DSRS offerings:

   * `dsrs_sections.csv` (Category, Description, URL)
   * `dsrs_internships.csv` (Area name, Description, Source URL)
   * `dsrs_services.csv` (Service description, any sub service details)
   * `dsrs_consulting.csv` (Consulting service description, sub service details)

The script uses requests to fetch HTML pages and BeautifulSoup to parse them. For the Student Internships page, since it displays content via JavaScript, I defined the four internship areas manually in code. For the Research Support page, the script locates the “At a high level” `<h6>` heading and its `<ul>` list to gather service names and sub service details. Consulting services are similarly hard coded because they do not appear in static HTML.

As a result, the CSV files hold a snapshot of DSRS’s core offerings at the moment the script runs.

## Structure and Organization

I designed a simple relational schema that lives in the SQLite file `dsrs_kb.db`. It has two tables:

1. **Category**

   * CategoryID (automatically generated key)
   * Name (for example Research Support)
   * Description (the paragraph under each category on the homepage)
   * URL (link to the detailed DSRS page)
   * LastUpdated (timestamp when the category was inserted)

2. **Item**

   * ItemID (automatically generated key)
   * CategoryID (foreign key linking to Category)
   * Title (for Internships this is the Area name, for Services this is the service description, for Consulting it is the consulting headline)
   * Description (sub service details or extended description)
   * LinkText (mostly None in this version, but reserved for clickable link labels if needed in the future)
   * URL (for internships this is always the Students page URL; for services and consulting it is None)
   * LastUpdated (timestamp when the item was inserted)

### Key Features and Functionalities

* **Versioning**
  Every time the pipeline runs, the script rebuilds both tables from scratch. This means each row has a new LastUpdated timestamp. Because the entire SQLite file is committed back to GitHub after each run, the Git history serves as a version control mechanism. It is possible to check out any commit to see exactly how many categories and items existed and what their descriptions were at that point in time.

* **Data Visualization**
  In the Colab notebook, I included a quick bar chart showing how many items appear in each category: Research Support, Student Internships, and Data Science Consulting. This makes it easy to spot if a category suddenly grows, for example if DSRS adds more research services.

* **Integration Points**

  * The CSV files can be loaded into business intelligence tools such as Tableau or Power BI, or into a Jupyter notebook for further analysis.
  * The SQLite database could be imported into a downstream analytics pipeline or serve as the backend for a small web API (for example, a Flask or FastAPI endpoint) that returns JSON responses.
  * In the future, an AI model could query the `dsrs_kb.db` to answer questions such as “What consulting services does DSRS offer related to cloud infrastructure?” or “List all internship areas and their responsibilities.”

## Maintenance and Growth Strategy

Keeping this knowledge base fresh and accurate is critical. My plan for maintenance and growth includes:

1. **Automated Weekly Refresh**

   * A GitHub Actions workflow named Weekly DSRS KB Refresh runs every Monday at fourteen hundred UTC (nine AM Central Time).
   * The workflow checks out the repository, installs dependencies, runs `refresh_dsrs_kb.py`, and commits any new or changed CSV files and the database back to GitHub.
   * Because `persist-credentials: true` and `permissions: contents: write` are configured, the workflow can push updates without manual intervention.

2. **On Demand Manual Trigger**

   * Sometimes DSRS may announce a new service or internship midweek. In that case, any repository collaborator can go to the Actions tab, select Weekly DSRS KB Refresh, and click Run workflow. This forces an immediate update so that the latest content is reflected right away.

3. **Change Tracking**

   * Every commit message follows the format:
     Weekly KB refresh: YYYY-MM-DD
   * It is possible to glance at the Git history to see exactly when the content changed. If a new internship area appears, there will be an additional row in `dsrs_internships.csv` compared to the previous snapshot.

4. **Adding New Information**

   * If DSRS creates new categories, for example a News page, someone can write a new function in `refresh_dsrs_kb.py` (for example `fetch_news()`) that collects headlines, dates, and URLs into a new DataFrame and writes `dsrs_news.csv`. Then they can update the database loading logic to insert those news items into a new News table.
   * Because the code is modular, adding new fetch functions and CSV writers is straightforward.

5. **Integrating into DSRS Workflows**

   * DSRS staff could add a link on their website footer saying “View Knowledge Base Archive.” That link would point to a static GitHub Pages site generated from the CSVs or to a lightweight Flask app that reads from `dsrs_kb.db`.
   * For AI projects, the Item and Category tables can be ingested into a datastore such as Pinecone or Elasticsearch to support natural language search. Each row’s timestamp allows analysts to filter strictly for recently added services.

## How to Run Locally

1. Install the required Python packages by running:

   ```
   pip install requests beautifulsoup4 pandas
   ```

2. Run the script:

   ```
   python refresh_dsrs_kb.py
   ```

   This command will recreate `dsrs_sections.csv`, `dsrs_internships.csv`, `dsrs_services.csv`, `dsrs_consulting.csv`, and `dsrs_kb.db` in your current directory. You can open these files or explore `dsrs_kb.db` with any SQLite client.

## GitHub Actions

* The workflow is scheduled to run every Monday at 9 AM Central Time using a cron schedule in the YAML file.
* It is also possible to trigger the workflow manually by clicking the Run workflow button under the Actions tab for Weekly DSRS KB Refresh in this repository.
* When the workflow runs, it will check out the repository, install dependencies, run `refresh_dsrs_kb.py`, and then commit any changed CSV files or the database back to the repo.

## Contact

If you have any questions or need more information, feel free to open an issue in this repository.
