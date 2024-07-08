from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    _tablename_ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', lazy=True)
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurant_pizzas')

    # add relationship


    # add serialization rules

    def _repr_(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    _tablename_ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza', lazy=True)
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.restaurant_pizzas')

    # add relationship

    # add serialization rules

    def _repr_(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    _tablename_ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price


    # add relationships

    # add serialization rules

    # add validation

    def _repr_(self):
        return f"<RestaurantPizza ${self.price}>"