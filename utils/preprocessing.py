import pandas as pd
import numpy as np



def clean_velocity_column(df, column_name):
    """
    Remove unidades 'km/h' e converte a coluna para float.
    """
    if column_name not in df.columns:
        return df

    df = df.copy()

    df[column_name] = (
        df[column_name]
        .astype(str)
        .str.replace("km/h", "", regex=False)
        .str.strip()
        .replace("", np.nan)
        .astype(float)
    )

    return df



def preprocess_data(df):
    """
    Aplica todas as etapas de limpeza necessárias ao dataset.
    """
    df = clean_velocity_column(df, "Velocidade")
    return df