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

  async function handleCompare(filesToUse) {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await compareDocuments(filesToUse ?? files, 'sbert')
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const flaggedCount = result?.flagged_pairs?.length ?? 0

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

          {error && (
            <div className="my-4 flex items-center gap-3 rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">
              <span className="text-xl">⚠️</span>
              {error}
            </div>
          )}

          {result && (
            <div className="mt-8 space-y-6">
              {/* Summary stats */}
              <div className="grid grid-cols-3 gap-4">
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

              <SimilarityMatrix documents={result.documents} matrix={result.matrix} />
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
