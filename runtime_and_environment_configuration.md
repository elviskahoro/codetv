# Runtime and Environment Configuration

## FastAPI Server Entry-Point
- The FastAPI server entry-point must be specified in `main.py`.
- The file should expose an instance of FastAPI as `app`.

## Environment Variables
- Secrets such as OpenAI key, MCP endpoint, and Galileo token must be stored in a `.env` file.
- Hard-coding sensitive data in the codebase is strictly prohibited.

### Agent Reliability (Galileo) Configuration
- **Optional Feature**: Agent reliability monitoring through Galileo can be enabled via the `ENABLE_GALILEO` environment variable.
- **Default Behavior**: When `ENABLE_GALILEO=false` or unset, the system must operate normally with graceful fallback.
- **Dependency Weight Warning**: Enabling Galileo adds significant dependency overhead. Consider impact on performance and bundle size.
- **Required Variables** (when enabled):
  - `ENABLE_GALILEO=true`
  - `GALILEO_API_KEY=your_galileo_api_key`
  - `GALILEO_PROJECT_ID=your_project_id` (optional, for project-specific tracking)

## `.env.example` Pattern
- Provide a `.env.example` file to demonstrate the required environment variables without exposing real values.
- This file serves as a template to ensure developers know which variables are necessary.

## Render Deploy Hook
- If relevant, include instructions for the Render deploy hook located at `/usr/local/bin/render` to ensure correct deployment setup.
