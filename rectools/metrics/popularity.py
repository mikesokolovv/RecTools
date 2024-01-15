#  Copyright 2024 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Popularity metrics."""

import typing as tp
from collections import Counter

import attr
import pandas as pd

from rectools import Columns
from rectools.metrics.base import MetricAtK
from rectools.utils import select_by_type


@attr.s
class ARP(MetricAtK):
    r"""
    Average Recommendations Popularity metric.

    Calculate the average popularity of the recommended items in each list,
    where "popularity" of item is the average number of ratings (interactions)
    for this item.

    .. math::
        ARP@k = \frac{1}{\left|U_{t}\right|}\sum_{u\in U_{t}^{}}\frac{\sum_{i\in L_{u}}\phi (i)}{\left | L_{u} \right |}

    where
    :math:`\phi (i)` is the number of times item i has been rated in the training set.
    :math:`|U_{t}|` is the number of users in the test set.
    :math:`L_{u}` is the list of recommended items for user u.

    Parameters
    ----------
    k : int
        Number of items at the top of recommendations list that will be used to calculate metric.

    Examples
    --------
    >>> reco = pd.DataFrame(
    ...     {
    ...         Columns.User: [1, 1, 2, 2, 2, 3, 3],
    ...         Columns.Item: [1, 2, 3, 1, 2, 3, 2],
    ...         Columns.Rank: [1, 2, 1, 2, 3, 1, 2],
    ...     }
    ... )
    >>> prev_interactions = pd.DataFrame(
    ...     {
    ...         Columns.User: [1, 1, 2, 2, 3, 3],
    ...         Columns.Item: [1, 2, 1, 3, 1, 2],
    ...     }
    ... )
    >>> ARP(k=1).calc_per_user(reco, prev_interactions).values
    array([3., 1., 1.])
    >>> ARP(k=3).calc_per_user(reco, prev_interactions).values
    array([2.5, 2. , 1.5])
    """

    def calc(self, reco: pd.DataFrame, prev_interactions: pd.DataFrame) -> float:
        """
        Calculate metric value.

        Parameters
        ----------
        reco : pd.DataFrame
            Recommendations table with columns `Columns.User`, `Columns.Item`, `Columns.Rank`.
        prev_interactions : pd.DataFrame
            Table with previous user-item interactions,
            with columns `Columns.User`, `Columns.Item`.

        Returns
        -------
        float
            Value of metric (average between users).
        """
        per_user = self.calc_per_user(reco, prev_interactions)
        return per_user.mean()

    def calc_per_user(
        self,
        reco: pd.DataFrame,
        prev_interactions: pd.DataFrame,
    ) -> pd.Series:
        """
        Calculate metric values for all users.

        Parameters
        ----------
        reco : pd.DataFrame
            Recommendations table with columns `Columns.User`, `Columns.Item`, `Columns.Rank`.
        prev_interactions : pd.DataFrame
            Table with previous user-item interactions,
            with columns `Columns.User`, `Columns.Item`.

        Returns
        -------
        pd.Series
            Values of metric (index - user id, values - metric value for every user).
        """
        pop_items = self.get_pop(prev_interactions)
        arp = reco.groupby(Columns.User).apply(
            lambda x: sum(pop_items[i] for i in x[Columns.Item][: self.k]) / len(x[Columns.Item][: self.k])
        )
        return arp

    def get_pop(self, prev_interactions: pd.DataFrame) -> tp.Dict[int, int]:
        """
        Calculate rating for each item in train set.

        Parameters
        ----------
        prev_interactions : pd.DataFrame
            Table with previous user-item interactions,
            with columns `Columns.User`, `Columns.Item`.

        Returns
        -------
        dict(int->int)
            Set with items' popularity rating (key - item id, value - number of interactions with item in training set).
        """
        return Counter(prev_interactions[Columns.Item])


PopularityMetric = ARP


def calc_popularity_metrics(
    metrics: tp.Dict[str, PopularityMetric],
    reco: pd.DataFrame,
    prev_interactions: pd.DataFrame,
) -> tp.Dict[str, float]:
    """
    Calculate popularity metrics (only AvgRP now).

    Warning: It is not recommended to use this function directly.
    Use `calc_metrics` instead.

    Parameters
    ----------
    metrics : dict(str -> PopularityMetric)
        Dict of metric objects to calculate,
        where key is metric name and value is metric object.
    reco : pd.DataFrame
        Recommendations table with columns `Columns.User`, `Columns.Item`, `Columns.Rank`.
    prev_interactions : pd.DataFrame
        Table with previous user-item interactions,
        with columns `Columns.User`, `Columns.Item`.

    Returns
    -------
    dict(str->float)
        Dictionary where keys are the same as keys in `metrics`
        and values are metric calculation results.
    """
    results = {}

    # ARP
    pop_metrics: tp.Dict[str, ARP] = select_by_type(metrics, ARP)
    if pop_metrics:
        for name, metric in pop_metrics.items():
            results[name] = metric.calc(reco, prev_interactions)

    return results