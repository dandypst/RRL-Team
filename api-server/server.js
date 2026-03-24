/**
 * RRL-Sensor API Server
 * 
 * Simple HTTP server untuk menerima data dari BOMBINO Gateway
 * Bisa di-deploy ke: Railway, Render, VPS, atau Raspberry Pi
 * 
 * Endpoints:
 * - POST /api/sensor-data    : Menerima data sensor periodik
 * - POST /api/alert          : Menerima alert immediate
 * - GET  /api/status         : Cek status server
 * - GET  /api/sections       : Get latest section status
 */

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.API_KEY || 'default-key-change-this';

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Database setup
const db = new sqlite3.Database('./rrl-sensor.db');

// Initialize database
db.serialize(() => {
  // Table for sensor readings
  db.run(`CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    timestamp INTEGER,
    uptime INTEGER,
    solar_voltage REAL,
    battery_voltage REAL,
    charge_current REAL,
    wifi_rssi INTEGER,
    lte_signal INTEGER,
    gps_valid INTEGER,
    latitude REAL,
    longitude REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  // Table for section status
  db.run(`CREATE TABLE IF NOT EXISTS section_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    section_id INTEGER,
    status TEXT,
    alert_count INTEGER,
    timestamp INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  // Table for alerts
  db.run(`CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    alert_type TEXT,
    priority TEXT,
    affected_sections TEXT,
    latitude REAL,
    longitude REAL,
    timestamp INTEGER,
    acknowledged INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
});

// API Key middleware
const validateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  if (!apiKey || apiKey !== API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
};

// Routes

// Health check
app.get('/api/status', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: Date.now(),
    version: '1.0.0'
  });
});

// Receive sensor data
app.post('/api/sensor-data', validateApiKey, (req, res) => {
  const data = req.body;
  
  console.log('[DATA] Received from:', data.device_id);
  
  // Insert system status
  db.run(
    `INSERT INTO sensor_readings 
     (device_id, timestamp, uptime, solar_voltage, battery_voltage, 
      charge_current, wifi_rssi, lte_signal, gps_valid, latitude, longitude)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      data.device_id,
      data.timestamp,
      data.uptime,
      data.system.solar_voltage,
      data.system.battery_voltage,
      data.system.charge_current,
      data.system.wifi_rssi,
      data.system.lte_signal,
      data.gps.valid ? 1 : 0,
      data.gps.lat || null,
      data.gps.lng || null
    ],
    function(err) {
      if (err) {
        console.error('[ERROR] Failed to insert sensor data:', err);
        return res.status(500).json({ error: 'Database error' });
      }
      
      // Insert section status
      const stmt = db.prepare(
        `INSERT INTO section_status (device_id, section_id, status, alert_count, timestamp)
         VALUES (?, ?, ?, ?, ?)`
      );
      
      data.sections.forEach(section => {
        stmt.run([
          data.device_id,
          section.id,
          section.status,
          section.alert_count,
          data.timestamp
        ]);
      });
      
      stmt.finalize();
      
      res.json({ success: true, id: this.lastID });
    }
  );
});

// Receive alert
app.post('/api/alert', validateApiKey, (req, res) => {
  const data = req.body;
  
  console.log('[ALERT] Received:', data.alert_type, 'from:', data.device_id);
  
  db.run(
    `INSERT INTO alerts 
     (device_id, alert_type, priority, affected_sections, latitude, longitude, timestamp)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [
      data.device_id,
      data.alert_type,
      data.priority,
      JSON.stringify(data.affected_sections),
      data.latitude || null,
      data.longitude || null,
      data.timestamp
    ],
    function(err) {
      if (err) {
        console.error('[ERROR] Failed to insert alert:', err);
        return res.status(500).json({ error: 'Database error' });
      }
      
      // TODO: Send WhatsApp notification here
      // sendWhatsAppAlert(data);
      
      res.json({ success: true, alert_id: this.lastID });
    }
  );
});

// Get latest section status
app.get('/api/sections', (req, res) => {
  db.all(
    `SELECT s.* FROM section_status s
     INNER JOIN (
       SELECT device_id, section_id, MAX(timestamp) as max_ts
       FROM section_status
       GROUP BY device_id, section_id
     ) latest ON s.device_id = latest.device_id 
              AND s.section_id = latest.section_id 
              AND s.timestamp = latest.max_ts
     ORDER BY s.section_id`,
    [],
    (err, rows) => {
      if (err) {
        console.error('[ERROR] Failed to get sections:', err);
        return res.status(500).json({ error: 'Database error' });
      }
      res.json(rows);
    }
  );
});

// Get recent alerts
app.get('/api/alerts', (req, res) => {
  const limit = parseInt(req.query.limit) || 50;
  
  db.all(
    `SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?`,
    [limit],
    (err, rows) => {
      if (err) {
        console.error('[ERROR] Failed to get alerts:', err);
        return res.status(500).json({ error: 'Database error' });
      }
      
      // Parse affected_sections JSON
      rows.forEach(row => {
        try {
          row.affected_sections = JSON.parse(row.affected_sections);
        } catch (e) {
          row.affected_sections = [];
        }
      });
      
      res.json(rows);
    }
  );
});

// Acknowledge alert
app.post('/api/alerts/:id/acknowledge', (req, res) => {
  const alertId = req.params.id;
  
  db.run(
    `UPDATE alerts SET acknowledged = 1 WHERE id = ?`,
    [alertId],
    function(err) {
      if (err) {
        console.error('[ERROR] Failed to acknowledge alert:', err);
        return res.status(500).json({ error: 'Database error' });
      }
      res.json({ success: true });
    }
  );
});

// Start server
app.listen(PORT, () => {
  console.log(`[SERVER] RRL-Sensor API running on port ${PORT}`);
  console.log(`[SERVER] API Key: ${API_KEY.substring(0, 8)}...`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n[SERVER] Shutting down...');
  db.close();
  process.exit(0);
});
