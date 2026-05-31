import pandas as pd
import numpy as np


def clean_velocity_column(df, column_name):
    """
    Remove unidades 'km/h' e converte a coluna para float.
    Exemplo:
    '5 km/h' -> 5.0
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


def create_elapsed_time_column(df, column_name):
    """
    Converte a coluna de data/hora em uma variável numérica:
    Tempo decorrido em segundos desde o primeiro registro.

    Exemplo:
    23.03.2023 18:26:58 -> 0 segundos
    23.03.2023 18:27:03 -> 5 segundos
    """
    if column_name not in df.columns:
        return df

    df = df.copy()

    df[column_name] = pd.to_datetime(
        df[column_name],
        format="%d.%m.%Y %H:%M:%S",
        errors="coerce"
    )

    initial_time = df[column_name].min()

    df["Tempo_decorrido_segundos"] = (
        df[column_name] - initial_time
    ).dt.total_seconds()

    return df


def split_coordinates_column(df, column_name):
    """
    Divide a coluna de coordenadas em duas colunas numéricas:
    Latitude e Longitude.

    Exemplo:
    '-8.018291, -34.949880'

    Resultado:
    Latitude = -8.018291
    Longitude = -34.949880
    """
    if column_name not in df.columns:
        return df

    df = df.copy()

    coordinates = df[column_name].astype(str).str.split(",", expand=True)

    if coordinates.shape[1] >= 2:
        df["Latitude"] = pd.to_numeric(
            coordinates[0].str.strip(),
            errors="coerce"
        )

        df["Longitude"] = pd.to_numeric(
            coordinates[1].str.strip(),
            errors="coerce"
        )

    return df


def preprocess_data(df):
    """
    Aplica todas as etapas de limpeza necessárias ao dataset.
    """
    df = clean_velocity_column(df, "Velocidade")
    df = create_elapsed_time_column(df, "Hora")
    df = split_coordinates_column(df, "Coordenadas")

    return df