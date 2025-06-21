## Setup
1. **Export your Moodle cookies:**
   - Log in to Moodle using your browser.
   - Use a browser extension like "EditThisCookie" to export your cookies as JSON.
   - Save the exported file as `moodle_cookies.json` in the same folder as this script.
2. **Configure the script:**
   - The URL to monitor is set in the `page_url` variable in `app.py`.
## Setup
1. **Export your Moodle cookies:**
   - Log in to Moodle using your browser.
   - Use a browser extension like "EditThisCookie" to export your cookies as JSON.
   - Save the exported file as `moodle_cookies.json` in the same folder as this script.
2. **Configure the script:**
   - The URL to monitor is set in the `page_url` variable in `app.py`.

## Usage
Run the script with:
```bash
python app.py
```
The script will check the page every minute and notify you if any changes are detected.

## Notes
- If you are redirected to the login page, your cookies may have expired. Re-export and replace `moodle_cookies.json`.
- Do not commit your `moodle_cookies.json` file to public repositories.