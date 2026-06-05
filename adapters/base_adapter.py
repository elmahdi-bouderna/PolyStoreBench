from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """
    Abstract base class for all PolyStoreBench adapters.
    Every adapter must implement the five core CRUD operations.
    run_query() and close() have default no-op implementations.
    """

    @abstractmethod
    def load_data(self, dataset_path: str) -> None:
        """Load dataset from disk into the adapter (no actual DB write yet)."""

    @abstractmethod
    def insert_data(self) -> None:
        """Write the loaded dataset into the target system."""

    @abstractmethod
    def read_data(self):
        """Read a representative sample (up to 100 records) from the system."""

    @abstractmethod
    def update_data(self) -> None:
        """Perform an update operation on the stored data."""

    @abstractmethod
    def delete_data(self) -> None:
        """Delete / purge data from the target system."""

    def run_query(self):
        """Execute an analytical query (optional — adapters may override)."""
        return None

    def close(self) -> None:
        """Release any open connections (optional — adapters should override)."""