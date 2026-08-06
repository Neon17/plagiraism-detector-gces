import { useState } from 'react'
import FileUploader from './components/FileUploader.jsx'
import SimilarityMatrix from './components/SimilarityMatrix.jsx'
import HighlightedText from './components/HighlightedText.jsx'
import WebCheck from './components/WebCheck.jsx'
import { compareDocuments } from './api.js'

export default function App() {
  const [tab, setTab] = useState('batch')
  const [files, setFiles] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [method, setMethod] = useState('sbert')
  const [threshold, setThreshold] = useState(0.7)

  async function handleCompare(filesToUse) {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await compareDocuments(filesToUse ?? files, method, threshold)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const flaggedCount = result?.flagged_pairs?.length ?? 0
  const skipped = result?.skipped ?? []

  return (
    <div className="mx-auto max-w-4xl px-5 py-10">
      {/* Hero */}
      <header className="mb-8 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-medium text-slate-300">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
          Free · No login · Powered by Sentence-BERT
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight">
          <span className="gradient-text">Plagiarism Detector</span>
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-slate-400">
          Upload a batch of documents and instantly see who copied from whom — with a
          similarity matrix and sentence-level highlights.
        </p>
      </header>

      {/* Tabs */}
      <div className="mx-auto mb-6 flex w-fit gap-1 rounded-full border border-white/10 bg-white/5 p-1">
        <TabButton active={tab === 'batch'} onClick={() => setTab('batch')}>
          Compare documents
        </TabButton>
        <TabButton active={tab === 'web'} onClick={() => setTab('web')}>
          Check against web
        </TabButton>
      </div>

      {tab === 'web' ? (
        <WebCheck />
      ) : (
        <>
          <FileUploader
            files={files}
            setFiles={setFiles}
            onCompare={handleCompare}
            loading={loading}
          />

          <Settings
            method={method}
            setMethod={setMethod}
            threshold={threshold}
            setThreshold={setThreshold}
            disabled={loading}
          />

          {error && (
            <div className="my-4 flex items-center gap-3 rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">
              <span className="text-xl">⚠️</span>
              {error}
            </div>
          )}

          {result && (
            <div className="mt-8 space-y-6">
              {/* Summary stats */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <StatCard label="Documents" value={result.documents.length} />
                <StatCard
                  label="Flagged pairs"
                  value={flaggedCount}
                  highlight={flaggedCount > 0}
                />
                <StatCard
                  label="Model"
                  value={result.model_fine_tuned ? 'Fine-tuned' : 'Pretrained'}
                  small
                />
              </div>

              {skipped.length > 0 && (
                <div className="rounded-2xl border border-amber-500/40 bg-amber-500/10 p-4 text-sm text-amber-200">
                  <p className="mb-1 font-medium">Some files were skipped:</p>
                  <ul className="list-inside list-disc space-y-0.5">
                    {skipped.map((s) => (
                      <li key={s.name}>
                        {s.name} — {s.error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <SimilarityMatrix documents={result.documents} matrix={result.matrix} />
              <ScoreLegend threshold={result.threshold} />
              <HighlightedText pairs={result.flagged_pairs} />
            </div>
          )}
        </>
      )}

      <footer className="mt-16 text-center text-xs text-slate-500">
        Built for Project II · Gandaki College of Engineering and Science
      </footer>
    </div>
  )
}

function Settings({ method, setMethod, threshold, setThreshold, disabled }) {
  return (
    <div className="card mt-4 flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
      <label className="flex items-center gap-3 text-sm text-slate-300">
        <span className="whitespace-nowrap">Engine</span>
        <select
          value={method}
          disabled={disabled}
          onChange={(e) => setMethod(e.target.value)}
          className="rounded-lg border border-white/10 bg-slate-900 px-3 py-1.5 text-sm text-slate-100"
        >
          <option value="sbert">Sentence-BERT (semantic)</option>
          <option value="tfidf">TF-IDF (baseline)</option>
        </select>
      </label>

      <label className="flex flex-1 items-center gap-3 text-sm text-slate-300 sm:max-w-xs">
        <span className="whitespace-nowrap">Threshold</span>
        <input
          type="range"
          min="0.4"
          max="0.95"
          step="0.05"
          value={threshold}
          disabled={disabled}
          onChange={(e) => setThreshold(Number(e.target.value))}
          className="flex-1 accent-sky-500"
        />
        <span className="w-10 text-right font-mono text-sky-300">
          {threshold.toFixed(2)}
        </span>
      </label>
    </div>
  )
}

function ScoreLegend({ threshold }) {
  const bands = [
    { color: 'bg-emerald-400', label: 'Below 0.40 — unrelated' },
    { color: 'bg-amber-400', label: '0.40 to 0.70 — same topic, worth a look' },
    { color: 'bg-red-400', label: `Above ${Number(threshold ?? 0.7).toFixed(2)} — flagged as copied` },
  ]
  return (
    <div className="card flex flex-col gap-2 p-4 text-xs text-slate-400 sm:flex-row sm:gap-6">
      {bands.map((b) => (
        <span key={b.label} className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${b.color}`} />
          {b.label}
        </span>
      ))}
    </div>
  )
}

function TabButton({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={
        'rounded-full px-5 py-2 text-sm font-medium transition ' +
        (active ? 'bg-sky-500 text-white shadow' : 'text-slate-300 hover:text-white')
      }
    >
      {children}
    </button>
  )
}

function StatCard({ label, value, highlight, small }) {
  return (
    <div className="card flex flex-col items-center justify-center py-5 text-center">
      <span
        className={
          (small ? 'text-lg ' : 'text-3xl ') +
          'font-bold ' +
          (highlight ? 'text-red-400' : 'text-sky-300')
        }
      >
        {value}
      </span>
      <span className="mt-1 text-xs uppercase tracking-wide text-slate-400">{label}</span>
    </div>
  )
}
