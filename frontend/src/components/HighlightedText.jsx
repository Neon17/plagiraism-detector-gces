import MatchHighlights from './MatchHighlights.jsx'

export default function HighlightedText({ pairs }) {
  if (!pairs || pairs.length === 0) {
    return (
      <div className="card text-center">
        <h2 className="text-lg font-semibold text-white">No plagiarism detected</h2>
        <p className="text-sm text-slate-400">No document pair crossed the threshold.</p>
      </div>
    )
  }
  return (
    <div className="space-y-5">
      {pairs.map((pair, idx) => (
        <div key={idx} className="card">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h3 className="font-semibold text-white">
              {pair.doc_a} <span className="text-slate-500">vs</span> {pair.doc_b}
            </h3>
            <span className="rounded-full bg-red-500/20 px-3 py-1 text-sm font-semibold text-red-300">
              similarity {(pair.score * 100).toFixed(0)}%
            </span>
          </div>

          <MatchHighlights percentCopied={pair.percent_copied} matches={pair.matches} />
        </div>
      ))}
    </div>
  )
}
