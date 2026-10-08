# GLAM SALON — VS Code Version

## 1. Install Python
Install Python 3.10+ and make sure **Add Python to PATH** is checked.

## 2. Open in VS Code
1. Extract this ZIP.
2. Open the folder `GLAM_SALON_VS_CODE` in VS Code.
3. Open **Terminal > New Terminal**.

## 3. Install Flask
Run:
```bash
pip install -r requirements.txt
```

If `pip` does not work, try:
```bash
python -m pip install -r requirements.txt
```

## 4. Run the system
Run:
```bash
python app.py
```

You should see a local address such as:
`http://127.0.0.1:5000`

Ctrl+Click the address in the VS Code terminal, or open it in Chrome.

## Login
Email: `admin@gmail.com`
Password: `admin123`

## Pictures
All service and promo pictures are already included in:
`static/images/`

5 services:
- Hair Cut
- Hair Color
- Rebond
- Manicure
- Spa

3 promos:
- Rebond Promo
- Manicure Promo
- Spa Promo

The pictures are local SVG files, so they do not need an internet connection.

## Important
Do not delete the `static` or `templates` folders. Flask needs them.

The database file `salon.db` is created automatically when the app starts.


## ONLINE DEPLOYMENT (Chrome link for friends)

This project is prepared for Render:
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Runtime: Python

After you upload this project to GitHub:
1. Open Render and sign in.
2. Create **New > Web Service**.
3. Connect the GitHub repository.
4. Choose the repository containing this project.
5. Render will use the settings above.
6. Click **Create Web Service**.
7. Wait for the deployment to finish.
8. Render will give you an `onrender.com` URL. Send that URL to your classmates.

Note: the Free plan is intended for testing/hobby use. Free web services can sleep after inactivity, so the first visit after a period of inactivity may take a little longer.
