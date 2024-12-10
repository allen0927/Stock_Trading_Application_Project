from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
# from flask_cors import CORS

from config import ProductionConfig
from stock_app.db import db
from stock_app.models.portfolio_model import PortfolioModel
from stock_app.models.stock_model import *
from stock_app.models.mongo_session_model import login_user, logout_user
from stock_app.models.user_model import Users

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

# Load environment variables from .env file
load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    portfolio_model = PortfolioModel()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################


    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)
    

    ####################################################
    #
    # Database
    #
    ####################################################


    @app.route('/api/init-db', methods=['POST'])
    def init_db():
        """
        Initialize or recreate database tables.

        This route initializes the database tables defined in the SQLAlchemy models.
        If the tables already exist, they are dropped and recreated to ensure a clean
        slate. Use this with caution as all existing data will be deleted.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.

        Logs:
            Logs the status of the database initialization process.
        """
        try:
            with app.app_context():
                app.logger.info("Dropping all existing tables.")
                db.drop_all()  # Drop all existing tables
                app.logger.info("Creating all tables from models.")
                db.create_all()  # Recreate all tables
            app.logger.info("Database initialized successfully.")
            return jsonify({"status": "success", "message": "Database initialized successfully."}), 200
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", str(e))
            return jsonify({"status": "error", "message": "Failed to initialize database."}), 500  

    ##########################################################
    #
    # User management
    #
    ##########################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-user', methods=['DELETE'])
    def delete_user() -> Response:
        """
        Route to delete a user.

        Expected JSON Input:
            - username (str): The username of the user to be deleted.

        Returns:
            JSON response indicating the success of user deletion.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue deleting the user from the database.
        """
        app.logger.info('Deleting user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')

            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

            # Call the User function to delete the user from the database
            app.logger.info('Deleting user: %s', username)
            Users.delete_user(username)

            app.logger.info("User deleted: %s", username)
            return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to delete user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Load user's combatants into the battle model
            login_user(user_id, portfolio_model)

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    @app.route('/api/logout', methods=['POST'])
    def logout():
        """
        Route to log out a user and save their combatants to MongoDB.

        Expected JSON Input:
            - username (str): The username of the user.

        Returns:
            JSON response indicating the success of the logout.

        Raises:
            400 error if input validation fails or user is not found in MongoDB.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            app.logger.error("Invalid request payload for logout.")
            raise BadRequest("Invalid request payload. 'username' is required.")

        username = data['username']

        try:
            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Save user's combatants and clear the battle model
            logout_user(user_id, portfolio_model)

            app.logger.info("User %s logged out successfully.", username)
            return jsonify({"message": f"User {username} logged out successfully."}), 200

        except ValueError as e:
            app.logger.warning("Logout failed for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Error during logout for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500



    ##########################################################
    #
    # Stock
    #
    ##########################################################


    @app.route('/api/get-stock-by-symbol', methods=['GET'])
    def get_stock_by_symbol(symbol: str) -> Response:
        """Route to retrieve stock info using the API.

        Path Parameter:
            - symbol (str): The stock ticker's symbol.

        Returns:
            JSON response with the stock details or error message.

        Raises:
            400 error if no input
            500 error there was an issue retrieving stock info
        """
        try:
            app.logger.info(f"Retrieving stock info: {symbol}")

            if not symbol:
                return make_response(jsonify({'error': 'Stock symbol is required'}), 400)

            stock = get_stock_by_symbol(symbol, PortfolioModel.ts, PortfolioModel.fd)
            return make_response(jsonify({'status': 'success', 'stock': stock}), 200)
        
        except Exception as e:
            app.logger.error(f"Error retrieving stock: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/stock-historical-data', methods=['GET'])
    def stock_historical_data(symbol: str, size: str) -> Response:
        """Route to retrieve price data for a stock within a specific date range.

        Path Parameter:
            - symbol (str): The stock ticker's symbol.

        Returns:
            JSON response with the stock data or error message.

        Raises:
            400 error if no input
            500 error there was an issue retrieving stock info
        """
        try:
            app.logger.info(f"Retrieving stock historical data: {symbol}")

            if not symbol:
                return make_response(jsonify({'error': 'Stock symbol is required'}), 400)

            data = stock_historical_data(symbol, PortfolioModel.ts, size)
            return make_response(jsonify({'status': 'success', 'data': data}), 200)
        
        except Exception as e:
            app.logger.error(f"Error retrieving stock: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/get-latest-price', methods = ['GET'])
    def get_latest_price(symbol: str) -> Response:
        """
        Route to get latest market price of a specific stock.

        Path Parameter:
            - symbol (str): The stock ticker's symbol.

        Returns:
            JSON response with the stock price or error message.

        Raises:
            400 error if no input
            500 error there was an issue retrieving stock info
        """
        try:
            app.logger.info(f"Retrieving latest stock price: {symbol}")

            if not symbol:
                return make_response(jsonify({'error': 'Stock symbol is required'}), 400)

            price = stock_historical_data(symbol, PortfolioModel.ts)
            return make_response(jsonify({'status': 'success', 'price': price}), 200)
        
        except Exception as e:
            app.logger.error(f"Error retrieving stock: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        

    ####################################################
    #
    # Portfolio
    #
    ####################################################

    @app.route('/api/profile-charge-funds', methods=['PUT'])
    def profile_charge_funds(value: float) -> Response:
        """
        Route to add funds to user's profile.

        Parameters:
            - value (float): the value added

        Returns:
            JSON response indicating the success of adding funds.

        Raises:
            400 error if value < 0
            500 error if there is an issue adding funds.
        """
        try:
            app.logger.info('Adding funds...')
            portfolio_model.profile_charge_funds(value)
            app.logger.info('Funds added.')
            return make_response(jsonify({'status': value + ' added'}), 200)
        
        except ValueError:
            app.logger.error("Attempt to add negative value")
            return make_response(jsonify({'error': 'value must be positive'}, 400))
        except Exception as e:
            app.logger.error("Failed to add funds: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/display-portfolio', methods=['GET'])
    def display_portfolio() -> Response:
        """
        Route to show user's portfolio

        Returns:
            JSON response with the user portfolio.

        Raises:
            500 error if there is an issue showing the portfolio.
        """
        try:
            app.logger.info(f"Retrieving portfolio...")   
            portfolio = portfolio_model.display_portfolio()
            return make_response(jsonify({'status': 'success', 'portfolio': portfolio}), 200)
        
        except Exception as e:
            app.logger.error(f"Error retrieving portfolio: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    
    @app.route('/api/look-up-stock', methods=['GET'])
    def look_up_stock(symbol: str) -> Response:
        """
        Route to look up info about a specific stock

        Returns:
            JSON response with the stock info

        Raises:
            400 error if there was a bad input
            500 error if there is an issue showing the portfolio.
        """
        try:
            app.logger.info(f"Retrieving stock info: {symbol}")

            if not symbol:
                return make_response(jsonify({'error': 'Stock symbol is required'}), 400)

            info = portfolio_model.look_up_stock(symbol)
            return make_response(jsonify({'status': 'success', 'info': info}), 200)
        
        except Exception as e:
            app.logger.error(f"Error retrieving stock info: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/update-latest-price', methods=['PUT'])
    def update_latest_price(symbol: str) -> Response:
        """
        Route to retrive and update latest price for a stock

        Parameters:
            - symbol (str): the stock symbol

        Returns:
            JSON response indicating the success of update and latest stock price.

        Raises:
            400 error if no input
            500 error if there is an issue updating stock price.
        """
        try:
            if not symbol:
                return make_response(jsonify({'error': 'Stock symbol is required'}), 400)
            
            app.logger.info('Updating price for stock ' + symbol + ' ...')
            value=portfolio_model.update_latest_price(symbol)
            app.logger.info('Price updated.')
            return make_response(jsonify({'status': 'success', 'new price': value}), 200)
        
        except Exception as e:
            app.logger.error("Failed to add funds: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/calculate-portfolio-value', methods=['GET'])
    def calculate_portfolio_value() -> Response:
        """
        Route to calculate total value of investment profile
            = funds + stocks

        Returns:
            JSON response with computed total value

        Raises:
            500 error if there is an issue computing the value.
        """
        try:
            app.logger.info(f"Calculating total portfolio value...")

            value = portfolio_model.calculate_portfolio_value()
            return make_response(jsonify({'status': 'success', 'value': value}), 200)
        
        except Exception as e:
            app.logger.error(f"Error calculating total value: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        

    @app.route('/api/calculate-asset-value', methods=['GET'])
    def calculate_asset_value() -> Response:
        """
        Route to calculate asset value of investment profile
            = stocks (does not include funds)

        Returns:
            JSON response with computed asset value

        Raises:
            500 error if there is an issue computing the value.
        """
        try:
            app.logger.info(f"Calculating total asset value...")

            value = portfolio_model.calculate_asset_value()
            return make_response(jsonify({'status': 'success', 'value': value}), 200)
        
        except Exception as e:
            app.logger.error(f"Error calculating asset value: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/buy-stock', methods=['POST', 'PUT'])
    def buy_stock(symbol: str, quantity: int) -> Response:
        """
        Route to buy shares of a specific stock

        Parameters:
            - symbol (str): the stock symbol
            - quantity (int): number of shares to buy

        Returns:
            JSON response with purchase successful

        Raises:
            400 error if quantity < 0
            401 error if insufficient funds
            500 error if there is an issue computing the value.
        """
        if quantity < 1:
            return make_response(jsonify({'error': 'quantity must be at least 1'}), 400)
        
        try:
            app.logger.info(f"Buying " + quantity + "shares of " + symbol + "...")
            portfolio_model.buy_stock(symbol, quantity)
            return make_response(jsonify({'status': 'success'}), 200)
        
        except ValueError:
            app.logger.error("Insufficient funds")
            return make_response(jsonify({'error': 'insufficient funds'}), 401)
        except Exception as e:
            app.logger.error(f"Error buying stock: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/sell-stock', methods=['PUT'])
    def sell_stock(symbol: str, quantity: int) -> Response:
        """
        Route to sell shares of a specific stock

        Parameters:
            - symbol (str): the stock symbol
            - quantity (int): number of shares to buy

        Returns:
            JSON response with sell successful

        Raises:
            400 error if quantity < 0
            401 error if insufficient shares
            500 error if there is an issue computing the value.
        """
        if quantity < 1:
            return make_response(jsonify({'error': 'quantity must be at least 1'}), 400)
        
        try:
            app.logger.info(f"Selling " + quantity + "shares of " + symbol + "...")
            portfolio_model.sell_stock(symbol, quantity)
            return make_response(jsonify({'status': 'success'}), 200)
        
        except ValueError:
            app.logger.error("Insufficient shares")
            return make_response(jsonify({'error': 'insufficient shares'}), 401)
        except Exception as e:
            app.logger.error(f"Error selling stock: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/add-interested-stock', methods=['POST'])
    def add_interested_stock(symbol: str) -> Response:
        """
        Route to "favorite" a stock

        Parameters:
            - symbol (str): the stock symbol

        Returns:
            JSON response with operation successful

        Raises:
            400 error if no input
            401 error if stock already in portfolio
            500 error if there is an issue computing the value.
        """
        
        try:
            if not symbol:
                return make_response(jsonify({'error': 'Stock symbol is required'}), 400)
            
            app.logger.info(f"Favoriting " + symbol + "...")
            portfolio_model.add_interested_stock(symbol)
            return make_response(jsonify({'status': 'favorited'}), 200)
        
        except ValueError:
            app.logger.error("Stock already exists in portfolio")
            return make_response(jsonify({'error': 'stock already in portfolio'}), 401)
        except Exception as e:
            app.logger.error(f"Error favoriting stock: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/remove-interested-stock', methods=['DELETE'])
    def remove_interested_stock(symbol: str) -> Response:
        """
        Route to sell all shares of a stock and remove from portfolio

        Parameters:
            - symbol (str): the stock symbol

        Returns:
            JSON response with operation successful

        Raises:
            400 error if no input
            401 error if stock not in portfolio
            500 error if there is an issue computing the value.
        """
        
        try:
            if not symbol:
                return make_response(jsonify({'error': 'Stock symbol is required'}), 400)
            
            app.logger.info(f"Deleting " + symbol + " from portfolio...")
            portfolio_model.remove_interested_stock(symbol)
            return make_response(jsonify({'status': 'deleted'}), 200)
        
        except ValueError:
            app.logger.error("Stock does not exists in portfolio")
            return make_response(jsonify({'error': 'stock not in portfolio'}), 401)
        except Exception as e:
            app.logger.error(f"Error deleting stock: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/clear-all-stocks', methods=['PUT'])
    def clear_all_stocks() -> Response:
        """
        Route to clear portfolio and set funds to 0

        Returns:
            JSON response with operation successful

        Raises:
            500 error if there is an issue clearing the portfolio.
        """
        
        try:       
            app.logger.info(f"Clearing portfolio...")
            portfolio_model.clear_all_stocks()
            return make_response(jsonify({'status': 'cleared'}), 200)
        
        except Exception as e:
            app.logger.error(f"Error clearing portfolio: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        


    @app.route('/api/load-stock', methods=['PUT'])
    def load_stock(stock) -> Response:
        """
        Route to add given stock to portfolio

        Returns:
            JSON response with operation successful

        Raises:
            400 error if no input
            500 error if there is an issue adding stock to portfolio.
        """
        
        try:
            if not stock:
                return make_response(jsonify({'error': 'Stock is required'}), 400)
            
            app.logger.info(f"Adding stock to portfolio...")
            portfolio_model.load_stock(stock)
            return make_response(jsonify({'status': 'success'}), 200)
        
        except Exception as e:
            app.logger.error(f"Error adding stock to portfolio: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-stock-holdings', methods=['GET'])
    def get_stock_holdings() -> Response:
        """
        Route to get user's stock holdings

        Returns:
            JSON response with stock holdings

        Raises:
            500 error if there is an issue accessing holdings
        """
        
        try:
            app.logger.info(f"Getting user holdings...")
            holdings = portfolio_model.get_stock_holdings()
            return make_response(jsonify({'status': 'success', 'holdings': holdings}), 200)
        
        except Exception as e:
            app.logger.error(f"Error getting stock holdings: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/get-funds', methods=['GET'])
    def get_funds() -> Response:
        """
        Route to get user's curre t funds

        Returns:
            JSON response with current funds

        Raises:
            500 error if there is an issue accessing curren t funds
        """
        
        try:
            app.logger.info(f"Getting user funds...")
            funds = portfolio_model.get_funds()
            return make_response(jsonify({'status': 'success', 'funds': funds}), 200)
        
        except Exception as e:
            app.logger.error(f"Error getting user funds: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)