from abc import ABC, abstractmethod
from collections import deque
from typing import Iterable, List, Type

GRAY, BLACK = 0, 1


class ComponentBase(ABC):
    """ """

    pass


class ProductBase(ABC):
    """ """


class ProducerBase(ABC):
    """ """

    required_components: List[ComponentBase]
    produced_components: List[ComponentBase]
    products: List[ProductBase]

    def __init__(self):
        """ """
        pass

    def _internal_produce(
        self, components: Iterable[ComponentBase], *args, **kwargs
    ) -> Iterable[ComponentBase]:
        self.validate_requirements(components)
        return self.produce(components, *args, **kwargs)

    @abstractmethod
    def produce(
        self, components: Iterable[ComponentBase], *args, **kwargs
    ) -> List[ComponentBase]:
        """ """
        pass

    def validate_requirements(
        self, produced_components: Iterable[ComponentBase]
    ) -> None:
        provided_classes = [p.__class__ for p in produced_components]
        missing_requirements = []
        for required in self.required_components:
            if required not in provided_classes:
                missing_requirements.append(required)
        if missing_requirements:
            raise RequirementNotMetException(self, missing_requirements)

    def can_produce(self) -> bool:
        return True

    def filter_components(
        self,
        available_components: Iterable[ComponentBase],
        target_class: Type[ComponentBase],
    ) -> Iterable[ComponentBase]:
        for component in available_components:
            if isinstance(component, target_class):
                yield component

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
        missing_requirements: List[ComponentBase],
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
            out_graph[producer] = producer.produced_components
            in_graph[producer] = producer.required_components

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

    def filter_components_for_producer(
        self, producer: ProducerBase, components: Iterable[ComponentBase]
    ) -> Iterable[ComponentBase]:
        for component in components:
            if component.__class__ in producer.required_components:
                yield component

    def start(self, *args, **kwargs):
        """ """
        produced_components = []
        for producer_class in self.get_producers():
            producer = producer_class()  # type: ignore
            if not producer.can_produce():
                continue

            produced_components.extend(
                producer._internal_produce(
                    produced_components,
                    *args,
                    **kwargs,
                )
            )

        if self.verbose:
            print("Produced: %s" % produced_components)
            bicomponents = self.find_biproducts(produced_components)
            if bicomponents:
                print("Bi-components: %s" % bicomponents)

        return produced_components

    def find_biproducts(
        self, final_components: List[ComponentBase]
    ) -> Iterable[ComponentBase]:
        counter = {f: 0 for f in final_components}
        actual_products = []
        for producer_class in self.get_producers():

            if hasattr(producer_class, "products"):
                actual_products.extend(producer_class.products)

            for product in final_components:
                if product.__class__ in producer_class.required_components:
                    counter[product] += 1

        return [
            p for p in counter if counter[p] == 0 and p.__class__ not in actual_products
        ]
