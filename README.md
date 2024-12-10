# Stock_Trading_Application_Project
CS 411 Final Project: Ting-Hung Jen
# Stock Portfolio Management API

## Overview

The Stock Trading Application is a comprehensive web-based system designed to manage user portfolios and facilitate interactions with stock market data. Built using Flask, the application serves as a platform for users to manage their investments, retrieve real-time market data, and execute various portfolio operations. The project integrates RESTful APIs, database management, and external financial data sources to deliver a robust and scalable solution. It allows users to perform operations such as user authentication, portfolio management, stock transactions (buy/sell), retrieving stock data, and updating portfolio details. The application integrates with the Alpha Vantage API to fetch real-time stock data and utilizes a database for managing user data and portfolios.
(*Note: There is a limit of API call of 25 requests a day for free version*)

---
### Running the Application
  - *1.Run the virtual machine given with steps:*
    ```bash
    - source setup_venv.sh
  - *2.Ensure you docker engine is open and run the docker-compose.yml file given with steps:*
    ```bash
    docker-compose build <- This should build the container.
    docker-compose up -d <- This should run the container.
  - After that, you are able to access the application via: http://localhost:5000
      ```To close and delete the container:
      docker-compose down
  - **Remember to Replace the API_Key in the .env file with your own key.**
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

### 4. Stock Operations**
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

### 5. Portfolio Management**
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

### 6. Add/Remove Funds**
- **Buy Stocks**
  - **Path:** `/api/buy-stock`
  - **Request Type:** `POST`
  - **Purpose:** `Buy shares of a stock.`
  - **Request Format:** `Query parameter: ?symbol=<stock-symbol>&quantity=<number of shares>`
  - **Response Format:**
    ```json
    {
      "status": "success",
    }
  - **Example:**
    ```bash
    curl -X POST -H "Content-Type: application/json" http://localhost:5000/api/buy-stock

- **Sell Stocks**
  - **Path:** `/api/sell-stock`
  - **Request Type:** `PUT`
  - **Purpose:** `Sell shares of a stock.`
  - **Request Format:** `Query parameter: ?symbol=<stock-symbol>&quantity=<number of shares>`
  - **Response Format:**
    ```json
    {
      "status": "success",
    }
  - **Example:**
    ```bash
    curl -X PUT -H "Content-Type: application/json" http://localhost:5000/api/sell-stock

- **Update Stock Prices**
  - **Path:** `/api/update-latest-price`
  - **Request Type:** `PUT`
  - **Purpose:** `Update latest stock price.`
  - **Request Format:** `Query parameter: ?symbol=<stock-symbol>`
  - **Response Format:**
    ```json
    {
      "status": "success",
      "new price": 94.32
    }
  - **Example:**
    ```bash
    curl -X PUT -H "Content-Type: application/json" http://localhost:5000/api/update-latest-price

- **Calculate Portfolio Value**
  - **Path:** `/api/calculate-portfolio-value`
  - **Request Type:** `GET`
  - **Purpose:** `Calculate total value of investment profile.`
  - **Request Format:** `None`
  - **Response Format:**
    ```json
    {
      "status": "success",
      "value": 1170000.0
    }
  - **Example:**
    ```bash
    curl -X GET http://localhost:5000/api/calculate-portfolio-value

- **Calculate Asset Value**
  - **Path:** `/api/calculate-asset-value`
  - **Request Type:** `GET`
  - **Purpose:** `Calculate total value of invested stocks.`
  - **Request Format:** `None`
  - **Response Format:**
    ```json
    {
      "status": "success",
      "value": 69900.0
    }
  - **Example:**
    ```bash
    curl -X GET http://localhost:5000/api/calculate-asset-value


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
Getting stock info by symbol (IBM)
Stock retrieved successfully by symbol (IBM).
{
  "status": "success",
  "stock": {
    "current_price": 231.76,
    "description": "International Business Machines Corporation (IBM) is an American multinational technology company headquartered in Armonk, New York, with operations in over 170 countries. The company began in 1911, founded in Endicott, New York, as the Computing-Tabulating-Recording Company (CTR) and was renamed International Business Machines in 1924. IBM is incorporated in New York. IBM produces and sells computer hardware, middleware and software, and provides hosting and consulting services in areas ranging from mainframe computers to nanotechnology. IBM is also a major research organization, holding the record for most annual U.S. patents generated by a business (as of 2020) for 28 consecutive years. Inventions by IBM include the automated teller machine (ATM), the floppy disk, the hard disk drive, the magnetic stripe card, the relational database, the SQL programming language, the UPC barcode, and dynamic random-access memory (DRAM). The IBM mainframe, exemplified by the System/360, was the dominant computing platform during the 1960s and 1970s.",
    "industry": "COMPUTER & OFFICE EQUIPMENT",
    "market_cap": "212668350000",
    "name": "International Business Machines",
    "sector": "TECHNOLOGY",
    "symbol": "IBM"
  }
}
Getting stock historical data for symbol (AAPL) with size (full)...
Stock historical data retrieved successfully for symbol (AAPL).
{
  "status": "success"
  #full output JSON redacted due to length
}
Getting stock latest price for symbol (IBM)...
Stock latest price retrieved successfully for symbol (IBM).
{
  "price": 231.76,
  "status": "success"
}
Adding 390000.00 worth of funds...
Added 390000.00 of funds.
{
  "status": "success"
}
Buying (4) shares of stock (IBM)...
Purchase successful.
{
  "status": "success"
}
Buying (4) shares of stock (SBUX)...
Purchase successful.
{
  "status": "success"
}
Selling (1) shares of stock (SBUX)...
Sell successful.
{
  "status": "success"
}
Removing stock (SBUX)...
Remove successful.
{
  "status": "success"
}
Buying (8) shares of stock (IBM)...
Purchase successful.
{
  "status": "success"
}
Getting user portfolio
User portfolio retrieved successfully.
{
  "portfolio": {
    "portfolio": [
      {
        "current_price": 231.76,
        "name": "International Business Machines",
        "quantity": 12,
        "symbol": "IBM",
        "total_value": 2781.12
      }
    ],
    "total_value": 1170000.0
  },
  "status": "success"
}
Calculating user portfolio value
Calculation success.
{
  "status": "success",
  "value": 1170000.0
}
Getting stock holdings...
Get holdings successful.
{
  "holdings": {
    "IBM": {
      "current_price": 231.76,
      "description": "International Business Machines Corporation (IBM) is an American multinational technology company headquartered in Armonk, New York, with operations in over 170 countries. The company began in 1911, founded in Endicott, New York, as the Computing-Tabulating-Recording Company (CTR) and was renamed International Business Machines in 1924. IBM is incorporated in New York. IBM produces and sells computer hardware, middleware and software, and provides hosting and consulting services in areas ranging from mainframe computers to nanotechnology. IBM is also a major research organization, holding the record for most annual U.S. patents generated by a business (as of 2020) for 28 consecutive years. Inventions by IBM include the automated teller machine (ATM), the floppy disk, the hard disk drive, the magnetic stripe card, the relational database, the SQL programming language, the UPC barcode, and dynamic random-access memory (DRAM). The IBM mainframe, exemplified by the System/360, was the dominant computing platform during the 1960s and 1970s.",
      "industry": "COMPUTER & OFFICE EQUIPMENT",
      "market_cap": "212668350000",
      "name": "International Business Machines",
      "quantity": 12,
      "sector": "TECHNOLOGY",
      "symbol": "IBM"
    }
  },
  "status": "success"
}
Getting funds...
Get holdings successful.
{
  "funds": 1167218.88,
  "status": "success"
}
Logging out user...
User logged out successfully.
All tests passed successfully!
 
