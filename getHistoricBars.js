import csvjson from 'csvjson';
import fs from 'fs';
// The API only returns data 20 days of minute data for the last complete month
const API_URL = 'https://api.topstepx.com/api/History/retrieveBars';
const AUTH_TOKEN = '' //#TODO: "get updated token from topstepx.com"
const CRUDE_OIL = 'CON.F.US.NQM.Q25'
const NATURAL_GAS = 'CON.F.US.NQG.Q25'
const MICRO_NQ = 'CON.F.US.MNQ.U25'
const EMINI_NQ = 'CON.F.US.ENQ.U25'
//EMINI NASDAQ 100 contract IDs
const contractIds = [
  { "code": "CON.F.US.ENQ.H24", "start": "2024-01-01T00:00:00Z", "end": "2024-03-31T23:59:00Z" },
  { "code": "CON.F.US.ENQ.M24", "start": "2024-04-01T00:00:00Z", "end": "2024-06-30T23:59:00Z" },
  { "code": "CON.F.US.ENQ.U24", "start": "2024-07-01T00:00:00Z", "end": "2024-09-30T23:59:00Z" },
  { "code": "CON.F.US.ENQ.Z24", "start": "2024-10-01T00:00:00Z", "end": "2024-12-31T23:59:00Z" },
  { "code": "CON.F.US.ENQ.H25", "start": "2025-01-01T00:00:00Z", "end": "2025-03-31T23:59:00Z" },
  { "code": "CON.F.US.ENQ.M25", "start": "2025-04-01T00:00:00Z", "end": "2025-06-30T23:59:00Z" }
];


const retrieveBars = async (contract, start, end) => {
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`
      },
      body: JSON.stringify({
        contractId: contract,
        live: false,
        startTime: start,
        endTime: end,
        unit: 3,
        unitNumber: 1,    // Number of units (e.g., 1 day, 5 minutes)
        limit: 1000000000,         // Maximum number of bars to return
        includePartialBar: false
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json(); // or response.text() if plain text
    console.log('Retrieved bars:', data);
    return data;
  } catch (error) {
    console.error('Failed to retrieve bars:', error);
    throw error;
  }
};

const date = new Date();
date.setUTCDate(date.getUTCDate()-3);
const currentDate = date.toISOString().split('T')[0] + 'T00:00:00Z';


// const data = await retrieveBars("CON.F.US.ENQ.M25","2025-06-01T00:00:00Z", "2025-06-30T23:59:00Z");
const data = []
const retrievedContracts = []

for (const contract of contractIds) {
    const { code, start, end } = contract;
    const endDate = end> currentDate ? currentDate : end; // Use current date if end is in the future
    try {
        console.log(`Retrieving bars for ${code} from ${start} to ${endDate}`);
        const bars = await retrieveBars(code, start, endDate);
        if (bars.bars?.length !== 0 && bars.bars !== null) {
          data.push(bars.bars.reverse());
          retrievedContracts.push(contract)
        }
        console.log(`Retrieved ${bars.length} bars for ${code}`);
    } catch (error) {
        console.error(`Error retrieving bars for ${code}:`, error);
    }
}

console.log(data, 'Total data chunks retrieved:', data.length);
console.log('Contracts retrieved:', retrievedContracts);
// Convert JSON to CSV
const csvData = csvjson.toCSV(data, {
        headers: 'key'
    });

// Write CSV data to file
fs.writeFile('historicBarsHour.csv', csvData, 'utf-8', (err) => {
        if (err) {
            console.error(err);
            return;
        }
        console.log('Conversion successful. CSV file created.');
    });
