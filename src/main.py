from src.reports import reports_
from src.services import servies_
from src.utils import setup_logging
from src.views import views_

logger = setup_logging()


def main() -> None:
    """
    отвечает за основную логику проекта с пользователем и связывает функциональности между собой.
    """
    views_()
    servies_()
    reports_()


if __name__ == "__main__":
    main()