from flask import Flask, request, jsonify
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)

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
    return jsonify(restaurant.to_dict(only=("id", "name", "address"), with_pizzas=True))

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    RestaurantPizza.query.filter_by(restaurant_id=id).delete()
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
        return jsonify({"error": str(e)}), 400
    
    restaurant = Restaurant.query.get(data["restaurant_id"])
    pizza = Pizza.query.get(data["pizza_id"])
    
    return jsonify({
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "pizza_id": restaurant_pizza.pizza_id,
        "restaurant_id": restaurant_pizza.restaurant_id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
    }), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)
