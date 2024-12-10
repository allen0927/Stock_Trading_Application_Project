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
      ```To close and delete the container:
      docker-compose down
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

- **Sample smoketest result when API call achieve limit**
  ```bash
  Checking health status...
  Service is healthy.
  Initializing the database...
  Database initialized successfully.
  Creating a new user...
  User created successfully.
  Logging in user...
  User logged in successfully.
  Getting stock info by symbol (IBM)
  Failed to get stock by symbol (IBM).
  {
    "error": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."
  }
  Getting stock historical data for symbol (AAPL) with size (full)...
  Failed to get stock historical data for symbol (AAPL).
  Response:
  Getting stock latest price for symbol (IBM)...
  Failed to get stock latest price for symbol (IBM).
  Response:
  {
    "error": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."
  }
  Adding 390000.00 worth of funds...
  Added 390000.00 of funds.
  {
    "status": "success"
  }
  Buying (4) shares of stock (IBM)...
  Purchase failed.
  {
    "error": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."
  }
  Buying (4) shares of stock (SBUX)...
  Purchase failed.
  {
    "error": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."
  }
  Selling (1) shares of stock (SBUX)...
  Sell failed.
  {
    "error": "Stock SBUX is not in your portfolio."
  }
  Removing stock (SBUX)...
  Remove failed.
  {
    "error": "stock not in portfolio"
  }
  Buying (8) shares of stock (IBM)...
  Purchase failed.
  {
    "error": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."
  }
  Getting user portfolio
  User portfolio retrieved successfully.
  {
    "portfolio": {
      "portfolio": [],
      "total_value": 390000.0
    },
    "status": "success"
  }
  Calculating user portfolio value
  Calculation success.
  {
    "status": "success",
    "value": 390000.0
  }
  Getting stock holdings...
  Get holdings successful.
  {
    "holdings": {},
    "status": "success"
  }
  Getting funds...
  Get holdings successful.
  {
    "funds": 390000.0,
    "status": "success"
  }
  Logging out user...
  User logged out successfully.
  All tests passed successfully!
