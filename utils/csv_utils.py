import os
import pandas as pd
from datetime import datetime
import logging

def save_results_to_csv(results, pdb_code, result_folder):
    """Saves the results to a CSV file with enhanced formatting and error handling."""
    
    # Ensure the results folder exists, if not create it
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    
    # Get current date and time to add to the file name (to make it unique)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    result_csv = os.path.join(result_folder, f"{pdb_code}_angles_{timestamp}.csv")
    
    try:
        # Create a DataFrame from results
        df = pd.DataFrame(results)
        
        # Check if the dataframe is empty
        if df.empty:
            raise ValueError("The results dataframe is empty.")
        
        # Standardize or modify column names for better readability
        df.columns = [col.strip().capitalize() for col in df.columns]
        
        # Format the numeric columns (like angles) for better readability
        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            df[col] = df[col].apply(lambda x: f"{x:0.2f}")  # Format numeric columns to 2 decimal places
        
        # Save the DataFrame to a CSV file
        df.to_csv(result_csv, index=False, header=True)
        
        # Log the success and file path
        logging.info(f"Results saved successfully to {result_csv}")
        return result_csv

    except Exception as e:
        # Log the error and raise it for further handling
        logging.error(f"Failed to save results to CSV: {e}")
        raise
