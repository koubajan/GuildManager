# Guild Manager - D2

We have recently talked about ERP systems in our Economics classes and I thought why not create a RPG ERP system.
This is a desktop application for managing an RPG Guild. It allows you to create heroes, manage their inventory, edit the game's item database (shop), and generate reports.

(For more detailed info read the documentation in /docs/Documentation)
It demonstrates the **Active Record** design pattern, **MySQL** database integration, and **Tkinter** GUI.

---

## How to Set Up on a New PC

Follow these steps to get the app running on a different computer (e.g., school PC).
Note: the folder data_samples contains the templates for importing data

### 1. Requirements
* **Python 3.x** installed.
* **MySQL Server** (I used MySQL Workbench) running.

### 2. Installation
1.  Download or clone this repository.
2.  Open a terminal/command prompt in the project folder.
3.  Install the required library:
    ```bash
    pip install mysql-connector-python
    ```

### 3. Database Setup
1.  Open your database manager.
2.  Create a new database (e.g., `guild_master_db`).
3.  Import the SQL script located in:
    * `sql/db_schema.sql` (or `import.sql`)
    * *This will create all necessary tables and views.*

### 4. Configuration (IMPORTANT)
The application **will not work** immediately because the configuration file with passwords is hidden (via `.gitignore`) for security (the original config.json IS MINE). You must create your own.

1.  Look for the file named `config.sample.json` in the main folder.
2.  **Rename it** to `config.json` (or make a copy named `config.json`).
3.  Open `config.json` in a text editor and fill in your database login details:
    ```json
    {
        "host": "localhost",
        "user": "root",       <-- Change if needed
        "password": "",       <-- Put your DB password here
        "database": "guild_master_db" <-- Or lit anything you put in while creating this
    }
    ```

### 5. Running the App
Run the main script from the terminal:
```bash
python src/main.py
