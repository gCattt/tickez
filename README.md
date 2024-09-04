# tickez
This webapp is designed to simplify the process of selling and managing tickets for music events, providing an easy-to-use platform for both event organizers and attendees.

For more detailed information, refer to the [tickez-report](./docs/tickez-report.pdf).

## Table of Contents
- [Features](#features)
- [Setup](#setup)
  - [Requirements](#requirements)
  - [Database](#database)
  - [Start](#start)
- [Recommendation System](#recommendation-system)
- [Testing](#testing)

## Features
The application offers the following features:
- **Event Browsing**: Users can view and filter a list of music events, initially sorted by date;
- **Ticket Purchase and Management**: Registered users can purchase and manage event tickets;
- **User-Based Recommendation System**: Registered users who have made at least one purchase can see recommended events based on the similarity with other users' purchase histories;
- **User Profile**: The site includes login and registration mechanisms, allowing for differentiated operations based on user roles;
- **Favorites and Notifications**: Registered users can follow events, organizers, or venues and receive updates;
- **Event Management**: Organizers can create and manage events, including detailed statistics;
- **Log Messages**: The application provides informative messages or pages about completed operations, enhancing security and usability.

## Setup
Follow these steps to set up and run the application.

### Requirements
Clone the repository:
```bash
git clone https://github.com/gCattt/tickez.git
cd tickez
```
Make sure `pipenv` is installed.
<br>
Install dependencies:
```bash
pipenv install
```
If `pipenv` complains about an already active venv, solve manually or force it with `--anyway` option.

Activate the virtual environment:
```bash
pipenv shell
```
Install all project dependencies listed in the _requirements.txt_ file:
```bash
pip install -r requirements.txt
```

### Database
Run the migrations to set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```
Run the following to setup a mock environment:
```bash
python setup.py
```
| Role                 | Username                                                                            | Password        |
|----------------------|-------------------------------------------------------------------------------------|-----------------| 
| Admin                | admin                                                                               | password        |
| Organizers           | taylorswift, edsheeran, elisa, ligabue, arianagrande, vascorossi, billieeilish, jovanotti, dualipa, erosramazzotti                                                                  | organizzatorepw |
| Registered Users     | mariarossi, lucaverdi, chiarabianchi, marcorusso, giorgiorossi   | clientepw        |
| Guest                | /                                                                                   | /               |

### Start
Start the development server:
```bash
python manage.py runserver
```
Once the server is running, go to http://localhost:8000/ and start exploring.

## Recommendation System
The recommendation system implemented in this application uses a **user-based collaborative filtering** approach.
- Similarity Matrix: The system connects users through a user-event matrix and calculates user similarity with **cosine similarity**, which results in a similarity matrix;
- Purchase Patterns: Based on the purchase history, a list of recommended events is generated for the registered users, excluding events they have already purchased.

## Testing
The project includes dedicated classes for **unit testing** key functionalities in the _users_ and _products_ applications.

To run test-cases:
```
python manage.py test users
python manage.py test products
```
