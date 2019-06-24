from bdc_sample.core.driver import CSVDriver
from datetime import datetime
import os

class InSitu(CSVDriver):
    """
    Driver for InSitu Sample for data loading to `sampledb`

    This class is an abstraction of repository https://github.com/e-sensing/inSitu.git

    **Make sure** you have `R` in PATH. You can download `R` in https://cran.r-project.org/
    """
    def __init__(self, directory, storager, user, system):
        """
        Create InSitu Samples data handlers
        :param directory: string Directory where converted files will be stored
        :param storager: PostgisAccessor
        """
        super().__init__(directory, storager, user, system)

        storager.open()

    def get_unique_classes(self, csv):
        return csv['label'].unique()

    def build_data_set(self, csv):
        csv['srid'] = 4326
        csv['class_id'] = csv['label'].apply(lambda row: self.storager.samples_map_id[row])
        csv['user_id'] = 1
        csv['lat'] = csv['latitude']
        csv['long'] = csv['longitude']
        return csv

    def load_data_sets(self):
        """
        Load data sets in memory using database format.
        Calls `R` script to generate CSV sample data set. After that,
        process the `CSV` files to the storager handler
        """

        # Read data sets (.rda) from R to CSV
        InSitu.generate_data_sets(self.directory)

        return super().load_data_sets()

    @classmethod
    def generate_data_sets(cls, directory):
        """
        Generates sample from inSitu package in R. It will generate `.csv` files
        inside the provided in this object creation.

        Make sure you have R installed on PATH.
        This function tries to install inSitu dependencies with the following commands:

        ```R
        install.packages("devtools")
        devtools::install_github("e-sensing/inSitu")
        install.packages("dplyr")
        ```

        After that, execute R functions to load `.rda` files and export to CSV
        """
        import subprocess
        from pathlib import Path

        scripts_directory = Path(__file__).parent.parent.parent / 'share/bdc_sample/scripts/'

        export_to_csv_script = scripts_directory / 'export-inSitu-samples-csv.R'
        install_dependencies_script = scripts_directory / 'install-inSitu.R'

        if not os.path.exists(directory):
            os.mkdir(directory)

        # Install dependencies
        subprocess.call('R --silent -f {}'.format(install_dependencies_script), shell=True)

        rcommands = 'R --silent -f {} --args {}'.format(export_to_csv_script, directory)
        # Execute script to generate Sample CSV data
        subprocess.call(rcommands, shell=True)