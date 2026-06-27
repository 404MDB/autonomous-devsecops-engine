const express = require('express');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const port = 3000;

// FIXED SECURITY FLAW 1: Fetching the key from a secure environment variable
const SECRET_KEY = process.env.UPI_SECRET_KEY || "fallback_secret_for_local_testing_only";

if (!process.env.UPI_SECRET_KEY) {
  console.warn("WARNING: UPI_SECRET_KEY is missing from the environment! Using fallback.");
}

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize an in-memory database with mock accounts
const db = new sqlite3.Database(':memory:');
db.serialize(() => {
  db.run("CREATE TABLE users (id INT, vpa TEXT, balance REAL, password TEXT)");
  db.run("INSERT INTO users VALUES (1, 'meet@upi', 5000.00, 'password123')");
  db.run("INSERT INTO users VALUES (2, 'merchant@upi', 10000.00, 'admin123')");
});

// Endpoint 1: Health Check
app.get('/', (req, res) => {
  res.send('UPI Mock Gateway is Online. Awaiting transactions...');
});

// Endpoint 2: Secure Login
app.post('/api/login', (req, res) => {
  const { vpa, password } = req.body;
  
  // FIXED SECURITY FLAW 2: Using Parameterized Queries to prevent SQL Injection
  const query = `SELECT id, vpa FROM users WHERE vpa = ? AND password = ?`;
  
  db.get(query, [vpa, password], (err, row) => {
    if (err) {
      return res.status(500).json({ success: false, message: "Database error" });
    }
    if (row) {
      // FIXED SECURITY FLAW 3: Added JWT expiration date (1 hour)
      const token = jwt.sign({ id: row.id, vpa: row.vpa }, SECRET_KEY, { expiresIn: '1h' });
      res.json({ success: true, token: token });
    } else {
      res.status(401).json({ success: false, message: "Invalid credentials" });
    }
  });
});

// Endpoint 3: Secure Transfer 
app.post('/api/upi/transfer', (req, res) => {
  const { amount, targetVpa } = req.body;
  const authHeader = req.headers.authorization;
  
  // FIXED SECURITY FLAW 4: Validating token signature before allowing transfer
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(403).json({ error: "Missing or malformed Auth Token" });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    res.json({
      status: "SUCCESS",
      message: `Transferred ₹${amount} to ${targetVpa}.`,
      transactionId: `TXN${Math.floor(Math.random() * 1000000)}`,
      user: decoded.vpa
    });
  } catch (err) {
    return res.status(401).json({ error: "Invalid or Expired Token" });
  }
});

// Endpoint 4: Secure Data Fetch
app.get('/api/user', (req, res) => {
  const vpa = req.query.vpa;
  
  // FIXED SECURITY FLAW 5: Parameterized query & explicitly selecting fields to prevent password exposure
  db.get(`SELECT id, vpa, balance FROM users WHERE vpa = ?`, [vpa], (err, row) => {
    if (err) {
      return res.status(500).json({ error: "Database error" });
    }
    if (row) {
      res.json(row); 
    } else {
      res.status(404).json({ error: "User not found" });
    }
  });
});

app.listen(port, () => {
  console.log(`Dummy UPI App listening at http://localhost:${port}`);
});