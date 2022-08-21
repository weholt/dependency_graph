from abc import ABC, abstractmethod
from collections import deque
from typing import Iterable, List, Type

GRAY, BLACK = 0, 1


class ProductBase(ABC):
    """ """

    pass


class ProducerBase(ABC):
    """ """

    required_component: List[ProductBase] = []
    provided_component: List[ProductBase] = []
    products: List[ProductBase] = []

    def __init__(self):
        """ """
        pass

    def _internal_produce(
        self, products: Type[ProductBase], *args, **kwargs
    ) -> Iterable[ProductBase]:
        self.validate_requirements(products)
        return self.produce(products, *args, **kwargs)

    @abstractmethod
    def produce(
        self, products: Type[ProductBase], *args, **kwargs
    ) -> List[ProductBase]:
        """ """
        raise Exception("Implement in subclass")

    def validate_requirements(self, provided_components: Iterable[ProductBase]) -> None:
        provided_classes = [p.__class__ for p in provided_components]
        missing_requirements = []
        for required in self.required_component:
            if required not in provided_classes:
                missing_requirements.append(required)
        if missing_requirements:
            raise RequirementNotMetException(self, missing_requirements)

    def can_produce(self) -> bool:
        return True

    def filter_products(
        self, available_products: Iterable[ProductBase], target_class: Type[ProductBase]
    ) -> Iterable[ProductBase]:
        for product in available_products:
            if isinstance(product, target_class):
                yield product

    def __str__(self) -> str:
        """

        :return:
        """
        return self.__class__.__name__


class RequirementNotMetException(Exception):
    """ """

    def __init__(
        self,
        producer: ProducerBase,
        missing_requirements: List[ProductBase],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.producer = producer
        self.missing_requirements = missing_requirements

    def __str__(self) -> str:
        return f"{self.producer} is missing these requirements: {self.missing_requirements}"


class DependencyGraph:
    """ """

    def __init__(self, *producers: Type[ProducerBase], verbose: bool = False) -> None:
        """ """
        self.producers = [*producers]
        self.verbose = verbose

    def add_producer(self, *producers: Type[ProducerBase]) -> None:
        """

        :param producer:
        :return:
        """
        self.producers.extend(producers)

    def topological(self, graph):
        order, enter, state = deque(), set(graph), {}

        def dfs(node):
            state[node] = GRAY
            for k in graph.get(node, ()):
                sk = state.get(k, None)
                if sk == GRAY:
                    raise ValueError("cycle")

                if sk == BLACK:
                    continue
                enter.discard(k)
                dfs(k)
            order.appendleft(node)
            state[node] = BLACK

        while enter:
            dfs(enter.pop())

        return order

    def get_sorted_producers(
        self, producers: Iterable[ProducerBase] = []
    ) -> Iterable[ProducerBase]:
        """

        :return:
        """
        producers_sorted = self.topological(self.producer_graph(producers))
        producers_sorted.reverse()
        return list(producers_sorted)

    def producer_graph(self, producers: List[ProducerBase] = []):
        """

        :return:
        """
        graph = {}
        out_graph = {}
        in_graph = {}

        for producer in producers or self.producers:
            out_graph[producer] = producer.provided_component
            in_graph[producer] = producer.required_component

        for in_ in in_graph:
            graph[in_] = []
            for out_ in out_graph:
                for in_req in in_graph[in_]:
                    for out_prov in out_graph[out_]:
                        if out_prov == in_req:
                            graph[in_].append(out_)

        return graph

    def get_producers(self) -> Iterable[ProducerBase]:
        """

        :return:
        """
        return self.get_sorted_producers()

    def filter_products_for_producer(
        self, producer: ProducerBase, products: Iterable[ProductBase]
    ) -> Iterable[ProductBase]:
        for product in products:
            if product.__class__ in producer.required_component:
                yield product

    def start(self, *args, **kwargs):
        """ """
        produced_products = []
        for producer_class in self.get_producers():
            producer = producer_class()  # type: ignore
            if not producer.can_produce():
                continue

            produced_products.extend(
                producer._internal_produce(
                    produced_products,
                    *args,
                    **kwargs,
                )
            )

        if self.verbose:
            print("Produced: %s" % produced_products)
            biproducts = self.find_biproducts(produced_products)
            if biproducts:
                print("Bi-products: %s" % biproducts)

        return produced_products

    def find_biproducts(
        self, final_products: List[ProductBase]
    ) -> Iterable[ProductBase]:
        counter = {f: 0 for f in final_products}
        actual_products = []
        for producer_class in self.get_producers():
            actual_products.extend(producer_class.products)
            for product in final_products:
                if product.__class__ in producer_class.required_component:
                    counter[product] += 1

        return [
            p for p in counter if counter[p] == 0 and p.__class__ not in actual_products
        ]
