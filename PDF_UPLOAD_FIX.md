# PDF upload freeze fix

The old `main.py` sent every PDF page, including rendered scan images, into
one Gemini Live conversation turn. Large PDFs could fill the Live context or
leave the upload worker waiting, which made voice and typed commands appear
dead after upload.

The updated `main.py` changes the flow:

1. A PDF is registered locally and its page count is checked.
2. Only a short `[DOCUMENT_READY]` message is sent to Gemini Live.
3. Follow-up requests use `document_engine` locally:
   - `mode="question"` for a page/question number or year/question number
   - `mode="search"` for a topic
   - `mode="repeated"` for duplicate questions
   - `mode="export_questions"` or `mode="export_repeated"` for Desktop PDFs
4. The audio and typed-command loop is not flooded with PDF contents.

Replace `main.py` along with the other files in `Nexa-PDF-Reading-Fix-v3.zip`.
The resulting package is a v4 fix and includes this document.