#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

##############################################
#
# User management
#
##############################################

# Function to create a user
create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
logout_user() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL/logout" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

##############################################
#
# Stock
#
##############################################

# Function to get stock by symbol
# implemented success
get_stock_by_symbol(){
  symbol=$1

  echo "Getting stock info by symbol ($symbol)"
  response=$(curl -s -X GET "$BASE_URL/get-stock-by-symbol?symbol=$symbol")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock retrieved successfully by symbol ($symbol)."
    echo "$response"
    if [ "$ECHO_JSON" = true ]; then
      echo "Stock JSON ($symbol):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get stock by symbol ($symbol)."
    echo "$response"
    exit 1
  fi
}

# Function to get stock historical data
stock_historical_data(){
  symbol=$1
  size=$2

  echo "Getting stock historical data for symbol ($symbol) with size ($size)..."
  response=$(curl -s -X GET "$BASE_URL/retrieve-stock-historical-data?symbol=$symbol&size=$size" \
    -H "Content-Type: application/json")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock historical data retrieved successfully for symbol ($symbol)."
    echo "$response"
    if [ "$ECHO_JSON" = true ]; then
      echo "Historical Data for ($symbol):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get stock historical data for symbol ($symbol)."
    echo "Response:"
    echo "$response"
    exit 1
  fi
}

# Function to get stock latest price
get_latest_price(){
  symbol=$1

  echo "Getting stock latest price for symbol ($symbol)..."
  response=$(curl -s -X GET "$BASE_URL/fetch-latest-price?symbol=$symbol" \
    -H "Content-Type: application/json")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock latest price retrieved successfully for symbol ($symbol)."
    echo "$response"
    if [ "$ECHO_JSON" = true ]; then
      echo "Stock latest price for ($symbol):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get stock latest price for symbol ($symbol)."
    echo "Response:"
    echo "$response"
    exit 1
  fi
}

##############################################
#
# Portfolio
#
##############################################

#Function to add funds to user's profile
profile_charge_funds(){
  value=$1
  echo "Adding $value worth of funds..."
  response=$(curl -s -X PUT "$BASE_URL/profile-charge-funds?value=$value" -H "Content-Type: application/json")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Added $value of funds."
    echo "$response"
  else
    echo "Failed to add funds."
    echo "$response"
    exit 1
  fi
}


# Function to get user portfolio
get_user_portfolio(){
  echo "Getting user portfolio"
  response=$(curl -s -X GET "$BASE_URL/display-portfolio")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "User portfolio retrieved successfully."
    echo "$response"
    if [ "$ECHO_JSON" = true ]; then
      echo "User portfolio:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get user portfolio."
    echo "$response"
    exit 1
  fi
}


# Function to calculate portfolio value
calculate_portfolio_value(){
  echo "Calculating user portfolio value"
  response=$(curl -s -X GET "$BASE_URL/calculate-portfolio-value")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Calculation success."
    echo "$response"
    if [ "$ECHO_JSON" = true ]; then
      echo "Value:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to calculate user portfolio value."
    echo "$response"
    exit 1
  fi
}


# Function to buy new stock
buy_new_stock(){
  symbol=$1
  quantity=$2

  echo "Buying ($quantity) shares of stock ($symbol)..."
  response=$(curl -s -X POST "$BASE_URL/buy-stock?symbol=$symbol&quantity=$quantity" -H "Content-Type: application/json")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Purchase successful."
    echo "$response"
  else
    echo "Purchase failed."
    echo "$response"
    exit 1
  fi
}

# Function to sell stock
sell_stock(){
  symbol=$1
  quantity=$2
  
  echo "Selling ($quantity) shares of stock ($symbol)..."
  response=$(curl -s -X PUT "$BASE_URL/sell-stock?symbol=$symbol&quantity=$quantity" -H "Content-Type: application/json")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Sell successful."
    echo "$response"
  else
    echo "Sell failed."
    echo "$response"
    exit 1
  fi
}


# Function to remove interested stock
remove_interested_stock(){
  symbol=$1

  echo "Removing stock ($symbol)..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-interested-stock?symbol=$symbol" -H "Content-Type: application/json")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Remove successful."
    echo "$response"
  else
    echo "Remove failed."
    echo "$response"
    exit 1
  fi
}



# Function to get stock holdings
get_stock_holdings(){
  echo "Getting stock holdings..."
  response=$(curl -s -X GET "$BASE_URL/get-stock-holdings")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Get holdings successful."
    echo "$response"
    if [ "$ECHO_JSON" = true ]; then
      echo "Holdings:"
      echo "$response" | jq .
    fi
  else
    echo "Get holdings failed."
    echo "$response"
    exit 1
  fi
}

# Function to get current funds
get_funds(){
  echo "Getting funds..."
  response=$(curl -s -X GET "$BASE_URL/get-funds")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Get holdings successful."
    echo "$response"
    if [ "$ECHO_JSON" = true ]; then
      echo "Funds:"
      echo "$response" | jq .
    fi
  else
    echo "Get funds failed."
    echo "$response"
    exit 1
  fi
}

# Function to initialize the database
init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Initialization Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initialize the database."
    echo "$response"
    exit 1
  fi
}



# Run all the steps in order
check_health
init_db
create_user
login_user

get_stock_by_symbol "IBM"
stock_historical_data "AAPL" "full"
get_latest_price "IBM"

profile_charge_funds 390000.00
buy_new_stock IBM 4
buy_new_stock SBUX 4
sell_stock SBUX 1
remove_interested_stock SBUX
buy_new_stock IBM 8

get_user_portfolio
calculate_portfolio_value
get_stock_holdings
get_funds

logout_user
echo "All tests passed successfully!"