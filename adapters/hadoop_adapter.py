import os
import subprocess


class HadoopAdapter:
    """
    Benchmarks HDFS operations via docker exec into the namenode container.
    Container name matches docker-compose: psb_namenode

    Operations:
      insert_data  — copy local file into HDFS  (docker cp + hdfs dfs -put)
      read_data    — cat first 4 KB from HDFS file
      update_data  — re-upload file with a header line added (simulate in-place update)
      delete_data  — remove HDFS directory
      run_query    — count files/bytes in HDFS directory (hdfs dfs -count)
    """

    def __init__(self, namenode_container="psb_namenode", hdfs_base_path="/benchmark"):
        self.namenode_container = namenode_container
        self.hdfs_base_path = hdfs_base_path
        self.dataset_path = None

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _docker_exec(self, *cmd, check=True, capture=False):
        """Run a command inside the namenode container."""
        full_cmd = ["docker", "exec", self.namenode_container] + list(cmd)
        return subprocess.run(
            full_cmd,
            check=check,
            capture_output=capture,
            text=True
        )

    def _copy_to_container(self, local_path, container_path):
        """docker cp local file → container."""
        subprocess.run(
            ["docker", "cp", local_path, f"{self.namenode_container}:{container_path}"],
            check=True
        )

    # ------------------------------------------------------------------ #
    #  Benchmark interface                                                 #
    # ------------------------------------------------------------------ #

    def load_data(self, dataset_path):
        self.dataset_path = dataset_path

    def insert_data(self):
        """Upload dataset to HDFS (overwrite if exists)."""
        if not self.dataset_path:
            raise ValueError("No dataset loaded for Hadoop.")

        filename = os.path.basename(self.dataset_path)
        container_tmp = f"/tmp/{filename}"

        # Copy file to namenode container
        self._copy_to_container(self.dataset_path, container_tmp)

        # Create HDFS directory
        self._docker_exec("hdfs", "dfs", "-mkdir", "-p", self.hdfs_base_path)

        # Upload to HDFS (overwrite)
        self._docker_exec(
            "hdfs", "dfs", "-put", "-f",
            container_tmp, f"{self.hdfs_base_path}/{filename}"
        )

    def read_data(self):
        """Read first 4 KB from all HDFS files in the benchmark directory."""
        result = self._docker_exec(
            "hdfs", "dfs", "-cat", f"{self.hdfs_base_path}/*",
            check=False, capture=True
        )
        return result.stdout[:4096]

    def update_data(self):
        """
        Simulate UPDATE: re-upload the same dataset to HDFS.
        HDFS is append-only / immutable — overwrite is the standard 'update' pattern.
        """
        self.insert_data()

    def delete_data(self):
        """Remove the entire benchmark HDFS directory."""
        self._docker_exec(
            "hdfs", "dfs", "-rm", "-r", "-f",
            self.hdfs_base_path,
            check=False
        )

    def run_query(self):
        """
        Aggregation proxy: count files and bytes in the HDFS directory.
        Returns the raw 'hdfs dfs -count' output.
        """
        result = self._docker_exec(
            "hdfs", "dfs", "-count", self.hdfs_base_path,
            capture=True, check=False
        )
        return result.stdout

    def close(self):
        """No persistent connection — nothing to close."""
        pass