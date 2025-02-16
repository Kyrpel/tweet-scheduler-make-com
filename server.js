import express from 'express'
import multer from 'multer'
import { exec } from 'child_process'
import fs from 'fs/promises'
import path from 'path'

const app = express()
const upload = multer({ dest: 'uploads/' })

app.post('/api/schedule', upload.single('credentialsFile'), async (req, res) => {
  try {
    const { openaiKey, sheetsId, tweets } = req.body
    const credentialsFile = req.file

    // Create temporary .env file
    await fs.writeFile('.env', `
OPENAI_API_KEY=${openaiKey}
GOOGLE_SHEETS_CREDENTIALS_FILE=${credentialsFile.path}
GOOGLE_SHEETS_ID=${sheetsId}
    `)

    // Create temporary tweets file
    const tweetsPath = path.join('uploads', 'tweets.txt')
    await fs.writeFile(tweetsPath, tweets)

    // Run the Python script
    exec('python3 GPT4_make_scheduler.py', async (error, stdout, stderr) => {
      // Clean up temporary files
      await fs.unlink('.env')
      await fs.unlink(credentialsFile.path)
      await fs.unlink(tweetsPath)

      if (error) {
        console.error('Error:', error)
        return res.status(500).json({ error: error.message })
      }

      res.json({ message: 'Tweets scheduled successfully', output: stdout })
    })
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({ error: error.message })
  }
})

app.listen(3000, () => {
  console.log('Server running on port 3000')
})
