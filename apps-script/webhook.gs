/**
 * Google Apps Script Webhook Handler for Accessible Housing Matcher
 * 
 * This script receives JotForm submissions via webhook and:
 * 1. Writes data to Google Sheets (master sheet and intake sheet)
 * 2. Creates per-applicant matching sheets
 * 
 * ========================================
 * CONFIGURATION SECTION - EDIT THESE VALUES
 * ========================================
 */

// TODO: REPLACE the strings below with your own Google Sheets IDs
// You can find each ID in your sheet's URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit

// Master housing database spreadsheet (contains all available housing units)
const MASTER_SPREADSHEET_ID = '19is049RiNyvLRpo0kpU1Xub8SaI_9XkO5a7Y2ILkC5U';

// JotForm intake spreadsheet (receives submissions from JotForm)
const DATABASE_SPREADSHEET_ID = '19FO0fWMxrCjPXLIXJYAAipJAgqpN79yyfagv5IPPiHg';

// Matching spreadsheet (creates one sheet per applicant for matching results)
const MATCHING_SPREADSHEET_ID = '1N2SgUB7ef8zexv2mxHHNztRhD-iy01qvbf6yv6iBUqA';

/**
 * ========================================
 * MAIN WEBHOOK FUNCTION
 * ========================================
 * This function is called by JotForm when a form is submitted.
 * Do NOT modify the logic below - only change the IDs above.
 */

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    // Use "sheet" from JotForm to decide which tab to write to
    // JotForm should send a field called "sheet" with value "Applicants" or "Units"
    const sheetName = data.sheet || 'Sheet1';

    // Clone data & remove "sheet" key so it isn't written as a column
    const record = Object.assign({}, data);
    delete record.sheet;

    // 1) Append to master + housing database
    appendToSpreadsheet(MASTER_SPREADSHEET_ID, sheetName, record);
    appendToSpreadsheet(DATABASE_SPREADSHEET_ID, sheetName, record);

    // 2) If this is the applicant JotForm, create per-applicant matching sheet
    //    Assumes your JotForm sets sheet="Applicants" for applicant submissions.
    if (sheetName === 'Applicants') {
      createApplicantSheet(record);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * ========================================
 * HELPER FUNCTIONS
 * ========================================
 * These functions handle writing to sheets and creating applicant sheets.
 * Do NOT modify these functions.
 */

/**
 * Append a record to a given spreadsheet + sheet.
 * Tries to handle inconsistent headers by extending them as needed.
 */
function appendToSpreadsheet(spreadsheetId, sheetName, record) {
  const ss = SpreadsheetApp.openById(spreadsheetId);
  
  // Get the sheet; if it doesn't exist, create it
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }

  const keys = Object.keys(record);
  
  // Ensure header row has at least as many columns as keys
  const existingLastCol = Math.max(sheet.getLastColumn(), keys.length);
  const headerRange = sheet.getRange(1, 1, 1, existingLastCol);
  let headerValues = headerRange.getValues()[0];
  let changed = false;
  
  for (let i = 0; i < keys.length; i++) {
    if (!headerValues[i]) {
      headerValues[i] = keys[i];
      changed = true;
    }
  }
  
  if (changed) {
    headerRange.setValues([headerValues]);
  }

  // Map record values in same order as keys; tolerate missing values
  const values = keys.map(k => (k in record ? record[k] : ''));
  sheet.appendRow(values);
}

/**
 * Create a per-applicant sheet in the matching spreadsheet.
 * Uses data from the JotForm submission ("record") and sets up formulas
 * to reference the master and accessible housing databases.
 */
function createApplicantSheet(record) {
  try {
    const ss = SpreadsheetApp.openById(MATCHING_SPREADSHEET_ID);
    
    // Build a reasonably unique, safe sheet name
    const applicantName =
      record.applicantName ||
      record.fullName ||
      record.name ||
      record.firstName ||
      record.email ||
      'Applicant';

    const timestampStr = Utilities.formatDate(
      new Date(),
      Session.getScriptTimeZone(),
      'yyyyMMdd_HHmmss'
    );

    let baseName = (applicantName + ' ' + timestampStr)
      .toString()
      .replace(/[\\\/\?\*\[\]]/g, ' '); // remove illegal chars

    if (baseName.length > 80) {
      baseName = baseName.substring(0, 80);
    }

    // If you have a TEMPLATE sheet, copy it; otherwise create a blank one
    let sheet;
    const template = ss.getSheetByName('TEMPLATE');
    if (template) {
      sheet = template.copyTo(ss).setName(baseName);
    } else {
      sheet = ss.insertSheet(baseName);
    }

    // Clear any existing content if copied from template (optional)
    // Comment this out if the template has important fixed content:
    // sheet.clearContents();

    // ----- 1. Write raw applicant data (Field / Value) -----
    const keys = Object.keys(record);
    sheet.getRange(1, 1, 1, 2).setValues([['Field', 'Value']]);
    const rowData = keys.map(k => [k, record[k]]);
    if (rowData.length > 0) {
      sheet.getRange(2, 1, rowData.length, 2).setValues(rowData);
    }

    // ----- 2. Matching section (uses both databases) -----
    let startRow = rowData.length + 4;
    sheet.getRange(startRow, 1).setValue('Matching Summary');
    
    // Import master database (you can narrow down range/sheet name as needed)
    sheet.getRange(startRow + 1, 1).setValue('Master Database (CYC – Accessible Housing)');
    sheet.getRange(startRow + 1, 2).setFormula(
      `=IMPORTRANGE("${MASTER_SPREADSHEET_ID}", "Sheet1!A:Z")`
    );

    // Import accessiblehousingdatabase
    sheet.getRange(startRow + 2, 1).setValue('Accessible Housing Database (JotForm Intakes)');
    sheet.getRange(startRow + 2, 2).setFormula(
      `=IMPORTRANGE("${DATABASE_SPREADSHEET_ID}", "Sheet1!A:Z")`
    );

    // Placeholder for your matching algorithm
    // Here you can write your real formula referencing the imported ranges.
    sheet.getRange(startRow + 3, 1).setValue('Match %');
    sheet.getRange(startRow + 3, 2).setFormula(
      '=IFERROR( /* TODO: insert matching formula using imported ranges + applicant data */ 0, 0)'
    );

    // Optionally, you can freeze the header row for readability
    sheet.setFrozenRows(1);

  } catch (err) {
    // Fail softly but log so you can debug in Execution Log
    console.error('Error creating applicant sheet:', err);
  }
}

