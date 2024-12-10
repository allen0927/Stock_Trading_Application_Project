# Stock_Trading_Application_Project
CS 411 Final Project
# Stock Portfolio Management API

## Overview

This API provides a comprehensive solution for managing a stock portfolio. It allows users to perform operations such as user authentication, portfolio management, stock transactions (buy/sell), retrieving stock data, and updating portfolio details. The application integrates with the Alpha Vantage API to fetch real-time stock data and utilizes a database for managing user data and portfolios.

---

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
Example:
bash
curl -X GET http://localhost:5000/api/health

2. Initialize Database
Path: /api/init-db
Request Type: POST
Purpose: Recreate all database tables, deleting existing data.
Request Format: None
Response Format:
json
{
  "status": "success",
  "message": "Database initialized successfully."
}
Example:
bash
curl -X POST http://localhost:5000/api/init-db

3. User Management
Create User
Path: /api/create-user
Request Type: POST
Purpose: Create a new user account.
Request Format:
json
{
  "username": "example_user",
  "password": "example_password"
}

Response Format:
json
{
  "status": "user added",
  "username": "example_user"
}
Example:
bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "example_user", "password": "example_password"}' http://localhost:5000/api/create-user
Delete User
Path: /api/delete-user
Request Type: DELETE
Purpose: Remove an existing user account.
Request Format:
json
{
  "username": "example_user"
}
Response Format:
json
{
  "status": "user deleted",
  "username": "example_user"
}
Example:
bash
curl -X DELETE -H "Content-Type: application/json" -d '{"username": "example_user"}' http://localhost:5000/api/delete-user
Login
Path: /api/login
Request Type: POST
Purpose: Log in a user and load their portfolio.
Request Format:
json
{
  "username": "example_user",
  "password": "example_password"
}
Response Format:
json
{
  "message": "User example_user logged in successfully."
}
Example:
bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "example_user", "password": "example_password"}' http://localhost:5000/api/login
Logout
Path: /api/logout
Request Type: POST
Purpose: Log out a user and save their portfolio.
Request Format:
json
{
  "username": "example_user"
}
Response Format:
json
{
  "message": "User example_user logged out successfully."
}
Example:
bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "example_user"}' http://localhost:5000/api/logout

4. Stock Operations
Get Stock by Symbol
Path: /api/get-stock-by-symbol
Request Type: GET
Purpose: Retrieve details of a stock using its symbol.
Request Format: Query parameter: ?symbol=<stock-symbol>
Response Format:
json
{
  "status": "success",
  "stock": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "current_price": 150.25
  }
}
Example:
bash
curl -X GET "http://localhost:5000/api/get-stock-by-symbol?symbol=AAPL"

5. Portfolio Management
Display Portfolio
Path: /api/display-portfolio
Request Type: GET
Purpose: Retrieve details of the user's portfolio.
Request Format: None
Response Format:
json
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
Example:
bash
curl -X GET http://localhost:5000/api/display-portfolio
Additional Routes
The application includes additional endpoints for operations such as:

Add/Remove Funds
Buy/Sell Stocks
Update Stock Prices
Calculate Portfolio/Asset Values
Each route follows a similar format and functionality. Please refer to the application code for detailed specifications.

Running the Application
Install the required dependencies using pip install -r requirements.txt.
Run the application using:
bash
python app.py
The application will start on http://localhost:5000.
This README can be extended with more details or examples if needed.
