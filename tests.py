import unittest

from dependency_graph import (DependencyGraph, ProducerBase, ProductBase,
                              RequirementNotMetException)


class Flour(ProductBase):
    pass


class Water(ProductBase):
    pass


class Salt(ProductBase):
    pass


class Yeast(ProductBase):
    pass


class Dough(ProductBase):
    pass


class TomatoSauce(ProductBase):
    pass


class Peppers(ProductBase):
    pass


class Cheese(ProductBase):
    pass


class Pepperoni(ProductBase):
    pass


class Onion(ProductBase):
    pass


class Mushrooms(ProductBase):
    pass


class Pineapple(ProductBase):
    pass


class Toppings(ProductBase):
    pass


class UncookedPizza(ProductBase):
    pass


class Pizza(ProductBase):
    pass


class Oven(ProductBase):
    pass


class TestProducerBase(ProducerBase):
    """
    Just a test-class with some helper functions to use when debugging the code
    """

    def _parse_products(self, products):
        """
        ...
        """

        def print_product(product: ProductBase):
            return (
                isinstance(product, ProductBase)
                and type(product).__name__
                or product.__name__
            )

        return ", ".join([print_product(p) for p in products])

    def info(self):
        print("\nWho I am: %s" % self.__class__.__name__)
        if self.__doc__:
            print("What I do: %s" % self.__doc__.strip())

        print(
            "What I require: %s"
            % (
                self.required_component
                and self._parse_products(self.required_component)
                or "Nothing"
            )
        )
        print("What I provide: %s" % self._parse_products(self.provided_component))


class IngridientsProducer(TestProducerBase):
    """
    Take all the ingridents out of the fridge
    """

    required_component = []
    provided_component = [
        Flour,
        Water,
        Yeast,
        Salt,
        Cheese,
        TomatoSauce,
        Onion,
        Peppers,
        Pepperoni,
        Mushrooms,
    ]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        for product in self.provided_component:
            yield product()


class DoughProducer(TestProducerBase):
    """
    Make the dough
    """

    required_component = [Flour, Water, Yeast, Salt]
    provided_component = [Dough]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        yield Dough()


class PineappleProducer(TestProducerBase):
    """
    I bring the pineapple, which nobody wants
    """

    required_component = []
    provided_component = [Pineapple]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        yield Pineapple()


class ToppingsProducer(TestProducerBase):
    """Make the topping"""

    required_component = [Dough, Onion, Pepperoni, Peppers, TomatoSauce, Mushrooms]
    provided_component = [Toppings]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        yield Toppings()


class CheeseProducer(TestProducerBase):
    "Provide some cheese."
    required_component = []
    provided_component = [Cheese]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        yield Cheese()


class OvenProducer(TestProducerBase):
    "Turning on the oven."
    required_component = []
    provided_component = [Oven]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        yield Oven()


class UncookedPizzaProducer(TestProducerBase):
    "Putting everything together"
    required_component = [Toppings, TomatoSauce, Cheese, Dough]
    provided_component = [UncookedPizza]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        yield UncookedPizza()


class PizzaProducer(TestProducerBase):
    "Cooking the pizza."
    required_component = [UncookedPizza, Oven]
    products = [Pizza]

    def produce(self, products, *args, **kwargs):
        """ """
        self.info()
        yield Pizza()


class PizzaTest(unittest.TestCase):
    """ """

    def test_making_pizza(self):
        dg = DependencyGraph(
            UncookedPizzaProducer,
            DoughProducer,
            PizzaProducer,
            IngridientsProducer,
            CheeseProducer,
            OvenProducer,
            ToppingsProducer,
        )

        final_product = None
        try:
            products = dg.start()
            final_product = products[-1].__class__.__name__
            print("\nFinal product: %s" % final_product)
        except RequirementNotMetException as ex:
            print("\n\n")
            print(ex)

        self.assertEqual(final_product, "Pizza")

    def test_making_pizza_biproducts(self):
        dg = DependencyGraph(
            UncookedPizzaProducer,
            DoughProducer,
            PizzaProducer,
            PineappleProducer,
            IngridientsProducer,
            CheeseProducer,
            OvenProducer,
            ToppingsProducer,
        )

        expected_gross_fruit = dg.find_biproducts(dg.start())[0].__class__
        self.assertEqual(expected_gross_fruit, Pineapple)

    def test_making_pizza_without_dough(self):
        dg = DependencyGraph(
            UncookedPizzaProducer,
            # DoughProducer,
            PizzaProducer,
            IngridientsProducer,
            CheeseProducer,
            OvenProducer,
            ToppingsProducer,
        )
        with self.assertRaises(RequirementNotMetException):
            dg.start()

    def _test_list(self):
        from typing import List, Type

        class Product:
            pass

        class Food(Product):
            pass

        class Drink(Product):
            pass

        class ShoppingBasket:
            def __init__(self, *items: Type[Product]):
                self.items = items

        basket = ShoppingBasket(Food, Drink)
        print(basket.items)


if __name__ == '__main__':
    unittest.main()