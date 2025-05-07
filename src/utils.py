import json
import logging
from logging import Logger
from pathlib import Path
from typing import Any

import pandas as pd


def setup_logging() -> Logger:
    """
    функция, которая настраивает логирование.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(module)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("logs.log", mode="w")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


def read_files(file_path: Any) -> Any:
    """открытие файла '.xls'"""
    if Path(file_path).suffix.lower() == ".xlsx":
        df = pd.read_excel(file_path)
        return df.to_dict(orient="records")
    elif Path(file_path).suffix.lower() == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("Неверный формат файла")


def write_data(file_: str, results: Any) -> None:
    """
    функция, которая записывает результаты в указанный файл.
    """
    try:
        if file_.endswith(".txt"):
            with open(file_, "a") as file:
                file.write(results)
        else:
            with open(file_, "w", encoding="utf8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка :{e}")
