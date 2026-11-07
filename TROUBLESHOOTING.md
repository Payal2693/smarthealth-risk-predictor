Troubleshooting Guide
This guide covers some common issues that may occur while setting up or running the SmartHealth Risk Predictor application.

1. Python Is Not Recognized
Problem: The terminal does not recognize the Python command.
Solution:
•	Check whether Python is installed.
•	Make sure Python is added to the system PATH.
•	Restart the terminal and try again.

2. Module Not Found
Problem: An error appears because a required Python library is missing.
Solution:
Run:
pip install -r requirements.txt

3. Application Does Not Start
Problem: The Flask application fails to run.
Solution:
•	Check the terminal for error messages.
•	Verify that the required project files are present.
•	Confirm that the dependencies are installed.

4. Database Error
Problem: The application cannot access the SQLite database.
Solution:
•	Check the database configuration.
•	Verify that the application has permission to access the database.
•	Follow the project's database initialization process if required.

5. Prediction Error
Problem: The prediction page does not display a result.
Solution:
•	Check whether all required input fields are completed.
•	Verify that the required trained model files are available.
•	Check the terminal for Python errors.

Need More Help?
Review the installation guide and check the application logs for additional information.
