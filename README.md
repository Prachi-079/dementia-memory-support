# Dementia Cognitive Engagement & Memory Support App

**Play. Remember. Connect.**

A beginner-friendly Streamlit MVP with patient/caregiver accounts, cognitive games, personal memories, basic activity history, language settings, voice prompts, accessibility settings, and the two supplied CSV datasets.

## 1. Requirements
- Ubuntu/Linux terminal
- Python 3.10 or 3.11 recommended
- Internet connection for installing packages

## 2. Extract the ZIP
Open Terminal and move to the folder where you downloaded the ZIP. For example:

```bash
cd ~/Downloads
unzip dementia_memory_support_app.zip
cd dementia_memory_support_app
```

If you extracted it somewhere else, use that folder path instead.

## 3. Create a virtual environment

```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
```

If `venv` is missing, run:

```bash
sudo apt update
sudo apt install python3-venv python3-pip -y
```

## 4. Install requirements (important)

Upgrade pip, then install the exact pinned packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify installation:

```bash
python -m pip check
```

The requirements file is intentionally small and pinned. Do not install packages globally; keep the virtual environment activated.

## 5. Run the website

```bash
python -m streamlit run app.py
```

The terminal will show a local address, normally:

`http://localhost:8501`

Open that address in Firefox or Chrome. Keep the terminal running while you use the app. Press `Ctrl+C` in the terminal to stop it.

## 6. First-time use
1. Select **Create account**.
2. Create a Patient account and remember its username/password.
3. Log in as the patient. Find the six-character connection code under **My Settings**.
4. Log out.
5. Create a separate Caregiver account and log in.
6. In the Caregiver Dashboard, enter the patient's connection code and request connection.
7. The caregiver can then view the patient's permitted memories and activity history. The patient can revoke access from **My Settings**.

For a quick test, create both accounts in the same browser/app database.

## 7. Deploy online using Streamlit Community Cloud

### A. Create a GitHub repository
1. Sign in to GitHub and create a new repository, for example `dementia-memory-support`.
2. Upload the contents of this extracted project folder. Make sure `app.py`, `requirements.txt`, and the `data` folder are at the repository root.
3. Do not upload your local `venv/`, `app.db`, or private patient photographs.

You can also push from Terminal (after creating an empty GitHub repository):

```bash
git init
git add app.py requirements.txt README.md .gitignore runtime.txt data/
git commit -m "Initial dementia memory support app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/dementia-memory-support.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username and use your actual repository URL.

### B. Publish on Streamlit Community Cloud
1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Choose **Create app**.
3. Select your repository and branch `main`.
4. Set the main file path to `app.py`.
5. Click **Deploy**. Wait for dependencies to install and the app to start.
6. Streamlit will provide a public app URL that you can open on another device.

## 8. Important deployment and privacy notes
- This is an educational MVP/prototype, not a clinically validated healthcare product.
- The included CSV files are only available for dataset exploration. No diagnosis or medical prediction is made.
- The app uses local SQLite and a local uploads folder. Streamlit Community Cloud's local filesystem is not a reliable permanent database/storage service: data, uploaded photos and accounts may be lost when the app restarts, is redeployed, or its instance is replaced. Treat the hosted version as a demo with test data only.
- Do not upload real patient information, identifiable family photographs, or passwords to a public demo. For real use, move authentication, database and photo storage to managed services with proper access controls, encryption, backups and consent.
- Browser voice support depends on the device/browser and available system voices. The reminder feature currently displays saved reminder times; it does not send background push notifications.
- Caregiver pairing code is a simple prototype connection flow. Before real-world deployment, add verified invitations, stronger session management, audit logs, secure managed storage, and a formal privacy/security review.

## 9. Common installation fixes

**`python3: command not found`**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

**`No module named streamlit`**
```bash
source venv/bin/activate
python -m pip install -r requirements.txt
```

**`pip install` fails or installs into the wrong Python**
```bash
source venv/bin/activate
which python
python --version
python -m pip --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Port 8501 is already in use**
```bash
python -m streamlit run app.py --server.port 8502
```

## Project structure

```text
dementia_memory_support_app/
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
├── .gitignore
├── data/
│   ├── OPTIMAL_combined_3studies_6feb2020.csv
│   └── dementia_patients_health_data.csv
└── uploads/
```
