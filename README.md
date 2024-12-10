# Stock_Trading_Application_Project
CS 411 Final Project: Ting-Hung Jen
# Stock Portfolio Management API

## Overview

This API provides a comprehensive solution for managing a stock portfolio. It allows users to perform operations such as user authentication, portfolio management, stock transactions (buy/sell), retrieving stock data, and updating portfolio details. The application integrates with the Alpha Vantage API to fetch real-time stock data and utilizes a database for managing user data and portfolios.

---
### Running the Application
  - *1.Run the vertual machine given with steps:*
    - source setup_venv.sh
  - *2.Run the docker-compose.yml file given with steps:*
    - docker-compose build <- This should build the container.
    - docker-compose up -d <- This should run the container.
    - After that, you are able to access the application via: http://localhost:5000* docker-compose up -d.
    - To close and delete the container:* docker-compose down
  - *Execute the smoketest before turns on the docker and virtual machine*
    ```Run the command to see result of smoketest:
    - ./smoketest.sh
  - *Execute the unit test before turns on the docker and virtual machine*
    ```Run the command to see result of unit tests:
    PYTHONPATH=$(pwd) pytest tests/selected_test_to_execute
**Now you can run the pytests.**
- **.env variable description**
  - * API KEY: The api key for AlphaVantage that will be used for retrieving information from API


## API Routes

### 1. Health Check
  - **Path:** `/api/health`
  - **Request Type:** `GET`
  - **Purpose:** Verify that the application is running.
  - **Request Format:** None
  - **Response Format:**  
    ```json
    {
      "status": "healthy"
    }
  - **Example:**
    ```bash
    curl -X GET http://localhost:5000/api/health

---

### 2. Initialize Database
  - **Path:** `/api/init-db`
  - **Request Type:** `POST`
  - **Purpose:** Recreate all database tables, deleting existing data.
  - **Request Format:** None
  - **Response Format:**  
    ```json
    {
      "status": "success",
      "message": "Database initialized successfully."
    }
  - **Example:**
    ```bash
    { curl -X POST http://localhost:5000/api/init-db }

### 3. User Management
  - **Create User**
  - **Path:** `/api/create-user`
  - **Request Type:** `POST`
  - **Purpose:** Create a new user account.
  - **Request Format:**
    ```json
    {
      "username": "example_user",
      "password": "example_password"
    }
  - **Response Format:**
    ```json
    {
      "status": "user added",
      "username": "example_user"
    }
  - **Example:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username": "example_user", "password": "example_password"}' http://localhost:5000/api/create-user

- **Delete User**
  - **Path:** `/api/delete-user`
  - **Request Type:** `DELETE`
  - **Purpose:** `Remove an existing user account.`
  - **Request Format:**
    ```json
    {
      "username": "example_user"
    }
  - **Response Format:**
    ```json
    {
      "status": "user deleted",
      "username": "example_user"
    }
  - **Example:**
    ```bash
    curl -X DELETE -H "Content-Type: application/json" -d '{"username": "example_user"}' http://localhost:5000/api/delete-user

- **Login**
  - **Path:** `/api/login`
  - **Request Type:** `POST`
  - **Purpose:** `Log in a user and load their portfolio.`
  - **Request Format:**
    ```json
    {
      "username": "example_user",
      "password": "example_password"
    }
  - **Response Format:**
    ```json
    {
      "message": "User example_user logged in successfully."
    }
  - **Example:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username": "example_user", "password": "example_password"}' http://localhost:5000/api/login

- **Logout**
  - **Path:** `/api/logout`
  - **Request Type:** `POST`
  - **Purpose:** `Log out a user and save their portfolio.`
  - **Request Format:**
    ```json
    {
      "username": "example_user"
    }
  - **Response Format:**
    ```json
    {
      "message": "User example_user logged out successfully."
    }
  - **Example:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username": "example_user"}' http://localhost:5000/api/logout

- **4. Stock Operations**
- **Get Stock by Symbol**
  - **Path:** `/api/get-stock-by-symbol`
  - **Request Type:** `GET`
  - **Purpose:** `Retrieve details of a stock using its symbol.`
  - **Request Format:** `Query parameter: ?symbol=<stock-symbol>`
  - **Response Format:**
    ```json
    {
      "status": "success",
      "stock": {
        "current_price": 230.0,
        "description": "International Business Machines Corporation (IBM) is an American multinational technology company headquartered in Armonk, New York, with operations in over 170 countries. The company began in 1911, founded in Endicott, New York, as the Computing-Tabulating-Recording Company (CTR) and was renamed International Business Machines in 1924. IBM is incorporated in New York. IBM produces and sells computer hardware, middleware and software, and provides hosting and consulting services in areas ranging from mainframe computers to nanotechnology. IBM is also a major research organization, holding the record for most annual U.S. patents generated by a business (as of 2020) for 28 consecutive years. Inventions by IBM include the automated teller machine (ATM), the floppy disk, the hard disk drive, the magnetic stripe card, the relational database, the SQL programming language, the UPC barcode, and dynamic random-access memory (DRAM). The IBM mainframe, exemplified by the System/360, was the dominant computing platform during the 1960s and 1970s.",
        "industry": "COMPUTER & OFFICE EQUIPMENT",
        "market_cap": "212668350000",
        "name": "International Business Machines",
        "sector": "TECHNOLOGY",
        "symbol": "IBM"
      }
    }
  - **Example:**
    ```bash
    curl -X GET "http://localhost:5000/api/get-stock-by-symbol?symbol=IBM"

- **5. Portfolio Management**
- **Display Portfolio**
  - **Path:** `/api/display-portfolio`
  - **Request Type:** `GET`
  - **Purpose:** `Retrieve details of the user's portfolio.`
  - **Request Format:** `None`
  - **Response Format:**
    ```json
    {
      "status": "success",
      "portfolio": [
        {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "quantity": 10,
          "current_price": 150.25,
          "total_value": 1502.5
        }
      ],
    "total_value": 2000.0
    }
  - **Example:**
    ```bash
    curl -X GET http://localhost:5000/api/display-portfolio

- **Additional Routes**
The application includes additional endpoints for operations such as:

- **Add/Remove Funds**
  - Buy/Sell Stocks
  - Update Stock Prices
  - Calculate Portfolio/Asset Values
  - Each route follows a similar format and functionality. Please refer to the application code for detailed specifications.
