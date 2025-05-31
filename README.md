# DSRS Knowledge Base Automation

## Overview
I’m a student at the University of Illinois, and I built this project to create a dynamic, automated knowledge base for Data Science Research Service (DSRS). DSRS drives data‐centric innovation on campus by providing infrastructure, research support, and student internships. Instead of manually collecting and updating information about DSRS’s offerings, I automated the process so that every week, the repository fetches the latest content, structures it, and makes it available both as CSV files and a SQLite database.

Everything happens in a single Google Colab notebook and a Python script called `refresh_dsrs_kb.py`. The GitHub Actions workflow in this repo runs that script every Monday at 9 AM Central Time and commits any changes back to the repository. That way, DSRS’s services, internships, and consulting information stay current without extra manual effort.

If you want to explore the code interactively, you can view and run it on Colab:
[Open the Colab Notebook](https://colab.research.google.com/drive/1JWt8YECXh8gbY2NJ8abPjqWXuDpMrNXT?usp=sharing)

## Motivation and Content Sourcing
DSRS publishes a lot of valuable information on its website, but it updates frequently. Instead of downloading web pages by hand or copying and pasting descriptions into a document, I wrote a pipeline that:

1. Scrapes top‐level categories from the DSRS homepage (Research Support, Student Internships, Data Science Consulting).
2. Fetches details for each category—like the four main internship areas under Students and all the research support services under Research Support.
3. Encodes consulting services in code (because that content is static and easier to define manually rather than scrape).
4. Collects this content into CSV files. Each CSV file represents one area of DSRS offerings:
   - `dsrs_sections.csv` (Category, Description, URL)
   - `dsrs_internships.csv` (Area name, Description, Source URL)
   - `dsrs_services.csv` (Service description, any sub-service details)
   - `dsrs_consulting.csv` (Consulting service description, sub-service details)

The script uses **requests** to fetch HTML pages and **BeautifulSoup** to parse them. For the Student Internships page—since it displays content via JavaScript—I defined the four internship areas manually in code. For the Research Support page, the script locates the “At a high level” `<h6>` heading and its `<ul>` list to gather service names and sub-service details. Consulting services are similarly hard-coded because they do not appear in static HTML.

By doing this, the CSV files hold a snapshot of DSRS’s core offerings at the moment the script runs.

## Structure and Organization
I designed a simple relational schema that lives in the SQLite file `dsrs_kb.db`. It has two tables:

1. **Category**  
   - `CategoryID` (automatically generated key)  
   - `Name` (e.g., “Research Support”)  
   - `Description` (the paragraph under each category on the homepage)  
   - `URL` (link to the detailed DSRS page)  
   - `LastUpdated` (timestamp when the category was inserted)

2. **Item**  
   - `ItemID` (automatically generated key)  
   - `CategoryID` (foreign key linking to Category)  
   - `Title` (for Internships this is the “Area” name, for Services this is the service description, for Consulting it is the consulting headline)  
   - `Description` (sub-service details or extended description)  
   - `LinkText` (mostly None in this version, but reserved for clickable link labels if needed in the future)  
   - `URL` (for internships this is always the Students page URL; for services and consulting it is None)  
   - `LastUpdated` (timestamp when the item was inserted)

### Key Features and Functionalities
- **Versioning**  
  Every time the pipeline runs, the script rebuilds both tables from scratch. That means each row has a new `LastUpdated` timestamp. Because the entire SQLite file is committed back to GitHub after each run, the Git history serves as a version control mechanism. You can check out any commit to see exactly how many categories and items existed, and what their descriptions were, at that point in time.

- **Data Visualization**  
  In the Colab notebook, I included a quick bar chart showing how many items appear in each category (Research Support, Student Internships, Data Science Consulting). This makes it easy to spot if a category suddenly grows (for example, if DSRS adds more research services).

- **Integration Points**  
  - The CSV files can be loaded into BI tools such as Tableau, Power BI, or into a Jupyter notebook for further analysis.  
  - The SQLite database could be imported into a downstream analytics pipeline or serve as the backend for a small web API (for example, a Flask or FastAPI endpoint) that returns JSON responses.  
  - In the future, an AI model could query the `dsrs_kb.db` to answer questions like “What consulting services does DSRS offer related to cloud infrastructure?” or “List all internship areas and their responsibilities.”

## Maintenance and Growth Strategy
Keeping this knowledge base fresh and accurate is critical. My plan for maintenance and growth includes:

1. **Automated Weekly Refresh**  
   - A GitHub Actions workflow named **Weekly DSRS KB Refresh** runs every Monday at 14:00 UTC (9 AM CT).  
   - The workflow checks out the repository, installs dependencies, runs `refresh_dsrs_kb.py`, and commits any new or changed CSVs and database back to GitHub.  
   - Because `persist-credentials: true` and `permissions: contents: write` are configured, the workflow can push updates without manual intervention.

2. **On-Demand Manual Trigger**  
   - Sometimes DSRS may announce a new service or internship midweek. In that case, any repository collaborator can go to the **Actions** tab, select “Weekly DSRS KB Refresh,” and click **Run workflow**. This forces an immediate update so that the latest content is reflected right away.

3. **Change Tracking**  
   - Every commit message follows the format:  
     ```
     Weekly KB refresh: YYYY-MM-DD
     ```  
   - You can glance at the Git history to see exactly when content changed. If a new internship area appears, you’ll see an additional row in `dsrs_internships.csv` compared to the previous snapshot.

4. **Adding New Information**  
   - If DSRS creates new categories—say, a “News” page—someone can write a new function in `refresh_dsrs_kb.py` (for example, `fetch_news()`) that collects headlines, dates, and URLs into a new DataFrame and writes `dsrs_news.csv`. Then update the database‐loading logic to insert those news items into a new `News` table.  
   - Because the code is modular, adding new “fetch_” functions and CSV writers is straightforward.

5. **Integrating into DSRS Workflows**  
   - DSRS staff could add a link on their website footer saying “View Knowledge Base Archive.” That link would point to a static GitHub Pages site generated from the CSVs (or a lightweight Flask app that reads from `dsrs_kb.db`).  
   - For AI projects, the `Item` and `Category` tables can be ingested into a datastore (like Pinecone or Elasticsearch) to support natural language search. Each row’s timestamp allows analysts to filter strictly for recently added services.

## How to Run Locally
If you want to run everything on your local machine or in another environment instead of GitHub Actions:

1. **Clone this repository**  
   ```bash
   git clone https://github.com/your‐username/dsrs-kb.git
   cd dsrs-kb
