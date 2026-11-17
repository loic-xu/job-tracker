import os

import pandas as pd
import pytest

from server.csv_repository import CandidatureRepository
from server.exceptions import CSVLockedError


@pytest.fixture
def repo(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,company,title,type,application_date,status,notes,link\n")
    os.environ["CSV_PATH"] = str(csv_file)
    return CandidatureRepository()


@pytest.fixture
def sample_data():
    return {
        "company": "Google",
        "title": "SWE",
        "type": "CDI",
        "application_date": "2026-08-06",
        "status": "Applied",
        "notes": "",
        "link": "https://google.com/careers",
    }


@pytest.fixture
def filled_repo(repo, sample_data):
    repo.add(sample_data)
    return repo


def test_get_all_empty(repo):
    assert repo.get_all() == []


def test_get_next_id_empty(repo):
    assert repo.get_next_id() == 1


def test_get_next_id_with_data(filled_repo):
    assert filled_repo.get_next_id() == 2


def test_add(repo, sample_data):
    result = repo.add(sample_data)
    assert result["id"] == 1
    assert result["company"] == "Google"

    rows = repo.get_all()
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["company"] == "Google"
    assert rows[0]["title"] == "SWE"
    assert rows[0]["type"] == "CDI"
    assert rows[0]["application_date"] == "2026-08-06"
    assert rows[0]["status"] == "Applied"
    assert rows[0]["notes"] == ""
    assert rows[0]["link"] == "https://google.com/careers"


def test_update(filled_repo):
    result = filled_repo.update(
        app_id=1, fields={"company": "AWS", "status": "To apply"}
    )
    assert result["id"] == 1
    assert result["company"] == "AWS"
    assert result["status"] == "To apply"

    rows = filled_repo.get_all()
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["company"] == "AWS"
    assert rows[0]["title"] == "SWE"
    assert rows[0]["type"] == "CDI"
    assert rows[0]["application_date"] == "2026-08-06"
    assert rows[0]["status"] == "To apply"
    assert rows[0]["notes"] == ""
    assert rows[0]["link"] == "https://google.com/careers"


def test_update_not_found(filled_repo):
    result = filled_repo.update(
        app_id=3, fields={"company": "AWS", "status": "To apply"}
    )
    assert result is None


def test_delete(filled_repo):
    assert filled_repo.delete(app_id=1)
    assert filled_repo.get_all() == []


def test_delete_not_found(filled_repo):
    assert not filled_repo.delete(app_id=8)
    assert len(filled_repo.get_all()) == 1


def test_get_stats(filled_repo):
    res = filled_repo.get_stats()
    assert res["total"] == 1
    assert res["by_status"]["Applied"] == 1


def test_csv_locked_error(repo, monkeypatch):
    def mock_read_csv(*args, **kwargs):
        raise PermissionError("Simulated locked file")

    monkeypatch.setattr(pd, "read_csv", mock_read_csv)
    with pytest.raises(CSVLockedError):
        repo.get_all()
