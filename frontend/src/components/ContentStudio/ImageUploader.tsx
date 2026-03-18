import { useRef, useState } from 'react'
import { imagesApi } from '../../api/client'

export default function ImageUploader({ campaignId }: { campaignId: string }) {
  const [uploading, setUploading] = useState(false)
  const [urls, setUrls] = useState<Record<string, string> | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    setUploading(true)
    try {
      const res = await imagesApi.upload(campaignId || 'default', file)
      setUrls(res.data.urls)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Image Upload</h3>
      <div
        className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center cursor-pointer hover:border-primary-400 transition-colors"
        onClick={() => inputRef.current?.click()}
        onDragOver={e => e.preventDefault()}
        onDrop={e => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
      >
        <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }} />
        {uploading ? (
          <p className="text-sm text-gray-500 animate-pulse">Uploading and resizing...</p>
        ) : (
          <>
            <p className="text-gray-400 text-3xl mb-2">📷</p>
            <p className="text-sm text-gray-500">Drag & drop or click to upload</p>
            <p className="text-xs text-gray-400 mt-1">Auto-resized for all platforms</p>
          </>
        )}
      </div>
      {urls && (
        <div className="mt-4 space-y-1">
          {Object.entries(urls).map(([platform, url]) => (
            <div key={platform} className="flex items-center justify-between text-xs">
              <span className="text-gray-500">{platform}</span>
              <a href={url} target="_blank" rel="noreferrer" className="text-primary-600 hover:underline truncate max-w-xs">{url}</a>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
