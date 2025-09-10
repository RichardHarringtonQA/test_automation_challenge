from robot.libraries.BuiltIn import BuiltIn

def verify_search_results(expected_text):
    # Get SeleniumLibrary instance to access browser
    selenium = BuiltIn().get_library_instance('SeleniumLibrary')
    # Get page source
    page_source = selenium.get_source()
    # Check if expected text appears in results
    if expected_text.lower() not in page_source.lower():
        raise AssertionError(f"Expected text '{expected_text}' not found in search results")