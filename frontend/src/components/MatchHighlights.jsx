// Used by both document-vs-document and text-vs-web results.
export default function MatchHighlights({ percentCopied, matches }) {
  return (
    <>
      <div className="mb-4">
        <div className="mb-1 flex justify-between text-xs text-slate-400">
          <span>Copied content</span>
          <span className="font-semibold text-red-300">{percentCopied}%</span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-amber-400 to-red-500 transition-all"
            style={{ width: `${percentCopied}%` }}
          />
        </div>
      </div>

      <div className="space-y-2">
        {matches.map((m, i) => (
          <div
            key={i}
            className={
              'rounded-lg px-3 py-2 text-sm ' +
              (m.copied
                ? 'border-l-4 border-red-500 bg-red-500/10 text-slate-100'
                : 'text-slate-500')
            }
          >
            {m.sentence}
            {m.copied && m.matched_with && (
              <div className="mt-1 text-xs italic text-red-300/80">
                matches: “{m.matched_with}” ({(m.score * 100).toFixed(0)}%)
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  )
}
