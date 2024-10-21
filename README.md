# Rule Engine Project

## Project Overview

The **Rule Engine Project** is a full-stack application designed to allow users to create, manage, and evaluate complex business rules based on various attributes. The backend is built with **Flask** and **SQLAlchemy**, interfacing with a **PostgreSQL** database, while the frontend is developed using **React**. The application ensures robust rule management with features like AST (Abstract Syntax Tree) generation, rule combination, and comprehensive testing using **Pytest**.

---

## Features

- **Rule Creation:** Users can create rules using a user-friendly interface, specifying rule names and defining conditions based on predefined attributes.
- **AST Generation:** Each rule is parsed and converted into an AST for efficient evaluation and management.
- **Rule Combination:** Combine multiple rules to form complex logical structures.
- **Rule Evaluation:** Test rules against sample data to verify their correctness.
- **Comprehensive Testing:** Ensure application reliability with a robust test suite using Pytest.
---

## Technologies Used

### Backend

- **Python 3.12**
- **Flask**
- **SQLAlchemy**
- **PostgreSQL**
- **Pytest**

### Frontend

- **React**
- **Axios**
- **CSS**

### Other Tools

- **Git**
- **Virtualenv**
- **Node.js & npm**

---

## Architecture

The application follows a **client-server** architecture:

- **Backend (Server):**
  - **Flask** serves as the RESTful API, handling rule creation, combination, and evaluation.
  - **SQLAlchemy** manages ORM with a **PostgreSQL** database.
  - **Pytest** ensures the reliability of backend functionalities through automated tests.

- **Frontend (Client):**
  - **React** provides a dynamic user interface for interacting with the rule engine.
  - **Axios** facilitates communication between the frontend and backend APIs.

---

## Getting Started

Follow these instructions to set up the project locally for development and testing purposes.

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.12**
- **Node.js (v14 or later) & npm**
- **PostgreSQL**

### Backend Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/nidhii-24/Rule-Engine-Project.git
   cd rule-engine-project/backend
   ```

2. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Backend Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the `backend` directory with the following variables:

   ```env
   DATABASE_URL=postgresql://username:password@localhost/rule_engine_db
   ```

   Replace `username`, `password`, and `rule_engine_db` with your PostgreSQL credentials and desired database name.

5. **Initialize the Database:**

   - **Create the PostgreSQL Database:**

     ```bash
     psql -U postgres
     ```

     ```sql
     CREATE DATABASE rule_engine_db;
     \q
     ```

6. **Start the Backend Server:**

   ```bash
   python run.py
   ```

   The server should be running at `http://localhost:5000`.

### Frontend Setup

1. **Navigate to the Frontend Directory:**

   ```bash
   cd ../frontend
   ```

2. **Install Frontend Dependencies:**

   ```bash
   npm install
   ```

3. **Configure Environment Variables:**

   Create a `.env` file in the `frontend` directory with the following variables:

   ```env
   REACT_APP_API_URL=http://localhost:5000
   ```

4. **Start the Frontend Development Server:**

   ```bash
   npm start
   ```

   The frontend should be accessible at `http://localhost:3000`.

---

## Running the Application

1. **Ensure Backend and Frontend Servers Are Running:**

   - Backend: `http://localhost:5000`
   - Frontend: `http://localhost:3000`

2. **Access the Application:**

   Open your browser and navigate to `http://localhost:3000` to interact with the Rule Engine.

---

## Testing

### Backend Testing with Pytest

1. **Activate the Virtual Environment:**

   ```bash
   source venv/bin/activate
   ```

2. **Navigate to the Backend Directory:**

   ```bash
   cd backend
   ```

3. **Run Tests:**

   ```bash
   pytest
   ```

