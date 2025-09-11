from model.train import get_csvs_df
import os
import pytest


def test_csvs_no_files():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("./")
    assert error.match("No CSV files found in provided data")


def test_csvs_no_files_invalid_path():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("/invalid/path/does/not/exist/")
    assert error.match("Cannot use non-existent path provided")


def test_csvs_creates_dataframe():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    datasets_directory = os.path.join(current_directory, 'datasets')
    result = get_csvs_df(datasets_directory)
    assert len(result) == 20


def test_github_actions_environment():
    """
    This test will intentionally fail in GitHub Actions to test branch protection.
    It checks if we're running in GitHub Actions environment.
    """
    import os
    
    # Check if running in GitHub Actions
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    if is_github_actions:
        # Intentionally fail in GitHub Actions
        assert False, "This test intentionally fails in GitHub Actions to test branch protection rules"
    else:
        # Pass locally
        assert True, "This test passes locally"