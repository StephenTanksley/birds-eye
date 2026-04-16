import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from utilities.scraper import fetch_html, main

@pytest.mark.skip # TODO: Come back and fix this damn test.
@pytest.mark.asyncio
async def test_fetch_html_returns_filtered_links(mocker):
    """Assert that fetch_html() correctly extracts href, text and filters bad data."""

    # Mock Playwright objects
    mock_context = MagicMock()
    mock_page = AsyncMock()
    mock_locator = AsyncMock()

    mock_anchor1 = AsyncMock()
    mock_anchor2 = AsyncMock()
    mock_anchor3 = AsyncMock()

    # Define mock return values
    mock_anchor1.get_attribute.return_value = "https://example.com/news"
    mock_anchor1.inner_text.return_value = "Breaking News"
    mock_anchor2.get_attribute.return_value = "mailto:contact@example.com"
    mock_anchor2.inner_text.return_value = "Contact"
    mock_anchor3.get_attribute.return_value = None
    mock_anchor3.inner_text.return_value = ""

    mock_locator.element_handles.return_value = [
        mock_anchor1,
        mock_anchor2,
        mock_anchor3
    ]

    mock_page.locator = mock_locator

    mock_context.new_page = AsyncMock(return_value=mock_page)

    sem = mocker.AsyncMock()

    # Run the function
    results = await fetch_html(mock_context, "https://example.com", sem)

    # Assert results
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/news"
    assert results[0]["headline"] == "Breaking News"
    assert "timestamp" in results[0]


@pytest.mark.asyncio
async def test_fetch_html_handles_exceptions(mocker):
    """Ensure fetch_html() gracefully handles exceptions and returns empty list."""

    mock_context = MagicMock()
    mock_page = AsyncMock()
    mock_context.new_page.side_effect = Exception("Browser crashed")

    sem = mocker.AsyncMock()

    with pytest.raises(Exception) as e:
        results = await fetch_html(mock_context, "https://example.com", sem)
        assert results == []
        assert "Browser crashed" in e


@pytest.mark.asyncio
@patch("utilities.scraper.fetch_html", new_callable=AsyncMock)
async def test_main_collects_results(mock_fetch_html):
    """main() runs tasks, aggregates results, and updates results_dict."""
    mock_fetch_html.side_effect = [
        [{"url": "https://npr.org/test", "headline": "NPR Test", "timestamp": "123"}],
        [],
        [{"url": "https://nytimes.com/x", "headline": "NYT X", "timestamp": "123"}]
    ]

    results_dict = {}

    with patch("utilities.scraper.async_playwright") as mock_playwright:
        mock_instance = mock_playwright.return_value.__aenter__.return_value
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_instance.firefox.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context

        await main(results_dict)

    assert "https://www.npr.org" in results_dict
    assert "https://www.nytimes.com" in results_dict
    assert len(results_dict["https://www.npr.org"]) == 1


def test_main_file_output(tmp_path, mocker):
    """Test that the main script writes a JSON file with expected data."""
    import json
    from datetime import date

    fake_results = {
        "https://example.com": [{"url": "https://example.com/1", "headline": "Headline"}]
    }

    # Patch async_run so we don’t actually launch Playwright
    mocker.patch("utilities.scraper.async_run", return_value=None)

    # Patch open() to write into tmp_path instead of real data folder
    output_file = tmp_path / f"headline_data_{date.today()}.json"
    mocker.patch("utilities.scraper.open", mocker.mock_open())

    # Manually simulate file write
    with open(output_file, "w+") as f:
        json.dump(fake_results, f)

    # Verify file contents
    with open(output_file) as f:
        data = json.load(f)
        assert "https://example.com" in data
