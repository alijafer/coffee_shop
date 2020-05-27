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


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getAllDrinksDetail(payload):
    '''
    GET /drinks-detail
        it is require the 'get:drinks-detail' permission
        it is contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    try:
        drinks = Drink.query.all()
        long_drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": long_drinks
        })
    except Exception:
        abort(401)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createDrinks(payload):
    '''
    POST /drinks
        it is create a new row in the drinks table
        it is require the 'post:drinks' permission
        it is contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''
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


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updateDrinks(payload, id):
    '''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it is respond with a 404 error if <id> is not found
        it is update the corresponding row for <id>
        it is require the 'patch:drinks' permission
        it is contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code 422 indicating reason for failure
    '''
    data = request.get_json()
    if data is None:
        abort(400)
    title = data.get('title', None)
    recipe = data.get('recipe', None)
    id_test = data.get('id', None)
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    if title is None:
        abort(400)
    try:
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrinks(payload, id):
    '''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it is respond with a 404 error if <id> is not found
        it is delete the corresponding row for <id>
        it is require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code 422 indicating reason for failure
    '''
    if id is None:
        abort(404)
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id,
            'message': "Question successfully deleted"
        })
    except Exception:
        abort(422)


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


@app.errorhandler(404)
def unprocessable(error):
    '''
error handler for 404
    error handler is conform to general task above
    '''
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized",
        "description": " The server could not verify that you are" +
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
    '''
error handler for AuthError
    error handler is conform to general task above
    '''
    response = jsonify(exception.error)
    response.status_code = exception.status_code
    return response
