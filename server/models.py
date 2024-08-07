from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        backref="restaurant",
        primaryjoin="Restaurant.id == RestaurantPizza.restaurant_id"
    )
    
    pizzas = db.relationship(
        "Pizza",
        secondary="restaurant_pizzas",
        backref="restaurants",
        primaryjoin="Restaurant.id == RestaurantPizza.restaurant_id",
        secondaryjoin="Pizza.id == RestaurantPizza.pizza_id"
    )

    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurants')

    def to_dict(self, only=None, with_pizzas=False):
        data = super().to_dict(only=only)
        if with_pizzas:
            data["pizzas"] = [pizza.to_dict() for pizza in self.pizzas]
        return data

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)
    
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        backref="pizza",
        primaryjoin="Pizza.id == RestaurantPizza.pizza_id"
    )
    
    restaurants = db.relationship(
        "Restaurant",
        secondary="restaurant_pizzas",
        backref="pizzas",
        primaryjoin="Restaurant.id == RestaurantPizza.restaurant_id",
        secondaryjoin="Pizza.id == RestaurantPizza.pizza_id"
    )

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.restaurant_pizzas')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
