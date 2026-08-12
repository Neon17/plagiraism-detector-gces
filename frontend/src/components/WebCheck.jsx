import { useRef, useState } from 'react'
import { checkWeb } from '../api.js'
import MatchHighlights from './MatchHighlights.jsx'

export default function WebCheck() {
  const [mode, setMode] = useState('text') // 'text' | 'file'
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [urls, setUrls] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  async function run() {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const urlList = urls
        .split('\n')
        .map((u) => u.trim())
        .filter(Boolean)
      const payload = { urls: urlList.length ? urlList : undefined }
      if (mode === 'file') payload.file = file
      else payload.text = text
      const data = await checkWeb(payload)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const canSubmit = mode === 'file' ? !!file : text.trim().length >= 20

  return (
    <div className="card">
      <h2 className="mb-1 text-lg font-semibold text-white">Check against the web</h2>
      <p className="mb-4 text-sm text-slate-400">
        Paste text or upload a document to search the internet for matching pages. Optionally
        add specific URLs (one per line) to compare against directly.
      </p>

      <div className="mb-4 flex w-fit gap-1 rounded-xl border border-white/10 bg-white/5 p-1">
        <ModeButton active={mode === 'text'} onClick={() => setMode('text')}>
          Paste text
        </ModeButton>
        <ModeButton active={mode === 'file'} onClick={() => setMode('file')}>
          Upload file
        </ModeButton>
      </div>

      {mode === 'text' ? (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
          placeholder="Paste the text you want to check…"
          className="w-full rounded-xl border border-white/10 bg-slate-900/60 p-3 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-sky-400"
        />
      ) : (
        <div
          onClick={() => inputRef.current?.click()}
          className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-white/15 p-6 text-center transition hover:border-sky-400/60 hover:bg-white/5"
        >
          {file ? (
            <p className="text-sm text-slate-200">
              Selected: <span className="font-medium text-sky-300">{file.name}</span>
            </p>
          ) : (
            <>
              <p className="text-sm font-medium text-slate-200">
                Click to <span className="text-sky-400">browse</span> a document
              </p>
              <p className="mt-1 text-xs text-slate-500">PDF · DOCX · TXT · PNG · JPG</p>
            </>
          )}
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="hidden"
          />
        </div>
      )}

      <textarea
        value={urls}
        onChange={(e) => setUrls(e.target.value)}
        rows={2}
        placeholder="Optional: https://example.com/page  (one URL per line)"
        className="mt-3 w-full rounded-xl border border-white/10 bg-slate-900/60 p-3 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-sky-400"
      />

      <button
        disabled={!canSubmit || loading}
        onClick={run}
        className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 px-5 py-3 font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:from-indigo-400 hover:to-purple-400 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
            Searching the web…
          </>
        ) : (
          'Check the web'
        )}
      </button>

      {error && (
        <div className="mt-4 rounded-xl border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-5">
          {result.sources.length === 0 ? (
            <p className="text-sm text-slate-400">
              No matching web pages found (or the search was blocked — try pasting specific URLs).
            </p>
          ) : (
            <ul className="space-y-2">
              {result.sources.map((s, i) => (
                <SourceRow key={i} source={s} />
              ))}
            </ul>
          )}
        </div>
      )}
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

function SourceRow({ source }) {
  const [open, setOpen] = useState(false)
  const hasCopied = source.matches?.some((m) => m.copied)

  return (
    <li className="overflow-hidden rounded-xl border border-white/10 bg-white/5">
      <div className="flex items-center justify-between gap-3 p-3">
        <a
          href={source.url}
          target="_blank"
          rel="noreferrer"
          className="max-w-[60%] truncate text-sm text-sky-300 hover:underline"
        >
          {source.url}
        </a>
        <div className="flex items-center gap-2">
          <span
            className={
              'rounded-full px-3 py-1 text-sm font-semibold ' +
              (source.plagiarised
                ? 'bg-red-500/20 text-red-300'
                : 'bg-emerald-500/20 text-emerald-300')
            }
          >
            {(source.score * 100).toFixed(0)}%
          </span>
          <button
            onClick={() => setOpen(!open)}
            aria-label={open ? 'Collapse' : 'Expand'}
            className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 transition hover:bg-white/10 hover:text-white"
          >
            <svg
              className={'h-4 w-4 transition-transform ' + (open ? 'rotate-180' : '')}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-white/10 p-3">
          {hasCopied ? (
            <MatchHighlights percentCopied={source.percent_copied} matches={source.matches} />
          ) : (
            <p className="text-sm text-slate-400">
              No copied sentences found on this page — the overall similarity is topical, not
              copied text.
            </p>
          )}
        </div>
      )}
    </li>
  )
}
