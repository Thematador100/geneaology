# AI Real Estate Genealogy Platform

A world-class AI-powered platform for real estate heir research, probate analysis, and genealogy investigation with extensive multi-source research capabilities.

## Features

- **Multi-Source Research**: Automated research across FamilyTreeNow, TruePeopleSearch, FastPeopleSearch, FindAGrave, and public records
- **PDF Processing**: Upload and analyze Tracers.com reports and genealogy documents
- **Smart Caching**: Intelligent result caching for faster repeat searches
- **Overage Data Management**: Upload and process foreclosure overage CSV files
- **Heir Research**: AI-powered identification of property heirs and relatives from multiple sources
- **Document Generation**: Create legal documents like Affidavits of Heirship
- **Real-time Analytics**: Track research progress, success rates, and statistics
- **Professional UI/UX**: Modern, responsive interface with interactive visualizations
- **Data Deduplication**: Automatically consolidates and deduplicates results from multiple sources

## Technology Stack

- **Backend**: Python Flask with enhanced research engine
- **Database**: SQLite with caching layer
- **Frontend**: HTML5, CSS3, JavaScript
- **Web Scraping**: BeautifulSoup4, Requests with smart rate limiting
- **Deployment**: Railway, Render, or any Platform-as-a-Service (PaaS)

## Quick Start (Local Development)

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/geneaology.git
cd geneaology
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:5000`

## Easy No-Code Deployment Options

### Option 1: Railway.app (Recommended - Simplest)

1. **Sign up** at [railway.app](https://railway.app)
2. **Click "New Project"** → **"Deploy from GitHub repo"**
3. **Connect your GitHub** account and select this repository
4. **Deploy!** - Railway auto-detects Flask and deploys automatically
5. Your app will be live at `https://your-app.railway.app`

**Costs**: Free tier available with 500 hours/month, then ~$5-10/month

### Option 2: Render.com (Also Very Easy)

1. **Sign up** at [render.com](https://render.com)
2. **Click "New"** → **"Web Service"**
3. **Connect your GitHub** repository
4. Render will auto-detect the `render.yaml` configuration
5. **Click "Create Web Service"**
6. Your app will be live at `https://your-app.onrender.com`

**Costs**: Free tier available (spins down after inactivity), paid plans start at $7/month

### Option 3: PythonAnywhere (Python-Specific Hosting)

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)
2. **Upload your files** or clone from GitHub
3. **Create a new web app** (Flask)
4. **Configure WSGI** to point to `app.py`
5. Your app will be live at `https://yourusername.pythonanywhere.com`

**Costs**: Free tier available, paid plans start at $5/month

### Option 4: Google Cloud Run (Containerized)

1. Install Google Cloud CLI
2. Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn app:app --bind 0.0.0.0:$PORT
```
3. Build and deploy:
```bash
gcloud run deploy --source .
```

**Costs**: Pay-per-use, free tier includes 2 million requests/month

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
PORT=5000
FLASK_ENV=production
FLASK_DEBUG=False
```

## Usage

### 1. Upload Overage Data
- Navigate to **"Upload Data"** tab
- Select your CSV file with property information
- Required columns: `Address`, `Owner`, `Value`, `Overage`, `Case`
- System processes and stores data automatically

### 2. Research Heirs & Genealogy
- Go to **"Research"** tab
- Enter property address OR person name
- AI searches **multiple sources simultaneously**:
  - FamilyTreeNow.com
  - TruePeopleSearch.com
  - FastPeopleSearch.com
  - FindAGrave.com
  - Public Records
- View consolidated results with relatives, addresses, phone numbers

### 3. PDF Analysis
- Upload Tracers.com reports or genealogy PDFs
- AI extracts names, addresses, relationships, financial data
- Structured data saved to database

### 4. Generate Documents
- Select a property from your database
- Click **"Generate Affidavit"**
- Download pre-filled Affidavit of Heirship template

### 5. View Analytics
- Dashboard shows:
  - Properties analyzed
  - Heirs identified
  - Research completed
  - Total overage value

## File Structure

```
geneaology/
├── app.py                 # Enhanced Flask application with multi-source research
├── index.html             # Frontend interface
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku/Railway deployment config
├── runtime.txt           # Python version specification
├── railway.json          # Railway-specific configuration
├── render.yaml           # Render deployment configuration
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── LICENSE               # License information
├── uploads/              # CSV file uploads (auto-created)
├── pdf_uploads/          # PDF file uploads (auto-created)
└── genealogy.db          # SQLite database (auto-created)
```

## API Endpoints

### Main Application
- `GET /` - Main application interface

### File Management
- `POST /upload` - Upload overage data CSV files
- `POST /upload-pdf` - Upload PDF documents for analysis
- `GET /api/pdf-list` - Get list of all uploaded PDFs
- `GET /api/pdf-analysis/<pdf_id>` - Get detailed PDF analysis

### Research & Data
- `POST /api/research` - Start AI multi-source research
- `GET /api/properties` - Get all properties from database
- `GET /api/analytics` - Get system analytics and statistics

### Document Generation
- `POST /api/generate-document` - Generate legal documents (Affidavits)

## Database Schema

### Properties Table
```sql
id, address, owner_name, property_value, case_number,
overage_amount, status, created_at
```

### Heirs Table
```sql
id, property_id, name, relationship, contact_info,
address, phone, verified, created_at
```

### PDF Documents Table
```sql
id, filename, original_name, file_path, extracted_text,
analyzed_data, source_type, created_at
```

### Research Results Table
```sql
id, query, result_type, data, created_at
```

### Research Cache Table (Performance)
```sql
id, query_hash, query, source, result_data,
created_at, expires_at
```

## Research Engine Features

### Multi-Source Search
The enhanced research engine searches multiple sources in parallel:
- **FamilyTreeNow**: Genealogy records, relatives, addresses
- **TruePeopleSearch**: Contact info, relatives, current addresses
- **FastPeopleSearch**: Additional people search data
- **FindAGrave**: Burial records, death dates, family members
- **Public Records**: Property ownership, court records

### Smart Caching
- Results cached for 24 hours
- Reduces repeated API calls
- Faster subsequent searches
- Database-backed cache

### Data Consolidation
- Automatically deduplicates relatives
- Merges addresses from multiple sources
- Consolidates phone numbers
- Provides source attribution

## Deployment Tips

### For Railway/Render:
1. **Push to GitHub** first
2. Connect repository in platform
3. Platform auto-detects Python/Flask
4. Deployment is automatic

### Database Persistence:
- SQLite works for small-medium deployments
- For production at scale, consider PostgreSQL
- Railway/Render offer database add-ons

### Environment Variables:
Set these in your hosting platform:
- `PORT` - Auto-set by most platforms
- `FLASK_ENV` - Set to `production`
- `FLASK_DEBUG` - Set to `False`

## Scaling Considerations

### Current Setup (Good for):
- ✅ Up to 1,000 properties
- ✅ Up to 10,000 research queries/month
- ✅ Small teams (1-10 users)

### For Larger Scale:
- Upgrade to PostgreSQL database
- Add Redis for caching
- Implement API rate limiting
- Use Celery for background tasks
- Deploy behind CDN (Cloudflare)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Database Locked
```bash
# Reset database (WARNING: Deletes all data)
rm genealogy.db
python app.py  # Will recreate database
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## License

This project is proprietary software. All rights reserved.

## Support & Contact

For support, questions, or feature requests:
- Create an issue on GitHub
- Contact the development team
- Check documentation at [project wiki]

---

**Built with ❤️ for real estate professionals**
