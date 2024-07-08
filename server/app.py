from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
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


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(only=("id", "name", "address")) for r in restaurants])


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(restaurant.to_dict(only=("id", "name", "address"), with_restaurants=True))


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict(only=("id", "name", "ingredients")) for p in pizzas])


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    restaurant_pizza = RestaurantPizza(
        price=data["price"],
        pizza_id=data["pizza_id"],
        restaurant_id=data["restaurant_id"],
    )
    try:
        db.session.add(restaurant_pizza)
        db.session.commit()
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 422
    return (
        jsonify(
            restaurant_pizza.to_dict(
                with_pizza=True,
                with_restaurant=True,
            )
        ),
        201,
    )

if __name__ == "_main_":
    app.run(port=5555, debug=True)