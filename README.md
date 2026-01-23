<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# SmashAI - Badminton Analysis

**SmashAI** is an AI-powered badminton smash analysis tool that uses computer vision and generative AI to measure speed, analyze technique, and improve your game.

## Run Locally

**Prerequisites:** Node.js 20+

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure Environment:**
   Set the `GEMINI_API_KEY` in `.env.local` to your Gemini API key.

3. **Run the app:**
   ```bash
   npm run dev
   ```
   Navigate to `http://localhost:4200/`.

## Deployment

### Frontend (Vercel)

1.  Push your code to GitHub.
2.  Import the repository into [Vercel](https://vercel.com).
3.  Vercel will detect the Angular project automatically.
4.  Deploy!

### Backend (Python)

The backend is built with FastAPI and uses `ffmpeg` for video processing. It can be deployed on platforms like **Railway** or **Render**.

**Requirements:**
- Python 3.10+
- FFmpeg installed on the server

## Project Structure

- `src/` - Angular frontend source code.
- `backend/` - FastAPI backend application.
- `backend/app/` - Core backend logic (API, Services).
