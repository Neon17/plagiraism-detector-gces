// Colour-coded intra-class similarity matrix (proposal step 7).
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
      <div className="overflow-x-auto">
        <table className="border-separate border-spacing-1">
          <thead>
            <tr>
              <th className="p-2" />
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
                  className="p-2 text-right text-xs font-semibold text-slate-400"
                >
                  D{i + 1}
                </th>
                {row.map((val, j) => (
                  <td
                    key={j}
                    style={cellStyle(val, i === j)}
                    className="h-12 w-12 rounded-lg text-center text-sm font-bold"
                  >
                    {i === j ? '—' : `${(val * 100).toFixed(0)}%`}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  )
}
