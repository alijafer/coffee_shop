import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def getAllDrinks():
    '''
    GET /drinks
        it is a public endpoint
        it contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
     drinks is the list of drinks
        or appropriate status code 500 indicating reason for failure
'''
    try:
        drinks = Drink.query.all()
        short_drinks = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            'drinks': short_drinks
        })
    except Exception:
            abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getAllDrinksDetail(payload):
    try:
        drinks = Drink.query.all()
        long_drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": long_drinks
        })
    except Exception:
            abort(401)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createDrinks(payload):
    try:
        data = request.get_json()
        title = data.get('title', None)
        recipe = data.get('recipe', None)
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({
            "success": True,
            'drinks': drink.long()
        })
    except Exception:
        abort(422)
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404



'''
error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized The server could not verify that you are" +
        " authorized to access the URL requested. You either supplied the " +
        "wrong credentials (e.g. a bad password), or your browser doesn't" +
        " understand how to supply the credentials required."
        }), 401


@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
        }), 400


@app.errorhandler(500)
def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal Server Error"
    }), 500


@app.errorhandler(AuthError)
def handle_auth_error(exception):
    response = jsonify(exception.error)
    response.status_code = exception.status_code
    return response