from unittest.mock import Mock

import pytest

import web_scraping


@pytest.fixture
def drivers(monkeypatch):
    monkeypatch.delenv('CHROME_DRIVER_PATH', raising=False)
    monkeypatch.delenv('EDGE_DRIVER_PATH', raising=False)
    chrome = Mock()
    edge = Mock()
    monkeypatch.setattr(web_scraping.webdriver, 'Chrome', chrome)
    monkeypatch.setattr(web_scraping.webdriver, 'Edge', edge)
    return chrome, edge


@pytest.mark.parametrize('os_name,browser,expected', [
    ('Windows_NT', '', 'edge'),
    ('Windows_NT', 'chrome', 'chrome'),
    ('Linux', '', 'chrome'),
    ('Linux', 'chrome', 'chrome'),
    ('Linux', 'edge', 'edge'),
])
def test_automatic_driver_selection(monkeypatch, drivers, os_name, browser, expected):
    monkeypatch.setattr(web_scraping, 'OS_NAME', os_name)
    chrome, edge = drivers
    selected, other = (edge, chrome) if expected == 'edge' else (chrome, edge)

    driver = web_scraping.build_driver(browser=browser, headless=False)

    assert driver is selected.return_value
    other.assert_not_called()
    kwargs = selected.call_args.kwargs
    assert not kwargs['service'].path  # Selenium Manager resolves the executable.
    assert '--headless' not in kwargs['options'].arguments


@pytest.mark.parametrize('browser,path_variable', [
    ('chrome', 'CHROME_DRIVER_PATH'),
    ('edge', 'EDGE_DRIVER_PATH'),
])
def test_local_driver_bypasses_download(monkeypatch, tmp_path, drivers, browser, path_variable):
    driver_file = tmp_path / 'driver.exe'
    driver_file.touch()
    monkeypatch.setenv(path_variable, str(driver_file))
    chrome, edge = drivers
    selected = edge if browser == 'edge' else chrome

    driver = web_scraping.build_driver(link='https://example.com', browser=browser)

    kwargs = selected.call_args.kwargs
    assert kwargs['service'].path == str(driver_file)
    assert '--headless' in kwargs['options'].arguments
    driver.get.assert_called_once_with('https://example.com')


def test_missing_local_driver_fails_before_startup(monkeypatch, tmp_path, drivers):
    monkeypatch.setenv('CHROME_DRIVER_PATH', str(tmp_path / 'missing.exe'))

    with pytest.raises(FileNotFoundError, match='WebDriver executable does not exist'):
        web_scraping.build_driver(browser='chrome')

    for driver in drivers:
        driver.assert_not_called()


def test_startup_failure_preserves_original_error(drivers, capsys):
    chrome, _ = drivers
    error = RuntimeError('Unable to obtain driver')
    chrome.side_effect = error

    with pytest.raises(RuntimeError) as raised:
        web_scraping.build_driver(browser='chrome')

    assert raised.value is error
    assert 'CHROME_DRIVER_PATH' in capsys.readouterr().out
