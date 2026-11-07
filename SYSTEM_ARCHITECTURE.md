System Architecture
1. Overview
SmartHealth Risk Predictor is a web-based application that combines a Flask backend, SQLite database and machine learning models to provide basic health risk screening.

2. Main Components
Frontend
The frontend provides the interface through which patients and staff interact with the application.
Backend
Flask handles user requests, application logic, authentication and communication between different components.
Database
SQLite stores application data such as user information and health assessment records.
Machine Learning Models
Two separate Random Forest models are used:
•	Heart disease risk prediction.
•	Diabetes risk prediction.

3. Application Workflow
  1.	The user opens the web application.
  2.	The frontend sends the request to the Flask backend.
  3.	Flask processes the request and interacts with the SQLite database when needed.
  4.	For a health assessment, Flask passes the input to the relevant machine learning model.
  5.	The model generates a prediction.
  6.	The result is displayed through the frontend.

4. Technology Stack
•	Python
•	Flask
•	SQLite
•	Scikit-learn
•	Random Forest
•	HTML and Bootstrap

5. Conclusion
The architecture connects the user interface, backend, database and machine learning models to provide a simple health data management and screening application.
