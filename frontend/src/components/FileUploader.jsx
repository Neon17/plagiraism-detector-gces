import { useRef, useState } from 'react'

export default function FileUploader({ files, setFiles, onCompare, loading }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [mode, setMode] = useState('upload') // 'upload' | 'text'
  const [texts, setTexts] = useState(['', ''])

  function addFiles(list) {
    setFiles([...files, ...Array.from(list)])
  }
  function removeFile(index) {
    setFiles(files.filter((_, i) => i !== index))
  }
  function onDrop(e) {
    e.preventDefault()
    setDragging(false)
    if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files)
  }

  function updateText(index, value) {
    setTexts(texts.map((t, i) => (i === index ? value : t)))
  }
  function addTextDoc() {
    setTexts([...texts, ''])
  }
  function removeTextDoc(index) {
    setTexts(texts.filter((_, i) => i !== index))
  }

  function handleSubmit() {
    if (mode === 'text') {
      const filledTexts = texts.filter((t) => t.trim())
      const textFiles = filledTexts.map(
        (t, i) => new File([t], `document-${i + 1}.txt`, { type: 'text/plain' })
      )
      onCompare(textFiles)
    } else {
      onCompare(files)
    }
  }

  const canSubmit =
    mode === 'upload'
      ? files.length >= 2
      : texts.filter((t) => t.trim()).length >= 2

  return (
    <div className="card">
      <div className="mb-5 flex gap-1 rounded-xl border border-white/10 bg-white/5 p-1 w-fit">
        <ModeButton active={mode === 'upload'} onClick={() => setMode('upload')}>
          Upload files
        </ModeButton>
        <ModeButton active={mode === 'text'} onClick={() => setMode('text')}>
          Type text
        </ModeButton>
      </div>

      {mode === 'upload' ? (
        <>
          <h2 className="mb-1 text-lg font-semibold text-white">Upload documents</h2>
          <p className="mb-4 text-sm text-slate-400">
            Add 2 or more files — PDF, DOCX, TXT, or images (OCR).
          </p>

          <div
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={
              'flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition ' +
              (dragging
                ? 'border-sky-400 bg-sky-400/10'
                : 'border-white/15 hover:border-sky-400/60 hover:bg-white/5')
            }
          >
            <svg className="mb-3 h-10 w-10 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5V18a2 2 0 002 2h14a2 2 0 002-2v-1.5M12 3v13.5M12 3l-4 4m4-4l4 4" />
            </svg>
            <p className="font-medium text-slate-200">
              Drag &amp; drop files here, or <span className="text-sky-400">browse</span>
            </p>
            <p className="mt-1 text-xs text-slate-500">PDF · DOCX · TXT · PNG · JPG</p>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
              onChange={(e) => addFiles(e.target.files)}
              className="hidden"
            />
          </div>

          {files.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {files.map((f, i) => (
                <span key={i} className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 py-1 pl-3 pr-1.5 text-sm text-slate-200">
                  <span className="max-w-[12rem] truncate">{f.name}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); removeFile(i) }}
                    className="flex h-5 w-5 items-center justify-center rounded-full bg-white/10 text-slate-400 hover:bg-red-500/30 hover:text-red-300"
                  >×</button>
                </span>
              ))}
            </div>
          )}
        </>
      ) : (
        <>
          <h2 className="mb-1 text-lg font-semibold text-white">Paste or type text</h2>
          <p className="mb-4 text-sm text-slate-400">Enter 2 or more documents to compare.</p>

          <div className="space-y-3">
            {texts.map((t, i) => (
              <div key={i}>
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">Document {i + 1}</span>
                  {texts.length > 2 && (
                    <button
                      onClick={() => removeTextDoc(i)}
                      className="text-xs text-slate-500 hover:text-red-400 transition"
                    >
                      Remove
                    </button>
                  )}
                </div>
                <textarea
                  value={t}
                  onChange={(e) => updateText(i, e.target.value)}
                  placeholder={`Paste document ${i + 1} here…`}
                  rows={5}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-sky-500/60 focus:ring-1 focus:ring-sky-500/30 resize-y transition"
                />
              </div>
            ))}
          </div>

          <button
            onClick={addTextDoc}
            className="mt-3 text-sm text-sky-400 hover:text-sky-300 transition"
          >
            + Add another document
          </button>
        </>
      )}

      <button
        disabled={!canSubmit || loading}
        onClick={handleSubmit}
        className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 px-5 py-3 font-semibold text-white shadow-lg shadow-sky-500/20 transition hover:from-sky-400 hover:to-indigo-400 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
            Analyzing…
          </>
        ) : (
          'Check plagiarism'
        )}
      </button>
    </div>
  )
}

function ModeButton({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={
        'rounded-lg px-4 py-1.5 text-sm font-medium transition ' +
        (active ? 'bg-sky-500 text-white shadow' : 'text-slate-400 hover:text-white')
      }
    >
      {children}
    </button>
  )
}
