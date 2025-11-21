# AI Real Estate Genealogy Platform - Setup Guide

This guide covers the activation system and LLM configuration for the AI Real Estate Genealogy Platform.

## Features

- **Activation System**: License-based activation for premium features
- **Multiple LLM Providers**: Support for Anthropic Claude, OpenAI, DeepSeek, Google Gemini, Cohere, and local models
- **AI-Powered Research**: Enhanced genealogy research with AI analysis
- **Flexible Configuration**: Environment-based configuration system

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the environment template:

```bash
cp .env.template .env
```

Edit `.env` and configure your settings:

```bash
# Activation Configuration
ACTIVATION_CODE=your-activation-code-here
ACTIVATION_ENABLED=false  # Set to 'true' to require activation

# LLM Provider Configuration
LLM_PROVIDER=anthropic  # Choose: anthropic, openai, deepseek, google, cohere, local

# API Keys (configure the provider(s) you want to use)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
# ... (see .env.template for all options)
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Activation System

### Demo Mode (Default)

By default, activation is **disabled** (`ACTIVATION_ENABLED=false`). In this mode:

- The system is always activated
- Demo activation codes are available for testing
- No license enforcement

**Demo Activation Codes:**
- `GENEALOGY-2024-PREMIUM`
- `OVERAGE-PRO-LICENSE`
- `HEIR-RESEARCH-UNLIMITED`

### Production Mode

To enable activation enforcement:

1. Set `ACTIVATION_ENABLED=true` in `.env`
2. Set your activation code: `ACTIVATION_CODE=YOUR-LICENSE-KEY`
3. Users must enter a valid activation code to use the system

### Using the Settings Panel

1. Navigate to **Settings** (gear icon in sidebar)
2. Enter your activation code
3. Click **Activate**
4. The system will validate and activate

## LLM Provider Configuration

### Supported Providers

#### 1. Anthropic (Claude) - Recommended

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Models:** claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307

#### 2. OpenAI (GPT-4)

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4-turbo-preview
```

**Models:** gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo

#### 3. DeepSeek

```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

**Models:** deepseek-chat, deepseek-coder

#### 4. Google (Gemini)

```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=your-api-key
GOOGLE_MODEL=gemini-pro
```

**Models:** gemini-pro, gemini-pro-vision

#### 5. Cohere

```bash
LLM_PROVIDER=cohere
COHERE_API_KEY=your-api-key
COHERE_MODEL=command
```

**Models:** command, command-light, command-nightly

#### 6. Local (Ollama)

```bash
LLM_PROVIDER=local
LOCAL_BASE_URL=http://localhost:11434
LOCAL_MODEL=llama2
```

**Requirements:** Ollama must be running locally. Install from [ollama.ai](https://ollama.ai)

**Models:** llama2, mistral, codellama, or any Ollama-compatible model

### Switching Providers

**Via Settings UI:**
1. Go to Settings → AI Provider Configuration
2. Select your desired provider from the dropdown
3. The system will switch providers immediately (API keys must be configured in `.env`)

**Via Environment:**
1. Edit `.env` file
2. Change `LLM_PROVIDER=<provider-name>`
3. Restart the application

### LLM Parameters

Customize LLM behavior:

```bash
LLM_TEMPERATURE=0.7    # Creativity (0.0-1.0)
LLM_MAX_TOKENS=2000    # Maximum response length
```

## AI-Enhanced Features

When an LLM is configured, the platform provides:

### 1. Genealogy Research Enhancement

- **AI Analysis**: Deep insights into family relationships and patterns
- **Heir Identification**: Intelligent suggestions for potential heirs
- **Address Analysis**: Pattern detection in location history
- **Contact Recommendations**: Prioritized contact strategies

### 2. Research Results

AI analysis appears in the research results with:
- Structured family relationship analysis
- Notable patterns and connections
- Actionable recommendations for heir outreach
- Risk assessment and verification suggestions

## API Endpoints

### Activation

- `GET /api/activation/status` - Get current activation and LLM status
- `POST /api/activation/validate` - Validate an activation code

### LLM Configuration

- `GET /api/config/llm` - Get current LLM configuration
- `POST /api/config/llm` - Update LLM provider (runtime only)

### Research (Enhanced)

- `POST /api/research` - Perform genealogy research with optional AI analysis

## Troubleshooting

### LLM Not Working

1. **Check API Key**: Ensure the correct API key is set in `.env`
2. **Verify Provider**: Check that `LLM_PROVIDER` matches your configured key
3. **Check Status**: Visit Settings to see LLM configuration status
4. **View Logs**: Check console for error messages

### Activation Issues

1. **Demo Mode**: If `ACTIVATION_ENABLED=false`, any code will work
2. **Code Format**: Enter codes exactly as shown (case-insensitive)
3. **Check Status**: Green badge = activated, Red = needs activation

### Import Errors

If you see import errors for LLM providers:

```bash
pip install anthropic openai google-generativeai cohere
```

Install only the providers you plan to use.

## Security Notes

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use environment variables** in production
3. **Rotate API keys** regularly
4. **Activation codes** are hashed for security
5. **API keys** are never exposed to the frontend

## Development

### Adding a New LLM Provider

1. Update `LLMProvider` class in `app.py`
2. Add initialization logic in `_initialize_client()`
3. Add generation logic in `generate()` method
4. Update `.env.template` with configuration options
5. Add to provider dropdown in `index.html`

### Testing

Test activation:
```python
# In Python console
from app import activation_system
activation_system.validate('GENEALOGY-2024-PREMIUM')
```

Test LLM:
```python
from app import llm_provider
result = llm_provider.generate('Hello, how are you?')
print(result)
```

## Support

For issues or questions:
- Check this documentation
- Review `.env.template` for all options
- Check console logs for errors
- Ensure all dependencies are installed

## License

This platform includes an optional activation system. Configure activation settings in `.env` file.
