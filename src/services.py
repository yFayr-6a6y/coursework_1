from typing import Any, List, Dict

from src.utils import setup_logging, write_data, read_files

logger = setup_logging()


def filter_state(operations: List[Dict[Any, Any]], search_query: str) -> List[Dict[Any, Any]]:
    """
    Фильтрует операции по строке поиска в полях 'Категория' или 'Описание'.

    Args:
        operations: Список словарей с данными транзакций.
        search_query: Строка для поиска (регистронезависимая).

    Returns:
        Список отфильтрованных операций.
    """
    if not operations or not search_query:
        logger.info("Операции или строка поиска отсутствуют")
        return []

    result = []
    search_query = search_query.lower()  # Приводим к нижнему регистру для регистронезависимого поиска

    for operation in operations:
        category = operation.get("Категория", "").lower()
        description = operation.get("Описание", "").lower()
        # Проверяем, содержится ли строка поиска в категории или описании
        if type(operation.get("Категория")) != float and type(operation.get("Описание")) != float:
            if search_query in category or search_query in description:
                result.append(operation)

    logger.info("Результат 'filter_state' для запроса '%s' - %s операций" % (search_query, len(result)))
    write_data("services.json", result)  # Исправлено имя файла
    return result

def servies_() -> None:
    """
    Запрашивает строку поиска и выводит отфильтрованные операции из Excel-файла.
    """
    search_query = input("Введите строку поиска (например, 'Переводы'): ")
    operations = read_files("../data/operations.xlsx")  # Загружаем данные из Excel
    filtered_operations = filter_state(operations, search_query)
    print(f"\nСервисы: {filtered_operations}")
