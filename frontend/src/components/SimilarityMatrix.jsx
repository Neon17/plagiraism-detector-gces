function cellStyle(value, isDiagonal) {
  if (isDiagonal) return { background: 'rgba(255,255,255,0.06)', color: '#64748b' }
  const v = Math.max(0, Math.min(1, value))
  // teal (low) -> amber -> red (high copy)
  const r = Math.round(20 + 235 * v)
  const g = Math.round(200 - 150 * v)
  const b = Math.round(140 - 80 * v)
  return { background: `rgb(${r}, ${g}, ${b})`, color: '#0b1220' }
}

export default function SimilarityMatrix({ documents, matrix }) {
  if (!matrix) return null
  return (
    <div className="card">
      <h2 className="mb-4 text-lg font-semibold text-white">Similarity matrix</h2>
      <div className="-mx-2 overflow-x-auto px-2">
        <table className="border-separate border-spacing-1">
          <thead>
            <tr>
              {/* Sticky corner for the row labels */}
              <th className="sticky left-0 z-10 bg-slate-950/80 p-2 backdrop-blur" />
              {documents.map((d, i) => (
                <th key={i} title={d} className="p-2 text-xs font-semibold text-slate-400">
                  D{i + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, i) => (
              <tr key={i}>
                <th
                  title={documents[i]}
                  className="sticky left-0 z-10 bg-slate-950/80 p-2 text-right text-xs font-semibold text-slate-400 backdrop-blur"
                >
                  D{i + 1}
                </th>
                {row.map((val, j) => (
                  <td
                    key={j}
                    style={cellStyle(val, i === j)}
                    className="h-10 w-10 rounded-lg text-center text-xs font-bold sm:h-12 sm:w-12 sm:text-sm"
                  >
                    {i === j ? '—' : `${(val * 100).toFixed(0)}%`}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center gap-3 text-xs text-slate-400">
        <span>Low</span>
        <div className="h-2 flex-1 rounded-full bg-gradient-to-r from-teal-400 via-amber-400 to-red-500" />
        <span>High copy</span>
      </div>

      <ul className="mt-3 grid grid-cols-1 gap-x-6 text-xs text-slate-500 sm:grid-cols-2 lg:grid-cols-3">
        {documents.map((d, i) => (
          <li key={i} className="truncate" title={d}>
            D{i + 1} = {d}
          </li>
        ))}
      </ul>
    </div>
  )
}
