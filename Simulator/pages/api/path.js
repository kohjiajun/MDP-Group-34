const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5002/path';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const backendResponse = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    const responseText = await backendResponse.text();
    let payload = null;

    try {
      payload = responseText ? JSON.parse(responseText) : null;
    } catch (parseError) {
      console.error('❌ Failed to parse backend response as JSON:', parseError);
    }

    if (!backendResponse.ok) {
      return res.status(backendResponse.status).json(
        payload || {
          error: `Backend responded with status ${backendResponse.status}`,
          raw: responseText,
        }
      );
    }

    return res.status(200).json(payload ?? {});
  } catch (error) {
    console.error('❌ Unable to reach backend service on port 5002:', error);
    return res.status(502).json({
      error: 'Failed to reach backend service on port 5002',
      details: error.message,
    });
  }
}