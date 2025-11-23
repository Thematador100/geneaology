# AI Real Estate Genealogy Platform

A world-class AI-powered platform for real estate heir research, probate analysis, and genealogy investigation.

## Features

- **PDF Processing**: Upload and analyze Tracers.com reports and other genealogy documents
- **Web Scraping**: Automated research from FamilyTreeNow.com and FindAGrave.com
- **Overage Data Management**: Upload and process foreclosure overage files
- **Heir Research**: AI-powered identification of property heirs and relatives
- **Document Generation**: Create legal documents like Affidavits of Heirship
- **Real-time Analytics**: Track research progress and success rates
- **Professional UI/UX**: Modern interface with interactive charts and visualizations

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: Web scraping with BeautifulSoup
- **Charts**: Chart.js for data visualization

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ai-genealogy-platform.git
cd ai-genealogy-platform
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

## Usage

### Upload Overage Data
1. Click "Upload Overage Data"
2. Select your CSV file with property information
3. System will process and store the data

### PDF Analysis
1. Click "Upload PDF"
2. Select Tracers.com reports or other genealogy PDFs
3. AI will extract names, addresses, relationships, and financial data

### Research Heirs
1. Enter property address or person name in search
2. AI will research genealogy data from multiple sources
3. View detailed family trees and contact information

### Generate Documents
1. Select a property from your database
2. Choose document type (Affidavit of Heirship)
3. Download generated legal document

## File Structure

```
ai-genealogy-platform/
├── app.py              # Main Flask application
├── index.html          # Frontend interface
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
└── uploads/           # File upload directory (created automatically)
```

## API Endpoints

- `GET /` - Main application interface
- `POST /api/upload` - Upload overage data files
- `POST /api/upload-pdf` - Upload PDF documents for analysis
- `POST /api/research` - Start AI research on person/property
- `POST /api/generate-document` - Generate legal documents
- `GET /api/properties` - Get all properties
- `GET /api/pdf-list` - Get list of uploaded PDFs
- `GET /api/pdf-analysis/<id>` - Get detailed PDF analysis
- `GET /api/analytics` - Get system analytics

## Database Schema

### Properties Table
- id, address, owner_name, property_value, case_number, overage_amount, status

### Heirs Table  
- id, property_id, name, relationship, contact_info, address, phone, verified

### PDF Documents Table
- id, filename, file_path, extracted_text, analyzed_data, source_type

### Research Results Table
- id, query, result_type, data, created_at

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Support

For support and questions, please contact the development team.

