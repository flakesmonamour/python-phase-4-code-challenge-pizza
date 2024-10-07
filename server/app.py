#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        result = jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants])
        return make_response(result, 200)

class RestaurantDetail(Resource):
    def get(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                return make_response(jsonify(restaurant.to_dict()), 200)
            else:
                return make_response(jsonify({"error": "Restaurant not found"}), 404)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

    def delete(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                db.session.delete(restaurant)
                db.session.commit()
                return make_response('', 204)
            else:
                return make_response(jsonify({"error": "Restaurant not found"}), 404)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

class PizzaList(Resource):
    def get(self):
        try:
            pizzas = Pizza.query.all()
            result = jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas])
            return make_response(result, 200)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

class RestaurantPizzaList(Resource):
    def post(self):
        try:
            data = request.get_json()
            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')

            if not 1 <= price <= 30:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)

            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()

            return make_response(jsonify(restaurant_pizza.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')
api.add_resource(RestaurantPizzaList, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)