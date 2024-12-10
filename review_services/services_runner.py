"""This file contains class that runs all the services on a Colab file."""

import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from streamlit.delta_generator import DeltaGenerator

from review_services.autoreview_spelling_grammar import spell_grammar_autoreview
from review_services.colab import Colab
from review_services.sft_validator import sft_validator
from utils import Status, get_colabs, logger


class ServicesRunner:
    """This class runs all the services on provided Folder."""

    def __init__(self, folder_id: str, folder_name: str = "Root Folder"):
        """Initializes the ServicesRunner class.

        Parameters
        ----------
        folder_id : str
            Folder ID of the folder to run services on.

        folder_name : str, optional
            Folder name, by default "Root Folder"
        """
        self.__files: list[dict[str, str]] = get_colabs(folder_id, folder_name)
        self.__validators: dict[str, callable[[dict[str, str]], Colab]] = {
            "SFT Validator": sft_validator,
            "AutoReview Spelling and Grammar": spell_grammar_autoreview,
        }

    def run_services(
        self,
        services_progress_bar: DeltaGenerator,
        services_eta_placeholder: DeltaGenerator,
    ) -> tuple[pd.DataFrame, float]:
        """Runs all the services with parallel processing support.

        Parameters
        ----------
        services_progress_bar : DeltaGenerator
            Streamlit progress bar for services processing.

        services_eta_placeholder : DeltaGenerator
            Streamlit placeholder for services ETA.

        Returns
        -------
        tuple[pd.DataFrame, float]
            Tuple containing the final results and pass rate
        """
        # Total number of tasks
        total_files = len(self.__files)  # Total number of files
        total_tasks = total_files * len(self.__validators)
        if total_tasks == 0:
            logger.warning("No tasks to process. Exiting.")
            return [], 0.0

        results = []
        completed_tasks = 0

        # Start time
        start_time = time.time()

        # Run validators in parallel for each file
        with ThreadPoolExecutor() as executor:
            future_to_file = {
                executor.submit(validator, file): (file, validator_name)
                for file in self.__files
                for validator_name, validator in self.__validators.items()
            }

            for future in as_completed(future_to_file):
                file, validator_name = future_to_file[future]
                try:
                    result: Colab = future.result()
                    result.colab_res.update({"validator": validator_name})
                    # Collect the result
                    results.append(result.colab_res)
                    del result
                except Exception as e:
                    # Handle any exceptions during validation
                    error_details = traceback.format_exc()
                    logger.error(
                        f"[Running Validations] Error processing file {file['name']}"
                        f"with {validator_name}: {error_details}"
                    )
                    results.append(
                        {
                            "colab_name": file["name"],
                            "colab_url": None,
                            "validator": validator_name,
                            "errors": [[None, None, str(e)]],
                            "status": Status.FAILED,
                        }
                    )

                # Update progress and ETA
                completed_tasks += 1
                progress = completed_tasks / total_tasks

                # Update UI every 5 tasks to reduce overhead
                # if completed_tasks % 5 == 0:
                services_progress_bar.progress(progress)
                elapsed_time = time.time() - start_time
                avg_time_per_task = elapsed_time / completed_tasks
                remaining_time = avg_time_per_task * (total_tasks - completed_tasks)
                services_eta_placeholder.text(f"Estimated time remaining: {self.__format_time(remaining_time)}")

        # Clear the ETA placeholder and progress bar after completion
        self.__clear_placeholders(services_eta_placeholder, services_progress_bar)

        # Format the results
        results_df = self.__format_results(results)

        # Calculate pass rate
        pass_rate = results_df["Status"].value_counts(normalize=True).get("Passed", 0) * 100

        return results_df, pass_rate

    @staticmethod
    def __clear_placeholders(*placeholders: DeltaGenerator):
        """Clear the given Streamlit placeholders."""
        for placeholder in placeholders:
            placeholder.empty()

    def __format_results(self, results: list[dict[str, str]]) -> pd.DataFrame:
        """Format the results to be displayed in a table.

        Parameters
        ----------
        results : list[dict[str, str]]
            List of results.

        Returns
        -------
        pd.DataFrame
            Formatted results with final status.
        """
        formatted_results = []
        for result in results:
            row = {
                "Colab Name": result["colab_name"],
                "Colab URL": result["colab_url"],
                "Validator": result["validator"],
                "Status": result["status"],
            }

            if result.get("errors") is None:
                row["Turn Number"], row["Block Number"], row["Error"] = None, None, None
                formatted_results.append(row.copy())
                continue

            for error in result.get("errors", []):
                row["Turn Number"], row["Block Number"], row["Error"] = error
                formatted_results.append(row.copy())

        df = pd.DataFrame(formatted_results).sort_values(["Turn Number", "Block Number"], na_position="first")

        def aggregate_errors(group: pd.DataFrame) -> str:
            """Aggregates errors for a single group of Turn Numbers.

            Parameters
            ----------
            group : pd.DataFrame
                A group of rows for a specific Colab and Turn Number.

            Returns
            -------
            str
                Aggregated errors as a formatted string.
            """
            if group.empty:
                return None

            result = []
            for i, (_, row) in enumerate(group.iterrows(), start=1):
                if row["Error"] is None:
                    continue
                err_str = f"{i}. [{row['Validator']}] "
                if pd.notna(row["Block Number"]):
                    err_str += f"Block {int(row['Block Number'])}: "
                err_str += row["Error"]
                result.append(err_str)

            return "\n".join(result)

        def aggregate_colab(group: pd.DataFrame) -> pd.Series:
            """Aggregates errors and determines the final status for a Colab.

            Parameters
            ----------
            group : pd.DataFrame
                A group of rows for a specific Colab.

            Returns
            -------
            pd.Series
                Aggregated errors and the final status.
            """
            if group.empty:
                return pd.Series({"Errors": None, "Status": Status.PASSED})

            result = []
            for _, row in group.iterrows():
                if pd.isna(row["Turn Number"]):
                    err_str = row["Errors"]
                else:
                    err_str = f"Turn {int(row['Turn Number'])}:\n{row['Errors']}"
                result.append(err_str)

            result = [err for err in result if err != ""]
            errors = "\n".join(result)
            final_status = "Failed" if any(group["Status"] == Status.FAILED) else Status.PASSED
            return pd.Series({"Errors": errors, "Status": final_status})

        # Aggregate errors for each group of Turn Numbers
        grouped_df = (
            df.groupby(["Colab Name", "Colab URL", "Turn Number", "Status"], dropna=False, sort=False)
            .apply(aggregate_errors)
            .reset_index(name="Errors")
        )

        # Aggregate errors for each Colab and determine final status
        final_df = grouped_df.groupby(["Colab Name", "Colab URL"]).apply(aggregate_colab).reset_index()

        return final_df

    def __format_time(self, seconds: float) -> str:
        """Format seconds into a human-readable format.

        Parameters
        ----------
        seconds : float
            Time in seconds.

        Returns
        -------
        str
            Time in human-readable format.
        """
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds %= 60
            return f"{int(minutes)} minutes {int(seconds)} seconds"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{int(hours)} hours {int(minutes)} minutes"
