# ShortTrack - URL Shortener with Click Analytics

![ShortTrack Banner](https://via.placeholder.com/1200x400?text=ShortTrack+Banner)

**ShortTrack** is a powerful URL shortening service that not only shortens your links but also tracks detailed analytics for each click. Gain insights into the number of clicks, geographic distribution, referrers, and much more.

## 🚀 Features

- **URL Shortening** – Quickly shorten long URLs into simple, shareable links.
- **Click Analytics** – Track the number of clicks, user location (country), referrer, and timestamp for every shortened URL.
- **Real-time Statistics** – Visualize your URL's performance with real-time tracking data.
- **Custom Short Links** – Create personalized short links for easier branding.
- **Simple API** – Integrate the URL shortening and analytics features into your applications.

## 🛠️ Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/your-github-username/shorttrack.git
cd shorttrack
````

### Step 2: Create and activate a virtual environment

For **Windows**:

```bash
python -m venv venv
.\venv\Scripts\activate
```

For **Linux/Mac**:

```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up the database

We are using **SQLite** for simplicity. To set up the database tables, run the following command:

```bash
python create_db.py
```

### Step 5: Start the Flask server

```bash
flask run
```

You can now access the application at [http://localhost:5000](http://localhost:5000).

## 🌐 API Usage

**ShortTrack** provides a simple API for shortening URLs and retrieving click analytics.

### Create a shortened URL

**POST** `/api/shorten`

Request Body:

```json
{
  "url": "https://www.example.com"
}
```

Response:

```json
{
  "shortened_url": "http://localhost:5000/abc123",
  "clicks": 0,
  "analytics": []
}
```

### Get Analytics for a shortened URL

**GET** `/api/analytics/{shortened_url}`

Response:

```json
{
  "url": "http://localhost:5000/abc123",
  "clicks": 123,
  "clicks_by_referrer": {
    "google.com": 45,
    "facebook.com": 30,
    "direct": 48
  },
  "clicks_by_country": {
    "US": 75,
    "RU": 25,
    "IN": 15
  }
}
```

## 📊 Dashboard

Once your app is up and running, you can navigate to the main page to view a **real-time dashboard** displaying the number of clicks, referrers, and geographical data of users who clicked on your shortened URLs.

### Structure

```
shorttrack/
│
├── app.py                # Main application file
├── config.py             # Flask application configuration
├── models.py             # Database models (Links, Clicks)
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates (index.html, dashboard.html)
├── create_db.py          # Database setup script
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## 📝 Contributing

1. Fork this repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit them: `git commit -am 'Add your feature'`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a pull request

## 📅 Future Enhancements

* Integration with Google Analytics or other analytics platforms.
* User authentication for managing custom short links.
* Multilingual support for global users.
* Enhanced real-time analytics with visual charts.

## 📬 Contact

For any questions or suggestions, feel free to open an issue in this repository or email us at [your-email@example.com](mailto:your-email@example.com).

---

🎉 **Join the ShortTrack community and help us improve URL tracking and analytics!**

---

### Breakdown of the Features in `README.md`:

1. **Features**: Highlights the core features like URL shortening, click analytics, real-time statistics, etc.
2. **Installation**: Provides clear steps to set up the project on the local machine, including creating a virtual environment, installing dependencies, and setting up the database.
3. **API Usage**: Shows how to use the API for shortening URLs and getting analytics on clicks. It provides example requests and responses.
4. **Dashboard**: Mentions a real-time dashboard (you can later build a dashboard page to display user data such as clicks, referrers, and geographical info).
5. **Contributing**: A section for open-source contributors to help improve the project.
6. **Future Enhancements**: Suggestions for the next steps and features that could be added to make the project more powerful.

### Next Steps to Implement Analytics:

1. **Database Models**: You need to set up models for **Links** and **Clicks** (shown earlier). When a user visits a shortened URL, the app will log the click in the **Clicks** table.
   
2. **Tracking Clicks**: 
   - On visiting a shortened URL (`/shortened_url` route), the app will log the click in the database with the timestamp, referrer, and optionally the country (based on `request.headers` or `IP`).
   
3. **Analytics**: 
   - The `/analytics/{shortened_url}` endpoint will aggregate click data, breaking it down by referrer and country, and return it in a JSON format.

By using this `README.md` file, you'll provide users with all the information they need to get started with **ShortTrack**, and allow developers to contribute or integrate the service into their own applications.
