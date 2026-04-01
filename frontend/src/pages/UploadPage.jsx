import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, Film, CheckCircle, AlertCircle } from 'lucide-react'
import { uploadVideo, startProcessing } from '../api'

export default function UploadPage() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState(0)

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      setFile(accepted[0])
      setError(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm'] },
    maxFiles: 1,
    maxSize: 500 * 1024 * 1024,
  })

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError(null)

    try {
      setProgress(30)
      const result = await uploadVideo(file)
      setProgress(70)

      await startProcessing(result.match_id)
      setProgress(100)

      setTimeout(() => {
        navigate(`/processing/${result.match_id}`)
      }, 500)
    } catch (e) {
      setError(e.message)
      setUploading(false)
      setProgress(0)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-xl w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">Upload Match Video</h1>
          <p className="mt-2 text-white/50 text-sm">
            Drag & drop a football match video to begin AI-powered analysis
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`
            glass-hover cursor-pointer p-12 text-center transition-all duration-300
            ${isDragActive ? 'border-accent bg-accent/5 shadow-glow' : ''}
            ${file ? 'border-green-500/30 bg-green-500/5' : ''}
          `}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-4">
            {file ? (
              <>
                <div className="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center">
                  <Film className="w-8 h-8 text-green-400" />
                </div>
                <div>
                  <p className="font-medium text-white">{file.name}</p>
                  <p className="text-sm text-white/40 mt-1">
                    {(file.size / (1024 * 1024)).toFixed(1)} MB
                  </p>
                </div>
              </>
            ) : (
              <>
                <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center">
                  <Upload className="w-8 h-8 text-white/30" />
                </div>
                <div>
                  <p className="font-medium text-white/70">
                    {isDragActive ? 'Drop video here' : 'Click or drag video file'}
                  </p>
                  <p className="text-sm text-white/30 mt-1">
                    MP4, AVI, MOV, MKV up to 500MB
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {uploading && (
          <div className="space-y-2">
            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-accent rounded-full transition-all duration-700 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-white/40 text-center">
              {progress < 50 ? 'Uploading...' : progress < 90 ? 'Starting analysis...' : 'Redirecting...'}
            </p>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-3 p-4 rounded-lg bg-red-500/10 border border-red-500/20">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`w-full btn-primary py-3 text-base ${
            !file || uploading ? 'opacity-40 cursor-not-allowed' : ''
          }`}
        >
          {uploading ? 'Processing...' : 'Analyze Match'}
        </button>
      </div>
    </div>
  )
}
