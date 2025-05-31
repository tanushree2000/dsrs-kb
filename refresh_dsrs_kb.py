import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from urllib.parse import urljoin
from datetime import datetime
import re

def fetch_sections():
    url = "https://dsrs.illinois.edu/"
    resp = requests.get(url); resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    base = "https://dsrs.illinois.edu"
    rows = []
    for h3 in soup.find_all("h3"):
        title = h3.get_text(strip=True)
        p = h3.find_next_sibling("p")
        desc = p.get_text(strip=True) if p else ""
        a = p.find("a") if p else None
        link = urljoin(base, a["href"]) if a else ""
        rows.append({"Category": title, "Description": desc, "URL": link})
    return pd.DataFrame(rows)

def fetch_internships():
    data = [
      {
        "Area": "Data Science and Machine Learning Infrastructure",
        "Description": (
          "For these interns, tasks can be anything from building out "
          "cloud infrastructure, working with Microsoft Azure, setting up ML environments, "
          "data processing, writing python code, feature engineering, and analyzing data "
          "through various data science methods. It also includes working with DSRS infrastructure, "
          "including S3, Docker, Kubernetes, etc."
        ),
        "SourceURL": "https://dsrs.illinois.edu/students"
      },
      {
        "Area": "Text and Data Mining",
        "Description": (
          "For these interns, tasks can be anything from collecting text data from various sources, "
          "cleaning/transforming data, and analyzing data through various text mining methods. "
          "Also might include NLP tasks, web scraping, API development and parallel computing, among others."
        ),
        "SourceURL": "https://dsrs.illinois.edu/students"
      },
      {
        "Area": "Data Science Web Visualization and Data Analytic",
        "Description": (
          "For these interns, there are projects that need to have some interactive visualization "
          "and to explore data using dashboards. Projects look to build interactive visualizations, "
          "web apps, websites using current technologies."
        ),
        "SourceURL": "https://dsrs.illinois.edu/students"
      },
      {
        "Area": "Data Science Business and Communications",
        "Description": (
          "For these interns, tasks can be anything from writing stories about our projects to assisting "
          "with data science projects through human coding of data and visualizing data results. "
          "These interns handle marketing of the DSRS, updating our website, blog posting and some management as well."
        ),
        "SourceURL": "https://dsrs.illinois.edu/students"
      }
    ]
    return pd.DataFrame(data)

def fetch_research_services():
    url = "https://inside.giesbusiness.illinois.edu/academic-units/di/dsrs"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    help_tag = soup.find("h6", string=re.compile(r"At a high level", re.IGNORECASE))
    if not help_tag:
        return pd.DataFrame(columns=["Service", "SubServices"])
    ul = help_tag.find_next("ul")
    if not ul:
        return pd.DataFrame(columns=["Service", "SubServices"])
    rows = []
    for li in ul.find_all("li", recursive=False):
        direct_texts = [t.strip() for t in li.find_all(string=True, recursive=False) if t.strip()]
        main = direct_texts[0] if direct_texts else ""
        nested_ul = li.find("ul")
        subs = [c.get_text(strip=True) for c in nested_ul.find_all("li")] if nested_ul else []
        rows.append({"Service": main, "SubServices": "; ".join(subs)})
    return pd.DataFrame(rows)

def fetch_consulting_services():
    data = [
      {
        "Service": "Assessment and recommendations of what statistical and data science methods are appropriate",
        "SubServices": "Inferential Statistics; Social Media Analytics; Text Mining; Natural Language Processing; Machine Learning; Deep Learning"
      },
      {
        "Service": "Execution of statistical and data science methods for your research study",
        "SubServices": "This may include sub-contracting the analyses to other units on campus to connect you with specialized expertise"
      },
      {
        "Service": "Assessment and recommendations for computational infrastructure needed to execute specified data science methods for your research",
        "SubServices": "On-Campus Computation; Cloud Computing; Custom-Built On-Premise Computation"
      },
      {
        "Service": "Assistance in acquiring computational resources for executing data science methods to your research",
        "SubServices": "This may include connecting with external campus units such as NCSA for cost-effective resources"
      },
      {
        "Service": "Assessment and recommendations for data needed to answer your research question(s)",
        "SubServices": "Social Media Data; Web Data; Financial Data"
      },
      {
        "Service": "Assistance in locating and acquiring data needed to answer your research question(s)",
        "SubServices": "(Funds to acquire data are the responsibility of you or your department)"
      }
    ]
    return pd.DataFrame(data)

def write_csv(df, filename):
    df.to_csv(filename, index=False)

def rebuild_db(db_path="dsrs_kb.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Item;")
    cur.execute("DROP TABLE IF EXISTS Category;")
    cur.execute("""
      CREATE TABLE Category(
        CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT, Description TEXT, URL TEXT, LastUpdated TIMESTAMP
      );
    """)
    cur.execute("""
      CREATE TABLE Item(
        ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        CategoryID INTEGER REFERENCES Category(CategoryID),
        Title TEXT, Description TEXT, LinkText TEXT, URL TEXT, LastUpdated TIMESTAMP
      );
    """)
    conn.commit()
    return conn

def load_categories(conn, csv_path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={"Category": "Name"})
    df["LastUpdated"] = datetime.utcnow()
    df.to_sql("Category", conn, if_exists="append", index=False)

def load_items(conn, csv_path, category_name, col_map):
    df = pd.read_csv(csv_path)
    df = df.rename(columns=col_map)
    df["LinkText"]   = None
    df["URL"]        = df["URL"] if "URL" in df.columns else None
    df["CategoryID"] = conn.execute(
        "SELECT CategoryID FROM Category WHERE Name = ?", (category_name,)
    ).fetchone()[0]
    df["LastUpdated"] = datetime.utcnow()
    df = df[["CategoryID", "Title", "Description", "LinkText", "URL", "LastUpdated"]]
    df.to_sql("Item", conn, if_exists="append", index=False)

def report_counts(db_path="dsrs_kb.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
      SELECT c.Name AS Category, COUNT(i.ItemID) AS Count
      FROM Item i
      JOIN Category c USING(CategoryID)
      GROUP BY c.Name
      ORDER BY Count DESC;
    """, conn)
    conn.close()
    print(df)

def main():
    df_sec  = fetch_sections()
    df_int  = fetch_internships()
    df_rs   = fetch_research_services()
    df_cons = fetch_consulting_services()

    write_csv(df_sec,  "dsrs_sections.csv")
    write_csv(df_int,  "dsrs_internships.csv")
    write_csv(df_rs,   "dsrs_services.csv")
    write_csv(df_cons, "dsrs_consulting.csv")

    conn = rebuild_db()
    load_categories(conn, "dsrs_sections.csv")
    load_items(conn, "dsrs_internships.csv", "Student Internships",
               {"Area":"Title","Description":"Description","SourceURL":"URL"})
    load_items(conn, "dsrs_services.csv", "Research Support",
               {"Service":"Title","SubServices":"Description"})
    load_items(conn, "dsrs_consulting.csv", "Data Science Consulting",
               {"Service":"Title","SubServices":"Description"})
    conn.commit()
    conn.close()

    report_counts()

if __name__ == "__main__":
    main()
