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
!! Running this funciton will add one
'''
# with app.app_context(): 
#     db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks() :
    # get data in database
    drinks = Drink.query.all()
    # return data in list
    short_drinks = [drink.short() for drink in drinks]
    # return data in user
    return jsonify({
        'success': True,
        'drinks': short_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload) :
    # get data in database
    drinks = Drink.query.all()
    # return data in list
    long_drinks = [drink.long() for drink in drinks]
    # return data in user
    return jsonify({
        'success': True,
        'drinks': long_drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload) :
    #get data in link
    data = request.get_json()
    title = data.get('title')
    recipe = data.get('recipe')
    # check if title already exists in the database
    existing_drink = Drink.query.filter_by(title=title).first()
    if existing_drink:
        abort(409)  # Conflict - title already exists
    #check data
    if not title :
        abort(400)
    elif not recipe :
        abort(400)
    else :
        # add data in database
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        # return data in user
        return jsonify({
        'success': True,
        'drinks': [drink.long()]
        })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    #get data in link
    data = request.get_json()
    title = data.get('title')
    recipe = data.get('recipe')
    # get data in database
    drink = Drink.query.get(id)
    #check data
    if not drink:
        abort(404)
    if title:
        drink.title = title
    if recipe:
        drink.recipe = json.dumps(recipe)
    # update data
    drink.update()
    # return data in user
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # get data in database
    drink = Drink.query.get(id)
    # check data
    if not drink:
        abort(404)
    else :
        #delete data
        drink.delete()
        # return data in user
        return jsonify({
            'success': True,
            'delete': id
        }), 200


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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def not_processed(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "This transaction cannot be processed"
    }), 400

@app.errorhandler(409)
def not_insert_data(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "It is not possible to add data to a name in the database"
    }), 409

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code