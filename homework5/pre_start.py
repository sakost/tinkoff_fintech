from app.db.init_db import init_db
from app.db.session import get_session


def main() -> None:
    Session = get_session()
    init_db(Session())


if __name__ == '__main__':
    main()
