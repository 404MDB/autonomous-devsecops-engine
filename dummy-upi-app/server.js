const express = require('express');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const port = 3000;

// INTENTIONAL SECURITY FLAW 1: Hardcoded cryptographic key
const SECRET_KEY = "super_secret_upi_key_123";

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

// Endpoint 2: Vulnerable Login
app.post('/api/login', (req, res) => {
  const { vpa, password } = req.body;
  
  // INTENTIONAL SECURITY FLAW 2: Severe SQL Injection vulnerability
  const query = `SELECT * FROM users WHERE vpa = '${vpa}' AND password = '${password}'`;
  
  db.get(query, (err, row) => {
    if (row) {
      // INTENTIONAL SECURITY FLAW 3: JWT token has no expiration date
      const token = jwt.sign({ id: row.id, vpa: row.vpa }, SECRET_KEY);
      res.json({ success: true, token: token });
    } else {
      res.status(401).json({ success: false, message: "Invalid credentials" });
    }
  });
});

// Endpoint 3: Vulnerable Transfer 
app.post('/api/upi/transfer', (req, res) => {
  const { amount, targetVpa } = req.body;
  const token = req.headers.authorization;
  
  // INTENTIONAL SECURITY FLAW 4: Missing token signature validation and balance check
  if (!token) {
    return res.status(403).json({ error: "Missing Auth Token" });
  }

  res.json({
    status: "SUCCESS",
    message: `Transferred ₹${amount} to ${targetVpa}.`,
    transactionId: `TXN${Math.floor(Math.random() * 1000000)}`
  });
});

// Endpoint 4: Data Exposure
app.get('/api/user', (req, res) => {
  const vpa = req.query.vpa;
  
  db.get(`SELECT * FROM users WHERE vpa = '${vpa}'`, (err, row) => {
    if (row) {
      // INTENTIONAL SECURITY FLAW 5: Sending the raw database row (exposing passwords to the frontend)
      res.json(row); 
    } else {
      res.status(404).json({ error: "User not found" });
    }
  });
});

app.listen(port, () => {
  console.log(`Dummy UPI App listening at http://localhost:${port}`);
});