# Quick Reference Card

Keep this handy while setting up the system.

## 📋 Configuration Checklist

### Apps Script (`apps-script/webhook.gs`)
- [ ] `MASTER_SPREADSHEET_ID` = Your master housing sheet ID
- [ ] `DATABASE_SPREADSHEET_ID` = Your JotForm intake sheet ID  
- [ ] `MATCHING_SPREADSHEET_ID` = Your matching spreadsheet ID

### Frontend (`frontend/src/config.js`)
- [ ] `API_URL` = Your backend API URL (or `http://localhost:8000` for local)
- [ ] `JOTFORM_APPLICANT_URL` = Your applicant form URL
- [ ] `JOTFORM_LANDLORD_URL` = Your landlord form URL
- [ ] `LOGO_URL` = Your logo URL (optional)

### JotForm
- [ ] Applicant form webhook → Apps Script Web App URL
- [ ] Landlord form webhook → Apps Script Web App URL
- [ ] Hidden field `sheet` = `"Applicants"` (applicant form)
- [ ] Hidden field `sheet` = `"Units"` (landlord form)

## 🔗 How to Find IDs

### Google Sheets ID
URL format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- Copy the long string between `/d/` and `/edit`

### JotForm Form ID
URL format: `https://form.jotform.com/FORM_ID`
- Copy the number at the end

### Apps Script Web App URL
After deploying:
1. Deploy → New deployment → Web app
2. Copy the URL (ends with `/exec`)

## ✅ Testing Checklist

1. Submit test entry in JotForm
2. Check intake spreadsheet → Should see new row
3. Check master spreadsheet → Should see new row
4. Check matching spreadsheet → Should see new sheet (for applicants)
5. Test frontend → Fill form, see matches appear

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Data not in sheets | Check Apps Script execution log |
| Frontend not loading | Check browser console (F12), verify API_URL |
| Webhook not working | Verify URL ends with `/exec`, check execution log |
| IMPORTRANGE error | Grant permission when prompted |

## 📞 Support Resources

- **Apps Script Execution Log**: script.google.com → Your project → Executions
- **Browser Console**: Press F12 → Console tab
- **JotForm Webhook Log**: JotForm → Form → Integrations → Webhooks → View logs

