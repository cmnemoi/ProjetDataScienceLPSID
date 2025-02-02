"""
We"re building the ML production pipeline in this script.
"""

# Imports
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, FunctionTransformer
from sklearn.pipeline import Pipeline, make_pipeline

from joblib import dump

np.random.seed(0)


# Fonctions
def import_dataset() -> tuple:
    """Import dataset, get only relevant variables and returns it in a (X,y) `tuple`.
    X and Y are `pandas.DataFrame`.
    """
    dataset = pd.read_csv("data/explored_dataset.csv").dropna()
    X = dataset.drop(
        [
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "store_and_fwd_flag",
            "PULocationID",
            "DOLocationID",
            "total_amount",
        ],
        axis=1,
    )
    y = dataset[["total_amount"]]

    return X, y


def trim(column: pd.Series) -> np.array:
    """Return a pandas.Series in which each value above 99e centile is trimmed at 99e centile"""
    quantile = column.quantile(q=0.99)[0]
    return np.array(
        [quantile if x[0] > quantile else x for x in column.values], dtype="object"
    ).reshape(-1, 1)


def fit_model(model, X, y) -> Pipeline:
    """Fit the given model to the (X,y) given as arguments ( (X_train, y_train) by default)
    Returns a sklearn.Pipeline object"""

    discrete_variables = [
        "VendorID",
        "passenger_count",
        "PULocationLabel",
        "DOLocationLabel",
        "payment_type",
        "day",
        "hour",
        "is_night_trip",
        "airport_trip",
        "is_sunday",
    ]
    quantitative_variables = ["trip_distance"]

    # columns need to be in the same order than column transformers to be properly transformed, wtf ?
    X = X[
        [
            "VendorID",
            "passenger_count",
            "PULocationLabel",
            "DOLocationLabel",
            "payment_type",
            "day",
            "hour",
            "is_night_trip",
            "airport_trip",
            "is_sunday",
            "trip_distance",
        ]
    ]

    cat_encoders = [
        (
            OrdinalEncoder(
                categories=[np.unique(X[column]).tolist()],
                handle_unknown="use_encoded_value",
                unknown_value=265,
                dtype=int,
            ),
            [column],
        )
        for column in discrete_variables
    ]

    numeric_transformer = (
        make_pipeline(FunctionTransformer(trim), StandardScaler()),
        quantitative_variables,
    )

    preprocessor = make_column_transformer(
        cat_encoders[0],
        cat_encoders[1],
        cat_encoders[2],
        cat_encoders[3],
        cat_encoders[4],
        cat_encoders[5],
        cat_encoders[6],
        cat_encoders[7],
        cat_encoders[8],
        cat_encoders[9],
        numeric_transformer,
    )

    model = make_pipeline(preprocessor, model)

    model = model.fit(X, y)

    return model


if __name__ == "__main__":
    print("Importing dataset...")
    X, y = import_dataset()
    print("Dataset imported")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=0
    )

    print("Training model...")
    pipeline = fit_model(LinearRegression(), X_train, y_train)
    print("Model trained.")

    print("Saving model...")
    dump(pipeline, filename="models/linear_regression_model.joblib")
    print("Model saved.")
