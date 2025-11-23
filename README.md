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
- **AI Recommendation Engine** (NEW): Intelligent recommendations for:
  - Priority ranking of heirs to contact
  - Properties requiring immediate attention
  - Next best actions based on data completeness
  - Similar case pattern matching

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

### Core Endpoints
- `GET /` - Main application interface
- `POST /upload` - Upload overage data files
- `POST /upload-pdf` - Upload PDF documents for analysis
- `POST /api/research` - Start AI research on person/property
- `POST /api/generate-document` - Generate legal documents
- `GET /api/properties` - Get all properties
- `GET /api/analytics` - Get system analytics

### Recommendation Endpoints (NEW)
- `GET /api/recommendations/dashboard` - Get comprehensive recommendations overview
- `GET /api/recommendations/properties` - Get properties ranked by priority (top 20)
- `GET /api/recommendations/heirs/<property_id>` - Get prioritized heir contact list
- `GET /api/recommendations/actions/<property_id>` - Get recommended next actions
- `GET /api/recommendations/similar/<property_id>` - Find similar properties for pattern analysis

## Database Schema

### Properties Table
- id, address, owner_name, property_value, case_number, overage_amount, status

### Heirs Table
- id, property_id, name, relationship, contact_info, address, phone, verified

### PDF Documents Table
- id, filename, file_path, extracted_text, analyzed_data, source_type

### Research Results Table
- id, query, result_type, data, created_at

## Recommendation System

The AI Recommendation Engine analyzes your property and heir data to provide intelligent, actionable recommendations.

### Key Features

**1. Heir Priority Scoring (0-100 points)**
- Verification status: Verified heirs score higher (40 points)
- Relationship closeness: Sons/daughters (30 pts) > siblings (18 pts) > cousins (9 pts)
- Contact completeness: Phone + address + email maximize score (20 points)
- Property value: Higher overage amounts increase urgency (10 points)

**2. Property Attention Scoring (0-100 points)**
- Overage amount: $100k+ = critical attention (30 points)
- Missing heirs: No heirs found = critical priority (40 points)
- Verification status: Unverified heirs need immediate action (20 points)
- Property status: Active cases prioritized (10 points)

**3. Smart Action Recommendations**
- Critical: Research heirs for properties with none found
- High: Verify unverified heirs
- Medium: Collect missing contact information
- Low: Expand research for additional relatives

**4. Pattern Matching**
- Identifies similar properties based on overage amounts
- Helps predict successful research strategies
- Finds comparable cases for reference

### Usage Examples

**Get Dashboard Overview:**
```bash
GET /api/recommendations/dashboard
```
Returns summary statistics and top 5 priority properties

**Get Property Priorities:**
```bash
GET /api/recommendations/properties
```
Returns all properties ranked by attention score (top 20)

**Get Heir Priorities for a Property:**
```bash
GET /api/recommendations/heirs/123
```
Returns ranked list of heirs to contact for property #123

**Get Next Actions:**
```bash
GET /api/recommendations/actions/123
```
Returns recommended next steps for property #123

**Find Similar Cases:**
```bash
GET /api/recommendations/similar/123
```
Returns similar properties for pattern analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Support

For support and questions, please contact the development team.

