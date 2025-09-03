import json
import os

import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extras import execute_values


class NeonConnector:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
        self.cursor = None

    def _create_cursor(self):
        self.connection = psycopg2.connect(self.connection_string)
        self.cursor = self.connection.cursor()
        
    def _exit(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            
    def _cast_int(self, num):
        if pd.notna(num):
            return round(num)
        else:
            return None

    def convert_df_to_records(self, df, int_cols=[], json_cols=[]):
        temp_df = df.copy()
        temp_df[json_cols] = temp_df[json_cols].map(lambda x: json.dumps(x) if pd.notna(x) else None)
        
        for col in temp_df.columns:
            if temp_df[col].dtype == "datetime64[ns]":
                temp_df[col] = temp_df[col].astype(str)
        
        temp_df["updated_on"] = pd.Timestamp.now(tz="GMT").strftime("%Y-%m-%d %H:%M:%S")
        temp_df = temp_df.replace({np.nan: None, 'NaT': None})
        records = temp_df.to_dict("records")

        for r in records:
            for col in int_cols:
                r[col] = self._cast_int(r[col])
        
        return records
    
    def batch_upsert(self, target_table, records, conflict_columns=[], batch_size=100):
        """Upsert a batch of records into a table. If a record with the same primary key already exists, it will be updated.

        Args:
            target_table (str): The name of the table to upsert records into.
            records (list): A list of dictionaries, where each dictionary represents a record to upsert.
            conflict_columns (list, optional): A list of column names to use for conflict resolution. Defaults to [].
            batch_size (int, optional): The number of records to upsert in each batch. Defaults to 100.
        """
        try:
            self._create_cursor()
            
            # Get column names from the first record
            column_names = list(records[0].keys())

            # Generate the INSERT INTO ... VALUES ... statement
            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                sql.Identifier(target_table),
                sql.SQL(', ').join(sql.Identifier(column) for column in column_names)
            )

            # Generate the ON CONFLICT DO UPDATE SET ... statement
            if conflict_columns:
                conflict_update_query = sql.SQL("ON CONFLICT ({}) DO UPDATE SET {}").format(
                    sql.SQL(', ').join(sql.Identifier(column) for column in conflict_columns),
                    sql.SQL(', ').join(sql.Identifier(column) + sql.SQL(' = EXCLUDED.') + sql.Identifier(column) for column in column_names)
                )
            else:
                conflict_update_query = sql.SQL("ON CONFLICT DO NOTHING")

            # Iterate over records in batches
            for i in range(0, len(records), batch_size):
                batch_records = records[i:i+batch_size]

                # Prepare the values for the current batch
                values = [tuple(record[column] for column in column_names) for record in batch_records]

                # Execute the upsert operation for the current batch
                execute_values(self.cursor, insert_query + conflict_update_query, values)
                
            # Commit the transaction
            self.connection.commit()
            
            print("Batch upsert completed successfully.")

        except psycopg2.Error as e:
            print("Error:", e)
            self.connection.rollback()

        finally:
            self._exit()

    def select_query(self, query):
        """Execute a SELECT query and return the results as a list of dictionaries.

        Args:
            query (str): The complete SELECT query to execute.

        Returns:
            list: A list of dictionaries, where each dictionary represents a row in the result set.
        """
        try:
            self._create_cursor()
            
            # Execute the query
            self.cursor.execute(query)

            # Fetch all rows from the result set
            rows = self.cursor.fetchall()

            # Get column names from the cursor description
            column_names = [desc[0] for desc in self.cursor.description]

            # Convert rows to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(column_names, row)))

            print("Query executed successfully.")

            return results

        except psycopg2.Error as e:
            print("Error executing query:", e)

        finally:
            self._exit()
    
    def delete_data(self, target_table, condition):
        """Delete data from a table based on a condition.

        Args:
            target_table (str): The name of the table from which to delete data.
            condition (str): The condition to use for deleting data. E.g. "id = 1". Do not include the "WHERE" keyword.
        """
        try:
            self._create_cursor()
            
            # Generate the DELETE FROM ... WHERE ... statement
            delete_query = sql.SQL("DELETE FROM {} WHERE {}").format(
                sql.Identifier(target_table),
                sql.SQL(condition)
            )

            # Execute the delete operation
            self.cursor.execute(delete_query)
            
            # Commit the transaction
            self.connection.commit()
            
            print("Data deleted successfully.")

        except psycopg2.Error as e:
            print("Error:", e)
            self.connection.rollback()

        finally:
            self._exit()
            
    def execute_function(self, function_name, args=[]):
        """Execute a stored function with the given name and arguments. Only use this function for DML functions (INSERT, UPDATE, DELETE).

        Args:
            function_name (str): The name of the function to execute.
            args (list, optional): A list of arguments to pass to the function. Defaults to [].

        Returns:
            Any: The result returned by the function.
        """
        try:
            self._create_cursor()
            
            # Construct the function call string with placeholders
            arg_placeholders = ', '.join('%s' for _ in args)
            function_call = f"SELECT {function_name}({arg_placeholders})"
            
            # Execute the function call with arguments
            self.cursor.execute(function_call, args)
            
            # Fetch the result returned by the function
            result = self.cursor.fetchall()
            
            # Commit the transaction
            self.connection.commit()
            
            print("Function executed successfully.")
            
            return result
            
        except psycopg2.Error as e:
            print("Error executing function:", e)
            self.connection.rollback()
            
        finally:
            self._exit()

if __name__ == "__main__":
    load_dotenv()
    connection_string = os.getenv("DATABASE_URL")
    neon_manager = NeonConnector(connection_string)
    