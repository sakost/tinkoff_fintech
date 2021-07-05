import concurrent.futures
from unittest import mock

from app import main


@mock.patch('app.main.scrape_concurrent')
@mock.patch('concurrent.futures.ThreadPoolExecutor')
def test_main(executor_patched: mock.Mock, scrape_concurrent_patched: mock.Mock):
    scrape_concurrent_patched.return_value = ['content1', 'content2']
    executor_patched.return_value = mock.MagicMock(spec=concurrent.futures.Executor)
    with mock.patch('app.main.export_content') as export_patched:
        future = concurrent.futures.Future()  # type: ignore[var-annotated]
        future.set_result('some result')
        export_patched.return_value = [future]
        main.main(26, 1)
        assert export_patched.call_count == 2

    assert executor_patched.call_count == 1
    assert scrape_concurrent_patched.call_count == 1
