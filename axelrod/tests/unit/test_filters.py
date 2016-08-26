import unittest
from axelrod.strategies._filters import *
from axelrod import filtered_strategies
from hypothesis import given, example
from hypothesis.strategies import sampled_from, integers
import operator


class TestFilters(unittest.TestCase):

    class TestStrategy(object):
        classifier = {
            'stochastic': True,
            'inspects_source': False,
            'memory_depth': 10,
            'makes_use_of': ['game', 'length']
        }

    @given(
        truthy=sampled_from([True, 'True', 'true', '1', 'Yes', 'yes']),
        falsy=sampled_from([False, 'False', 'false', '0', 'No', 'no'])
    )
    @example(truthy=True, falsy=False)
    def test_boolean_filter(self, truthy, falsy):
        self.assertTrue(
            passes_boolean_filter(self.TestStrategy, 'stochastic', truthy))
        self.assertFalse(
            passes_boolean_filter(self.TestStrategy, 'stochastic', falsy))
        self.assertTrue(
            passes_boolean_filter(self.TestStrategy, 'inspects_source', falsy))
        self.assertFalse(
            passes_boolean_filter(self.TestStrategy, 'inspects_source', truthy))


    @given(
        smaller=integers(min_value=0, max_value=9),
        larger=integers(min_value=11, max_value=100),
    )
    @example(smaller='0', larger=float('inf'))
    def test_operator_filter(self, smaller, larger):
        self.assertTrue(passes_operator_filter(
            self.TestStrategy, 'memory_depth', smaller, operator.ge))
        self.assertTrue(passes_operator_filter(
            self.TestStrategy, 'memory_depth', larger, operator.le))
        self.assertFalse(passes_operator_filter(
            self.TestStrategy, 'memory_depth', smaller, operator.le))
        self.assertFalse(passes_operator_filter(
            self.TestStrategy, 'memory_depth', larger, operator.ge))


    def test_list_filter(self):
        self.assertTrue(passes_in_list_filter(
            self.TestStrategy, 'makes_use_of', 'game'))
        self.assertTrue(passes_in_list_filter(
            self.TestStrategy, 'makes_use_of', 'length'))
        self.assertFalse(passes_in_list_filter(
            self.TestStrategy, 'makes_use_of', 'test'))

    @given(
        truthy=sampled_from([True, 'True', 'true', '1', 'Yes', 'yes']),
        falsy=sampled_from([False, 'False', 'false', '0', 'No', 'no']),
        smaller=integers(min_value=0, max_value=9),
        larger=integers(min_value=11, max_value=100),
    )
    @example(truthy=True, falsy=False, smaller='2', larger=float('inf'))
    def test_passes_filterset(self, truthy, falsy, smaller, larger):

        full_passing_filterset = {
            'stochastic': truthy,
            'inspects_source': falsy,
            'min_memory_depth': smaller,
            'max_memory_depth': larger,
            'makes_use_of': 'length'
        }

        sparse_passing_filterset = {
            'stochastic': truthy,
            'inspects_source': falsy,
            'makes_use_of': 'length'
        }

        full_failing_filterset = {
            'stochastic': falsy,
            'inspects_source': falsy,
            'min_memory_depth': smaller,
            'max_memory_depth': larger,
            'makes_use_of': 'length'
        }

        sparse_failing_filterset = {
            'stochastic': falsy,
            'inspects_source': falsy,
            'min_memory_depth': smaller,
        }

        self.assertTrue(passes_filterset(
            self.TestStrategy, full_passing_filterset))
        self.assertTrue(passes_filterset(
            self.TestStrategy, sparse_passing_filterset))
        self.assertFalse(passes_filterset(
            self.TestStrategy, full_failing_filterset))
        self.assertFalse(passes_filterset(
            self.TestStrategy, sparse_failing_filterset))

    def test_filtered_strategies(self):

        class StochasticTestStrategy(object):
            classifier = {
                'stochastic': True,
                'memory_depth': float('inf'),
                'makes_use_of': []
            }

        class MemoryDepth2TestStrategy(object):
            classifier = {
                'stochastic': False,
                'memory_depth': 2,
                'makes_use_of': []
            }

        class UsesLengthTestStrategy(object):
            classifier = {
                'stochastic': True,
                'memory_depth': float('inf'),
                'makes_use_of': ['length']
            }

        strategies = [
            StochasticTestStrategy,
            MemoryDepth2TestStrategy,
            UsesLengthTestStrategy
        ]

        stochastic_filterset = {
            'stochastic': True
        }

        deterministic_filterset = {
            'stochastic': False
        }

        uses_length_filterset = {
            'stochastic': True,
            'makes_use_of': 'length'
        }

        self.assertEqual(
            filtered_strategies(stochastic_filterset, strategies),
            [StochasticTestStrategy, UsesLengthTestStrategy])
        self.assertEqual(
            filtered_strategies(deterministic_filterset, strategies),
            [MemoryDepth2TestStrategy])
        self.assertEqual(
            filtered_strategies(uses_length_filterset, strategies),
            [UsesLengthTestStrategy])