from river import metrics, tree
from river.base.typing import FeatureName


def test_river_aprende_patron_fraude_basico():
    model = tree.HoeffdingTreeClassifier(grace_period=5, delta=0.9, leaf_prediction="mc")
    metric = metrics.Accuracy()

    legit: list[tuple[dict[FeatureName, object], object]] = [
        ({"amount": amt, "distance": dist}, 0)
        for amt, dist in [
            (10.5, 2.0),
            (25.0, 5.1),
            (5.0, 1.0),
            (30.0, 8.0),
            (15.0, 3.5),
            (20.0, 4.0),
            (12.0, 2.5),
            (8.0, 1.5),
            (22.0, 6.0),
            (18.0, 4.5),
            (9.0, 2.0),
            (27.0, 7.0),
            (11.0, 3.0),
            (16.0, 3.8),
            (23.0, 5.5),
        ]
    ]

    fraud: list[tuple[dict[FeatureName, object], object]] = [
        ({"amount": amt, "distance": dist}, 1)
        for amt, dist in [
            (5000.0, 1500.0),
            (4500.0, 2000.0),
            (4800.0, 1800.0),
            (5100.0, 1600.0),
            (4700.0, 2100.0),
            (5200.0, 1700.0),
            (4900.0, 1900.0),
            (5300.0, 2200.0),
            (4600.0, 1550.0),
            (5400.0, 2300.0),
            (4850.0, 1850.0),
            (5050.0, 1650.0),
            (4750.0, 2050.0),
            (5150.0, 1750.0),
            (4950.0, 1950.0),
        ]
    ]

    # Interleave legit and fraud samples so the tree sees both classes early
    data_stream: list[tuple[dict[FeatureName, object], object]] = []
    for pair in zip(legit, fraud):
        data_stream.extend(pair)

    for x, y in data_stream:
        y_pred = model.predict_one(x)
        if y_pred is not None:
            metric.update(y, y_pred)
        model.learn_one(x, y)

    nueva_tx: dict[FeatureName, object] = {"amount": 4800.0, "distance": 1800.0}

    prediccion = model.predict_one(nueva_tx)

    assert prediccion in [0, 1]
    assert prediccion == 1
