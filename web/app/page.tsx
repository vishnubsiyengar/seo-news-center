"use client"
import { useEffect, useState } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Shield, Zap, Info, ExternalLink } from 'lucide-react'

// 1. Initialize Supabase (Using the keys from your shopping list)
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export default function SEODashboard() {
  const [articles, setArticles] = useState<any[]>([])

  useEffect(() => {
    async function fetchArticles() {
      const { data } = await supabase
        .from('articles')
        .select('*')
        .order('created_at', { ascending: false })
      if (data) setArticles(data)
    }
    fetchArticles()
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <header className="max-w-4xl mx-auto mb-8">
        <h1 className="text-3xl font-bold text-slate-900">SEO News Center</h1>
        <p className="text-slate-500">Uncolored Intelligence for Builders</p>
      </header>

      <main className="max-w-4xl mx-auto space-y-6">
        {articles.map((article) => (
          <div key={article.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
            {/* Card Header: Confidence Pill */}
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div className="flex items-center gap-2">
                <Shield className={`w-4 h-4 ${article.confidence_score > 7 ? 'text-emerald-500' : 'text-amber-500'}`} />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
                  Confidence: {article.confidence_score}/10
                </span>
              </div>
              <span className="text-xs text-slate-400">{new Date(article.created_at).toLocaleDateString()}</span>
            </div>

{/* Category Tag */}
<div className="mt-2 flex items-center gap-2">
  <span className="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 text-[10px] font-bold uppercase tracking-tighter">
    {article.category}
  </span>
</div>

            {/* Card Body: The MECE Summary */}
            <div className="p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">{article.source_name} Update</h2>
              
              <div className="prose prose-slate max-w-none">
                <pre className="whitespace-pre-wrap font-sans text-slate-700 text-sm leading-relaxed">
                  {article.summary_technical}
                </pre>
              </div>

              {/* Food for Thought Section */}
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
                <h3 className="flex items-center gap-2 text-blue-700 font-bold text-sm mb-2">
                  <Zap className="w-4 h-4" /> Food for Thought
                </h3>
                <ul className="list-disc list-inside text-sm text-blue-600 space-y-1">
                  {article.food_for_thought?.map((q: string, i: number) => (
                    <li key={i}>{q}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Footer: Read Original */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-100">
              <a href={article.source_url} target="_blank" className="flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-800">
                Read Original Article <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        ))}
      </main>
    </div>
  )
}