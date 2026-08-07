from pathlib import Path
import pandas as pd
import os
import logging
from dotenv import load_dotenv
from exceptions import CSVLockedError

logger = logging.getLogger(__name__)
load_dotenv()


class CandidatureRepository:
    """Repository handling job applications persistence in a CSV file."""

    def __init__(self, csv_path: str | None = None):
        self.csv_path = csv_path or self._get_csv_path()

    def _get_csv_path(self) -> Path:
        csv_path = os.getenv("CSV_PATH")
        if csv_path is None:
            raise ValueError("CSV_PATH environment variable is not set.")
        return Path(csv_path)

    def _read_df(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.csv_path, keep_default_na=False)
            if not df.empty and "id" in df.columns:
                df["id"] = df["id"].astype(int)
            return df
        except PermissionError as e:
            logger.error(f"Failed to read CSV file at {self.csv_path}: {e}")
            raise CSVLockedError(
                "The CSV file is already opened by another application."
            )

    def _write_df(self, df: pd.DataFrame) -> None:
        try:
            df.to_csv(self.csv_path, index=False, encoding="utf-8-sig")
        except PermissionError as e:
            logger.error(f"Failed to write to CSV file at {self.csv_path}: {e}")
            raise CSVLockedError(
                "The CSV file is already opened by another application."
            )

    def get_all(self) -> list[dict]:
        """Retrieve all job applications from the CSV file as a list of dictionaries."""
        return self._read_df().to_dict(orient="records")

    def get_next_id(self) -> int:
        """Calculate the next available integer ID for a new job application."""
        df = self._read_df()
        if df.empty:
            return 1
        return int(df["id"].max() + 1)

    def add(self, data: dict) -> dict:
        """
        Add a new job application to the CSV file with an auto-generated ID.
        Args:
            data (dict): Application fields without the ID.
        Returns:
            dict: The newly created application containing its assigned ID.
        """
        id = self.get_next_id()
        df = self._read_df()
        new_data = pd.DataFrame([data])
        new_data["id"] = id
        new_df = pd.concat([df, new_data], axis=0)
        self._write_df(new_df)
        return new_data.to_dict(orient="records")[0]

    def update(self, app_id: int, fields: dict) -> dict | None:
        """
        Update specific fields of an existing job application by ID.
        Args:
            app_id (int): Target application ID.
            fields (dict): Key-value pairs of fields to update.
        Returns:
            dict | None: The updated application dict if found, None otherwise.
        """
        df = self._read_df()
        if app_id not in df["id"].values:
            return None

        for key, value in fields.items():
            df.loc[df["id"] == app_id, key] = value

        self._write_df(df)
        return df[df["id"] == app_id].iloc[0].to_dict()

    def delete(self, app_id: int) -> bool:
        """
        Delete a job application from the CSV file by ID.
        Args:
            app_id (int): Target application ID.
        Returns:
            bool: True if the record was found and deleted, False otherwise.
        """
        df = self._read_df()
        if app_id not in df["id"].values:
            return False
        df = df[df["id"] != app_id]
        self._write_df(df)
        return True

    def get_stats(self) -> dict:
        """
        Compute statistics on job applications (total count and status breakdown).
        Returns:
            dict: Statistics dictionary containing 'total' and 'by_status' keys.
        """
        df = self._read_df()
        total = len(df)
        return {"total": total, "by_status": df["status"].value_counts().to_dict()}
