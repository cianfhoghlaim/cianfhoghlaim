// Fake Express server or similar could go here
// In production this is handled by TanStack Start or an API framework
import express from 'express';
import fetch from 'node-fetch';

const app = express();
app.use(express.json());

// Replace with actual Dive ID from your MD account
const DIVE_ID = process.env.MOTHERDUCK_DIVE_ID || "default_dive_id";

app.post('/api/motherduck/embed-session', async (req, res) => {
  try {
    const token = process.env.MOTHERDUCK_TOKEN;
    if (!token) return res.status(500).json({ error: "Missing token" });

    const response = await fetch(`https://api.motherduck.com/v1/dives/${DIVE_ID}/embed-session`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username: "oideachais_service_user" })
    });

    const data = await response.json();
    res.json({ session: data.session });
  } catch (error) {
    res.status(500).json({ error: error.toString() });
  }
});

app.listen(8000, () => {
  console.log("MotherDuck API Mock Server listening on port 8000");
});
