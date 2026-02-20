# Face Authentication System - Developer Guide

This guide explains how to install and run the Face Authentication System, specifically addressing the common challenges with `dlib` and `face-recognition` on Windows.

## 🚀 Quick Start (Installation)

Follow these steps exactly to avoid common C++ compiler and library version errors.

### 1. Prerequisite: Python version
Ensure you are using **Python 3.12**. You can check this by running:
```powershell
python --version
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to avoid library conflicts.
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Special Step: Install `dlib` on Windows
`dlib` usually requires heavy C++ build tools. To bypass this, install from the provided `.whl` (Wheel) file included in this project:
```powershell
pip install .\dlib-19.24.99-cp312-cp312-win_amd64.whl
```

### 4. Install Project Requirements
Install the remaining libraries using the `requirements.txt` file:
```powershell
pip install -r requirements.txt
```

---

## 🛠 Troubleshooting Common Issues

### Issue: "RuntimeError: Unsupported image type"
**Cause:** Newer versions of `numpy` (2.0+) are incompatible with current `dlib` binaries.
**Fix:** Ensure you are using `numpy<2.0`. Our `requirements.txt` handles this automatically by locking to `1.26.4`.

### Issue: "ModuleNotFoundError: No module named 'pkg_resources'"
**Cause:** `face-recognition` requires `setuptools`, but newer versions of `setuptools` (70.0+) removed `pkg_resources`.
**Fix:** We have locked `setuptools` to version `69.5.1` in the `requirements.txt`.

---

## 🏃 How to Run the Files

### 1. `face_auth_system.py` (Local Testing)
This file is designed for local desktop testing. It will:
*   Register a user locally (save their face data into `saved_models/user_faces/`).
*   Open your webcam for real-time verification.
*   **Run command:**
    ```powershell
    python face_auth_system.py
    ```

### 2. `FaceAIService` (For Django/Web Developers)
This is a clean, production-ready class designed to be imported into a Django project.
*   **get_face_encoding**: Use this in your "Registration" view when a user uploads a photo. Save the resulting list to your database.
*   **verify_face**: Use this in your "Login" view. Pass it a frame from the browser webcam and the encoding stored in your database.

---

## 📂 Project Structure
*   `face_auth_system.py`: The core AI service and testing script.
*   `FaceAIService`: The integration-ready version for web apps.
*   `requirements.txt`: Locked versions of all libraries.
*   `saved_models/user_faces/`: Folder where local face profiles are stored as `.joblib` files.
*   `dlib-19.24.99-cp312-cp312-win_amd64.whl`: Pre-built dlib binary for Windows.